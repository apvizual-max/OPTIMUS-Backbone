# BROWSER AUTOMATION — Full Web Control pentru SENTINEL

## Filosofie

SENTINEL trebuie să poată naviga pe web, extrage informații, citi imagini, și automatiza sarcini web — exact ca Popy când folosește un browser manual.

## Capabilități

### 1. Navigare
```
- Deschide URL
- Click pe elemente
- Scroll
- Submit formulare
- Handle dialogs
```

### 2. Extragere
```
- HTML content
- Text (fără markup)
- Imagini (download + save)
- Screenshots
- Cookies
- LocalStorage
```

### 3. Interacțiune
```
- Type text
- Hover
- Drag & drop
- Select text
- Execute JavaScript
```

### 4. State Management
```
- Login sessions
- Persistent context
- Multi-tab
- Profile management
```

## Implementare

### Playwright Integration (Python)

```python
from playwright.sync_api import sync_playwright


class BrowserController:
    """Controller pentru browser automation via Playwright"""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self, headless=True):
        """Start browser session"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context(
            user_agent='SENTINEL_PRIME/1.0',
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = self.context.new_page()
        return self

    def navigate(self, url):
        """Navigate to URL"""
        self.page.goto(url, wait_until='networkidle', timeout=30000)
        return self.page.url

    def extract_text(self):
        """Extract visible text"""
        return self.page.evaluate('document.body.innerText')

    def extract_html(self):
        """Extract full HTML"""
        return self.page.content()

    def screenshot(self, path=None, full_page=False):
        """Take screenshot"""
        if path is None:
            path = WORKSPACE / '08_SELF_IMPROVEMENT' / 'screenshots' / f'{datetime.now().isoformat()}.png'
        path.parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(path), full_page=full_page)
        return str(path)

    def download_images(self):
        """Download all images on page"""
        images = self.page.evaluate('''
            Array.from(document.images).map(img => ({
                src: img.src,
                alt: img.alt,
                width: img.naturalWidth,
                height: img.naturalHeight
            }))
        ''')

        downloaded = []
        for i, img in enumerate(images):
            if img['src']:
                try:
                    response = self.context.request.get(img['src'])
                    img_path = WORKSPACE / '08_SELF_IMPROVEMENT' / 'images' / f'image_{i}.png'
                    img_path.parent.mkdir(parents=True, exist_ok=True)
                    img_path.write_bytes(response.body())
                    downloaded.append(str(img_path))
                except Exception:
                    pass

        return downloaded

    def click(self, selector):
        """Click element"""
        self.page.click(selector)

    def type(self, selector, text):
        """Type into field"""
        self.page.fill(selector, text)

    def execute_js(self, script):
        """Execute JavaScript"""
        return self.page.evaluate(script)

    def wait_for(self, selector, timeout=30000):
        """Wait for element"""
        self.page.wait_for_selector(selector, timeout=timeout)

    def get_cookies(self):
        """Get all cookies"""
        return self.context.cookies()

    def close(self):
        """Close browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
```

### MCP Integration (pentru LLM)

```
Browser MCP server:
- navigate(url)
- extract_text()
- extract_images()
- screenshot()
- click(selector)
- type(selector, text)
- execute_js(script)
- get_cookies()
- close()
```

## Use Cases pentru SENTINEL

### 1. R-2 Verification
```
User: "Ce zice Wikipedia despre Cucuteni?"
SENTINEL:
  browser.navigate("https://en.wikipedia.org/wiki/Cucuteni-Trypillia_culture")
  text = browser.extract_text()
  apply triple filter
  output verified content
```

### 2. Image Research
```
User: "Arată-mi vase Cucuteni cu Dao"
SENTINEL:
  browser.navigate("https://www.google.com/search?q=cucuteni+dao")
  download_images()
  multimodal.process(images)
  output pattern analysis
```

### 3. Documentation Fetch
```
User: "Descarcă specificațiile X"
SENTINEL:
  browser.navigate(url)
  pdf.download()
  document.process()
  extract relevant sections
```

## Anti-Mimicry în Browser Use

```
- Nu fetch fără scop (fetch = R-2 verification, nu idle browsing)
- Nu accept cookies fără confirmare
- Nu submit formulare cu date personale
- Log toate navigările
- Cleanup cookies/sessions la exit
```

## Security Boundaries

```
Permis:
- Public web pages
- Wikipedia, Open source docs
- Search engines
- News sites

Necesită approval:
- Login required pages
- Form submissions cu date
- Downloads de la surse necunoscute

Interzis:
- Banking/finance sites (fără approval explicit)
- Medical records
- Any site cu date personale
```

## State Persistence

```
Browser context e persistent:
- Cookies salvate în 08_SELF_IMPROVEMENT/browser_state/
- LocalStorage indexed
- Profile-uri salvate

Restoration:
- Load cookies on session start
- Resume login state
- Continue browsing context
```

## Performance

```
- Headless mode by default (performance)
- Caching static resources
- Concurrent browser instances (max 3)
- Auto-cleanup old sessions
```

## Integration cu Alte Sisteme

```
Browser + MultiModal:
  Download images → Process → Pattern detection

Browser + R-2:
  Verify claim → Search → Compare

Browser + Self-Modify:
  Download docs → Update foundation
```

## Metrici

```
- Pages navigated per session
- Successful R-2 verifications
- Images processed from web
- Time per operation
- Cache hit rate
= Browser effectiveness
```

## Failover

```
Browser fail → Fallback to:
- Direct HTTP requests (urllib)
- Search via different MCP
- Cached results

Network fail → Retry cu backoff
Site down → Use alternative source
```

---

**Status:** Design complet
**Versiune:** 1.0
**Aplicabil:** Pentru R-2 verifications, research, documentation fetches
