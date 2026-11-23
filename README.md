# 온라인 상호존중 문화 확산 캠페인

경기기계공업고등학교 · 경기 북부 상호존중 문화 확산 캠페인

> 학생 시민성 함양을 위한 **'존중문화 만들기'**
> 회차당 10분 이내의 가벼운 온라인 캠페인을 **알기 → 해보기 → 퍼뜨리기** 순서로 3회 운영합니다.
> 학생 참여는 **구글폼(또는 패들렛) + 캡처 제출**로 받습니다.

---

## 진행 현황

| 회차 | 주제 | 성격 | 기간 | 상태 |
|---|---|---|---|---|
| 1 | [온라인 매너 + 좋은 댓글](round1-manner/) | 알기 (인식) | 11/23(월) ~ 11/27(금) | 🟢 진행 중 |
| 2 | [말 바꾸기 챌린지](round2-rephrase/) | 해보기 (실천) | (날짜 기입) | ⚪ 준비 |
| 3 | [존중 메시지 카드 퍼뜨리기](round3-card/) | 퍼뜨리기 (확산) | (날짜 기입) | ⚪ 준비 |

※ 기말고사·졸업 일정은 피해서 주 1회 운영합니다.
※ 2회만 운영할 경우: 1회차와 3회차만 하고, 2회차의 말 바꾸기 예문은 3회차 카드 문구로 씁니다.
※ 3학년이 현장실습 중이면 1·2학년 위주로 하고, 3학년은 온라인으로만 참여합니다.

---

## 폴더 구조

```
respect-campaign/
├─ README.md                 ← 지금 보는 파일 (개요·진행 현황)
├─ docs/index.html           ← 학생용 안내 페이지 (GitHub Pages로 공개, QR은 이 페이지로)
├─ round1-manner/           ← 1회차 안내·폼 문항·결과 (워드클라우드)
├─ round2-rephrase/          ← 2회차 안내·'말 바꾸기' 예문 세트·우수작
├─ round3-card/              ← 3회차 안내·카드 문구 예시·대표 결과물
├─ data/participation.csv    ← 회차별·학급별 참여 인원 (이름 없음)
├─ data/raw/                 ← 폼 원본 응답 보관용 (⚠ git에 올라가지 않음)
├─ scripts/
│  ├─ make_wordcloud.py      ← 폼 응답 CSV → 워드클라우드 PNG + 많이 나온 단어 TOP 20
│  └─ participation.py       ← 폼 응답 CSV → 학급별 참여 인원 집계 → 참여율 표
└─ requirements.txt          ← 파이썬 패키지 목록
```

### 처음 한 번만: 파이썬 준비

Python 3.10 이상을 설치할 때 **'Add python.exe to PATH'**를 체크합니다. 그다음 이 폴더에서 아래 명령을 한 번 실행합니다.

```
pip install -r requirements.txt
```

---

## 매 회차 운영 순서

**회차 전 (담당 교사)**
1. 해당 회차 폴더의 `README.md`를 보고 구글폼(또는 패들렛)을 만듭니다.
2. `docs/index.html` 맨 위의 `FORMS` 설정에 폼 주소를 넣고 커밋합니다. 안내 페이지 버튼이 바뀝니다.
3. 담임 선생님께 **QR + 안내 슬라이드 1장**만 보냅니다. QR은 안내 페이지 주소로 한 번만 만들면 3회 내내 씁니다.

**종례 (5~10분)**
4. 학생은 QR로 들어가서 참여하고 캡처를 업로드합니다.

**회차 후 (담당 교사)**
5. 폼 응답을 CSV로 내려받아 `data/raw/`에 저장합니다. 이 폴더는 git에서 제외됩니다.
6. 참여 인원 집계: `python scripts/participation.py count data/raw/round1.csv --round 1`
   - 처음 한 번은 `data/participation.csv`를 엑셀로 열어 **재적** 칸을 채웁니다. 참여율 계산에 씁니다.
   - 참여율 표 만들기: `python scripts/participation.py summary` → `data/summary.md`
7. (1회차) 워드클라우드: `python scripts/make_wordcloud.py data/raw/round1.csv` → `round1-manner/results/`
8. 대표 캡처 2~3장을 **모자이크 처리 후** `roundN-.../results/`에 넣습니다.
9. 위 '진행 현황' 표의 상태를 바꾸고 커밋합니다.

---

## 개인정보 원칙 (꼭 지키기)

- ❌ **학번·이름·원본 캡처는 GitHub에 올리지 않습니다.** 원본은 구글 드라이브(폼 업로드 폴더)에만 둡니다.
- ❌ 결과물에 **얼굴·실명·카톡 프로필 사진·전화번호**가 보이면 모자이크하거나 쓰지 않습니다.
- ✅ GitHub에는 **학년·학과·반 단위 집계, 워드클라우드, 가공된 대표작**만 올립니다.
- ✅ 상점은 구글 시트의 학번으로 부여하고, 상점 명단은 저장소에 남기지 않습니다.
- ✅ 패들렛을 쓰면 **'승인 후 게시'**를 켜서 비방 글을 막습니다.

---

## 처음 한 번만: GitHub에 올리기

1. github.com에서 새 저장소 `respect-campaign`을 만듭니다. README 추가는 체크하지 않습니다.
2. 이 폴더에서 아래 명령을 실행합니다.
   ```
   git add .
   git commit -m "캠페인 저장소 시작"
   git branch -M main
   git remote add origin https://github.com/hongyul67-cpu/respect-campaign.git
   git push -u origin main
   ```
3. 저장소의 **Settings → Pages**에서 Branch를 `main`, 폴더를 `/docs`로 저장합니다.
   1~2분 뒤 `https://hongyul67-cpu.github.io/respect-campaign/` 주소가 생깁니다. 이 주소로 QR을 만듭니다.

> 무료 계정에서 GitHub Pages는 **공개 저장소**에서만 됩니다. 그래서 개인정보 원칙이 더 중요합니다.

---

## 결과보고 자료로 쓸 것

- 회차별 참여 인원·참여율: `data/summary.md` (`python scripts/participation.py summary`)
- 1회차 워드클라우드: `round1-manner/results/`
- 2회차 학과별 우수작: `round2-rephrase/results/`
- 3회차 대표 카드·숏폼 캡처: `round3-card/results/`
