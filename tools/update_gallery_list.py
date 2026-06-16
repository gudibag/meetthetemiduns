#!/usr/bin/env python3
"""Update index.html gallery image list from the images folder."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / 'index.html'
IMG_DIR = ROOT / 'images'

VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
GALLERY_MARKER = re.compile(
    r"(const galleryImages = \[\n)([\s\S]*?)(\n\];\n)",
    flags=re.MULTILINE,
)

if not HTML_FILE.exists():
    raise SystemExit(f'index.html not found at {HTML_FILE}')
if not IMG_DIR.exists():
    raise SystemExit(f'images directory not found at {IMG_DIR}')

images = sorted(
    [p.name for p in IMG_DIR.iterdir() if p.suffix.lower() in VALID_EXTENSIONS and p.is_file()]
)
if not images:
    raise SystemExit('No images found in images/ to build the gallery list.')

entries = ',\n'.join(f"  'images/{name}'" for name in images)
replacement = f"const galleryImages = [\n{entries}\n];\n"

content = HTML_FILE.read_text(encoding='utf-8')
new_content, count = GALLERY_MARKER.subn(lambda m: m.group(1) + entries + m.group(3), content, count=1)
if count == 0:
    raise SystemExit('Could not find galleryImages array marker in index.html')

HTML_FILE.write_text(new_content, encoding='utf-8')
print(f'Updated galleryImages with {len(images)} entries from images/')
