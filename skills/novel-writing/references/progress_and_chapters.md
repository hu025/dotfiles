# Novel Progress & Chapter Reading

## Reliable Chapter Count (use this, not progress.json)

`progress.json` `current_chapter` field often returns `?` — field names vary across project versions.

**Always count from filesystem instead:**

```python
import os, glob, re

def get_chapter_range(novel_root):
    chapters_dir = os.path.join(novel_root, 'chapters')
    files = glob.glob(f'{chapters_dir}/*')
    nums = []
    for f in files:
        base = os.path.basename(f)
        m = re.search(r'第(\d+)章', base)
        if m:
            nums.append(int(m.group(1)))
    return f"已完成 {max(nums)} 章" if nums else "无章节文件"
```

**Known project paths (verified 2026-06-28):**
- 末日一小时: `/home/saber/.hermes/novels/小说/末日一小时，我搬空超市杀穿末世/`
- 高武重生: `/home/saber/.hermes/novels/小说/高武重生：我的词条顿悟系统/`

**Known chapter file formats:**
- `.txt` files named `第01章.txt`, `第02章.txt` ... (末日一小时)
- `.md` files named `第10章_深夜伏击，斩草除根.md` ... (高武重生 — regex `第(\d+)章` works for both)

## Reading progress.json (supplementary only)

If you also want total/target plan, read `progress.json` with these known field names:
- `total_chapters` — planned total (not always present)
- `current_chapter` — often unreliable, treat as optional
- `chapter` — sometimes used instead of `current_chapter`

```python
import json
with open(progress_json_path) as f:
    d = json.load(f)
total = d.get('total_chapters', '?')
# current_chapter is unreliable — don't rely on it for actual count
```

## Quick Probe One-liner

```bash
# Count chapters by filename
find "/path/to/chapters" -name "*.md" -o -name "*.txt" | \
  grep -oP '第\K\d+' | sort -n | tail -1
```
