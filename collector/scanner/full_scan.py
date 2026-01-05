"""
Full Scan Pipeline - Complete scan flow

Combineert Scout + Capture + Gemini:

1. Scout check (snel, goedkoop)
2. Als hash ZELFDE → Stop (geen wijziging)
3. Als hash ANDERS → Capture screenshot
4. Gemini analyse
5. Database opslaan

Waarom deze volgorde:
- Scout is snel/goedkoop → eerst doen
- Capture is langzaam/duur → alleen bij wijziging
- Gemini kost geld → alleen bij wijziging
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from django.utils import timezone

# Setup Django
django_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(django_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from shared.models import Target, Scan
from collector.scanner.scout import scout_scan_sync
from collector.scanner.capture import capture_screenshot_sync
from collector.analyzer.gemini import analyze_screenshot
from dashboard.views import set_scan_progress


def perform_full_scan(target_id: int, force_capture: bool = False) -> dict:
    """
    Voer een complete scan uit van een target.
    
    Flow:
    1. Scout check (hash) - skipped if force_capture=True
    2. Als geen wijziging → Stop
    3. Als wijziging → Capture + Gemini
    4. Save to database
    
    Args:
        target_id: Database ID van target
        force_capture: If True, skip scout check and go directly to capture (faster for manual scans)
        
    Returns:
        {
            'success': bool,
            'scan_id': int (optional),
            'changed': bool,
            'message': str,
            'error': str (optional)
        }
    """
    result = {
        'success': False,
        'scan_id': None,
        'changed': False,
        'message': '',
        'error': None
    }
    
    try:
        # Get target from database
        # Waarom try/except: Target kan verwijderd zijn
        target = Target.objects.get(id=target_id)
        
        print(f"\n{'='*60}")
        print(f"🎯 Scanning: {target.name}")
        print(f"   URL: {target.url}")
        if force_capture:
            print(f"   ⚡ FAST MODE: Skipping scout check")
        print(f"{'='*60}\n")
        
        new_hash = None
        
        if not force_capture:
            # STEP 1: Scout check (hash)
            # Waarom eerst: Snel en goedkoop
            set_scan_progress(target_id, 'scout')
            print("🔍 Step 1: Scout mode (hash check)...")
            scout_result = scout_scan_sync(target.url)
            
            if not scout_result['success']:
                result['error'] = f"Scout failed: {scout_result['error']}"
                return result
            
            new_hash = scout_result['hash']
            print(f"   ✅ Hash: {new_hash}")
            print(f"   📸 Images: {scout_result['image_count']}")
            
            # Check if changed
            # Waarom target.last_hash: Vergelijk met vorige scan
            changed = target.last_hash != new_hash if target.last_hash else True
            result['changed'] = changed
            
            if not changed:
                # No change detected
                print(f"\n   ✓ No changes detected")
                print(f"   Hash matches previous scan\n")
                
                # Notify UI
                set_scan_progress(target_id, 'no_change')
                
                result['success'] = True
                result['message'] = 'No changes detected'
                
                # Update last_scan_at maar niet last_hash
                target.last_scan_at = timezone.now()
                target.save()
                
                return result
            
            # Change detected!
            print(f"\n🔄 CHANGE DETECTED!")
            print(f"   Old hash: {target.last_hash or 'None (eerste scan)'}")
            print(f"   New hash: {new_hash}\n")
        else:
            # Force capture mode - skip scout, mark as changed
            # Generate a unique hash based on timestamp (will be accurate after Gemini analyzes)
            import hashlib
            new_hash = hashlib.md5(f"{target.id}_{datetime.now().isoformat()}".encode()).hexdigest()
            result['changed'] = True
            print("⚡ Skipping scout check - going directly to capture...")
        
        # STEP 2: Capture screenshot
        # Waarom nu: Alleen bij wijziging (screenshots zijn groot/duur)
        set_scan_progress(target_id, 'capture')
        print("📸 Step 2: Capture mode (screenshot)...")
        
        # Create screenshot filename met absoluut pad
        # Waarom timestamp: Unieke naam per scan
        # Waarom absoluut: Crawlee kan vanuit andere dir draaien
        from django.conf import settings
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_filename = f"{target.id}_{timestamp}.png"
        screenshot_path = Path(settings.BASE_DIR) / 'storage' / 'screenshots' / screenshot_filename
        
        # Ensure screenshots directory exists
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"   💾 Screenshot path: {screenshot_path}")
        capture_result = capture_screenshot_sync(target.url, str(screenshot_path))
        
        if not capture_result['success']:
            result['error'] = f"Capture failed: {capture_result['error']}"
            
            # Create failed scan record
            scan = Scan.objects.create(
                target=target,
                screenshot_path='',
                content_hash=new_hash,
                status='failed',
                error_message=result['error']
            )
            
            return result
        
        print(f"   ✅ Screenshot saved: {screenshot_filename}\n")
        
        # STEP 3: Gemini analyse
        # Waarom laatste: Duurste operatie, alleen als screenshot OK is
        set_scan_progress(target_id, 'gemini')
        print("🤖 Step 3: Gemini AI analyse...")
        
        # Haal vorige scan op voor vergelijking
        # Waarom: Gemini heeft context nodig voor "Was X -> Is Y"
        previous_scan = target.scans.filter(
            status='success',
            analysis_json__isnull=False
        ).order_by('-scanned_at').first()
        
        previous_analysis = previous_scan.analysis_json if previous_scan else None
        
        if previous_analysis:
            print(f"   📊 Comparing with previous scan (#{previous_scan.id})...")
        else:
            print(f"   📊 Baseline scan (first analysis)...")
        
        gemini_result = analyze_screenshot(
            str(screenshot_path), 
            target.name,
            previous_analysis=previous_analysis
        )
        
        if not gemini_result['success']:
            result['error'] = f"Gemini failed: {gemini_result['error']}"
            
            # Create scan with screenshot but without analysis
            scan = Scan.objects.create(
                target=target,
                screenshot_path=f"screenshots/{screenshot_filename}",
                content_hash=new_hash,
                status='success',  # Screenshot OK, alleen analyse failed
                analysis_json=None,
                error_message=result['error']
            )
            result['scan_id'] = scan.id
            
            return result
        
        analysis = gemini_result['analysis']
        print(f"   ✅ Type: {analysis.get('type', 'unknown')}")
        print(f"   ✅ Title: {analysis.get('title', 'N/A')}\n")
        
        # STEP 4: Save to database
        # Waarom nu: Alles is succesvol, nu kunnen we opslaan
        set_scan_progress(target_id, 'saving')
        print("💾 Step 4: Saving to database...")
        
        scan = Scan.objects.create(
            target=target,
            screenshot_path=f"screenshots/{screenshot_filename}",
            content_hash=new_hash,
            status='success',
            analysis_json=analysis
        )
        
        # Update target
        # Waarom beide: last_hash voor volgende compare, last_scan_at voor scheduling
        target.last_hash = new_hash
        target.last_scan_at = timezone.now()
        target.save()
        
        print(f"   ✅ Scan #{scan.id} created")
        print(f"   ✅ Target updated\n")
        
        # Mark scan as complete
        set_scan_progress(target_id, 'complete')
        
        result['success'] = True
        result['scan_id'] = scan.id
        result['message'] = f"Change detected and analyzed (Scan #{scan.id})"
        
    except Target.DoesNotExist:
        result['error'] = f'Target {target_id} not found'
    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'
        import traceback
        traceback.print_exc()
    
    return result


# CLI interface
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python full_scan.py <target_id>")
        print("Example: python full_scan.py 1")
        sys.exit(1)
    
    target_id = int(sys.argv[1])
    result = perform_full_scan(target_id)
    
    print(f"{'='*60}")
    if result['success']:
        print(f"✅ SUCCESS: {result['message']}")
    else:
        print(f"❌ FAILED: {result['error']}")
    print(f"{'='*60}\n")
