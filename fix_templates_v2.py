
import re

filepath = '/Users/ramondeboer/antigrafity/meerkat/templates/dashboard/index.html'

with open(filepath, 'r') as f:
    lines = f.readlines()

new_lines = []
buffer = ""
in_tag = False
tag_type = None # '{{' or '{%'

# Context fix: remove stray <span lines I introduced
# If line is just whitespace and <span, and next line also starts with <span class=..., drop proper one?
# Visual check:
# 599: <span
# 600: <span class=...
# I should drop 599 if 600 is the real one.

sanitized_lines = []
skip_next = False
for i, line in enumerate(lines):
    stripped = line.strip()
    # Detect my previous corruption
    if stripped == '<span' and i+1 < len(lines):
        next_line = lines[i+1].strip()
        if next_line.startswith('<span class='):
            continue # Skip this stray line
    
    # Detect the bad regex replacement in header (indentation)
    if 'class="text-[11px] font-semibold' in line and '<span' in line and lines[i-1].strip() == '<span':
         # The previous line might be valid <span if I replaced class= with <span class=
         # But in Step 1664: 906 <span, 907 <span class=...
         # So 906 is the old one?
         # Original 906 was <span. Original 907 was class=...
         # My earlier sed/regex made 907 into <span class=... without removing 906?
         # No, I used re.sub on content.
         pass
    
    sanitized_lines.append(line)

# Now join tags
final_lines = []
current_line = ""

for line in sanitized_lines:
    # If we are effectively building a line
    if current_line:
        # Check if the combined line now has a closing tag
        temp_line = current_line + " " + line.strip()
        
        if tag_type == '{{' and '}}' in line:
            # Found closing
            # Normalize whitespace inside the tag?
            # extract content between {{ and }}
            # For now just join them
            current_line += " " + line.strip()
            # Replace internal newlines/spaces with single space
            current_line = re.sub(r'\{\{\s+', '{{ ', current_line)
            current_line = re.sub(r'\s+\}\}', ' }}', current_line)
            final_lines.append(current_line + "\n")
            current_line = ""
            tag_type = None
            continue
            
        elif tag_type == '{%' and '%}' in line:
             current_line += " " + line.strip()
             current_line = re.sub(r'\{%\s+', '{% ', current_line)
             current_line = re.sub(r'\s+%\}', ' %}', current_line)
             final_lines.append(current_line + "\n")
             current_line = ""
             tag_type = None
             continue
        else:
            # Still not closed, keep appending
            current_line += " " + line.strip()
            continue

    # Not currently building a line, check if this line OPENS a tag but DOES NOT CLOSE IT
    # Check for {{
    if '{{' in line and '}}' not in line:
        # Check if it's really a tag start and not just text?
        # Assuming {{ is always a tag start here
        current_line = line.rstrip()
        tag_type = '{{'
        continue
    
    # Check for {%
    # But wait, {% if ... %} ... {% elif (split here)
    # The line might have multiple tags.
    # We care about the LAST tag being unclosed.
    # e.g. ... {% endif %} ... {% elif
    
    # Simple check: count {% and %}
    open_count = line.count('{%')
    close_count = line.count('%}')
    if open_count > close_count:
        # formatting is broken
        current_line = line.rstrip()
        tag_type = '{%'
        continue
    
    # Also check {{ count
    v_open = line.count('{{')
    v_close = line.count('}}')
    if v_open > v_close:
        current_line = line.rstrip()
        tag_type = '{{'
        continue

    # Otherwise valid line
    final_lines.append(line)

# Write back
with open(filepath, 'w') as f:
    f.writelines(final_lines)

print("Fixed with line parser")
