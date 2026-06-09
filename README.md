# 🦥 SLO퀘스트 — RPG 듀오링고 스케줄러

> **"Slow but Steady"** — 나무늘보 마스코트 Slo와 함께 매일의 할 일을 RPG 퀘스트처럼 클리어하는 게이미피케이션 일정 관리 앱

---

## 목차

1. [프로그램 개요](#1-프로그램-개요)
2. [실행 환경 및 의존성](#2-실행-환경-및-의존성)
3. [실행 방법](#3-실행-방법)
4. [파일 구조](#4-파일-구조)
5. [주요 기능](#5-주요-기능)
6. [화면(탭) 구성](#6-화면탭-구성)
7. [게이미피케이션 시스템 규칙](#7-게이미피케이션-시스템-규칙)
8. [데이터 스키마 (slo_data.json)](#8-데이터-스키마-slo_datajson)
9. [함수 레퍼런스](#9-함수-레퍼런스)
10. [Google Calendar 연동](#10-google-calendar-연동)
11. [테마 및 디자인 토큰](#11-테마-및-디자인-토큰)

---

## 1. 프로그램 개요

**SLO퀘스트**는 Python의 `tkinter` GUI 라이브러리로 제작된 데스크톱 일정 관리 앱입니다.  
할 일을 **RPG 퀘스트** 형태로 등록하고, 완료할 때마다 **경험치(XP)** 를 획득해 레벨을 올리며, 매일 꾸준히 달성하면 **연속 스트릭(🔥)** 이 쌓이는 듀오링고식 게이미피케이션 구조를 채택했습니다.

| 항목 | 설명 |
|------|------|
| 언어 | Python 3.x |
| GUI 프레임워크 | tkinter + ttk |
| 데이터 저장 | 로컬 JSON 파일 (`slo_data.json`) |
| 화면 해상도 | 414 × 850 px (모바일 비율 고정) |
| 인터페이스 언어 | 한국어 |

---

## 2. 실행 환경 및 의존성

### 필수 요건

- **Python 3.8 이상** (표준 라이브러리만 사용)
- tkinter는 Python 기본 포함 (별도 설치 불필요)

### 사용하는 표준 라이브러리

| 라이브러리 | 용도 |
|-----------|------|
| `tkinter` | GUI 창 및 위젯 구현 |
| `tkinter.ttk` | 콤보박스 · 스크롤바 등 고급 위젯 |
| `tkinter.messagebox` | 팝업 알림 · 경고 · 확인 대화상자 |
| `json` | 데이터 직렬화 및 파일 입출력 |
| `os` | 파일 경로 탐색 및 존재 여부 확인 |
| `datetime` | 날짜 계산, 오늘 날짜 처리 |
| `calendar` | 달력 그리드 생성 및 월 이동 |
| `re` | AI 자연어 파서용 정규식 처리 |

### 선택적 의존성 (Google Calendar 연동 시)

```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

> Google Calendar 연동 없이도 앱의 모든 핵심 기능은 정상 동작합니다.

---

## 3. 실행 방법

```bash
# chapter10 디렉토리로 이동
cd CT_Algorithms/chapter10

# 앱 실행
python gui_1.py
```

최초 실행 시 `slo_data.json` 파일이 자동으로 생성됩니다.  
이후 실행부터는 저장된 유저 데이터를 불러와 이어서 진행합니다.

---

## 4. 파일 구조

```
chapter10/
├── gui_1.py          # 메인 소스 파일 (전체 앱 로직 포함)
├── slo_data.json     # 유저 데이터 영구 저장소 (자동 생성)
├── credentials.json  # (선택) Google Calendar OAuth 자격증명
├── token.pickle      # (선택) Google Calendar 인증 토큰 캐시
└── README.md         # 이 설명서
```

---

## 5. 주요 기능

### ① AI 자연어 퀘스트 파서
화면 오른쪽 하단의 **오렌지색 `+` 버튼**을 누르면 AI 자연어 입력 모달이 열립니다.

- 평어체로 과제를 입력하면 **제목, 마감일, 난이도**를 자동 분석합니다.
- **날짜 인식**: `오늘`, `내일`, `모레`, `N월 N일`, `YYYY-MM-DD`, `MM/DD` 형식 지원
- **난이도 인식**: `상/하드/어려움/Hard` → Hard(200XP), `중/보통/Medium` → Medium(100XP), `하/이지/쉬움/Easy` → Easy(50XP)

입력 예시:
```
내일까지 알고리즘 과제 제출 난이도 하드
6월 15일 생물 시험 복습
오늘 영어 단어 외우기 easy
```

### ② 나무늘보 캐릭터 'Slo' 커스터마이징
- `tkinter Canvas`에 벡터 도형으로 직접 그려진 나무늘보 캐릭터
- 생명(❤️)이 2개 이하면 **취침 상태** (감은 눈 + Zzz...)로 전환
- 레벨업 보상으로 장비 해금 및 장착 가능

| 장비 | 해금 레벨 | 외관 |
|------|----------|------|
| 🧡 주황색 목도리 | Lv.1 (기본) | 목 주위 주황 스카프 |
| 🕶️ 멋쟁이 선글라스 | Lv.3 | 검은 선글라스 |
| 👑 황금 왕관 | Lv.5 | 황금색 삼지창 왕관 |

### ③ 뽀모도로 집중 타이머
- 오늘 미완료 퀘스트와 연동하여 집중 세션 진행
- 타이머 작동 중 나무늘보 캐릭터가 1초마다 눈을 깜빡이는 애니메이션
- 타이머 완료 시 프로그레스 바 충전 애니메이션 후 퀘스트 자동 완료 처리

| 모드 | 시간 |
|------|------|
| 10초 데모 | 기능 테스트용 |
| 5분 | 짧은 집중 |
| 25분 (정식) | 뽀모도로 표준 |

### ④ 인터랙티브 달력
- 월별 달력 그리드에서 날짜 선택
- 퀘스트를 모두 완료한 날짜는 **오렌지 동그라미**로 표시
- 과거 날짜 퀘스트 열람, 오늘 날짜는 퀘스트 완료 체크 가능

### ⑤ 하루 경과 시뮬레이션
달력 화면 하단의 **⌛ 버튼**으로 날짜가 하루 지난 상황을 미리 체험합니다.  
어제 미완료 퀘스트가 있으면 하트 차감 및 스트릭 판정이 진행됩니다.

---

## 6. 화면(탭) 구성

하단 네비게이션 바의 5개 탭으로 구성됩니다.

| 탭 아이콘 | 탭 이름 | 상태 |
|----------|--------|------|
| 🏠 | 홈 대시보드 | 구현 완료 |
| 📋 | 퀘스트 상세 목록 | 추후 업데이트 예정 |
| ⏱️ | Slo's 집중 타이머 | 구현 완료 |
| 📅 | 달력 & 일정 관리 | 구현 완료 |
| 📊 | 통계 & 분석 보고서 | 추후 업데이트 예정 |

### 🏠 홈 대시보드 레이아웃

```
┌─────────────────────────────────┐
│ 🦥 Level 1        1🔥 ❤️❤️❤️❤️❤️  │  ← 상단 헤더 (레벨, 스트릭, 하트)
├─────────────────────────────────┤
│  [나무늘보 캐릭터]  [👗 Slo's 옷장]  │  ← 캐릭터 카드
│      Slow but Steady            │
│  You're 650XP away from Level 2!│
│  ▓▓▓▓▒▒▒▒▒▒ 35%               │  ← XP 프로그레스 바
├─────────────────────────────────┤
│  🔥 1 DAYS  ❤️ 5 HEARTS  👑 Lv.1 │  ← 미니 스탯 배지
├─────────────────────────────────┤
│  Today's Quests    2 REMAINING  │  ← 퀘스트 목록
│  ⚪ 알고리즘 과제    Hard · 200XP │
│  ⚪ 생물 시험 복습  Medium · 100XP│
├─────────────────────────────────┤
│ 🦥 "Doing great! One more..."   │  ← 말풍선 격려 메시지
└─────────────────────────────────┘
                              [+]   ← FAB 퀘스트 추가 버튼
```

---

## 7. 게이미피케이션 시스템 규칙

### 경험치(XP) 시스템

| 퀘스트 난이도 | XP 보상 |
|-------------|--------|
| Easy (쉬움) | 50 XP |
| Medium (보통) | 100 XP |
| Hard (어려움) | 200 XP |
| 일일 올패스 보너스 🔥 | +50 XP |

- **레벨업 기준:** 누적 1,000 XP 달성 시 레벨 1 상승
- 레벨업 시 하트가 5개로 **완전 충전** 됩니다.
- 퀘스트 완료를 취소(토글 되돌리기) 하면 XP도 환수됩니다.

### 하트(❤️) 시스템

- **최대 5개**, 시작 시 5개로 초기화
- 전날 퀘스트를 완료하지 못한 채 날짜가 바뀌면 **하트 1개 차감**
- 하트가 0이 되면 스트릭이 **0으로 리셋**
- 레벨업 시 하트 5개로 복구

### 스트릭(🔥) 시스템

- 오늘 퀘스트를 **모두 완료**하면 스트릭 +1일
- 미완료 퀘스트가 있으면:
  - 하트가 남아 있는 경우 → 하트 1개 소모로 스트릭 **동결(유지)**
  - 하트가 0인 경우 → 스트릭 **0일 리셋**

스트릭 보상(+50XP)은 **하루에 한 번만** 지급됩니다.

### 생명(Heart)이 2개 이하일 때

나무늘보 Slo가 취침 상태(👀→uu + Zzz...)로 표시되어 위기 상황을 시각적으로 알려줍니다.

---

## 8. 데이터 스키마 (slo_data.json)

앱의 모든 데이터는 스크립트와 같은 디렉토리의 `slo_data.json`에 자동 저장됩니다.

```json
{
  "user": {
    "level": 1,
    "xp": 350,
    "streak": 1,
    "heart": 5,
    "last_date": "2026-06-07",
    "inventory": ["orange_scarf"]
  },
  "quest_list": [
    {
      "id": "q_1234567890",
      "title": "알고리즘 과제",
      "difficulty": "Hard",
      "due_date": "2026-06-07",
      "xp_reward": 200,
      "is_completed": false
    }
  ],
  "equipped": {
    "orange_scarf": true,
    "sunglasses": false,
    "crown": false
  }
}
```

### 필드 설명

#### user 객체

| 필드 | 타입 | 설명 |
|------|------|------|
| `level` | int | 현재 유저 레벨 (1부터 시작) |
| `xp` | int | 현재 레벨 내 누적 XP (0~999) |
| `streak` | int | 연속 달성 일수 |
| `heart` | int | 남은 생명 수 (0~5) |
| `last_date` | string | 마지막 로그인 날짜 (YYYY-MM-DD) |
| `inventory` | array | 보유 중인 장비 ID 목록 |

#### quest 객체

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | string | 고유 퀘스트 ID (타임스탬프 기반, e.g. `q_1234567890`) |
| `title` | string | 과제 제목 |
| `difficulty` | string | `"Easy"` / `"Medium"` / `"Hard"` |
| `due_date` | string | 마감일 (YYYY-MM-DD) |
| `xp_reward` | int | XP 보상량 (50 / 100 / 200) |
| `is_completed` | bool | 완료 여부 |

> `slo_data.json`을 직접 수정하여 데이터를 편집할 수 있습니다. 앱 재시작 후 반영됩니다.

---

## 9. 함수 레퍼런스

### 데이터 관리

| 함수 | 설명 |
|------|------|
| `load_data()` | `slo_data.json`에서 유저 데이터 불러오기. 파일 없으면 기본값으로 초기화 |
| `save_data()` | 현재 `app_state`를 `slo_data.json`에 저장 |
| `check_and_update_streak()` | 오늘 퀘스트 전체 완료 여부 검사 후 스트릭 갱신 및 보너스 XP 지급 |

### 캐릭터 드로잉

| 함수 | 파라미터 | 설명 |
|------|---------|------|
| `draw_vector_sloth(canvas, x, y, scale, is_sleeping, equipped)` | canvas, 좌표, 배율, 수면여부, 장비dict | 캔버스에 나무늘보 캐릭터를 벡터 도형으로 렌더링 |
| `draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs)` | canvas, 좌표 쌍, 모서리 반지름 | 둥근 모서리 직사각형 그리기 |
| `draw_experience_bar(canvas, xp_value)` | canvas, 현재 XP | 주황색 XP 프로그레스 바 렌더링 |

### AI 자연어 파서

```python
result = ai_quest_parser("내일까지 알고리즘 과제 제출 하드")
# 반환값:
# {
#     "title": "알고리즘 과제",
#     "difficulty": "Hard",
#     "due_date": "2026-06-08",
#     "xp_reward": 200
# }
```

### 화면 렌더링

| 함수 | 설명 |
|------|------|
| `create_header(parent)` | 상단 레벨 · 하트 · 스트릭 헤더 생성 |
| `draw_home_view(parent)` | 홈 대시보드 전체 렌더링 |
| `draw_quests_section(parent)` | 오늘의 퀘스트 카드 목록 렌더링 |
| `draw_timer_view(parent)` | 뽀모도로 타이머 탭 렌더링 |
| `draw_calendar_view(parent)` | 달력 탭 렌더링 |
| `draw_coming_soon_view(parent, tab_idx)` | 미구현 탭 안내 화면 렌더링 |

### 퀘스트 제어

| 함수 | 설명 |
|------|------|
| `open_add_quest_modal()` | AI 자연어 퀘스트 추가 모달 창 열기 |
| `toggle_quest_status(quest_id)` | 퀘스트 완료/미완료 토글 및 XP 가감 |
| `delete_quest(quest_id)` | 확인 팝업 후 퀘스트 삭제 |
| `check_level_up(gained_xp)` | XP 기준 레벨업 여부 판단 및 장비 해금 처리 |

### 타이머

| 함수 | 설명 |
|------|------|
| `perform_timer_completion(quest_id)` | 타이머 완료 시 프로그레스 바 애니메이션 실행 후 퀘스트 자동 완료 |

### 달력 및 시뮬레이션

| 함수 | 설명 |
|------|------|
| `sync_google_calendar()` | Google Calendar API로 오늘 퀘스트 일정 푸시 |
| `simulate_next_day()` | 하루 경과 상황을 모의로 시뮬레이션 |
| `show_api_dialog_box(title, text)` | 안내 텍스트 팝업 창 표시 |

### 네비게이션 및 업데이트

| 함수 | 설명 |
|------|------|
| `switch_tab(tab_idx)` | 탭 전환 및 해당 화면 렌더링 (0=홈, 2=타이머, 3=달력) |
| `create_bottom_nav(parent)` | 하단 5탭 네비게이션 바 생성 |
| `update_badges()` | 헤더 · 미니 스탯 배지 실시간 업데이트 |

### 진입점

| 함수 | 설명 |
|------|------|
| `main()` | 앱 초기화, 창 생성, 데이터 로드, 날짜 페널티 처리, 메인 루프 시작 |

---

## 10. Google Calendar 연동

### 설정 방법

1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. **Google Calendar API** 활성화
3. OAuth 2.0 클라이언트 ID 생성 후 `credentials.json` 다운로드
4. `credentials.json`을 `gui_1.py`와 같은 디렉토리에 저장

### 동작 방식

- 달력 탭의 **📅 구글 캘린더 동기화** 버튼 클릭
- 최초 실행 시 브라우저에서 Google 계정 인증 진행
- 오늘 날짜의 미완료 퀘스트를 `[SLOQuest]` 접두어와 함께 Google 캘린더 이벤트로 생성
- 이벤트 기본 시간: **오후 5:00~6:00** (Asia/Seoul 기준)
- 인증 토큰은 `token.pickle`에 캐시되어 이후 자동 인증

`credentials.json`이 없거나 인증에 실패해도 앱은 정상 동작합니다.  
이 경우 로컬 JSON 동기화 안내 팝업이 표시됩니다.

---

## 11. 테마 및 디자인 토큰

앱 전체에 일관되게 사용되는 색상 및 폰트 상수입니다.

### 색상 팔레트

| 변수명 | 색상값 | 용도 |
|--------|--------|------|
| `BG_COLOR` | `#FFF8F3` | 전체 배경 (따뜻한 크림 베이지) |
| `CARD_BG` | `#FCF5EF` | 카드 배경 (연한 모래베이지) |
| `WHITE` | `#FFFFFF` | 카드 내부, 흰색 영역 |
| `TEXT_BROWN` | `#5A3A1F` | 주 텍스트 (밤색) |
| `ACCENT_ORANGE` | `#FF9500` | 핵심 강조, 스트릭 활성, 버튼 |
| `GRAY_TEXT` | `#8C8C8C` | 비활성 텍스트, 부제목 |
| `BORDER_COLOR` | `#EADBCD` | 위젯 경계선 |
| `ACCENT_BLUE` | `#5CA5F0` | 말풍선 테두리 |

### 폰트

| 변수명 | 설정 | 용도 |
|--------|------|------|
| `FONT_MAIN` | 맑은 고딕, 11 | 기본 본문 |
| `FONT_BOLD` | 맑은 고딕, 11, bold | 강조 텍스트 |
| `FONT_TITLE` | 맑은 고딕, 16, bold | 섹션 제목 |
| `FONT_SMALL` | 맑은 고딕, 9 | 작은 부가 정보 |

---

## 전역 상태 (`app_state`)

앱의 모든 런타임 상태를 보관하는 단일 딕셔너리입니다.

| 키 | 타입 | 설명 |
|----|------|------|
| `user` | dict | 유저 스탯 (level, xp, streak, heart, ...) |
| `quest_list` | list | 전체 퀘스트 배열 |
| `equipped` | dict | 장비 장착 상태 |
| `current_tab` | int | 현재 활성 탭 인덱스 |
| `selected_date` | string | 달력에서 선택된 날짜 (YYYY-MM-DD) |
| `main_container` | Widget | 중앙 콘텐츠 Frame 위젯 참조 |
| `root` | Tk | Tkinter 루트 창 참조 |
| `tab_buttons` | list | 하단 탭 라벨 리스트 |
| `timer_running` | bool | 타이머 동작 여부 |
| `timer_seconds` | int | 타이머 남은 초 |
| `timer_target_id` | string | 집중 중인 퀘스트 ID |
| `timer_job` | int | tkinter after() 콜백 ID |
| `streak_label` | Widget | 스트릭 라벨 위젯 참조 (실시간 업데이트용) |
| `lives_label` | Widget | 하트 라벨 위젯 참조 |
| `gems_label` | Widget | 레벨 라벨 위젯 참조 |

---

*이 문서는 `gui_1.py` v1.0 기준으로 작성되었습니다.*
