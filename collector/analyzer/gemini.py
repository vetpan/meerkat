"""
Gemini Analyzer - Strategic Market Intelligence

Gebruikt Google Gemini om screenshots te analyseren volgens
professionele Competitor Intelligence methodiek.

Twee modi:
1. Eerste meting (Baseline) - Eerste analyse
2. Monitoring (Vergelijking) - Compare met vorige
"""

import json
import google.generativeai as genai
from django.conf import settings
from PIL import Image


def analyze_screenshot(screenshot_path: str, target_name: str, previous_analysis: dict = None) -> dict:
    """
    Analyseer screenshot met Gemini Vision.
    
    Twee modi:
    1. Eerste meting (Baseline) - Eerste analyse
    2. Monitoring (Vergelijking) - Compare met vorige
    
    Args:
        screenshot_path: Pad naar screenshot
        target_name: Naam van target
        previous_analysis: Vorige analyse (None = eerste meting)
        
    Returns:
        {
            'success': bool,
            'analysis': dict,
            'error': str (optional)
        }
    """
    result = {
        'success': False,
        'analysis': None,
        'error': None
    }
    
    try:
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Use Gemini 2.5 Flash
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Load image
        img = Image.open(screenshot_path)
        
        # Kies prompt op basis van modus
        if previous_analysis is None:
            # NULMETING (BASELINE)
            prompt = f"""**ROL:**
Je bent een Strategic Market Intelligence lead en top analist gespecialiseerd in Competitor Intelligence met 15 jaar ervaring in de Nederlandse telecom markt.

**DOEL:**
Breng de fundamentele status van de website "{target_name}" in kaart op basis van 4 kernpijlers. Dit is de 'waarheid' voor toekomstige vergelijkingen. Wees ZEER gedetailleerd en uitgebreid.

**STIJL:**
- Objectief en feitelijk, maar ook uitgebreid en gedetailleerd.
- Citeer teksten exact zoals ze op het scherm staan, inclusief koppen en subkoppen.
- Beschrijf ook de visuele elementen: kleuren van banners, positionering, grootte.
- Elke categorie moet 3-5 volledige zinnen bevatten, geen opsommingen of korte bullets.

**ANALYSE CATEGORIEËN (minimaal 3-5 zinnen per categorie):**
1. PROMOTIE: Beschrijf alle actieve conversie-drijvers in detail. Welke banners zijn zichtbaar? Welke kleuren? Welke teksten? Zijn er kortingsteksten? Hoeveel korting? Welke voorwaarden staan vermeld? Is er urgentie (bijv. "nu", "tijdelijk", "alleen vandaag")?
2. PRIJS: Welke prijzen staan er exact? Welke pakketten worden aangeboden? Wat zijn de maandprijzen? Zijn er eenmalige kosten? Welke valuta? Wat is de looptijd van contracten? Zijn er instapkosten of kortingen?
3. PRODUCTEN_DIENSTEN: Welke producten of diensten worden aangeboden? Welke categorieën zie je in de navigatie? Welke features worden uitgelicht? Wat zijn USPs? Worden er bundles aangeboden?
4. MARKETING_BOODSCHAP: Wat is de letterlijke H1/H2 kop? Welke waardeproposities worden gecommuniceerd? Welke emotionele triggers worden gebruikt? Wie is de doelgroep? Welke toon wordt aangeslagen?

**OUTPUT:**
Genereer een JSON object met deze structuur:
{{
    "type": "baseline",
    "title": "Eerste meting {target_name}",
    "summary": "Uitgebreide samenvatting van de huidige status in 2-3 zinnen",
    "baseline": [
        {{
            "category": "PROMOTIE",
            "status": "Gedetailleerde beschrijving van minimaal 3-5 zinnen over alle promoties, banners, kleuren, kortingen en voorwaarden die je ziet"
        }},
        {{
            "category": "PRIJS",
            "status": "Gedetailleerde beschrijving van minimaal 3-5 zinnen over alle prijzen, pakketten, looptijden en voorwaarden"
        }},
        {{
            "category": "PRODUCTEN_DIENSTEN",
            "status": "Gedetailleerde beschrijving van minimaal 3-5 zinnen over alle producten, diensten en features"
        }},
        {{
            "category": "MARKETING_BOODSCHAP",
            "status": "Gedetailleerde beschrijving van minimaal 3-5 zinnen over de kernboodschap, koppen en tone-of-voice"
        }}
    ],
    "advice": "Uitgebreid strategisch advies in minimaal 3 zinnen: wat zou je monitoren en waarom?"
}}

Genereer ALLEEN JSON, geen markdown backticks, geen tekst ervoor of erna."""

        else:
            # MONITORING (VERGELIJKING)
            prompt = f"""**ROL:**
Je bent een Strategic Market Intelligence lead en top analist gespecialiseerd in Competitor Intelligence. Je rapporteert direct aan de CEO en Marketing Director. Je moet ZEER gedetailleerde en uitgebreide analyses leveren.

**DOEL:**
Vergelijk de NIEUWE situatie (deze screenshot) met de OUDE situatie van "{target_name}". Rapporteer elke strategische wijziging binnen de 4 kernpijlers met UITGEBREIDE details.

**OUDE SITUATIE:**
{json.dumps(previous_analysis, indent=2)}

**FILTER:**
- Negeer ruis (pixels, cookies, tech-fouten).
- Rapporteer alleen wijzigingen met zakelijke impact, maar wees ZEER GEDETAILLEERD in je beschrijvingen.

**RAPPORTAGE STIJL:**
- HEEL BELANGRIJK: "before_value" en "after_value" moeten elk minimaal 4-6 volledige zinnen bevatten!
- Beschrijf exact wat er was en wat er nu is, met alle relevante details.
- Citeer letterlijke teksten van de website tussen aanhalingstekens.
- Vermeld kleuren, posities, grootte van elementen waar relevant.
- "business_implication" moet minimaal 2-3 zinnen zijn met concrete impact.

**ANALYSE CATEGORIEËN:**
1. PROMOTIE (Tactisch): Nieuwe campagnes, kortingscodes, seizoensdeals of verwijderde acties.
2. PRIJS (Strategisch): Prijsverhogingen/-verlagingen, structuurwijzigingen in abonnementen.
3. PRODUCTEN_DIENSTEN (Strategisch): Nieuwe features gelanceerd, diensten verwijderd.
4. MARKETING_BOODSCHAP (Strategisch): Wijziging in H1/Koppen, nieuwe pay-off, tone-of-voice.

**OUTPUT:**
Genereer een JSON object met deze structuur:
{{
    "type": "critical" of "stable",
    "title": "Korte krachtige titel van de belangrijkste wijziging",
    "summary": "CEO-level samenvatting in 2-3 zinnen met concrete cijfers en impact",
    "changes": [
        {{
            "category": "PROMOTIE" of "PRIJS" of "PRODUCTEN_DIENSTEN" of "MARKETING_BOODSCHAP",
            "before_value": "UITGEBREIDE beschrijving van de oude situatie in 4-6 volledige zinnen. Citeer exact de oude teksten, prijzen, promoties. Beschrijf de visuele elementen die je daarbij zag. Welke kleuren, welke posities, welke urgentie?",
            "after_value": "UITGEBREIDE beschrijving van de nieuwe situatie in 4-6 volledige zinnen. Citeer exact de nieuwe teksten, prijzen, promoties. Beschrijf de visuele elementen die je nu ziet. Welke veranderingen in stijl of toon?",
            "change_description": "Kernwijziging in 1 zin: Was [X] → Is [Y]",
            "business_implication": "Waarom is dit belangrijk? Welke strategische beweging maakt de concurrent? Wat betekent dit voor de markt? Minimaal 2-3 zinnen.",
            "impact_score": 1-10
        }}
    ],
    "advice": "Uitgebreid strategisch advies in minimaal 3-4 zinnen: wat moet de organisatie doen? Welke tegenzet is nodig? Welke risico's zijn er?"
}}

**TYPE:**
- "critical" als impact_score >= 7 OF meerdere strategische wijzigingen
- "stable" als alleen kleine tactische wijzigingen of geen wijzigingen

**BELANGRIJK:** Gebruik NOOIT korte beschrijvingen. Elke before_value en after_value moet minimaal 4 zinnen zijn!

Genereer ALLEEN JSON, geen markdown backticks, geen tekst ervoor of erna."""
        
        # Generate content
        response = model.generate_content([prompt, img])
        
        # Parse response
        response_text = response.text.strip()
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON
        analysis = json.loads(response_text)
        
        result['success'] = True
        result['analysis'] = analysis
        
    except json.JSONDecodeError as e:
        result['error'] = f'JSON parse error: {str(e)}\nResponse: {response_text[:200]}'
    except Exception as e:
        result['error'] = f'Gemini error: {str(e)}'
    
    return result


# Test functie
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python gemini.py <screenshot_path> <target_name>")
        sys.exit(1)
    
    result = analyze_screenshot(sys.argv[1], sys.argv[2])
    
    if result['success']:
        print(json.dumps(result['analysis'], indent=2))
    else:
        print(f"ERROR: {result['error']}")
