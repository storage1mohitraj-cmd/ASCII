import os
import sys
import time
import glob
import math
import argparse
import subprocess

ESC = "\x1b"

def enable_windows_ansi():
    if os.name != "nt":
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint()
        kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass

def set_windows_font(height=None, width=None, face=None):
    if os.name != "nt":
        return
    if height is None and width is None and face is None:
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
        class CONSOLE_FONT_INFOEX(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_ulong),
                ("nFont", ctypes.c_ulong),
                ("dwFontSize", COORD),
                ("FontFamily", ctypes.c_uint),
                ("FontWeight", ctypes.c_uint),
                ("FaceName", ctypes.c_wchar * 32),
            ]
        info = CONSOLE_FONT_INFOEX()
        info.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
        info.nFont = 0
        info.dwFontSize.X = 0 if width is None else int(width)
        info.dwFontSize.Y = 0 if height is None else int(height)
        info.FontFamily = 54
        info.FontWeight = 400
        if face:
            fname = str(face)[:31]
            info.FaceName = fname
        kernel32.SetCurrentConsoleFontEx(handle, False, ctypes.byref(info))
    except Exception:
        pass

def get_windows_font():
    if os.name != "nt":
        return None
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
        class CONSOLE_FONT_INFOEX(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_ulong),
                ("nFont", ctypes.c_ulong),
                ("dwFontSize", COORD),
                ("FontFamily", ctypes.c_uint),
                ("FontWeight", ctypes.c_uint),
                ("FaceName", ctypes.c_wchar * 32),
            ]
        info = CONSOLE_FONT_INFOEX()
        info.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
        kernel32.GetCurrentConsoleFontEx(handle, False, ctypes.byref(info))
        return {"height": info.dwFontSize.Y, "width": info.dwFontSize.X, "face": info.FaceName}
    except Exception:
        return None

def set_windows_console_size(cols=None, lines=None):
    if os.name != "nt":
        return
    if cols is None and lines is None:
        return
    try:
        parts = []
        if cols is not None:
            parts.append(f"cols={int(cols)}")
        if lines is not None:
            parts.append(f"lines={int(lines)}")
        if parts:
            subprocess.call(f"mode con: {' '.join(parts)}", shell=True)
    except Exception:
        pass

def get_terminal_size():
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 120, 30

def move_cursor(row, col):
    sys.stdout.write(f"{ESC}[{row};{col}H")

def hide_cursor():
    sys.stdout.write(f"{ESC}[?25l")

def show_cursor():
    sys.stdout.write(f"{ESC}[?25h")

def clear_region(top, left, width, height):
    for r in range(height):
        move_cursor(top + r, left)
        sys.stdout.write(" " * max(0, width))

def load_frames_from_files(pattern):
    frames = []
    for file in sorted(glob.glob(pattern)):
        with open(file, "r", encoding="utf-8") as f:
            frames.append(f.read())
    return frames

def load_frames_from_single_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    # Split frames by one or more blank lines
    chunks = [chunk for chunk in content.split("\n\n") if chunk.strip()]
    return chunks

def normalize_frame(frame):
    lines = frame.splitlines()
    if not lines:
        return [""]
    return lines

def compute_max_dims(frames_lines):
    max_w = 0
    max_h = 0
    for lines in frames_lines:
        max_h = max(max_h, len(lines))
        for ln in lines:
            max_w = max(max_w, len(ln))
    return max_w, max_h

def stretch_x(lines, new_w):
    if new_w <= 0:
        return lines
    out = []
    for ln in lines:
        src = ln
        w = len(src)
        if w == 0:
            out.append("".ljust(new_w))
            continue
        row = []
        for j in range(new_w):
            idx = int(j * w / new_w)
            if idx >= w:
                idx = w - 1
            row.append(src[idx])
        out.append("".join(row))
    return out

def resample_y(lines, new_h):
    if new_h <= 0:
        return lines
    h = len(lines)
    if h == 0:
        return [""]
    if new_h >= h:
        return lines
    out = []
    for r in range(new_h):
        idx = int(r * h / new_h)
        if idx >= h:
            idx = h - 1
        out.append(lines[idx])
    return out

def main():
    parser = argparse.ArgumentParser(description="Play ASCII animation in a screen corner")
    parser.add_argument("--source", default=r"C:\\Users\\mohit\\ascii-live\\animations\\my-animation\\*.txt*", help="Glob for multiple frame files or a single file path with frames separated by blank lines")
    parser.add_argument("--corner", choices=["top-left", "top-right", "bottom-left", "bottom-right"], default="top-left", help="Screen corner to render the animation")
    parser.add_argument("--pad-x", type=int, default=2, help="Horizontal padding from the edge")
    parser.add_argument("--pad-y", type=int, default=1, help="Vertical padding from the edge")
    parser.add_argument("--fps", type=float, default=20.0, help="Frames per second")
    parser.add_argument("--frame-width", type=int, default=None, help="Explicit frame width override")
    parser.add_argument("--target-width", type=int, default=None, help="Target width after downscaling")
    parser.add_argument("--target-height", type=int, default=None, help="Target height after downscaling")
    parser.add_argument("--fit", type=float, default=None, help="Fraction of terminal size for target region (0.05-1.0)")
    parser.add_argument("--scale", type=float, default=0.5, help="Downscale factor between 0.02 and 1.0")
    parser.add_argument("--square", action="store_true", help="Force 1:1 aspect ratio (width == height)")
    parser.add_argument("--square-stretch", action="store_true", help="Make square by stretching width to match height without cropping")
    parser.add_argument("--font-size", type=int, default=None, help="Console font height in pixels (Windows)")
    parser.add_argument("--font-width", type=int, default=None, help="Console font width in pixels (Windows)")
    parser.add_argument("--font-name", default=None, help="Console font name (Windows)")
    parser.add_argument("--tiny", action="store_true", help="Shrink console font aggressively for compact display (Windows)")
    parser.add_argument("--mode-cols", type=int, default=None, help="Console columns for Windows resize")
    parser.add_argument("--mode-lines", type=int, default=None, help="Console lines for Windows resize")
    parser.add_argument("--zoom-out", action="store_true", help="Aggressive zoom out: tiny font and large console size")
    parser.add_argument("--color", default="green", help="Foreground color name or 256-code (e.g., '34' or 'green')")
    parser.add_argument("--bg", default="black", help="Background color name or 256-code (e.g., '40' or 'black')")
    parser.add_argument("--bold", action="store_true", help="Render text in bold/intense mode")
    parser.add_argument("--new-window", action="store_true", help="Launch the animation in a new console window")
    parser.add_argument("--child", action="store_true", help="Internal flag to prevent re-spawn when launching new window")
    args = parser.parse_args()

    # Defaults when no CLI args provided
    if len(sys.argv) == 1:
        args.source = r"C:\\Users\\mohit\\ascii-live\\animations\\my-animation\\all frame.txt"
        args.corner = "top-left"
        args.pad_x = 0
        args.pad_y = 0
        args.fps = 20
        args.square_stretch = True
        args.new_window = True
        args.font_size = 5
        args.font_width = 3
        args.font_name = "Consolas"
        args.zoom_out = True
        args.mode_cols = 640
        args.mode_lines = 240

    if args.new_window and not args.child:
        if os.name == "nt":
            child_argv = [sys.executable, os.path.abspath(__file__)]
            for a in sys.argv[1:]:
                if a == "--new-window":
                    continue
                child_argv.append(a)
            child_argv.append("--child")
            try:
                subprocess.Popen(child_argv, creationflags=subprocess.CREATE_NEW_CONSOLE)
                return
            except Exception:
                pass

    enable_windows_ansi()
    if args.tiny and os.name == "nt":
        set_windows_font(height=6, width=3, face=args.font_name or "Consolas")
    else:
        set_windows_font(height=args.font_size, width=args.font_width, face=args.font_name)
    if os.name == "nt":
        if args.zoom_out:
            if args.font_size is None:
                set_windows_font(height=5, width=2, face=args.font_name or "Consolas")
            set_windows_console_size(cols=args.mode_cols or 640, lines=args.mode_lines or 240)
        else:
            set_windows_console_size(cols=args.mode_cols, lines=args.mode_lines)

    # Load frames
    if os.path.isfile(args.source):
        frames = load_frames_from_single_file(args.source)
    else:
        frames = load_frames_from_files(args.source)

    frames_lines = [normalize_frame(f) for f in frames]
    orig_w, orig_h = compute_max_dims(frames_lines)
    target_w = None
    target_h = None

    term_cols, term_rows = get_terminal_size()
    pad_x = max(0, args.pad_x)
    pad_y = max(0, args.pad_y)
    avail_cols = max(1, term_cols - pad_x)
    avail_rows = max(1, term_rows - pad_y)

    if args.fit is not None:
        fit = max(0.05, min(1.0, args.fit))
        target_w = max(1, int(math.floor(avail_cols * fit)))
        target_h = max(1, int(math.floor(avail_rows * fit)))
    elif args.target_width or args.target_height:
        if args.target_width and args.target_height:
            target_w, target_h = args.target_width, args.target_height
        elif args.target_width:
            target_w = args.target_width
            target_h = max(1, int(round(orig_h * (target_w / max(1, orig_w)))))
        else:
            target_h = args.target_height
            target_w = max(1, int(round(orig_w * (target_h / max(1, orig_h)))))
    elif args.frame_width:
        target_w = args.frame_width
        target_h = max(1, int(round(orig_h * (target_w / max(1, orig_w)))))
    else:
        scale = max(0.02, min(1.0, args.scale if args.scale is not None else 1.0))
        target_w = max(1, int(math.floor(orig_w * scale)))
        target_h = max(1, int(math.floor(orig_h * scale)))
        target_w = min(target_w, avail_cols)
        target_h = min(target_h, avail_rows)

    if args.square:
        m = max(1, min(target_w or 1, target_h or 1))
        target_w = m
        target_h = m

    if args.square_stretch:
        term_cols, term_rows = get_terminal_size()
        pad_x = max(0, args.pad_x)
        max_w0, max_h0 = compute_max_dims(frames_lines)
        desired = max(1, min(max_h0, term_cols - pad_x))
        frames_lines = [stretch_x(lines, desired) for lines in frames_lines]
        target_w = orig_w
        target_h = orig_h

    step_x = max(1, int(math.floor(orig_w / max(1, target_w))))
    step_y = max(1, int(math.floor(orig_h / max(1, target_h))))

    if step_x > 1 or step_y > 1:
        def shrink_xy(lines):
            out = []
            for r in range(0, len(lines), step_y):
                ln = lines[r]
                out.append(ln[::step_x])
            return out if out else [""]
        frames_lines = [shrink_xy(lines) for lines in frames_lines]

    max_w, max_h = compute_max_dims(frames_lines)
    region_w = args.frame_width if args.frame_width and args.frame_width > 0 else max_w
    region_h = max_h

    cols, rows = term_cols, term_rows

    region_w = max(1, min(region_w, max(1, cols - pad_x)))
    region_h = max(1, min(region_h, max(1, rows - pad_y)))

    if args.corner == "top-left":
        left = 1 + pad_x
        top = 1 + pad_y
    elif args.corner == "top-right":
        left = max(1, cols - region_w - pad_x)
        top = 1 + pad_y
    elif args.corner == "bottom-left":
        left = 1 + pad_x
        top = max(1, rows - region_h - pad_y)
    else:
        left = max(1, cols - region_w - pad_x)
        top = max(1, rows - region_h - pad_y)

    delay = 1.0 / max(1e-6, args.fps)

    def color_code(name, is_bg=False):
        basic = {
            "black": 30,
            "red": 31,
            "green": 32,
            "yellow": 33,
            "blue": 34,
            "magenta": 35,
            "cyan": 36,
            "white": 37,
        }
        if isinstance(name, str) and name.isdigit():
            code = int(name)
            return code
        base = basic.get(str(name).lower(), 32)
        return base + 10 if is_bg else base

    fg = color_code(args.color, is_bg=False)
    bg = color_code(args.bg, is_bg=True)
    bold_prefix = f"{ESC}[1m" if args.bold else ""
    color_prefix = f"{bold_prefix}{ESC}[{fg}m{ESC}[{bg}m"
    reset = f"{ESC}[0m"

    try:
        hide_cursor()
        # Pre-clear region once
        clear_region(top, left, region_w, region_h)
        while True:
            for lines in frames_lines:
                # Erase previous frame region
                clear_region(top, left, region_w, region_h)
                # Draw current frame
                for r, ln in enumerate(lines):
                    move_cursor(top + r, left)
                    sys.stdout.write(color_prefix + (ln[:region_w]).ljust(region_w) + reset)
                sys.stdout.flush()
                time.sleep(delay)
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        sys.stdout.flush()

if __name__ == "__main__":
    main()
