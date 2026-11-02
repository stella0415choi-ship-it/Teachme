"""Galmuri11 픽셀 폰트(OFL)를 teach-me.html 안의 FONTS 블록에 넣는다.

아티팩트는 Google Fonts 말고 다른 곳에서 폰트를 불러올 수 없어서 파일 안에 직접 넣는다.
실행: python3 tools/embed_fonts.py
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
html_path = ROOT / "teach-me.html"
faces = [("Galmuri11", "Galmuri11.woff2"), ("Galmuri11 Bold", "Galmuri11-Bold.woff2")]
css = ""
for family, file in faces:
    b64 = base64.b64encode((ROOT / "assets" / "fonts" / file).read_bytes()).decode()
    css += "@font-face{font-family:'%s';src:url(data:font/woff2;base64,%s) format('woff2');font-display:swap}\n" % (family, b64)
block = "<!-- FONTS:START -->\n<style id=\"fonts\">\n" + css + "</style>\n<!-- FONTS:END -->"
html = html_path.read_text(encoding="utf-8")
new, n = re.subn(r"<!-- FONTS:START -->.*?<!-- FONTS:END -->", lambda m: block, html, flags=re.S)
if n != 1:
    raise SystemExit("teach-me.html에서 FONTS 표시를 찾지 못했어요.")
html_path.write_text(new, encoding="utf-8")
print("폰트 넣음 / 파일 크기:", html_path.stat().st_size // 1024, "KB")
