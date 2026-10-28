#!/usr/bin/env python3
"""
Browser Automation for SENTINEL_PRIME
Real Playwright-based browser control - navigation, scraping, screenshots, image reading.
All code/comments/messages in English.
"""
import asyncio
import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


WORKSPACE = Path(os.environ.get('WORKSPACE_ROOT', 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Optimus-Dashboard\\SENTINEL_PRIME'))
SCREENSHOTS_DIR = WORKSPACE / '09_LOGS' / 'screenshots'
SCRAPED_DIR = WORKSPACE / '09_LOGS' / 'scraped'


class BrowserAutomation:
    """Browser automation using Playwright"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.screenshots_dir = SCREENSHOTS_DIR
        self.scraped_dir = SCRAPED_DIR
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.scraped_dir.mkdir(parents=True, exist_ok=True)
        self._playwright = None
        self._browser = None
        self._context = None

    async def start(self):
        """Initialize browser"""
        from playwright.async_api import async_playwright
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context(
            user_agent='SENTINEL_PRIME/1.0 (Browser Automation)',
            viewport={'width': 1280, 'height': 800}
        )
        return True

    async def stop(self):
        """Close browser"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def navigate(self, url: str, wait_until: str = 'domcontentloaded', timeout: int = 30000) -> Dict:
        """
        Navigate to URL.
        Returns dict with status, title, final_url, content_length.
        """
        if not self._context:
            await self.start()

        try:
            page = await self._context.new_page()
            response = await page.goto(url, wait_until=wait_until, timeout=timeout)
            title = await page.title()
            content = await page.content()

            result = {
                'status': 'OK',
                'url': url,
                'final_url': page.url,
                'title': title,
                'http_status': response.status if response else None,
                'content_length': len(content),
                'navigated_at': datetime.now().isoformat()
            }

            await page.close()
            return result
        except Exception as e:
            return {
                'status': 'ERROR',
                'url': url,
                'error': str(e),
                'navigated_at': datetime.now().isoformat()
            }

    async def screenshot(self, url: str, full_page: bool = True, timeout: int = 30000) -> Dict:
        """
        Navigate to URL and take a screenshot.
        Returns dict with status, screenshot_path, page_info.
        """
        if not self._context:
            await self.start()

        try:
            page = await self._context.new_page()
            await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            await page.wait_for_load_state('networkidle', timeout=timeout)

            title = await page.title()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = ''.join(c if c.isalnum() else '_' for c in url.replace('https://', '').replace('http://', ''))[:50]
            screenshot_path = self.screenshots_dir / f"{safe_name}_{timestamp}.png"

            await page.screenshot(path=str(screenshot_path), full_page=full_page)

            result = {
                'status': 'OK',
                'url': url,
                'title': title,
                'screenshot_path': str(screenshot_path),
                'full_page': full_page,
                'captured_at': datetime.now().isoformat()
            }

            await page.close()
            return result
        except Exception as e:
            return {
                'status': 'ERROR',
                'url': url,
                'error': str(e),
                'captured_at': datetime.now().isoformat()
            }

    async def scrape(self, url: str, selectors: Optional[Dict[str, str]] = None, timeout: int = 30000) -> Dict:
        """
        Scrape content from URL.
        If selectors provided, extract specific elements. Otherwise extract text + structure.
        Returns dict with status, content, structure.
        """
        if not self._context:
            await self.start()

        try:
            page = await self._context.new_page()
            await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            await page.wait_for_load_state('networkidle', timeout=timeout)

            title = await page.title()
            full_text = await page.evaluate('document.body.innerText')

            extracted = {'title': title}
            if selectors:
                for name, selector in selectors.items():
                    try:
                        elements = await page.query_selector_all(selector)
                        extracted[name] = [
                            await el.inner_text() for el in elements[:20]
                        ]
                    except Exception as e:
                        extracted[name] = f'ERROR: {e}'
            else:
                # Default extraction
                try:
                    headings = await page.query_selector_all('h1, h2, h3')
                    extracted['headings'] = [
                        await h.inner_text() for h in headings[:30]
                    ]
                except Exception:
                    extracted['headings'] = []

                try:
                    links = await page.query_selector_all('a[href]')
                    extracted['links'] = [
                        {'text': await a.inner_text(), 'href': await a.get_attribute('href')}
                        for a in links[:50]
                    ]
                except Exception:
                    extracted['links'] = []

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = ''.join(c if c.isalnum() else '_' for c in url.replace('https://', '').replace('http://', ''))[:50]
            scraped_file = self.scraped_dir / f"{safe_name}_{timestamp}.json"
            scraped_file.write_text(
                json.dumps({'url': url, 'extracted': extracted, 'text_length': len(full_text)}, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )

            result = {
                'status': 'OK',
                'url': url,
                'title': title,
                'extracted': extracted,
                'text_preview': full_text[:500],
                'text_length': len(full_text),
                'scraped_file': str(scraped_file),
                'scraped_at': datetime.now().isoformat()
            }

            await page.close()
            return result
        except Exception as e:
            return {
                'status': 'ERROR',
                'url': url,
                'error': str(e),
                'scraped_at': datetime.now().isoformat()
            }

    async def read_images(self, url: str, image_selector: str = 'img', timeout: int = 30000) -> Dict:
        """
        Navigate to URL and read image src attributes + alt texts.
        Returns dict with images list (src, alt, base64 if available).
        """
        if not self._context:
            await self.start()

        try:
            page = await self._context.new_page()
            await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            await page.wait_for_load_state('networkidle', timeout=timeout)

            images = await page.query_selector_all(image_selector)
            image_data = []
            for img in images[:30]:
                src = await img.get_attribute('src')
                alt = await img.get_attribute('alt')
                if src:
                    image_data.append({
                        'src': src,
                        'alt': alt or '',
                        'is_absolute': src.startswith('http')
                    })

            result = {
                'status': 'OK',
                'url': url,
                'images_found': len(image_data),
                'images': image_data,
                'read_at': datetime.now().isoformat()
            }

            await page.close()
            return result
        except Exception as e:
            return {
                'status': 'ERROR',
                'url': url,
                'error': str(e),
                'read_at': datetime.now().isoformat()
            }

    async def fill_form(self, url: str, fields: Dict[str, str], submit_selector: Optional[str] = None, timeout: int = 30000) -> Dict:
        """
        Fill a form on a page.
        fields: dict mapping selector -> value.
        submit_selector: optional selector to click after filling.
        """
        if not self._context:
            await self.start()

        try:
            page = await self._context.new_page()
            await page.goto(url, wait_until='domcontentloaded', timeout=timeout)

            for selector, value in fields.items():
                await page.fill(selector, value)

            if submit_selector:
                await page.click(submit_selector)
                await page.wait_for_load_state('networkidle', timeout=timeout)

            result = {
                'status': 'OK',
                'url': url,
                'fields_filled': list(fields.keys()),
                'submitted': submit_selector is not None,
                'final_url': page.url,
                'filled_at': datetime.now().isoformat()
            }

            await page.close()
            return result
        except Exception as e:
            return {
                'status': 'ERROR',
                'url': url,
                'error': str(e),
                'filled_at': datetime.now().isoformat()
            }

    async def execute_javascript(self, url: str, script: str, timeout: int = 30000) -> Dict:
        """
        Navigate to URL and execute JavaScript.
        Returns dict with result of script execution.
        """
        if not self._context:
            await self.start()

        try:
            page = await self._context.new_page()
            await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
            result_value = await page.evaluate(script)

            result = {
                'status': 'OK',
                'url': url,
                'script': script[:200],
                'result': result_value,
                'executed_at': datetime.now().isoformat()
            }

            await page.close()
            return result
        except Exception as e:
            return {
                'status': 'ERROR',
                'url': url,
                'error': str(e),
                'executed_at': datetime.now().isoformat()
            }


def main():
    """Demo: browser automation"""
    async def _demo():
        browser = BrowserAutomation(headless=True)
        await browser.start()

        # Test 1: Navigate to about:blank
        result = await browser.navigate('about:blank')
        print(f"Test 1 (navigate about:blank): {result['status']}")
        print(f"  Title: {result.get('title', 'N/A')}")

        # Test 2: Scrape a real URL (example.com)
        result = await browser.scrape('https://example.com')
        print(f"\nTest 2 (scrape example.com): {result['status']}")
        if result['status'] == 'OK':
            print(f"  Title: {result['title']}")
            print(f"  Text length: {result['text_length']}")
            print(f"  Headings: {result['extracted'].get('headings', [])[:3]}")

        await browser.stop()
        print("\nBrowser automation demo complete")

    asyncio.run(_demo())


if __name__ == '__main__':
    main()
