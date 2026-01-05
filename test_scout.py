"""Test scout met example.com (altijd bereikbaar)"""
from collector.scanner.scout import scout_scan

print("🔍 Testing Scout Mode with example.com...")
result = scout_scan('http://example.com')

print(f"\n✅ Success: {result['success']}")
if result['success']:
    print(f"🔑 Hash: {result['hash']}")
    print(f"📸 Images: {result['image_count']}")
    print(f"📝 Preview: {result['text_preview']}")
else:
    print(f"❌ Error: {result['error']}")
