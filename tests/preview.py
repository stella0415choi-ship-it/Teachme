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
        await page.wait_for_timeout(700)
        await page.screenshot(path=OUT / "1a-home.png")
        # 잡담 4턴 → 공부하러 가기 질문
        for _ in range(4):
            await page.click(".dbox.tap")
            await page.wait_for_timeout(150)
            await page.click(".choice >> nth=0")
            await page.wait_for_timeout(250)
        await page.screenshot(path=OUT / "1b-home-chat.png")
        await page.click(".dbox.tap")
        await page.wait_for_timeout(200)
        await page.screenshot(path=OUT / "1c-home-ask.png", full_page=True)
        await page.click("text=공부하러 가기")
        await page.wait_for_timeout(300)
        await page.screenshot(path=OUT / "1d-study.png", full_page=True)
        await page.click("text=새 학습")
        await page.wait_for_timeout(300)
        await page.screenshot(path=OUT / "1-upload.png", full_page=True)
        await page.click("text=예시 자료 넣기")
        await page.click("text=자료 분석하기")
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / "2-outline.png", full_page=True)
        await page.click("text=다음: 목표 고르기")
        await page.wait_for_timeout(300)
        await page.click(".info >> nth=0")
        await page.screenshot(path=OUT / "2b-goal.png")
        await page.click("text=가르치기 시작")
        await page.wait_for_timeout(300)
        await page.fill("textarea", "무단 통치 때는 헌병이 경찰 일을 했어. 문화 통치 때는 헌병 경찰제를 보통 경찰제로 바꿨어.")
        await page.click('button[aria-label="보내기"]')
        await page.wait_for_timeout(500)
        await page.screenshot(path=OUT / "3-teach.png")
        await page.click(".tc-face")
        await page.wait_for_timeout(200)
        await page.screenshot(path=OUT / "4-note.png")
        await page.click(".modal >> text=런타임")
        await page.wait_for_timeout(200)
        await page.screenshot(path=OUT / "5-runtime.png")
        await page.click(".modal >> text=닫기")
        await page.click("text=수업 끝내고 시험 보기")
        await page.wait_for_timeout(2200)
        await page.screenshot(path=OUT / "5b-exam-q1.png")
        await page.wait_for_timeout(3800)
        await page.screenshot(path=OUT / "5c-exam-q2.png")
        await page.wait_for_selector(".score", timeout=30000)
        await page.wait_for_timeout(400)
        await page.screenshot(path=OUT / "6-review.png", full_page=True)
        # 내 학습, 업적, 설정
        await page.click(".navbar >> text=홈")
        await page.wait_for_timeout(300)
        await page.click(".navbar >> text=공부")
        await page.click("text=내 학습")
        await page.wait_for_timeout(300)
        await page.screenshot(path=OUT / "7-library.png", full_page=True)
        await page.click(".navbar >> text=다이어리")
        await page.wait_for_timeout(300)
        await page.screenshot(path=OUT / "8-diary.png")
        await page.click(".navbar >> text=설정")
        await page.wait_for_timeout(300)
        await page.screenshot(path=OUT / "9-settings.png", full_page=True)
        # 새로고침해도 남는지
        await page.reload()
        await page.wait_for_timeout(600)
        await page.click(".title")
        await page.wait_for_timeout(700)
        await page.click(".navbar >> text=공부")
        await page.click("text=내 학습")
        await page.wait_for_timeout(300)
        n = await page.locator(".folder").count()
        print("새로고침 뒤 내 학습 폴더 수:", n)
        await browser.close()
    print("스크린샷:", OUT)
    print("오류:", errors or "없음")


if __name__ == "__main__":
    asyncio.run(main())
