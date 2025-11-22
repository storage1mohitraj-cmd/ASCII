import os

def refix_gina():
    input_path = r"c:\Users\mohit\ascii-live\frames\gina.go"
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract content between backticks
    parts = content.split('`')
    all_lines = []
    # The odd indices should be the frames (1, 3, 5...)
    for i in range(1, len(parts), 2):
        frame_str = parts[i]
        # Split by newline
        lines = frame_str.strip('\n').split('\n') 
        # Note: split('\n') might give an empty string at end if trailing newline
        # But looking at previous output, the lines seemed clean.
        # Let's be careful.
        # In fix_gina.py, I joined with \n.
        # So split('\n') should recover them.
        all_lines.extend(lines)
        
    print(f"Total lines extracted: {len(all_lines)}")
    
    frame_height = 97
    frames = []
    current_frame = []
    
    for line in all_lines:
        current_frame.append(line)
        if len(current_frame) == frame_height:
            frames.append("\n".join(current_frame))
            current_frame = []
            
    if current_frame:
        print(f"Warning: {len(current_frame)} lines leftover.")
        
    print(f"Created {len(frames)} frames.")

    # Construct Go file content
    go_content = "package frames\n\n"
    go_content += "var Gina = DefaultFrameType(GinaFrames)\n\n"
    go_content += "var GinaFrames = []string{\n"
    
    for frame in frames:
        # Escape backticks if any
        if "`" in frame:
            frame = frame.replace("`", "` + \"`\" + `")
            
        go_content += "\t`\n" + frame + "\n`,\n"
        
    go_content += "}\n"
    
    with open(input_path, 'w', encoding='utf-8') as f:
        f.write(go_content)
    
    print("Successfully updated gina.go")

if __name__ == "__main__":
    refix_gina()
