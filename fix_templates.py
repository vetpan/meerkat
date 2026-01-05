
import re
import os

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Pattern to find split django tags {{ ... }}
    # We look for {{ that is NOT followed by }} on the same line (or close)
    # But simpler: replace `{{\n\s+` with `{{ `
    
    # Fix 1: multi-line {{ variable }}
    # Regex: {{ followed by whitespace/newlines, content, whitespace/newlines, }}
    content = re.sub(r'\{\{\s*\n\s*([^\}]+?)\s*\n?\s*\}\}', r'{{ \1 }}', content)

    # Fix 2: multi-line {% tag %}
    # Regex: {% followed by content %}
    content = re.sub(r'\{%\s*\n\s*([^\%]+?)\s*\n?\s*%\}', r'{% \1 %}', content)
    
    # Fix 3: specifically inside the sidebar where I might have messed up tags
    # "class=... >" -> "<span class=... >"
    # Look for: <p ...>...</p>\s+class=
    content = re.sub(r'(</p>\s*)class="([^"]+)"\s*>([^<]+)</span>', r'\1<span class="\2">\3</span>', content)

    # Specific fix for the Header IF tag if it's still split differently
    # {% if ... %}\n ... {% endif %}
    # This is harder to regex safely globally, but we can target specific strings.
    
    # Check for the sidebar corruption specifically
    # If we see `class="...` at start of line without a tag
    content = re.sub(r'^\s+class="', '                                            <span class="', content, flags=re.MULTILINE)
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Fixed {filepath}")

fix_file('/Users/ramondeboer/antigrafity/meerkat/templates/dashboard/index.html')
