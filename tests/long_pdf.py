"""긴 PDF(쪽 단위 텍스트화 + BM25 검색) 테스트.

실행: python3 tests/long_pdf.py
- 80쪽짜리 한국어 PDF를 만들어 올리고, 쪽 수 인식, 묶음 분석, 쪽 번호 표시,
  가르칠 때 추적기에 원문 전체가 아니라 관련 조각만 가는지 확인한다.
"""
import asyncio
import pathlib
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "out"
TOPICS = ["광합성", "세포 호흡", "삼투 현상", "효소의 작용", "유전자 발현", "신경 전달", "호르몬 조절", "생태계 순환"]


def make_pdf_html():
    pages = []
    for i in range(80):
        t = TOPICS[i % len(TOPICS)]
        body = (f"{t} 단원 {i + 1}쪽. {t}은(는) 생명 활동에서 중요한 과정이다. "
                f"이 쪽에서는 {t}의 조건과 결과를 설명한다. 특이 표시어 키워드{i + 1}번이 이 쪽에만 나온다. ") * 6
        pages.append(f'<section style="page-break-after:always;font-size:14px;line-height:1.7">{body}</section>')
    return "<html><body style=\"font-family:'Noto Sans CJK KR'\">" + "".join(pages) + "</body></html>"


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        maker = await browser.new_page()
        await maker.set_content(make_pdf_html())
        pdf_path = OUT / "long-test.pdf"
        await maker.pdf(path=str(pdf_path), format="A5")
        await maker.close()

        html = (ROOT / "teach-me.html").read_text(encoding="utf-8")
        mock = (ROOT / "tests" / "mock-ai.js").read_text(encoding="utf-8")
        html = html.replace('<div id="app"></div>', "<script>" + mock + "</script>\n<div id=\"app\"></div>", 1)
        (OUT / "long.html").write_text(html, encoding="utf-8")

        page = await browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto((OUT / "long.html").as_uri())
        await page.wait_for_timeout(500)
        await page.click(".title")
        await page.wait_for_timeout(600)
        await page.click(".menu >> text=공부")
        await page.click("text=새 학습")
        await page.wait_for_timeout(300)
        await page.set_input_files("#file", str(pdf_path))
        await page.wait_for_function("document.querySelector('textarea').value.length > 1000", timeout=60000)
        toast = await page.locator(".toast").last.text_content()
        print("업로드 알림:", toast)
        await page.click("text=자료 분석하기")
        await page.wait_for_selector("text=가르치기 시작", timeout=60000)
        n_an = await page.evaluate("window.__prompts.filter(x => x.text.indexOf('자료 분석 계층') >= 0).length")
        print("분석 묶음 수:", n_an)
        labels = await page.locator(".sec-title .pg").all_text_contents()
        print("구간 쪽 표시:", labels)
        await page.screenshot(path=OUT / "long-outline.png", full_page=True)
        await page.click("text=가르치기 시작")
        await page.wait_for_timeout(300)
        await page.fill("textarea", "광합성 단원에서 특이 표시어 키워드41번이 나오는 쪽을 설명할게.")
        await page.click("text=보내기")
        await page.wait_for_timeout(600)
        tr = await page.evaluate("window.__prompts.filter(x => x.text.indexOf('이해 상태 추적기') >= 0).slice(-1)[0]")
        src = tr["text"].split("[원문")[1].split("[학습 목표]")[0]
        print("추적기 원문 글자 수:", len(src), "/ 키워드41번 포함:", "키워드41번" in src.replace(" ", "").replace("\\n", ""), "/ p.41 표시:", "[p.41]" in src)
        i = src.find("[p.41]"); print("p.41 조각:", src[i:i+160].replace("\\n", " "))
        await page.click('role=tab[name="런타임"]')
        await page.wait_for_timeout(200)
        note = await page.locator(".pill.see").first.text_content()
        print("런타임 기록:", note)
        await page.screenshot(path=OUT / "long-runtime.png", full_page=True)
        await browser.close()
        print("오류:", errors or "없음")


if __name__ == "__main__":
    asyncio.run(main())
