"""폼 응답 CSV → 워드클라우드 PNG + 많이 나온 단어 TOP 20

사용법 (저장소 폴더에서):
    python scripts/make_wordcloud.py data/raw/round1.csv

옵션:
    --column 댓글      문장이 들어 있는 열 이름 일부 (기본: '댓글')
    --out 폴더         결과 저장 폴더 (기본: round1-manner/results)
    --top 20           표에 넣을 단어 수

학번·이름 열은 읽지 않습니다. 댓글 문장 열만 사용합니다.
"""
import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 조사: 긴 것부터 떼어냅니다. 떼고 남은 말이 2글자 이상일 때만 뗍니다.
JOSA = sorted(
    ["에게서", "으로써", "으로서", "에서는", "이라도", "까지", "부터", "에게", "한테",
     "으로", "에서", "보다", "처럼", "만큼", "이나", "라도", "께서", "은", "는", "이",
     "가", "을", "를", "에", "의", "도", "로", "와", "과", "만", "나"],
    key=len, reverse=True,
)

# 동사 끝: '생각하기', '존중하겠습니다' → '생각', '존중'
ENDINGS = sorted(
    ["하겠습니다", "하겠어요", "하겠다", "할게요", "할게", "합니다", "해요", "하자",
     "하기", "하지", "하는", "한다", "하고", "해서", "하면"],
    key=len, reverse=True,
)

# 한 글자지만 의미 있는 말
KEEP_SHORT = {"욕", "말", "글", "답", "톡", "댓"}

STOPWORDS = {
    "나는", "저는", "내가", "제가", "우리", "우리가", "나", "저", "온라인", "온라인상",
    "것", "거", "때", "더", "꼭", "항상", "절대", "절대로", "잘", "한번", "번", "한",
    "하나", "모든", "모두", "같이", "그냥", "정말", "진짜", "많이", "먼저", "서로",
    "있게", "없이", "되기", "되는", "된다", "되도록", "있는", "없는", "위해", "대해",
    "않기", "않고", "않을", "않는", "않는다", "않겠습니다", "않을게요", "않겠다", "안하기",
    "하기", "하지", "했으면", "좋겠다", "약속", "약속합니다", "합니다", "입니다",
    "댓글", "너무", "봤어요", "봤습니다", "있어요", "있습니다", "같아요", "보고", "앞으로",
    "많으셨어요", "많으세요", "주셔서", "됐어요", "알았어요", "해주셔서", "해요", "드려요",
}


def read_csv(path: Path) -> list[dict]:
    """구글 시트 CSV(UTF-8)와 엑셀 CSV(CP949) 둘 다 읽습니다."""
    for enc in ("utf-8-sig", "cp949"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    sys.exit(f"[오류] {path} 파일의 글자 인코딩을 읽을 수 없습니다.")


def find_column(headers: list[str], keyword: str) -> str:
    matches = [h for h in headers if keyword in h and not any(x in h for x in ("캡처", "업로드"))]
    if not matches:
        sys.exit(
            f"[오류] '{keyword}'가 들어간 열이 없습니다.\n"
            f"       열 목록: {headers}\n"
            f"       --column 옵션으로 열 이름 일부를 알려주세요."
        )
    return matches[0]


def normalize(token: str) -> str | None:
    for j in JOSA:
        if token.endswith(j) and len(token) - len(j) >= 2:
            token = token[: -len(j)]
            break
    for e in ENDINGS:
        if token.endswith(e):
            stem = token[: -len(e)]
            if len(stem) >= 2 or stem in KEEP_SHORT:
                token = stem
            break
    if token in STOPWORDS or token.startswith("않"):
        return None
    if len(token) < 2 and token not in KEEP_SHORT:
        return None
    return token


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[가-힣A-Za-z0-9]+", text)
    return [w for w in (normalize(t) for t in words) if w]


def find_font() -> str:
    candidates = [
        "C:/Windows/Fonts/malgunbd.ttf",
        "C:/Windows/Fonts/malgun.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    sys.exit("[오류] 한글 글꼴(맑은 고딕 등)을 찾지 못했습니다.")


PALETTE = ["#2f6fed", "#12805c", "#b4540a", "#7c3aed", "#be185d", "#0f766e", "#1d2433"]


def render(counter: Counter, font_path: str, out: Path,
           width: int = 1600, height: int = 900, max_words: int = 120) -> None:
    """많이 나온 단어일수록 크게, 가운데부터 나선형으로 배치합니다 (Pillow만 사용)."""
    import math
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    items = counter.most_common(max_words)
    hi, lo = items[0][1], items[-1][1]
    placed: list[tuple[int, int, int, int]] = []
    cx, cy, pad = width / 2, height / 2, 6

    def hits(box):
        x0, y0, x1, y1 = box
        if x0 < 10 or y0 < 10 or x1 > width - 10 or y1 > height - 10:
            return True
        return any(x0 < b[2] + pad and x1 + pad > b[0] and y0 < b[3] + pad and y1 + pad > b[1]
                   for b in placed)

    for i, (word, count) in enumerate(items):
        t = (count - lo) / (hi - lo) if hi > lo else 1.0
        size = int(30 + 130 * (t ** 0.7))
        while size >= 18:
            font = ImageFont.truetype(font_path, size)
            l, tp, r, b = draw.textbbox((0, 0), word, font=font)
            w, h = r - l, b - tp
            spot = None
            for step in range(6000):
                a = step * 0.12
                rad = 2.2 * a
                x = cx + rad * math.cos(a) * (width / height) - w / 2
                y = cy + rad * math.sin(a) - h / 2
                box = (int(x), int(y), int(x + w), int(y + h))
                if not hits(box):
                    spot = box
                    break
                if rad > width:
                    break
            if spot:
                placed.append(spot)
                draw.text((spot[0] - l, spot[1] - tp), word, font=font,
                          fill=PALETTE[i % len(PALETTE)])
                break
            size = int(size * 0.85)

    img.save(out)


def main() -> None:
    p = argparse.ArgumentParser(description="폼 응답 CSV로 워드클라우드를 만듭니다.")
    p.add_argument("csv", type=Path, help="폼 응답 CSV 파일 (예: data/raw/round1.csv)")
    p.add_argument("--column", default="댓글", help="문장이 들어 있는 열 이름 일부")
    p.add_argument("--title", default="1회차 좋은 댓글에 많이 나온 단어")
    p.add_argument("--out", type=Path, default=ROOT / "round1-manner" / "results")
    p.add_argument("--top", type=int, default=20)
    args = p.parse_args()

    if not args.csv.exists():
        sys.exit(f"[오류] 파일이 없습니다: {args.csv}")

    rows = read_csv(args.csv)
    if not rows:
        sys.exit("[오류] 응답이 한 건도 없습니다.")
    col = find_column(list(rows[0].keys()), args.column)
    sentences = [r[col].strip() for r in rows if r.get(col, "").strip()]

    counter: Counter[str] = Counter()
    for s in sentences:
        counter.update(set(tokenize(s)))  # 한 사람이 같은 단어를 여러 번 써도 1번으로

    if not counter:
        sys.exit("[오류] 워드클라우드에 쓸 단어가 없습니다.")

    args.out.mkdir(parents=True, exist_ok=True)
    png = args.out / "wordcloud.png"
    render(counter, find_font(), png)

    top = counter.most_common(args.top)
    md = args.out / "top-words.md"
    lines = [
        f"# {args.title}",
        "",
        f"- 응답 수: **{len(sentences)}건**",
        f"- 서로 다른 단어 수: {len(counter)}개",
        "",
        "| 순위 | 단어 | 쓴 학생 수 |",
        "|---|---|---|",
    ]
    lines += [f"| {i} | {w} | {c} |" for i, (w, c) in enumerate(top, 1)]
    lines += ["", "![워드클라우드](wordcloud.png)", ""]
    md.write_text("\n".join(lines), encoding="utf-8")

    print(f"응답 {len(sentences)}건 · 단어 {len(counter)}개")
    print("TOP 10: " + ", ".join(f"{w}({c})" for w, c in top[:10]))
    print(f"저장: {png.relative_to(ROOT) if png.is_relative_to(ROOT) else png}")
    print(f"저장: {md.relative_to(ROOT) if md.is_relative_to(ROOT) else md}")


if __name__ == "__main__":
    main()
