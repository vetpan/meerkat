# 🚀 Meerkat Intelligence - Setup Instructies

## Voor Ramon - Volg deze stappen!

### 1️⃣ Oude Meerkat Folder Verwijderen

```bash
# Optie A: Verplaats oude naar backup
mv ~/meerkat ~/meerkat-backup

# OF Optie B: Verwijder oude (als je zeker weet)
rm -rf ~/meerkat
```

### 2️⃣ Nieuwe Package Uitpakken

```bash
# Download meerkat-clean.tar.gz naar je Downloads
cd ~/Downloads

# Uitpakken naar je home folder
tar -xzf meerkat-clean.tar.gz -C ~/

# Check of het gelukt is
ls -la ~/meerkat
```

Je zou moeten zien:
```
manage.py
config/
shared/
dashboard/
targets/
collector/
templates/
static/
storage/
pyproject.toml
...
```

### 3️⃣ Installeer Dependencies

```bash
cd ~/meerkat

# UV installeren (als je het nog niet hebt)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Dependencies installeren
uv sync

# Playwright browser
uv run playwright install chromium
```

### 4️⃣ Database is Al Klaar!

De database zit al in de package met:
- ✅ Migrations applied
- ✅ Test data (Ziggo, Odido)

**Je hoeft GEEN** `migrate` te doen!

### 5️⃣ Maak Admin Account

```bash
uv run python manage.py createsuperuser
```

Vul in:
- Username: **admin**
- Email: (laat leeg of vul in)
- Password: **admin123** (of iets anders)

### 6️⃣ Start & Test

```bash
# Start server
uv run python manage.py runserver
```

Open in browser: **http://127.0.0.1:8000/admin**

Login met je admin account en je ziet:
- ✅ Targets (Ziggo, Odido)
- ✅ Scans (nog leeg)

## ✅ Verificatie Checklist

Na setup zou je dit moeten hebben:

```bash
cd ~/meerkat

# Check: manage.py bestaat
ls -la manage.py

# Check: database bestaat
ls -la db.sqlite3

# Check: UV werkt
uv run python manage.py check

# Output: System check identified no issues (0 silenced).
```

## 🎯 Wat Nu?

Je bent klaar voor **Stap 3: Basis Web Interface**!

We gaan bouwen:
1. Base template met Tailwind CSS
2. Dashboard pagina
3. URL routing
4. Eerste werkende frontend

## ❓ Problemen?

### Kan meerkat folder niet vinden?
```bash
# Check waar je bent
pwd

# Ga naar home
cd ~

# Check of meerkat er is
ls -la | grep meerkat
```

### uv not found?
```bash
# Installeer UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Herstart terminal
# Probeer opnieuw
which uv
```

### Port 8000 already in use?
```bash
# Stop oude server: Ctrl+C
# Of gebruik andere port:
uv run python manage.py runserver 8001
```

Succes! 🦡
