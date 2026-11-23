"""3회차 존중 메시지 카드 만들기 → docs/cards/card-1.png ~ card-N.png

사용법 (저장소 폴더에서):
    python scripts/make_cards.py

문구를 바꾸고 싶으면 아래 CARDS 목록만 고친 뒤 다시 실행하세요.
(줄바꿈은 \n 으로 넣습니다. 한 줄에 10~12글자 정도가 보기 좋습니다.)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "cards"

# (받는 사람, 문구, 배경색, 강조색)
CARDS = [
    ("친구에게", "보내기 전 3초,\n읽는 사람을\n생각해요", "#e8f0ff", "#2f6fed"),
    ("친구에게", "다른 생각은\n틀린 생각이\n아니에요", "#e6f6ef", "#12805c"),
    ("친구에게", "읽씹 대신\n\"확인했어!\"\n한마디", "#f1ecff", "#7c3aed"),
    ("가족에게", "오늘도\n고생 많으셨어요.\n늘 고마워요", "#fff3e6", "#b4540a"),
    ("선생님께", "선생님,\n오늘 수업\n감사합니다", "#e4f5f3", "#0f766e"),
    ("현장실습 · 직장", "인사부터\n존중입니다", "#e9edf5", "#1d2433"),
    ("현장실습 · 직장", "모르면\n물어보는 것도\n예의예요", "#eef4ff", "#1e4fb8"),
    ("모두에게", "얼굴 보고 못 할 말은\n온라인에서도\n하지 않아요", "#fdecf3", "#be185d"),
]

SIZE = 1080


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for name in (["malgunbd.ttf"] if bold else []) + ["malgun.ttf"]:
        p = Path("C:/Windows/Fonts") / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


def text_w(d: ImageDraw.ImageDraw, s: str, f) -> int:
    l, _, r, _ = d.textbbox((0, 0), s, font=f)
    return r - l


def make(i: int, to: str, msg: str, bg: str, accent: str) -> Path:
    img = Image.new("RGB", (SIZE, SIZE), bg)
    d = ImageDraw.Draw(img)
    m = 80

    # 받는 사람 라벨
    lf = font(40)
    lw = text_w(d, to, lf)
    d.rounded_rectangle([m, m, m + lw + 60, m + 76], radius=38, fill=accent)
    d.text((m + 30, m + 12), to, font=lf, fill="white")

    # 큰 따옴표
    d.text((m - 6, 190), "\u201c", font=font(220), fill=accent)

    # 본문: 가장 긴 줄이 폭에 맞도록 글자 크기 조정
    lines = msg.split("\n")
    size = 120
    while size > 60:
        f = font(size)
        if max(text_w(d, ln, f) for ln in lines) <= SIZE - 2 * m:
            break
        size -= 4
    f = font(size)
    lh = int(size * 1.35)
    y = (SIZE - lh * len(lines)) // 2 + 60
    for ln in lines:
        d.text((m, y), ln, font=f, fill="#1d2433")
        y += lh

    # 아래 줄
    d.rectangle([m, SIZE - 150, m + 90, SIZE - 142], fill=accent)
    d.text((m, SIZE - 120), "경기기계공업고등학교 상호존중 캠페인", font=font(34, bold=False), fill="#5b6475")

    path = OUT / f"card-{i}.png"
    img.save(path, optimize=True)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(CARDS, 1):
        print("저장:", make(i, *c).relative_to(ROOT))


if __name__ == "__main__":
    main()
