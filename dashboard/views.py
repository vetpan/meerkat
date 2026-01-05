"""
Dashboard Views
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.cache import cache
from shared.models import Target


# Scan progress states
SCAN_STATES = {
    'idle': {'step': 0, 'message': 'Klaar'},
    'starting': {'step': 1, 'message': 'Scan starten...'},
    'scout': {'step': 2, 'message': 'Wijzigingen detecteren...'},
    'no_change': {'step': 2, 'message': 'Geen wijzigingen gevonden'},
    'capture': {'step': 3, 'message': 'Screenshot maken...'},
    'gemini': {'step': 4, 'message': 'AI analyse uitvoeren...'},
    'saving': {'step': 5, 'message': 'Resultaten opslaan...'},
    'complete': {'step': 6, 'message': 'Scan voltooid!'},
    'failed': {'step': -1, 'message': 'Scan mislukt'}
}


def set_scan_progress(target_id: int, state: str, detail: str = None):
    """Set scan progress in cache for real-time polling"""
    progress = SCAN_STATES.get(state, SCAN_STATES['idle']).copy()
    progress['state'] = state
    if detail:
        progress['detail'] = detail
    cache.set(f'scan_progress_{target_id}', progress, timeout=300)


def get_scan_progress(target_id: int) -> dict:
    """Get scan progress from cache"""
    return cache.get(f'scan_progress_{target_id}', SCAN_STATES['idle'].copy())


def index(request):
    """
    Dashboard homepage met target lijst en scan timeline
    """
    # Haal alle targets op
    # Waarom prefetch_related: Voorkomt N+1 queries voor scans
    targets = Target.objects.all().prefetch_related('scans').order_by('-created_at')
    
    # Check of er een target is geselecteerd
    selected_target_id = request.GET.get('target')
    selected_target = None
    scans = []
    
    if selected_target_id:
        try:
            selected_target = Target.objects.prefetch_related('scans').get(id=selected_target_id)
            # Haal scans op, nieuwste eerst
            # Waarom order_by('-scanned_at'): Timeline van nieuw naar oud
            scans = selected_target.scans.filter(status='success').order_by('-scanned_at')[:20]
        except Target.DoesNotExist:
            pass
    elif targets.exists():
        # Selecteer eerste target als er geen is geselecteerd
        selected_target = targets.first()
        scans = selected_target.scans.filter(status='success').order_by('-scanned_at')[:20]
    
    context = {
        'targets': targets,
        'selected_target': selected_target,
        'scans': scans,
    }
    
    return render(request, 'dashboard/index.html', context)


def faq(request):
    """FAQ page - redirects to help FAQ"""
    from django.shortcuts import redirect
    return redirect('dashboard:help_faq')


# ==========================================
# Help Section Views
# ==========================================

def help_index(request):
    """Help center landing page"""
    return render(request, 'dashboard/help/index.html')


def help_getting_started(request):
    """Getting started guide"""
    return render(request, 'dashboard/help/getting_started.html')


def help_targets(request):
    """Managing targets documentation"""
    return render(request, 'dashboard/help/targets.html')


def help_scans(request):
    """Scans and analysis documentation"""
    return render(request, 'dashboard/help/scans.html')


def help_features(request):
    """Features and capabilities documentation"""
    return render(request, 'dashboard/help/features.html')


def help_faq(request):
    """Frequently asked questions"""
    return render(request, 'dashboard/help/faq.html')



@require_POST
def trigger_scan(request, target_id):
    """
    Trigger een scan via API (HTMX)
    
    Waarom Celery: Background tasks voor long-running processes
    Fallback naar threading als Celery niet draait
    
    Manual scans use force_capture=True to skip scout check for speed
    """
    try:
        target = Target.objects.get(id=target_id)
        
        # Probeer Celery task te starten
        # Waarom try/except: Celery kan niet draaien in development
        try:
            from django.conf import settings
            # Forceer threading in development (DEBUG=True) omdat er waarschijnlijk geen worker draait
            if settings.DEBUG:
                raise Exception("Development mode: Use threading fallback")

            from collector.tasks import scan_target_task
            scan_target_task.delay(target_id)
        except Exception:
            # Fallback naar threading als Celery niet werkt
            # Use force_capture=True to skip scout check (faster for manual scans)
            import threading
            from collector.scanner.full_scan import perform_full_scan
            
            def run_scan():
                try:
                    set_scan_progress(target_id, 'starting')
                    # Use force_capture=False to check for changes first (saves resources)
                    perform_full_scan(target_id, force_capture=False)
                    set_scan_progress(target_id, 'complete')
                except Exception as e:
                    set_scan_progress(target_id, 'failed', str(e))
            
            thread = threading.Thread(target=run_scan)
            thread.daemon = True
            thread.start()
        
        # Set initial progress
        set_scan_progress(target_id, 'starting')
        
        return JsonResponse({
            'success': True,
            'message': f'Scan started for {target.name}',
            'estimated_time': '~15-20 seconds'
        })
        
    except Target.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Target not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def scan_status(request, target_id):
    """Get current scan progress for a target"""
    progress = get_scan_progress(target_id)
    progress['target_id'] = target_id
    return JsonResponse(progress)


@require_POST
def toggle_target(request, target_id):
    """Toggle target active/paused"""
    import json as json_lib
    try:
        target = Target.objects.get(id=target_id)
        data = json_lib.loads(request.body)
        
        target.status = 'active' if data.get('active') else 'paused'
        target.save()
        
        return JsonResponse({'success': True, 'status': target.status})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST  
def create_target(request):
    """Create new target and optionally start first scan"""
    try:
        name = request.POST.get('name')
        url = request.POST.get('url')
        interval = request.POST.get('interval', 15)
        
        # Check for duplicates
        if Target.objects.filter(url=url).exists():
            return JsonResponse({'success': False, 'error': 'Deze site wordt al gemonitord.'}, status=400)

        target = Target.objects.create(
            name=name,
            url=url,
            interval=int(interval),
            status='active'
        )
        
        # Start eerste scan automatisch via Celery
        try:
            from collector.tasks import scan_target_task
            scan_target_task.delay(target.id)
        except Exception:
            # Fallback naar threading
            import threading
            from collector.scanner.full_scan import perform_full_scan
            
            def run_scan():
                perform_full_scan(target.id)
            
            thread = threading.Thread(target=run_scan)
            thread.daemon = True
            thread.start()
        
        return JsonResponse({'success': True, 'id': target.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def update_target(request, target_id):
    """Update target"""
    import json as json_lib
    try:
        target = Target.objects.get(id=target_id)
        data = json_lib.loads(request.body)
        
        target.name = data.get('name', target.name)
        target.url = data.get('url', target.url)
        target.interval = int(data.get('interval', target.interval))
        target.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def delete_target(request, target_id):
    """Delete target"""
    try:
        Target.objects.get(id=target_id).delete()
        return JsonResponse({'success': True})
    except Target.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Target not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def delete_scan(request, scan_id):
    """Delete individual scan and its screenshot"""
    try:
        from shared.models import Scan
        import os
        
        scan = Scan.objects.get(id=scan_id)
        target_id = scan.target_id
        
        # Delete screenshot file if exists
        if scan.screenshot_path:
            if os.path.exists(scan.screenshot_path):
                os.remove(scan.screenshot_path)
        
        # Delete the scan record
        scan.delete()
        
        return JsonResponse({'success': True, 'target_id': target_id})
    except Scan.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Scan not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def matrix_view(request):
    """
    Comparison Matrix View
    Shows side-by-side comparison of latest baselines for all active targets.
    """
    targets = Target.objects.filter(status='active').order_by('name')
    matrix_data = []
    
    # Define the rows we want to show
    categories = [
        {'id': 'MARKETING_BOODSCHAP', 'label': 'Marketing & Boodschap', 'icon': '📣'},
        {'id': 'PROMOTIE', 'label': 'Acties & Promoties', 'icon': '🏷️'},
        {'id': 'PRIJS', 'label': 'Prijzen & Tarieven', 'icon': '💎'},
        {'id': 'PRODUCTEN_DIENSTEN', 'label': 'Producten & Aanbod', 'icon': '📦'},
    ]
    
    for target in targets:
        # Find latest baseline scan
        # We iterate to find the first 'baseline' type because Django JSON lookup can be database dependent
        scans = target.scans.filter(status='success').order_by('-scanned_at')[:20] # optimizations
        
        baseline_scan = None
        for scan in scans:
            if scan.analysis_json and scan.analysis_json.get('type') == 'baseline':
                baseline_scan = scan
                break
        
        # Build data dictionary for this target { category_id: text }
        cat_data = {}
        if baseline_scan and 'baseline' in baseline_scan.analysis_json:
            for item in baseline_scan.analysis_json['baseline']:
                cat_data[item.get('category')] = item.get('status')
        
        matrix_data.append({
            'target': target,
            'scan': baseline_scan,
            'data': cat_data
        })
    
    context = {
        'matrix_data': matrix_data,
        'categories': categories,
    }
    
    return render(request, 'dashboard/matrix.html', context)


