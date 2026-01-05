"""
Scout Mode - Hash-based Change Detection

Gebruikt Crawlee's BeautifulSoupCrawler om te checken of een pagina is veranderd.
Geen browser = sneller, goedkoper.
"""

import hashlib
import asyncio
from bs4 import BeautifulSoup
from crawlee.crawlers import BeautifulSoupCrawler


def extract_content(soup: BeautifulSoup) -> dict:
    """
    Extract visible text en image URLs van BeautifulSoup object.
    
    Args:
        soup: BeautifulSoup parsed HTML
        
    Returns:
        {
            'text': str,      # Alle zichtbare tekst
            'images': list,   # Alle image URLs
            'hash': str       # MD5 hash
        }
    """
    # Verwijder scripts en styles (niet zichtbaar voor gebruiker)
    for script in soup(['script', 'style', 'meta', 'noscript', 'head']):
        script.decompose()
    
    # Extract visible text
    text = soup.get_text(separator=' ', strip=True)
    # Normalize whitespace (meerdere spaties -> 1 spatie)
    text = ' '.join(text.split())
    
    # Extract image URLs
    images = []
    for img in soup.find_all('img', src=True):
        images.append(img['src'])
    
    # Maak hash van tekst + images gecombineerd
    # Waarom: Als tekst OF images veranderen, verandert hash
    content = f"{text}|{'|'.join(images)}"
    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
    
    return {
        'text': text,
        'images': images,
        'image_count': len(images),
        'hash': content_hash
    }


async def scout_scan(target_url: str) -> dict:
    """
    Scout scan: Check of pagina is veranderd via hash.
    
    Gebruikt Crawlee's BeautifulSoupCrawler voor:
    - Automatische user-agent rotation
    - Error handling
    - Rate limiting
    
    Args:
        target_url: URL om te scannen
        
    Returns:
        {
            'success': bool,
            'hash': str,           # MD5 hash van content
            'text_preview': str,   # Eerste 200 chars
            'image_count': int,    # Aantal images gevonden
            'error': str           # Error message (als failed)
        }
    """
    result = {
        'success': False,
        'hash': None,
        'text_preview': None,
        'image_count': 0,
        'error': None
    }
    
    # Storage voor content (wordt gevuld door request_handler)
    content_data = {}
    
    async def request_handler(context) -> None:
        """
        Handler die Crawlee aanroept voor elke request.
        
        Waarom async: Crawlee gebruikt asyncio voor performance
        """
        # context.soup is de BeautifulSoup object van de pagina
        content = extract_content(context.soup)
        content_data.update(content)
    
    try:
        # Setup BeautifulSoupCrawler
        # Waarom deze settings:
        # - max_requests_per_crawl=1: We willen alleen deze ene pagina
        # - request_handler: Onze functie die de content extract
        crawler = BeautifulSoupCrawler(
            request_handler=request_handler,
            max_requests_per_crawl=1,
        )
        
        # Run de crawl
        # Waarom als list: Crawlee accepteert meerdere URLs tegelijk
        await crawler.run([target_url])
        
        # Check of we data hebben gekregen
        if content_data:
            result.update({
                'success': True,
                'hash': content_data['hash'],
                'text_preview': content_data['text'][:200] + '...',
                'image_count': content_data['image_count']
            })
        else:
            result['error'] = 'Geen content gevonden'
            
    except Exception as e:
        # Vang alle errors op (netwerk, parsing, etc)
        result['error'] = str(e)
    
    return result


def scout_scan_sync(target_url: str) -> dict:
    """
    Synchronous wrapper voor scout_scan.
    
    Waarom nodig: Django views/commands zijn sync, maar Crawlee is async.
    Deze functie maakt een event loop om async code te runnen.
    """
    return asyncio.run(scout_scan(target_url))


# Test functie (alleen als je direct dit bestand runt)
if __name__ == '__main__':
    print("🔍 Testing Scout Mode met Crawlee...")
    print("=" * 60)
    
    # Test URL (example.com werkt altijd)
    test_url = 'http://example.com'
    print(f"Scanning: {test_url}")
    print("-" * 60)
    
    result = scout_scan_sync(test_url)
    
    print(f"\n✅ Success: {result['success']}")
    if result['success']:
        print(f"🔑 Hash: {result['hash']}")
        print(f"📸 Images: {result['image_count']}")
        print(f"📝 Preview: {result['text_preview'][:100]}...")
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("💡 Op jouw machine test met: ziggo.nl en odido.nl")
