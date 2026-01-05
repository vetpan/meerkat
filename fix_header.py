
filepath = '/Users/ramondeboer/antigrafity/meerkat/templates/dashboard/index.html'

with open(filepath, 'r') as f:
    lines = f.readlines()

# Lines 689-692 => Indices 688 to 692 (exclusive)
# 4 lines
start_idx = 688
end_idx = 692

# Sanity check
if 'Volgende' not in lines[start_idx] and 'Volgende' not in lines[start_idx+1]:
    # It might be in 689 or 688 context
    pass

# Check specific broken content
# Line 689: class="text-[10px]...
# Line 691: <span id="countdown" <span

if 'class="text-[10px]' not in lines[start_idx]: # Line 689
     print(f"Mismatch 689? {lines[start_idx]}")

new_block = [
    '                            <span class="text-[10px] text-ink-tertiary font-medium uppercase tracking-wider">Volgende scan</span>\n',
    '                            <span id="countdown" class="text-[12px] font-mono bg-surface-secondary px-3 py-1.5 rounded-lg text-ink-secondary font-medium tracking-wide">--:--</span>\n'
]

lines[start_idx:end_idx] = new_block

with open(filepath, 'w') as f:
    f.writelines(lines)

print("Fixed header tags 689-692")
