#!/usr/bin/env python3
"""
Resize and center-crop images to fixed aspect ratio targets.
Saves outputs under `images/resized/{WxH}/` and optional WebP alongside.

Usage: python resize_images.py
"""
from PIL import Image
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / 'images'
OUT_DIR = IMG_DIR / 'resized'
TARGETS = [ (1600,1067), (3200,2133) ]  # 3:2 aspect
CREATE_WEBP = True
QUALITY = 82

if not IMG_DIR.exists():
    print('images/ directory not found at', IMG_DIR)
    sys.exit(1)

images = [p for p in IMG_DIR.iterdir() if p.suffix.lower() in ('.jpg','.jpeg','.png') and p.is_file()]
if not images:
    print('No jpg/png images found in', IMG_DIR)
    sys.exit(0)

OUT_DIR.mkdir(parents=True, exist_ok=True)

def center_crop_to_ratio(img: Image.Image, target_w:int, target_h:int) -> Image.Image:
    target_ratio = target_w / target_h
    w, h = img.size
    src_ratio = w / h
    if abs(src_ratio - target_ratio) < 1e-6:
        return img
    if src_ratio > target_ratio:
        # source is wider -> crop width
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        # source is taller -> crop height
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

print(f'Found {len(images)} images. Resizing to: {TARGETS}')
for img_path in images:
    try:
        with Image.open(img_path) as im:
            im = im.convert('RGB')
            for tw, th in TARGETS:
                out_sub = OUT_DIR / f'{tw}x{th}'
                out_sub.mkdir(parents=True, exist_ok=True)
                cropped = center_crop_to_ratio(im, tw, th)
                resized = cropped.resize((tw, th), Image.LANCZOS)
                out_name = out_sub / img_path.name
                resized.save(out_name, format='JPEG', quality=QUALITY, optimize=True)
                print('Wrote', out_name)
                if CREATE_WEBP:
                    webp_name = out_sub / (img_path.stem + '.webp')
                    resized.save(webp_name, format='WEBP', quality=80, method=6)
                    print('Wrote', webp_name)
    except Exception as e:
        print('Error processing', img_path, e)

print('Done.')
