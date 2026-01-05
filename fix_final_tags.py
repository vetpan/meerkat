
filepath = '/Users/ramondeboer/antigrafity/meerkat/templates/dashboard/index.html'

with open(filepath, 'r') as f:
    lines = f.readlines()

# Fix 1: Sidebar Interval
# Lines 599-601 [598:601] -> 3 lines
idx1_start = 598
idx1_end = 601
if '<span' not in lines[idx1_start] or 'target.interval' not in lines[idx1_end-1]:
    print(f"Mismatch 1: {lines[idx1_start]} ... {lines[idx1_end-1]}")
    # proceed if close?
    pass

lines[idx1_start:idx1_end] = [
    '                                            <span class="text-[10px] px-1.5 py-0.5 bg-surface-secondary text-ink-tertiary rounded-md font-mono">{{ target.interval }}m</span>\n'
]

# Note: Indices shift after replacement! 
# Original 598:601 (3 lines) replaced by 1 line. Delta = -2.
delta1 = -2

# Fix 2: Sidebar URL
# Original Lines 603-604 [602:604].
# Adjusted indices: Start = 602 + delta1 = 600.
idx2_start = 602 + delta1
idx2_end = 604 + delta1
# Check
if '<p' not in lines[idx2_start] or 'target.url' not in lines[idx2_end-1]:
    print(f"Mismatch 2: {lines[idx2_start]} ... {lines[idx2_end-1]}")

lines[idx2_start:idx2_end] = [
    '                                        <p class="text-[11px] text-ink-tertiary truncate mt-0.5">{{ target.url|slice:":35" }}...</p>\n'
]

# Original 602:604 (2 lines) replaced by 1 line. Delta = -1. 
# Total Delta = -2 + -1 = -3.
delta2 = delta1 - 1

# Fix 3: Status
# Original Lines 830-831 [829:831].
# Adjusted: 829 + delta2 = 826.
idx3_start = 829 + delta2
idx3_end = 831 + delta2

if '<p' not in lines[idx3_start] or 'latest_scan' not in lines[idx3_end-1]:
    print(f"Mismatch 3: {lines[idx3_start]} ... {lines[idx3_end-1]}")

lines[idx3_start:idx3_end] = [
    '                            <p class="text-[13px] font-semibold text-success">Stabiel sinds {{ latest_scan.scanned_at|timesince }}</p>\n'
]

with open(filepath, 'w') as f:
    f.writelines(lines)

print("Fixed final tags")
