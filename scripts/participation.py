"""회차별·학급별 참여 인원 집계

사용법 (저장소 폴더에서):
    python scripts/participation.py count data/raw/round1.csv --round 1
        → 폼 응답을 학년·학과·반으로 세어 data/participation.csv에 반영합니다.
          학번 열이 있으면 같은 학번의 중복 제출은 1명으로 셉니다. 학번은 저장하지 않습니다.

    python scripts/participation.py summary
        → 회차별·학년별·학급별 참여율 표를 data/summary.md로 만듭니다.

data/participation.csv의 '재적' 칸은 처음 한 번 엑셀로 채워 주세요.
재적이 비어 있으면 참여율 대신 참여 인원만 표시합니다.
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TALLY = ROOT / "data" / "participation.csv"
SUMMARY = ROOT / "data" / "summary.md"
FIELDS = ["회차", "학년", "학과", "반", "재적", "참여"]
ROUND_NAMES = {"1": "온라인 매너 + 좋은 댓글", "2": "말 바꾸기 챌린지", "3": "존중 카드 퍼뜨리기"}


def read_csv(path: Path) -> list[dict]:
    """구글 시트 CSV(UTF-8)와 엑셀에서 저장한 CSV(CP949) 둘 다 읽습니다."""
    for enc in ("utf-8-sig", "cp949"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    sys.exit(f"[오류] {path} 파일의 글자 인코딩을 읽을 수 없습니다.")


def write_tally(rows: list[dict]) -> None:
    rows.sort(key=lambda r: (num(r["회차"]), num(r["학년"]), r["학과"], num(r["반"])))
    # utf-8-sig: 엑셀에서 열어도 한글이 깨지지 않습니다.
    with open(TALLY, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in FIELDS} for r in rows)


def num(v: str) -> int:
    m = re.search(r"\d+", str(v))
    return int(m.group()) if m else 0


def digits(v: str) -> str:
    m = re.search(r"\d+", str(v))
    return m.group() if m else str(v).strip()


def pick(headers: list[str], keyword: str, exact_first: bool = True) -> str | None:
    if exact_first and keyword in headers:
        return keyword
    for h in headers:
        if keyword in h:
            return h
    return None


def cmd_count(args: argparse.Namespace) -> None:
    if not args.csv.exists():
        sys.exit(f"[오류] 파일이 없습니다: {args.csv}")
    responses = read_csv(args.csv)
    if not responses:
        sys.exit("[오류] 응답이 한 건도 없습니다.")
    headers = list(responses[0].keys())
    c_grade = pick(headers, "학년")
    c_dept = pick(headers, "학과")
    c_class = pick(headers, "반")
    c_id = pick(headers, "학번", exact_first=False)
    missing = [n for n, c in (("학년", c_grade), ("학과", c_dept), ("반", c_class)) if not c]
    if missing:
        sys.exit(f"[오류] 폼 응답에 {missing} 열이 없습니다. 열 목록: {headers}")

    seen: set[str] = set()
    counts: Counter[tuple[str, str, str]] = Counter()
    dup = 0
    for r in responses:
        if c_id:
            sid = re.sub(r"\D", "", r.get(c_id, "")) or r.get(c_id, "").strip()
            if sid and sid in seen:
                dup += 1
                continue
            seen.add(sid)
        key = (digits(r[c_grade]), r[c_dept].strip(), digits(r[c_class]))
        counts[key] += 1

    rnd = str(args.round)
    tally = read_csv(TALLY) if TALLY.exists() else []
    enrolled = {(t["학년"], t["학과"], t["반"]): t["재적"] for t in tally if t.get("재적")}

    others = [t for t in tally if t["회차"] != rnd]
    this_round = {(t["학년"], t["학과"], t["반"]): t for t in tally if t["회차"] == rnd}
    # 이 회차에 이미 있던 학급은 0으로 초기화한 뒤 다시 셉니다.
    for t in this_round.values():
        t["참여"] = "0"
    for key, n in counts.items():
        row = this_round.setdefault(
            key, {"회차": rnd, "학년": key[0], "학과": key[1], "반": key[2],
                  "재적": enrolled.get(key, "")}
        )
        row["참여"] = str(n)
    # 다른 회차에만 있던 학급도 이 회차 행을 만들어 둡니다(참여 0).
    for key, e in enrolled.items():
        this_round.setdefault(key, {"회차": rnd, "학년": key[0], "학과": key[1],
                                    "반": key[2], "재적": e, "참여": "0"})

    write_tally(others + list(this_round.values()))
    total = sum(counts.values())
    print(f"{rnd}회차: {len(counts)}개 학급, 참여 {total}명" + (f" (중복 제출 {dup}건 제외)" if dup else ""))
    no_enroll = [k for k in this_round if not this_round[k].get("재적")]
    if no_enroll:
        print(f"※ 재적이 비어 있는 학급 {len(no_enroll)}개: data/participation.csv를 엑셀로 열어 채워 주세요.")
    print(f"저장: {TALLY.relative_to(ROOT)}")


def rate(part: int, enr: int) -> str:
    return f"{part / enr * 100:.1f}%" if enr else "-"


def cmd_summary(_: argparse.Namespace) -> None:
    if not TALLY.exists():
        sys.exit("[오류] data/participation.csv가 없습니다. 먼저 count를 실행하세요.")
    rows = read_csv(TALLY)
    by_round: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_round[r["회차"]].append(r)

    out = ["# 회차별 참여 실적", "", "| 회차 | 주제 | 참여 | 재적 | 참여율 |", "|---|---|---|---|---|"]
    for rnd in sorted(by_round, key=num):
        rs = by_round[rnd]
        part = sum(num(r["참여"]) for r in rs)
        enr = sum(num(r["재적"]) for r in rs)
        out.append(f"| {rnd} | {ROUND_NAMES.get(rnd, '')} | {part} | {enr or '-'} | {rate(part, enr)} |")

    for rnd in sorted(by_round, key=num):
        rs = by_round[rnd]
        out += ["", f"## {rnd}회차 {ROUND_NAMES.get(rnd, '')}", "",
                "| 학년 | 참여 | 재적 | 참여율 |", "|---|---|---|---|"]
        grades: dict[str, list[int]] = defaultdict(lambda: [0, 0])
        for r in rs:
            grades[r["학년"]][0] += num(r["참여"])
            grades[r["학년"]][1] += num(r["재적"])
        for g in sorted(grades, key=num):
            p, e = grades[g]
            out.append(f"| {g}학년 | {p} | {e or '-'} | {rate(p, e)} |")

        out += ["", "| 학년 | 학과 | 반 | 참여 | 재적 | 참여율 |", "|---|---|---|---|---|---|"]
        for r in rs:
            p, e = num(r["참여"]), num(r["재적"])
            out.append(f"| {r['학년']} | {r['학과']} | {r['반']} | {p} | {e or '-'} | {rate(p, e)} |")

        ranked = [r for r in rs if num(r["재적"])]
        if ranked:
            best = max(ranked, key=lambda r: num(r["참여"]) / num(r["재적"]))
            out += ["", f"**참여율 1위:** {best['학년']}학년 {best['학과']} {best['반']}반 "
                        f"({rate(num(best['참여']), num(best['재적']))})"]

    SUMMARY.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:4 + len(by_round)]))
    print(f"\n저장: {SUMMARY.relative_to(ROOT)}")


def main() -> None:
    p = argparse.ArgumentParser(description="캠페인 참여 인원 집계")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("count", help="폼 응답 CSV를 학급별로 세어 participation.csv에 반영")
    c.add_argument("csv", type=Path)
    c.add_argument("--round", type=int, required=True, choices=[1, 2, 3])
    c.set_defaults(func=cmd_count)
    s = sub.add_parser("summary", help="참여율 표(data/summary.md) 만들기")
    s.set_defaults(func=cmd_summary)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
