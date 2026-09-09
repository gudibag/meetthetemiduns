#!/usr/bin/env python3
"""Scan workspace files and update dates to include weekday, e.g.
November 20, 2026 -> Friday, November 20, 2026
"""
import re
from datetime import date
from pathlib import Path

WEEKDAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
MONTHS = {
    'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
    'July':7,'August':8,'September':9,'October':10,'November':11,'December':12
}

month_name_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})'
slash_pattern = r'\b(\d{1,2})/(\d{1,2})/(\d{2,4})\b'
iso_pattern = r'\b(\d{4})-(\d{2})-(\d{2})\b'

WK_LOOKBEHIND = re.compile(r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s*$')

def insert_weekday_for_monthname(match, text):
    start = match.start()
    # avoid adding if there's already a weekday just before
    pre = text[max(0, start-20):start]
    if re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s*$', pre):
        return match.group(0)
    mname, day_s, year_s = match.group(1), match.group(2), match.group(3)
    day_i = int(day_s)
    year_i = int(year_s)
    month_i = MONTHS[mname]
    try:
        wk = date(year_i, month_i, day_i).strftime('%A')
    except Exception:
        return match.group(0)
    return f"{wk}, {mname} {day_i}, {year_i}"

def insert_weekday_for_slash(match, text):
    start = match.start()
    pre = text[max(0, start-20):start]
    if re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s*$', pre):
        return match.group(0)
    m, d, y = match.group(1), match.group(2), match.group(3)
    mm, dd = int(m), int(d)
    yy = int(y)
    if yy < 100:
        yy += 2000
    try:
        dt = date(yy, mm, dd)
    except Exception:
        return match.group(0)
    return f"{dt.strftime('%A')}, {dt.strftime('%B')} {dt.day}, {dt.year}"

def insert_weekday_for_iso(match, text):
    start = match.start()
    pre = text[max(0, start-20):start]
    if re.search(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s*$', pre):
        return match.group(0)
    y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
    try:
        dt = date(y, m, d)
    except Exception:
        return match.group(0)
    return f"{dt.strftime('%A')}, {dt.strftime('%B')} {dt.day}, {dt.year}"

def process_text(text):
    # month-name style
    text = re.sub(month_name_pattern, lambda m: insert_weekday_for_monthname(m, text), text)
    # slash style
    text = re.sub(slash_pattern, lambda m: insert_weekday_for_slash(m, text), text)
    # iso style
    text = re.sub(iso_pattern, lambda m: insert_weekday_for_iso(m, text), text)
    return text

def should_process(path: Path):
    return path.suffix.lower() in {'.html', '.htm', '.md', '.txt', '.gs'}

def main():
    root = Path('.').resolve()
    changed = []
    for p in root.rglob('*'):
        if not p.is_file():
            continue
        if not should_process(p):
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        new = process_text(text)
        if new != text:
            # backup
            backup = p.with_suffix(p.suffix + '.bak')
            try:
                p.rename(backup)
                backup.write_text(text, encoding='utf-8')
            except Exception:
                # if rename fails, continue by writing a .bak
                p.with_suffix(p.suffix + '.bak').write_text(text, encoding='utf-8')
            p.write_text(new, encoding='utf-8')
            changed.append(str(p))
    if changed:
        print('Updated files:')
        for c in changed:
            print(' -', c)
    else:
        print('No changes made.')

if __name__ == '__main__':
    main()
