# 🚀 Stap 3 - Update Instructies

## Wat is er nieuw?

Je krijgt **3 nieuwe bestanden**:
1. `templates/base.html` - Base template
2. `templates/dashboard.html` - Dashboard pagina
3. `dashboard/views.py` - Dashboard view (updated)

En **1 geüpdatet bestand**:
4. `config/urls.py` - URL routing (updated)

## Optie A: Nieuwe Package Downloaden (Aanbevolen)

Als je **opnieuw wilt beginnen** met een verse install:

```bash
# Verwijder oude
rm -rf ~/meerkat

# Download en pak uit
cd ~/Downloads
tar -xzf meerkat-stap3.tar.gz -C ~/

# Ga naar folder
cd ~/meerkat

# Dependencies (als nog niet gedaan)
uv sync
uv run playwright install chromium

# Start server
uv run python manage.py runserver
```

Open: **http://127.0.0.1:8000** (GEEN /admin meer!)

## Optie B: Bestanden Handmatig Kopiëren

Als je je **huidige setup wilt behouden**:

1. **Kopieer nieuwe bestanden**:
   - `templates/base.html` (nieuw)
   - `templates/dashboard.html` (nieuw)

2. **Vervang deze bestanden**:
   - `dashboard/views.py`
   - `config/urls.py`

3. **Check de `templates/` folder bestaat**:
```bash
cd ~/meerkat
mkdir -p templates
```

4. **Test**:
```bash
uv run python manage.py check
uv run python manage.py runserver
```

## ✅ Wat zou je moeten zien?

Na het starten van de server en openen van **http://127.0.0.1:8000**:

### ✨ De echte dashboard!
- Sidebar links met "MEERKAT INTELLIGENCE" logo
- Ziggo en Odido in de lijst met groene status dots
- Ziggo is geselecteerd (auto-selected)
- Header met toggle switch en "SCAN NOW" button
- "Wachten op eerste scan..." placeholder

### 🎨 Styling
- Mooie Tailwind CSS styling
- Groene glow op status dots
- Hover effects op sidebar items
- Professional look!

## 🧪 Test het!

1. **Klik op Odido** in sidebar
   - URL wordt: `?target=2`
   - Odido wordt geselecteerd

2. **Klik op Ziggo** terug
   - URL wordt: `?target=1`
   - Ziggo wordt geselecteerd

3. **Hover over items** in sidebar
   - Achtergrond wordt wit

4. **Bekijk de toggle switch**
   - Animated slider
   - Groen als actief

## ❓ Problemen?

### Zie je nog steeds de Django raket?
- Check of je naar `http://127.0.0.1:8000` gaat (NIET /admin)
- Check of `config/urls.py` het dashboard pad heeft

### Geen styling?
- Check of `templates/base.html` Tailwind CDN heeft
- Check je internet connectie (Tailwind via CDN)

### Targets niet zichtbaar?
```bash
# Check of test data er is
cd ~/meerkat
uv run python manage.py shell

from shared.models import Target
print(Target.objects.all())
# Zou Ziggo en Odido moeten tonen

# Zo niet, maak test data:
exit()
uv run python create_test_data.py
```

### Server errors?
```bash
# Check configuratie
uv run python manage.py check

# Check of templates folder bestaat
ls -la templates/
```

## 🎯 Volgende Keer

**Stap 4: Scout Mode** - We gaan de scanner bouwen!
- BeautifulSoup crawler
- Hash-based change detection
- Eerste echte scan functionaliteit

Klaar voor de volgende stap? 🦡
