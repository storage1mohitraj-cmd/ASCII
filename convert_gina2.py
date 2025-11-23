import os

def convert_gina2():
    input_path = r'c:\Users\mohit\ascii-live\frames\gina2.go'
    output_path = r'c:\Users\mohit\ascii-live\frames\gina2.go'

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Configuration
    lines_per_frame = 98
    total_frames = 67
    
    frames = []
    current_frame = []
    
    for i, line in enumerate(lines):
        # Remove the newline character for processing, but keep it for the string
        # Actually, we want to reconstruct the frame string.
        # The raw file has newlines.
        
        # Check if we are at a split point
        if (i + 1) % lines_per_frame == 0:
            # This is the last line of a frame (likely empty or separator)
            # Based on observation, line 98 is empty.
            # So we append the accumulated lines to frames list
            # We exclude the separator line if it's just empty/padding
            # Let's include it if it's part of the art, but previous analysis said it's empty.
            # Let's just join what we have.
            frames.append("".join(current_frame))
            current_frame = []
        else:
            current_frame.append(line)
            
    # Handle any remaining lines if they didn't hit the modulo (e.g. last frame)
    if current_frame:
        frames.append("".join(current_frame))

    print(f"Total frames found: {len(frames)}")
    
    # Construct Go file content
    go_content = """package frames

import "time"

var Gina2 = FrameType{
	GetFrame:  DefaultGetFrame(Gina2Frames),
	GetLength: DefaultGetLength(Gina2Frames),
	GetSleep: func() time.Duration {
		return time.Millisecond * 100
	},
}

var Gina2Frames = []string{
"""

    for frame in frames:
        # Escape backticks if any (though we checked and found none)
        safe_frame = frame.replace("`", "` + \"`\" + `")
        go_content += f"\t`{safe_frame}`,\n"

    go_content += "}\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(go_content)

    print(f"Successfully wrote Go code to {output_path}")

if __name__ == "__main__":
    convert_gina2()
