# ✅ Stap 4 Voltooid: Scout Mode

## Wat hebben we gebouwd?

### 1. Scout Scanner (`collector/scanner/scout.py`)

**Hash-based Change Detection** zonder browser!

```python
def scout_scan(target_url: str) -> dict:
    # 1. Fetch HTML met requests
    # 2. Extract visible text met BeautifulSoup
    # 3. Extract image URLs
    # 4. Maak MD5 hash
    # 5. Return hash + metadata
```

**Wat detecteert het:**
- ✅ Tekstwijzigingen ("€45" → "€49")
- ✅ Nieuwe/verwijderde afbeeldingen
- ✅ Content updates

**Wat negeert het:**
- ❌ CSS/styling wijzigingen
- ❌ JavaScript code
- ❌ Meta tags
- ❌ Scripts

### 2. Management Command (`scan_target`)

**Usage:**
```bash
# Scan specifieke target
python manage.py scan_target 1

# Scan alle active targets
python manage.py scan_target --all
```

**Features:**
- ✅ Scout scan uitvoeren
- ✅ Hash vergelijken met database
- ✅ Change detection
- ✅ Scan record aanmaken
- ✅ Target updaten (last_hash, last_scan_at)
- ✅ Mooie output met kleuren

### 3. Content Extraction

```python
def extract_content(html: str) -> dict:
    # Verwijder scripts, styles, meta
    # Extract visible text
    # Extract image URLs
    # Maak hash: MD5(text + images)
```

**Output:**
```python
{
    'text': "Welkom bij Ziggo...",
    'images': ['/img1.jpg', '/img2.jpg'],
    'image_count': 2,
    'hash': '7c19e4855ddb801005fc96983f5a0330'
}
```

## 🧪 Testen (Op Jouw Machine!)

### Test 1: Scan Ziggo
```bash
cd ~/meerkat
uv run python manage.py scan_target 1
```

**Verwachte output:**
```
============================================================
🎯 Scanning: Ziggo
   URL: https://www.ziggo.nl/internet
============================================================
🔄 CHANGE DETECTED!
   Old hash: None (eerste scan)
   New hash: abc123...
✅ Scan #1 created
✅ Target updated
   Images found: 45
   Text preview: Welkom bij Ziggo Internet...
```

### Test 2: Scan Opnieuw
```bash
uv run python manage.py scan_target 1
```

**Verwachte output:**
```
✓ No changes detected
   Hash: abc123...
```

### Test 3: Scan Alle Targets
```bash
uv run python manage.py scan_target --all
```

Scant Ziggo EN Odido!

## 📊 Database Impact

Na een scan:

**Target wordt geupdatet:**
```python
target.last_hash = "abc123..."
target.last_scan_at = "2025-12-08 20:00:00"
```

**Scan record wordt aangemaakt (bij wijziging):**
```python
Scan.objects.create(
    target=target,
    content_hash="abc123...",
    status='success',
    analysis_json={
        'type': 'scout',
        'changed': True,
        'image_count': 45,
        ...
    }
)
```

## 🎯 Hoe het Werkt

```
1. User: python manage.py scan_target 1
   ↓
2. Command haalt Target op uit database
   ↓
3. scout_scan(target.url) wordt aangeroepen
   ↓
4. requests.get() haalt HTML op
   ↓
5. BeautifulSoup extract tekst + images
   ↓
6. MD5 hash wordt gemaakt
   ↓
7. Hash vergelijken met target.last_hash
   ↓
8. Als ANDERS → Wijziging gedetecteerd!
   ↓
9. Scan record in database + target update
   ↓
10. Success! 🎉
```

## 💡 Design Beslissingen

### Waarom BeautifulSoup + requests (niet Crawlee)?
- **Simpeler** - Minder dependencies, minder complexiteit
- **Sneller** - Geen browser overhead
- **Betrouwbaarder** - Minder dingen die stuk kunnen
- Crawlee was overkill voor simpele HTML parsing

### Waarom MD5 hash?
- **Snel** - Hash berekenen is instant
- **Compact** - 32 characters vs hele HTML opslaan
- **Betrouwbaar** - Zelfde content = zelfde hash
- **Privacy** - We slaan geen volledige HTML op

### Waarom visible text only?
- **Relevant** - Users zien alleen visible content
- **Stabiel** - Code changes zijn niet interessant
- **Accuraat** - Focust op commerciële wijzigingen

## 🚫 Wat Werkt NOG NIET?

Dit komt in latere stappen:

- ❌ **Screenshots** - Komt in Stap 5 (Playwright)
- ❌ **Gemini analyse** - Komt in Stap 5
- ❌ **Auto scanning** - Komt in Stap 8 (scheduler)
- ❌ **SCAN NOW button** - Komt in Stap 8 (HTMX)
- ❌ **Cookie banners** - Komt in Stap 5

## 📁 Nieuwe Bestanden

```
meerkat/
├── collector/scanner/
│   ├── scout.py                      ✅ NIEUW - Scout scanner
│   └── test_scout_mock.py           ✅ NIEUW - Mock test
│
└── shared/management/commands/
    └── scan_target.py                ✅ NIEUW - Management command
```

## 🎯 Volgende Stap

**Stap 5: Capture & Gemini Analyse**

We gaan bouwen:
1. Playwright crawler (browser automation)
2. Screenshot maken (full page)
3. Cookie banner handling
4. Gemini API integratie
5. AI analyse van wijzigingen

Dan hebben we de complete scan pipeline! 🚀

## 📝 Opmerkingen voor Ramon

**Let op:** In mijn test environment kon ik geen echte websites scannen (network restrictions). MAAR de code is getest met mock data en zal op jouw machine wel werken!

Test het met:
```bash
uv run python manage.py scan_target 1
```

Als het werkt zie je:
- ✅ Hash van Ziggo website
- ✅ Aantal images
- ✅ Text preview
- ✅ Scan in database

Laat me weten als je errors krijgt! 🦡
