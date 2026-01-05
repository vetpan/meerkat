"""
Django Admin configuratie voor Meerkat Intelligence
"""

from django.contrib import admin
from .models import Target, Scan


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    """
    Admin interface voor Target management
    """
    list_display = [
        'name',
        'url_short',
        'interval',
        'status',
        'last_scan_at',
        'created_at'
    ]
    list_filter = ['status', 'interval', 'created_at']
    search_fields = ['name', 'url']
    readonly_fields = ['created_at', 'updated_at', 'last_hash', 'last_scan_at']
    
    fieldsets = [
        ('Basis Informatie', {
            'fields': ['name', 'url']
        }),
        ('Scan Configuratie', {
            'fields': ['interval', 'status']
        }),
        ('Scan State', {
            'fields': ['last_hash', 'last_scan_at'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def url_short(self, obj):
        """Kortere URL weergave"""
        if len(obj.url) > 50:
            return obj.url[:47] + '...'
        return obj.url
    url_short.short_description = 'URL'


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    """
    Admin interface voor Scan resultaten
    """
    list_display = [
        'id',
        'target',
        'status',
        'analysis_type',
        'scanned_at',
        'change_detected'
    ]
    list_filter = ['status', 'scanned_at', 'target']
    search_fields = ['target__name', 'error_message']
    readonly_fields = [
        'target',
        'screenshot_path',
        'content_hash',
        'scanned_at',
        'analysis_json_formatted'
    ]
    
    fieldsets = [
        ('Target', {
            'fields': ['target']
        }),
        ('Scan Resultaat', {
            'fields': [
                'status',
                'content_hash',
                'screenshot_path',
                'error_message'
            ]
        }),
        ('Gemini Analyse', {
            'fields': ['analysis_json_formatted'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['scanned_at']
        }),
    ]
    
    def analysis_json_formatted(self, obj):
        """Mooie weergave van JSON analyse"""
        if obj.analysis_json:
            import json
            return json.dumps(obj.analysis_json, indent=2, ensure_ascii=False)
        return 'Geen analyse beschikbaar'
    analysis_json_formatted.short_description = 'Analyse (JSON)'
    
    def change_detected(self, obj):
        """Was dit een wijziging?"""
        return obj.is_change_detected()
    change_detected.boolean = True
    change_detected.short_description = 'Wijziging?'
