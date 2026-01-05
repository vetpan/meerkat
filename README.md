# 🦡 Meerkat Intelligence

SaaS platform voor het monitoren van commerciële wijzigingen op competitor websites.

## 📁 Project Structuur

```
meerkat/                          # Project root
├── manage.py                     # Django management script
├── pyproject.toml                # UV dependencies
├── uv.lock                       # Lock file
├── db.sqlite3                    # SQLite database (na migrate)
│
├── config/                       # Django settings
│   ├── settings.py               # Configuratie
│   ├── urls.py                   # URL routing
│   └── wsgi.py                   # WSGI app
│
├── shared/                       # Database models (Target, Scan)
│   ├── models.py                 # ✨ Target & Scan models
│   ├── admin.py                  # Django admin interface
│   └── migrations/               # Database migrations
│
├── dashboard/                    # Dashboard app (main screen)
│   ├── views.py                  # Views
│   └── templates/                # Templates
│
├── targets/                      # Target management app
│   ├── views.py                  # CRUD views
│   └── templates/                # Templates
│
├── collector/                    # Data collection (scanner)
│   ├── scanner/
│   │   ├── scout.py              # Hash-based change detection
│   │   ├── capture.py            # Screenshot maken
│   │   └── cookies.py            # Cookie banner handling
│   ├── analyzer/
│   │   └── gemini.py             # Gemini AI analyse
│   └── scheduler/
│       └── jobs.py               # Scan scheduling
│
├── templates/                    # Global templates
├── static/                       # Static files (CSS, JS)
│   ├── css/
│   └── js/
│
├── storage/                      # File storage
│   └── screenshots/              # Screenshot bestanden
│
└── create_test_data.py           # Test data script
```

## 🚀 Quick Start

### 1. Installatie

```bash
cd meerkat

# Dependencies installeren
uv sync

# Playwright browser
uv run playwright install chromium
```

### 2. Database Setup

```bash
# Migrations (al gedaan in package)
uv run python manage.py migrate

# Test data (Ziggo, Odido)
uv run python create_test_data.py
```

### 3. Admin Account

```bash
uv run python manage.py createsuperuser

# Vul in:
# Username: admin
# Email: (optioneel)
# Password: admin123
```

### 4. Start Server

```bash
uv run python manage.py runserver
```

Open: **http://127.0.0.1:8000/admin**

## ✅ Wat is Klaar? (Stap 1 & 2)

### Stap 1: Project Setup ✅
- UV project met dependencies
- Django configuratie
- Folder structuur
- Apps aangemaakt

### Stap 2: Database Models ✅
- **Target model** - Websites om te monitoren
- **Scan model** - Scan resultaten met screenshots
- Django admin interface
- Test data (Ziggo, Odido)

## 🎯 Volgende Stappen

- **Stap 3**: Basis Web Interface
- **Stap 4**: Scout Mode (hash detection)
- **Stap 5**: Capture & Gemini Analyse
- **Stap 6**: Dashboard Design (zoals screenshot)
- **Stap 7**: Target Management
- **Stap 8**: Live Updates (HTMX)

## 🔧 Handige Commands

```bash
# Server starten
uv run python manage.py runserver

# Database
uv run python manage.py makemigrations
uv run python manage.py migrate

# Admin
uv run python manage.py createsuperuser

# Shell (Python REPL met Django)
uv run python manage.py shell

# Check configuratie
uv run python manage.py check
```

## 📦 Dependencies

- Django 6.0 - Web framework
- Crawlee - Web scraping
- Playwright - Browser automation
- BeautifulSoup4 - HTML parsing
- Google Generative AI - Gemini API
- Pillow - Image processing

## 🔑 Configuratie

**Gemini API Key** (in `config/settings.py`):
```python
GEMINI_API_KEY = 'AIzaSyB-Zf9aeJsjs69MPnS0COvFYmReF5sYYGE'
```

**Timezone**: Europe/Amsterdam
**Language**: nl-nl

## 📚 Documentatie

- `STAP_2_COMPLEET.md` - Uitleg van database models
- `STAP_2_SETUP.md` - Setup instructies

Klaar om verder te bouwen! 🚀
