"""가짜 AI(mock-ai.js)를 넣은 복사본으로 모든 화면을 끝까지 눌러보고 스크린샷을 찍는다.

실행: python3 tests/preview.py
결과: tests/out/ 폴더에 화면별 PNG, 자바스크립트 오류가 있으면 마지막에 출력.
게시용 teach-me.html은 건드리지 않는다.
"""
import asyncio
import pathlib
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "out"


def build_preview():
    html = (ROOT / "teach-me.html").read_text(encoding="utf-8")
    mock = (ROOT / "tests" / "mock-ai.js").read_text(encoding="utf-8")
    html = html.replace('<div id="app"></div>', "<script>" + mock + "</script>\n<div id=\"app\"></div>", 1)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "preview.html"
    path.write_text(html, encoding="utf-8")
    return path


async def main():
    page_path = build_preview()
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(page_path.as_uri())
        await page.wait_for_timeout(300)
        await page.screenshot(path=OUT / "0-title-intro.png")
        await page.wait_for_timeout(4500)
        await page.screenshot(path=OUT / "0-title.png")
        await page.click("text=눌러서 시작하기")
        await page.wait_for_timeout(600)
        await page.screenshot(path=OUT / "1-upload.png", full_page=True)
        await page.click("text=예시 자료 넣기")
        await page.click("text=자료 분석하기")
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / "2-outline.png", full_page=True)
        await page.click("text=가르치기 시작")
        await page.wait_for_timeout(300)
        await page.fill("textarea", "무단 통치 때는 헌병이 경찰 일을 했어. 문화 통치 때는 헌병 경찰제를 보통 경찰제로 바꿨어.")
        await page.click("text=보내기")
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / "3-teach.png", full_page=True)
        await page.click('role=tab[name="지민의 공책"]')
        await page.wait_for_timeout(200)
        await page.screenshot(path=OUT / "4-note.png", full_page=True)
        await page.click('role=tab[name="런타임"]')
        await page.wait_for_timeout(200)
        await page.screenshot(path=OUT / "5-runtime.png", full_page=True)
        await page.click("text=수업 끝내고 시험 보기")
        await page.wait_for_timeout(800)
        await page.screenshot(path=OUT / "6-review.png", full_page=True)
        await browser.close()
    print("스크린샷:", OUT)
    print("오류:", errors or "없음")


if __name__ == "__main__":
    asyncio.run(main())
