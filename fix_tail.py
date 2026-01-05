
filepath = '/Users/ramondeboer/antigrafity/meerkat/templates/dashboard/index.html'

with open(filepath, 'a') as f:
    f.write("\n            // Fixed truncation\n")
    f.write("        }\n")
    f.write("        {% endif %}\n")
    f.write("    </script>\n")
    f.write("{% endblock %}\n")

print("Appended closing tags")
