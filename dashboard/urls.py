"""
Dashboard URL Configuration
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('matrix/', views.matrix_view, name='matrix'),
    path('api/scan/<int:target_id>/', views.trigger_scan, name='trigger_scan'),
    path('api/scan/<int:target_id>/status/', views.scan_status, name='scan_status'),
    path('api/targets/<int:target_id>/toggle/', views.toggle_target, name='toggle_target'),
    path('api/targets/<int:target_id>/update/', views.update_target, name='update_target'),
    path('api/targets/create/', views.create_target, name='create_target'),
    path('api/targets/<int:target_id>/delete/', views.delete_target, name='delete_target'),
    path('api/scans/<int:scan_id>/delete/', views.delete_scan, name='delete_scan'),
    
    # Help section
    path('help/', views.help_index, name='help_index'),
    path('help/getting-started/', views.help_getting_started, name='help_getting_started'),
    path('help/targets/', views.help_targets, name='help_targets'),
    path('help/scans/', views.help_scans, name='help_scans'),
    path('help/features/', views.help_features, name='help_features'),
    path('help/faq/', views.help_faq, name='help_faq'),
]
