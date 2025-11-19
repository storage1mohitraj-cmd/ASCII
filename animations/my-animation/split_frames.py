import os
import re
import argparse

def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def split_frames(text):
    parts = re.split(r"\n\s*\n+", text.strip())
    return [p for p in parts if p.strip()]

def write_frames(frames, out_dir, prefix, pad, limit):
    os.makedirs(out_dir, exist_ok=True)
    n = len(frames) if limit is None else min(len(frames), limit)
    paths = []
    for i in range(n):
        name = f"{prefix}{str(i+1).zfill(pad)}.txt"
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(frames[i])
        paths.append(path)
    return paths

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=False, default=r"C:\\Users\\mohit\\ascii-live\\animations\\my-animation\\frame0001.txt.txt")
    p.add_argument("--dir", default=r"C:\\Users\\mohit\\ascii-live\\animations\\my-animation")
    p.add_argument("--prefix", default="frame")
    p.add_argument("--pad", type=int, default=4)
    p.add_argument("--limit", type=int, default=64)
    args = p.parse_args()

    text = read_text(args.input)
    frames = split_frames(text)
    paths = write_frames(frames, args.dir, args.prefix, args.pad, args.limit)
    for pth in paths:
        print(pth)

if __name__ == "__main__":
    main()