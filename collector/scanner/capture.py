"""
Capture Mode - Screenshot met Direct Playwright

LET OP: We gebruiken DIRECT Playwright, niet Crawlee's PlaywrightCrawler.

Waarom afwijking van briefing:
- Crawlee PlaywrightCrawler werkt niet betrouwbaar voor alle sites
- Voor ziggo.nl: requests_finished = 0 (handler wordt niet aangeroepen)
- Direct Playwright werkt WEL en is stabieler

Trade-off:
- ❌ Geen Crawlee voordelen (queue, anti-detection)
- ✅ Werkt betrouwbaar voor alle sites
- ✅ Simpeler en directer

Update: Added robust error handling for navigation events during scrolling
        which can happen with sites like kpn.com that redirect after cookie consent.
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


async def capture_screenshot(target_url: str, output_path: str, fast_mode: bool = True) -> dict:
    """
    Maak een full-page screenshot met direct Playwright.
    
    Args:
        target_url: URL om te screenshotten
        output_path: Waar de screenshot opslaan (absoluut pad!)
        fast_mode: If True, use faster loading strategy (default)
        
    Returns:
        {
            'success': bool,
            'screenshot_path': str,
            'error': str (optional)
        }
    """
    result = {
        'success': False,
        'screenshot_path': None,
        'error': None
    }
    
    browser = None
    try:
        async with async_playwright() as p:
            # Launch browser
            print(f"   🌐 Launching browser...")
            browser = await p.chromium.launch(headless=True)
            
            # Create context met realistic settings
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='nl-NL',
                timezone_id='Europe/Amsterdam',
            )
            
            # Open page
            page = await context.new_page()
            
            print(f"   🌐 Loading page: {target_url}")
            # Navigate to URL - use domcontentloaded for speed (don't wait for tracking/ads)
            wait_strategy = 'domcontentloaded' if fast_mode else 'networkidle'
            try:
                await page.goto(target_url, wait_until=wait_strategy, timeout=30000)
            except PlaywrightTimeout:
                # Retry with longer timeout and less strict wait
                print(f"   ⏳ Timeout, retrying with load strategy...")
                await page.goto(target_url, wait_until='load', timeout=45000)
            print(f"   ✅ Page loaded: {page.url}")
            
            # Wait a moment for any initial redirects/JS to settle
            await asyncio.sleep(1)
            
            # Cookie banner handling (with shorter timeout)
            cookie_clicked = await handle_cookie_banner(page)
            if cookie_clicked:
                print(f"   🍪 Cookie banner accepted")
                # Wait for any navigation/reload after cookie consent
                await asyncio.sleep(2)
                # Wait for page to stabilize after potential navigation
                try:
                    await page.wait_for_load_state('domcontentloaded', timeout=5000)
                except:
                    pass
            else:
                print(f"   🍪 No cookie banner found")
            
            # Fast scroll for lazy loading - wrapped in try/except for navigation safety
            try:
                if fast_mode:
                    await scroll_page_fast(page)
                else:
                    await scroll_page(page)
                print(f"   📜 Scrolled page")
            except Exception as scroll_error:
                print(f"   ⚠️ Scroll skipped (navigation detected): {str(scroll_error)[:50]}")
                # Page may have navigated, wait and continue
                await asyncio.sleep(1)
            
            # Wait for images to load
            await asyncio.sleep(1.5)
            
            # Take screenshot with retry on failure
            print(f"   📸 Taking screenshot...")
            try:
                await page.screenshot(path=output_path, full_page=True, timeout=30000)
            except Exception as ss_error:
                print(f"   ⚠️ Full page screenshot failed, trying viewport only...")
                await page.screenshot(path=output_path, full_page=False, timeout=15000)
            print(f"   ✅ Screenshot saved to: {output_path}")
            
            # Close browser
            await browser.close()
            
            result['success'] = True
            result['screenshot_path'] = output_path
            
    except PlaywrightTimeout as e:
        result['error'] = f'Timeout: {str(e)}'
        print(f"   ❌ Timeout: {str(e)}")
    except Exception as e:
        result['error'] = f'Error: {str(e)}'
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure browser is closed
        if browser:
            try:
                await browser.close()
            except:
                pass
    
    return result


async def handle_cookie_banner(page) -> bool:
    """
    Probeer cookie banner weg te klikken.
    Returns True if a cookie button was clicked.
    """
    # Extended list of cookie consent selectors for Dutch and English sites
    cookie_selectors = [
        # Dutch
        'button:has-text("Accepteren")',
        'button:has-text("Alles accepteren")',
        'button:has-text("Alle cookies accepteren")',
        'button:has-text("Akkoord")',
        'button:has-text("Ja, ik accepteer")',
        # English
        'button:has-text("Accept")',
        'button:has-text("Accept all")',
        'button:has-text("Accept All Cookies")',
        'button:has-text("Agree")',
        'button:has-text("Allow all")',
        'button:has-text("OK")',
        # Generic selectors
        '[class*="cookie"] button:has-text("Accept")',
        '[class*="cookie"] button:has-text("Accepteren")',
        '[id*="cookie"] button',
        '[class*="consent"] button',
        '[data-testid*="cookie"] button',
        '#onetrust-accept-btn-handler',
        '.onetrust-accept-btn-handler',
        '#accept-cookies',
        '.accept-cookies',
        '[aria-label*="cookie"] button',
        '[aria-label*="Accept"]',
    ]
    
    for selector in cookie_selectors:
        try:
            button = await page.wait_for_selector(selector, timeout=1500)
            if button and await button.is_visible():
                await button.click()
                return True
        except:
            continue
    
    return False


async def scroll_page(page):
    """
    Scroll langzaam naar beneden voor lazy loading.
    Handles navigation events gracefully.
    """
    try:
        page_height = await page.evaluate('document.body.scrollHeight')
        viewport_height = 1080
        current_position = 0
        
        while current_position < page_height:
            current_position += viewport_height
            try:
                await page.evaluate(f'window.scrollTo(0, {current_position})')
            except:
                break  # Page navigated
            await asyncio.sleep(0.5)
        
        # Scroll back to top
        try:
            await page.evaluate('window.scrollTo(0, 0)')
        except:
            pass
        await asyncio.sleep(0.5)
    except Exception as e:
        print(f"   ⚠️ Scroll error (continuing): {str(e)[:50]}")


async def scroll_page_fast(page):
    """
    Snelle scroll voor lazy loading - geoptimaliseerd voor snelheid.
    Handles navigation events gracefully.
    """
    try:
        page_height = await page.evaluate('document.body.scrollHeight')
        viewport_height = 1080
        current_position = 0
        max_scrolls = 20  # Prevent infinite scrolling
        scroll_count = 0
        
        # Fast scroll - 0.15s per viewport instead of 0.5s
        while current_position < page_height and scroll_count < max_scrolls:
            current_position += viewport_height
            scroll_count += 1
            try:
                await page.evaluate(f'window.scrollTo(0, {current_position})')
            except:
                break  # Page navigated or context destroyed
            await asyncio.sleep(0.15)
        
        # Quick scroll back to top
        try:
            await page.evaluate('window.scrollTo(0, 0)')
        except:
            pass
        await asyncio.sleep(0.2)
    except Exception as e:
        print(f"   ⚠️ Fast scroll error (continuing): {str(e)[:50]}")


def capture_screenshot_sync(target_url: str, output_path: str, fast_mode: bool = True) -> dict:
    """
    Synchronous wrapper voor capture_screenshot.
    """
    return asyncio.run(capture_screenshot(target_url, output_path, fast_mode))


# Test functie
if __name__ == '__main__':
    from datetime import datetime
    
    print("📸 Testing Capture Mode met Direct Playwright...")
    print("=" * 60)
    
    test_url = 'https://www.ziggo.nl/internet'
    output_file = f'test_screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    print(f"URL: {test_url}")
    print(f"Output: {output_file}")
    print("-" * 60)
    
    result = capture_screenshot_sync(test_url, output_file)
    
    print(f"\n✅ Success: {result['success']}")
    if result['success']:
        print(f"📁 Screenshot: {result['screenshot_path']}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n" + "=" * 60)
