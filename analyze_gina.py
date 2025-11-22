import collections

def analyze_patterns():
    path = r"c:\Users\mohit\ascii-live\frames\gina.go"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract lines from string literals again
    parts = content.split('`')
    all_lines = []
    for i in range(1, len(parts), 2):
        frame_str = parts[i]
        lines = frame_str.strip().split('\n')
        all_lines.extend(lines)
        
    print(f"Total lines: {len(all_lines)}")
    
    # Check line lengths
    lengths = [len(line) for line in all_lines]
    print(f"Common line lengths: {collections.Counter(lengths).most_common(5)}")
    
    # Find the most common line
    line_counts = collections.Counter(all_lines)
    most_common_line, count = line_counts.most_common(1)[0]
    print(f"Most common line (appears {count} times): {most_common_line[:50]}...")
    
    # Find indices of the most common line
    indices = [i for i, line in enumerate(all_lines) if line == most_common_line]
    print(f"Indices of most common line: {indices[:10]}...")
    
    # Calculate differences
    if len(indices) > 1:
        diffs = [indices[i+1] - indices[i] for i in range(len(indices)-1)]
        print(f"Common intervals: {collections.Counter(diffs).most_common(5)}")

if __name__ == "__main__":
    analyze_patterns()
