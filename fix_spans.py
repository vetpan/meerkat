
import re

filepath = '/Users/ramondeboer/antigrafity/meerkat/templates/dashboard/index.html'

with open(filepath, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Check for corrupted <span class= that should be class=
    # It typically matches indentation and <span class=" but has no closing </span> or even > on the same line sometimes
    if '<span class="' in line:
        # Check if it has a closing </span>
        if '</span>' in line:
            # Likely valid (e.g. the sidebar one)
            new_lines.append(line)
        else:
            # Likely corrupted button attribute
            # Check if it ends with " (quote) or similar, indicating it's just an attribute line
            # Revert <span class=" to class="
            # We need to preserve indentation? 
            # The corruption added <span, effectively shifting.
            # <span class="...
            # We want class="...
            replaced = line.replace('<span class="', 'class="')
            new_lines.append(replaced)
    else:
        new_lines.append(line)

with open(filepath, 'w') as f:
    f.writelines(new_lines)

print("Fixed corrupted spans")
