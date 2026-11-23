"""학생 안내 페이지 QR 이미지 만들기 (교실 화면·슬라이드용)

사용법 (저장소 폴더에서):
    python scripts/make_qr.py
    python scripts/make_qr.py --url https://... --title "존중 캠페인" --out qr.png
"""
import argparse
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
URL = "https://hongyul67-cpu.github.io/respect-campaign/"


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    for name in (["malgunbd.ttf"] if bold else []) + ["malgun.ttf"]:
        p = Path("C:/Windows/Fonts") / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


def centered(draw: ImageDraw.ImageDraw, y: int, text: str, f, fill: str, width: int) -> int:
    l, t, r, b = draw.textbbox((0, 0), text, font=f)
    draw.text(((width - (r - l)) / 2 - l, y - t), text, font=f, fill=fill)
    return y + (b - t)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--url", default=URL)
    p.add_argument("--title", default="온라인에서도 존중해요")
    p.add_argument("--sub", default="QR 찍고 → 매너 읽고 → 좋은 댓글 달고 → 캡처 제출")
    p.add_argument("--out", type=Path, default=ROOT / "qr-code.png")
    a = p.parse_args()

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=24, border=2)
    qr.add_data(a.url)
    qr.make(fit=True)
    code = qr.make_image(fill_color="#1d2433", back_color="white").convert("RGB")

    W, H = 1200, 1600
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 16], fill="#2f6fed")

    y = centered(d, 90, "경기기계공업고등학교 · 상호존중 캠페인", font(40, bold=False), "#5b6475", W)
    y = centered(d, y + 40, a.title, font(84), "#1d2433", W)

    size = 820
    code = code.resize((size, size), Image.NEAREST)
    qy = y + 70
    d.rounded_rectangle([(W - size) / 2 - 24, qy - 24, (W + size) / 2 + 24, qy + size + 24],
                        radius=36, outline="#2f6fed", width=8)
    img.paste(code, ((W - size) // 2, qy))

    y = centered(d, qy + size + 80, a.sub, font(40), "#2f6fed", W)
    centered(d, y + 40, "참여하면 상점! · 아이디·프로필 사진은 가리고 캡처", font(34, bold=False), "#5b6475", W)
    centered(d, H - 70, a.url, font(26, bold=False), "#9aa3b2", W)

    img.save(a.out)
    print(f"저장: {a.out}")


if __name__ == "__main__":
    main()
