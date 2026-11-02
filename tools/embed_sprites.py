"""assets/harin/*.webp 표정 그림과 assets/title/*.png 타이틀 그림을 teach-me.html 안의 sprites 블록에 넣는다.

아티팩트는 HTML 파일 하나로 올려야 해서 그림을 파일 안에 글자(base64)로 넣어 둔다.
그림을 바꾸거나 추가한 뒤 실행: python3 tools/embed_sprites.py
"""
import base64
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
html_path = ROOT / "teach-me.html"
data = {}
for f in sorted((ROOT / "assets" / "harin").glob("*.webp")):
    data[f.stem] = "data:image/webp;base64," + base64.b64encode(f.read_bytes()).decode()
# 타이틀 화면 그림(로고, 이모티콘 스티커)은 title-이름 으로 넣는다. 큰 발표용 PNG(logo-x24 등)는 빼고.
for f in sorted((ROOT / "assets" / "title").glob("*.png")):
    if "-x" in f.stem:
        continue
    data["title-" + f.stem] = "data:image/png;base64," + base64.b64encode(f.read_bytes()).decode()

block = (
    "<!-- SPRITES:START -->\n"
    '<script id="sprites" type="application/json">' + json.dumps(data) + "</script>\n"
    "<!-- SPRITES:END -->"
)
html = html_path.read_text(encoding="utf-8")
new, n = re.subn(r"<!-- SPRITES:START -->.*?<!-- SPRITES:END -->", lambda m: block, html, flags=re.S)
if n != 1:
    raise SystemExit("teach-me.html에서 SPRITES 표시를 찾지 못했어요.")
html_path.write_text(new, encoding="utf-8")
print("넣은 그림:", ", ".join(data), "/ 파일 크기:", html_path.stat().st_size // 1024, "KB")
