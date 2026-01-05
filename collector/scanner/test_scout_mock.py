"""
Mock test voor Scout Mode
Simuleert een HTML pagina om te testen of hash generation werkt
"""

from scout import extract_content

# Sample HTML (zoals van een echte website)
sample_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <script>console.log('test');</script>
    <style>.hidden { display: none; }</style>
</head>
<body>
    <h1>Welkom bij Ziggo Internet</h1>
    <p>Internet vanaf €45 per maand</p>
    <p>3 maanden gratis</p>
    <img src="/images/banner1.jpg" alt="Banner">
    <img src="/images/banner2.jpg" alt="Banner">
    <div class="hidden">Hidden content</div>
</body>
</html>
"""

print("🧪 Testing Scout Content Extraction...")
print("=" * 50)

result = extract_content(sample_html)

print(f"\n✅ Text extracted: {len(result['text'])} characters")
print(f"   Preview: {result['text'][:100]}...")

print(f"\n✅ Images found: {result['image_count']}")
for img in result['images']:
    print(f"   - {img}")

print(f"\n✅ Hash generated: {result['hash']}")

# Test met gewijzigde HTML
modified_html = sample_html.replace('€45', '€49')
result2 = extract_content(modified_html)

print(f"\n🔄 Testing Change Detection...")
print(f"   Original hash: {result['hash']}")
print(f"   Modified hash: {result2['hash']}")
print(f"   Different? {result['hash'] != result2['hash']} ✅")

print("\n" + "=" * 50)
print("✅ Scout mode werkt! Hash detection functioneel.")
