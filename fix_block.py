
filepath = '/Users/ramondeboer/antigrafity/meerkat/templates/dashboard/index.html'

with open(filepath, 'r') as f:
    lines = f.readlines()

# Indicies: 908 is index 907
# 921 is index 920
start_idx = 907 
end_idx = 921 # We want to remove up to line 921 inclusive. So slice [907:921]. Wait, 921-907 = 14 lines.
# Check lines
# Line 908: <div class="flex items-center gap-2">
# Line 921: title="Verwijder deze scan">

# Sanity check
if 'flex items-center gap-2' not in lines[start_idx]:
    print(f"Mismatch at start: {lines[start_idx]}")
    exit(1)
if 'title="Verwijder' not in lines[end_idx-1]: # end_idx is exclusive, so last removed is end_idx-1
    print(f"Mismatch at end: {lines[end_idx-1]}")
    exit(1)

new_block = [
    '                            <div class="flex items-center gap-2">\n',
    '                                <span class="text-[11px] font-semibold uppercase tracking-wide {% if scan.analysis_json.type == \'critical\' %}text-danger{% elif scan.analysis_json.type == \'baseline\' %}text-accent{% else %}text-success{% endif %}">\n',
    '                                    {% if scan.analysis_json.type == \'critical\' %}⚠️ Wijziging gesignaleerd{% elif scan.analysis_json.type == \'baseline\' %}📊 Nulmeting{% else %}✓ Stabiel{% endif %}\n',
    '                                </span>\n',
    '                            </div>\n',
    '                            <div class="flex items-center gap-3">\n',
    '                                <span class="text-[10px] text-ink-tertiary font-mono">{{ scan.scanned_at|date:"d M H:i" }}</span>\n',
    '                                <button onclick="deleteScan({{ scan.id }})" class="p-1.5 rounded-lg text-ink-tertiary hover:text-danger hover:bg-danger/10 transition-all" title="Verwijder deze scan">\n'
]

lines[start_idx:end_idx] = new_block

with open(filepath, 'w') as f:
    f.writelines(lines)

print("Fixed broken block 908-921")
