
filepath = '/Users/ramondeboer/antigrafity/meerkat/templates/dashboard/index.html'

with open(filepath, 'r') as f:
    lines = f.readlines()

# Line 959 is index 958
# Line 968 is index 967
start_idx = 958
end_idx = 968 # Slice stops before this index

# Sanity check
if '<div class="flex items-center gap-2">' not in lines[start_idx]: # Line 959
    # Maybe indentation differs?
    if 'gap-2' not in lines[start_idx]:
        print(f"Mismatch at 959: {lines[start_idx]}")
        exit(1)

new_block = [
    '                                        <div class="flex items-center gap-2">\n',
    '                                            <span class="text-[10px] font-bold uppercase tracking-wide {% if change.impact_score >= 7 %}text-danger{% else %}text-accent{% endif %}">{{ change.category }}</span>\n',
    '                                            <span class="text-[10px] font-bold font-mono {% if change.impact_score >= 7 %}bg-danger/10 text-danger{% else %}bg-accent/10 text-accent{% endif %} px-2 py-0.5 rounded">IMPACT {{ change.impact_score }}/10</span>\n',
    '                                        </div>\n'
]

lines[start_idx:end_idx] = new_block

with open(filepath, 'w') as f:
    f.writelines(lines)

print("Fixed broken block 959-968")
