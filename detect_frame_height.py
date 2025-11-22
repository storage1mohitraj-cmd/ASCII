import re

def detect_height():
    path = r"c:\Users\mohit\ascii-live\frames\gina.go"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract content between backticks
    # The file structure is `...`,\n`...`, etc.
    # We can just split by backticks.
    parts = content.split('`')
    # parts[0] is header
    # parts[1] is frame 1
    # parts[2] is comma/newline
    # parts[3] is frame 2
    # ...
    
    # Let's look at frame 1
    if len(parts) < 2:
        print("Could not find frames.")
        return

    # Reconstruct the full raw lines from all frames to check periodicity
    all_lines = []
    # The odd indices should be the frames (1, 3, 5...)
    for i in range(1, len(parts), 2):
        frame_str = parts[i]
        lines = frame_str.strip().split('\n')
        all_lines.extend(lines)
        
    print(f"Total lines extracted: {len(all_lines)}")
    
    if not all_lines:
        return

    first_line = all_lines[0]
    print(f"First line: {first_line[:50]}...")
    
    # Find occurrences of the first line
    matches = []
    for i, line in enumerate(all_lines):
        if line == first_line:
            matches.append(i)
            
    print(f"First line repeats at indices: {matches}")
    
    if len(matches) > 1:
        diffs = [matches[i+1] - matches[i] for i in range(len(matches)-1)]
        print(f"Differences (Frame Heights): {diffs}")
    else:
        print("First line does not repeat exactly. Checking fuzzy match or other lines.")

if __name__ == "__main__":
    detect_height()
