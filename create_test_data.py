"""
Script om test data aan te maken voor Meerkat Intelligence
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from shared.models import Target

# Create test targets
targets_to_create = [
    {
        'name': 'Ziggo',
        'url': 'https://www.ziggo.nl/internet',
        'interval': 15,
        'status': 'active'
    },
    {
        'name': 'Odido',
        'url': 'https://www.odido.nl/mobiel',
        'interval': 15,
        'status': 'active'
    }
]

print("🦡 Meerkat Intelligence - Test Data Creator")
print("=" * 50)

for target_data in targets_to_create:
    # Check if target already exists
    existing = Target.objects.filter(url=target_data['url']).first()
    
    if existing:
        print(f"⏭️  Target '{target_data['name']}' bestaat al")
    else:
        target = Target.objects.create(**target_data)
        print(f"✅ Target '{target.name}' aangemaakt")

print("\n" + "=" * 50)
print(f"📊 Totaal {Target.objects.count()} targets in database")
print("\nJe kunt de targets bekijken op:")
print("  http://127.0.0.1:8000/admin/shared/target/")
