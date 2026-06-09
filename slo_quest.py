import tkinter as tk  # GUI 구현을 위한 기본 tkinter 라이브러리 임포트
from tkinter import messagebox  # 팝업 메시지 박스 유틸리티 임포트
from tkinter import ttk  # 세련된 콤보박스 및 스크롤바 등 사용을 위한 ttk 임포트
import json  # 데이터 저장을 위해 JSON 처리 표준 라이브러리 임포트
import os  # 파일 경로 탐색 및 파일 확인용 os 라이브러리 임포트
import datetime  # 날짜 계산 및 오늘 날짜 처리를 위한 datetime 임포트
import calendar  # 달력 격자 생성 및 월 이동을 위한 calendar 임포트
import re  # AI 자연어 파싱을 위한 정규식 라이브러리 임포트
import threading  # 집중 모드 백그라운드 창 감지 스레드용 임포트

# =========================================================================
# 1. 앱 전역 설정 (파스텔톤의 고유 테마 컬러 및 폰트 정의)
# =========================================================================
BG_COLOR = "#FFF8F3"          # 전체 배경색 (편안하고 따뜻한 크림 베이지)
CARD_BG = "#FCF5EF"           # 메인 영웅 카드 배경색 (연한 모래베이지)
WHITE = "#FFFFFF"             # 카드 내부 박스 및 일반 위젯용 완벽한 흰색
TEXT_BROWN = "#5A3A1F"        # 주 폰트 색상 (슬로퀘스트 고유 밤색)
ACCENT_ORANGE = "#FF9500"     # 핵심 강조 및 스트릭 활성용 오렌지 컬러
GRAY_TEXT = "#8C8C8C"         # 마감/완료 처리 및 부제목용 비활성 그레이
BORDER_COLOR = "#EADBCD"      # 미세한 위젯 경계선 구분을 위한 소프트 브라운
ACCENT_BLUE = "#5CA5F0"       # 말풍선 영역 테두리를 위한 산뜻한 블루
GREEN_ALIVE = "#2E7D32"       # 하트 5개 생기넘침 상태 텍스트 색
RED_DANGER = "#D32F2F"        # 하트 2개 이하 위기 상태 텍스트 색
WARN_BG = "#FFF3E0"           # 경고 배지 배경 (연한 오렌지)

# 기본 폰트 패밀리 지정 (한글 맑은 고딕 탑재)
FONT_NAME = "맑은 고딕"
FONT_MAIN = (FONT_NAME, 11)
FONT_BOLD = (FONT_NAME, 11, "bold")
FONT_TITLE = (FONT_NAME, 16, "bold")
FONT_SMALL = (FONT_NAME, 9)
FONT_HERO = (FONT_NAME, 18, "bold")     # 홈화면 레벨/퀘스트 수 강조
FONT_TIMER = ("Consolas", 46, "bold")  # 타이머 숫자 (압도적 크기)
FONT_XP_HINT = (FONT_NAME, 10, "bold")  # 경험치 힌트 볼드

# JSON 파일명 정의 (기획서 명세 대응 단일 JSON 저장소)
JSON_FILE = "slo_data.json"

# =========================================================================
# 2. 전역 상태 사전 (기획서 JSON 스키마 명세에 100% 매칭하는 상태 객체)
# =========================================================================
app_state = {
    "user": {
        "level": 1,                 # 현재 유저 레벨 (기본값: 1)
        "xp": 0,                    # 현재 경험치 (1000XP 도달 시 레벨업)
        "streak": 0,                # 스트릭 불꽃 연속 달성 일수
        "heart": 5,                 # 생명 하트 개수 (최대 5개)
        "last_date": "",            # 스트릭 페널티 판정을 위한 최종 로그인 날짜
        "inventory": ["orange_scarf"]  # 해금된 의상 장비 인벤토리 리스트
    },
    # 퀘스트 배열 리스트 (id, title, difficulty, due_date, xp_reward, is_completed)
    "quest_list": [],
    "equipped": {
        "orange_scarf": True,      # 주황색 목도리 장착 상태
        "sunglasses": False,       # 멋쟁이 선글라스 장착 상태
        "crown": False             # 황금 왕관 장착 상태
    },
    "current_tab": 0,               # 현재 탭 상태 (0: 홈화면, 3: 달력화면)
    "selected_date": "",            # 달력 선택일 (YYYY-MM-DD)
    "main_container": None,         # 중앙 콘텐츠 가변 영역
    "root": None,                   # Tkinter root 창
    "tab_buttons": [],              # 하단 네비게이션 탭 라벨 리스트

    # 뽀모도로 타이머 작동 상태
    "timer_running": False,
    "timer_seconds": 0,
    "timer_target_id": "",
    "timer_job": None,

    # 집중 모드 백그라운드 창 감지 스레드 상태
    "monitor_thread": None,        # threading.Thread 인스턴스
    "monitor_stop_flag": False,    # True 시 모니터 루프 안전 종료
    "warning_open": False,         # 경고 팝업 중복 방지 플래그 (팝업이 열려 있는 동안 True)
    "warning_count": 0,            # 딴짓 경고 누적 횟수 (타이머 시작 시 0으로 초기화, 3회 시 페널티)

    # 전역 컴포넌트 라벨 참조 보관함
    "streak_label": None,
    "lives_label": None,
    "gems_label": None,
    "xp_label": None
}

# 달력 이동용 전역 포인터
cal_year = datetime.date.today().year
cal_month = datetime.date.today().month

# =========================================================================
# 3. JSON 파일 데이터베이스 보존 연동 로직
# =========================================================================


def load_data():
    """
    [함수 역할] JSON 파일(slo_data.json)로부터 유저 스탯, 인벤토리, 퀘스트 목록을 복원합니다.
    파일이 존재하지 않는 경우 기획 명세에 정의된 초기값으로 완벽하게 구성합니다.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, JSON_FILE)

        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                app_state["user"] = data.get("user", app_state["user"])
                app_state["quest_list"] = data.get(
                    "quest_list", app_state["quest_list"])
                app_state["equipped"] = data.get(
                    "equipped", app_state["equipped"])
                return

        # 기본 디폴트 데이터 구성 (기획 스펙과 정확히 대칭)
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        app_state["user"] = {
            "level": 1,
            "xp": 0,
            "streak": 0,
            "heart": 5,
            "last_date": today_str,
            "inventory": ["orange_scarf"]
        }
        app_state["quest_list"] = [
            {
                "id": "q1",
                "title": "알고리즘 과제",
                "difficulty": "Hard",
                "due_date": today_str,
                "xp_reward": 200,
                "is_completed": False
            }
        ]
        app_state["equipped"] = {
            "orange_scarf": True,
            "sunglasses": False,
            "crown": False
        }
        save_data()
    except Exception as e:
        print(f"JSON 로드 중 문제 발생 (기본값 설정): {e}")


def save_data():
    """
    [함수 역할] 현재 상태(유저 스탯, 인벤토리, 퀘스트, 장비 상태)를 slo_data.json 파일로 영구 보관합니다.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, JSON_FILE)

        payload = {
            "user": app_state["user"],
            "quest_list": app_state["quest_list"],
            "equipped": app_state["equipped"]
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"JSON 저장 실패: {e}")


def get_d_day_string(due_date_str):
    """
    [함수 역할] 두 날짜 간의 일수 차이를 계산하여 D-Day 포맷 스트링으로 반환합니다.
    """
    try:
        today = datetime.date.today()
        due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
        delta = (due_date - today).days
        if delta == 0:
            return "D-Day"
        elif delta > 0:
            return f"D-{delta}"
        else:
            return f"D+{abs(delta)}"
    except Exception:
        return ""


def check_and_update_streak():
    """
    [함수 역할] 스케줄러 개편에 따라 스트릭 처리는 데이터 보존 및 완료 현황 갱신만 수행합니다.
    """
    try:
        save_data()
        update_badges()
    except Exception as e:
        print(f"업데이트 오류: {e}")


def get_sloth_status():
    """
    [함수 역할] 일정의 상태에 따라 나무늘보의 기분을 결정합니다.
    - dead: 기한 초과 일정(과거 날짜의 미완료 일정)이 있는 경우
    - angry: 마감이 오늘인 미완료 일정(D-Day)이 있는 경우
    - nervous: 마감이 내일인 미완료 일정(D-1)이 있는 경우
    - happy_heart: 모든 과제를 끝냈을 때
    - happy: 과제가 없는 경우 또는 그 외 평상시
    """
    try:
        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")
        tomorrow_str = (
            today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        quests = app_state.get("quest_list", [])

        # 1. 기한 초과 일정(과거 날짜의 미완료 일정)이 있는 경우
        overdue = [
            q for q in quests
            if q["due_date"] < today_str and not q["is_completed"]
        ]
        if overdue:
            return "dead"

        # 2. 마감이 오늘인 미완료 일정(D-Day)이 있는 경우 -> 화냄
        d_day_quests = [
            q for q in quests
            if q["due_date"] == today_str and not q["is_completed"]
        ]
        if d_day_quests:
            return "angry"

        # 3. 마감이 내일인 미완료 일정(D-1)이 있는 경우 -> 땀 흘림
        d_1_quests = [
            q for q in quests
            if q["due_date"] == tomorrow_str and not q["is_completed"]
        ]
        if d_1_quests:
            return "nervous"

        # 4. 과제가 없는 경우 -> 평상시
        if not quests:
            return "happy"

        # 5. 모든 과제를 끝냈을 때 -> 신남
        if all(q["is_completed"] for q in quests):
            return "happy_heart"

    except Exception as e:
        print(f"나무늘보 상태 조회 에러: {e}")

    # 기본값 (과제가 존재하며 미완료된 것이 있으나 마감이 2일 이상 남은 평상시)
    return "happy"


# =========================================================================
# 3-B. 집중 모드 백그라운드 창 감지 헬퍼 (열품타 스타일 1단계)
# =========================================================================


# 집중 모드 화이트리스트: 이 키워드가 창 제목에 포함되면 '공부 중'으로 판정
_FOCUS_WHITELIST_BASE = [
    "code", "visual studio code", "finder", "safari", "chrome",
    "word", "hwp", "notion", "맑은", "slo",
    "terminal", "iterm", "python", "powershell", "electron",
]


def get_active_window_title():
    """
    [함수 역할] macOS / Windows 모두에서 외부 라이브러리 설치 없이
    현재 최상단 활성화 앱 이름을 반환하는 하이브리드 엔진.
    - macOS : osascript (내장 AppleScript 실행기)
    - Windows: PowerShell Get-Process (내장 명령어)
    - 실패 시 OS별 안전 기본값 반환 ("Finder" / "Explorer")
    """
    import sys
    import subprocess
    try:
        if sys.platform == "darwin":
            cmd = (
                "osascript -e 'tell application \"System Events\" to "
                "get name of first application process "
                "whose frontmost is true'")
            return subprocess.check_output(
                cmd, shell=True, text=True, timeout=5).strip()
        elif sys.platform == "win32":
            ps_cmd = (
                "Add-Type -Name Win32 -Namespace Native -MemberDefinition "
                "'[DllImport(\"user32.dll\")] "
                "public static extern IntPtr GetForegroundWindow();';"
                "$hwnd = [Native.Win32]::GetForegroundWindow();"
                "(Get-Process | "
                "Where-Object { $_.MainWindowHandle -eq $hwnd } | "
                "Select-Object -First 1).ProcessName")
            result = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                text=True, timeout=5
            ).strip()
            return result if result else "Explorer"
        else:
            return "Finder"
    except Exception:
        return "Finder" if sys.platform == "darwin" else "Explorer"


def _get_effective_whitelist():
    """
    [함수 역할] 기본 화이트리스트에 현재 타이머와 연계된 퀘스트 제목을 동적으로 추가하여 반환합니다.
    """
    whitelist = list(_FOCUS_WHITELIST_BASE)
    target_id = app_state.get("timer_target_id", "")
    if target_id:
        for quest in app_state.get("quest_list", []):
            if quest.get("id") == target_id:
                # 퀘스트 제목의 단어들을 키워드로 추가 (2글자 이상만)
                for word in quest.get("title", "").split():
                    if len(word) >= 2:
                        whitelist.append(word.lower())
                break
    return whitelist


def _apply_focus_penalty():
    """
    [함수 역할] 경고 3회 누적 시 호출되는 최종 페널티 실행 함수.
    메인 UI 스레드에서 실행되므로 UI 갱신이 완전히 안전합니다.
    """
    from tkinter import messagebox
    # ① 모니터링 루프 종료
    _stop_monitor_thread()
    # ② 타이머 작동 플래그 정지 (timer_tick은 자연스럽게 멈춤)
    app_state["timer_running"] = False
    # ③ 상단 헤더 배지 실시간 갱신
    update_badges()

    # ④ 창 강제 전면화
    root = app_state.get("root")
    if root:
        root.attributes("-topmost", True)
        root.lift()
        root.focus_force()

    # ⑤ 최종 실패 팝업
    messagebox.showerror(
        "집중 모드 강제 종료",
        "경고 3회 누적으로 타이머가 강제 종료됩니다.\n다시 일정에 집중해주세요!"
    )

    if root:
        root.attributes("-topmost", False)

    # ⑥ 데이터 즉시 저장
    save_data()


def _show_focus_warning():
    """
    [함수 역할] 메인 UI 스레드에서 실행되는 경고 팝업 표시 함수.
    root.after()를 통해 호출되며, 팝업이 열린 동안 warning_open 플래그로 중복 방지.
    3회 누적 도달 시 _apply_focus_penalty()를 호출합니다.
    """
    from tkinter import messagebox
    if not app_state["timer_running"]:
        return

    # 경고 카운트 증가
    app_state["warning_count"] += 1
    count = app_state["warning_count"]
    app_state["warning_open"] = True

    root = app_state.get("root")
    try:
        if root:
            root.attributes("-topmost", True)
            root.lift()
            root.focus_force()

        if count >= 3:
            # 3회 도달 → 페널티 실행 후 종료
            _apply_focus_penalty()
        else:
            # 1~2회: 경각심 자극 경고 팝업 (동적 메시지)
            messagebox.showwarning(
                f"집중 경고 ({count}/3)",
                f"지금은 선택하신 일정에 집중할 시간입니다!\n"
                f"딴짓을 멈춰주세요. (경고 누적: {count}/3)"
            )
    finally:
        # 사용자가 팝업을 닫으면 반드시 플래그 해제 (예외 발생 시에도 보장)
        app_state["warning_open"] = False
        if root:
            root.attributes("-topmost", False)


def _monitor_loop():
    """
    [함수 역할] 타이머 작동 중 1초마다 현재 활성 창 이름을 검사하는 루프.
    - 화이트리스트에 없는 창이 감지되면 '딴짓'으로 판정하고 UI 경고창을 띄웁니다.
    - app_state["monitor_stop_flag"]가 True가 되면 안전하게 종료됩니다.
    - macOS / Windows 하이브리드 엔진(subprocess)으로 실제 창 이름을 추적합니다.
    """
    import time
    import sys
    os_name = "macOS" if sys.platform == "darwin" else "Windows"
    print(f"[집중 모니터] 백그라운드 창 감지 시작 ({os_name} 하이브리드 모드)")
    while not app_state["monitor_stop_flag"]:
        title = get_active_window_title()
        if title:
            print(f"[집중 모니터] 활성 창: {title}")
            # ── 딴짓 판정 ──
            title_lower = title.lower()
            whitelist = _get_effective_whitelist()
            is_focused = any(kw in title_lower for kw in whitelist)
            if not is_focused:
                print(f"[집중 경고] 딴짓 감지됨! → {title}")
                # 경고창이 이미 열려 있지 않을 때만 스케줄링
                if not app_state["warning_open"]:
                    root = app_state.get("root")
                    if root:
                        root.after(0, _show_focus_warning)
        time.sleep(1)
    print("[집중 모니터] 백그라운드 창 감지 종료")


def _start_monitor_thread():
    """
    [함수 역할] 집중 타이머 시작 시 백그라운드 모니터 스레드를 생성하고 구동합니다.
    이미 실행 중이면 중복 생성하지 않습니다.
    """
    if app_state["monitor_thread"] and app_state["monitor_thread"].is_alive():
        return  # 이미 동작 중 → 중복 실행 방지
    # 타이머 시작 시 경고 카운트를 반드시 0으로 초기화
    app_state["monitor_stop_flag"] = False
    app_state["warning_count"] = 0
    app_state["warning_open"] = False
    t = threading.Thread(target=_monitor_loop, daemon=True)
    app_state["monitor_thread"] = t
    t.start()


def _stop_monitor_thread():
    """
    [함수 역할] 집중 타이머 종료(포기/완료) 시 모니터 스레드에 정지 플래그를 세워 안전하게 종료합니다.
    """
    app_state["monitor_stop_flag"] = True
    app_state["monitor_thread"] = None


# =========================================================================
# 5. 나무늘보 캐릭터 드로잉 및 상태별 표정 오버레이
# =========================================================================

def draw_vector_sloth(canvas, x_center, y_center, scale=1.0, status="happy"):
    """
    [함수 역할] 나무늘보 캐릭터 이미지 로드 및 기분(status: dead, nervous, angry, happy_heart, happy)
    에 따른 실시간 감정을 보여줍니다.
    """
    canvas.delete("sloth_part")
    canvas.delete("sloth_image")

    # 1. 상태에 맞는 이미지 파일명 설정
    if status == "dead":
        img_name = "sloth_dead.png"
    elif status == "nervous":
        img_name = "sloth_nervous.png"
    elif status == "angry":
        img_name = "sloth_angry.png"
    elif status == "happy_heart":
        img_name = "sloth_happy_heart.png"
    else:
        img_name = "sloth_happy_wave.png"

    # 2. 이미지 로드 및 크기 조정 (Pillow)
    try:
        from PIL import Image, ImageTk
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(script_dir, img_name)

        # 이미지 파일이 없으면 기존 sloth.png를 백업으로 사용
        if not os.path.exists(img_path):
            img_path = os.path.join(script_dir, "sloth.png")

        if os.path.exists(img_path):
            img = Image.open(img_path)
            # 120x120 비율을 유지하며 최대 크기로 조정 (찌그러짐 방지)
            img.thumbnail((120, 120), Image.Resampling.LANCZOS)
            app_state["sloth_image_data"] = ImageTk.PhotoImage(img)
            # 이미지 생성
            canvas.create_image(
                x_center,
                y_center,
                image=app_state["sloth_image_data"],
                tags="sloth_image")
        else:
            # 백업용 원그리기 (이미지 파일 분실 대비)
            canvas.create_oval(
                x_center - 40,
                y_center - 40,
                x_center + 40,
                y_center + 40,
                fill="#A88C74",
                tags="sloth_part")
    except Exception as e:
        print(f"이미지 로딩 중 오류: {e}")



def draw_vector_stopwatch(canvas, pct):
    """
    [함수 역할] 캔버스에 집중 진행률을 나타내는 심플하고 직관적인 스톱워치/타이머 그래픽을 그립니다.
    """
    canvas.delete("timer_parts")
    cx, cy = 80, 75
    r = 50
    # 다이얼 배경 (둥근 원)
    canvas.create_oval(
        cx - r,
        cy - r,
        cx + r,
        cy + r,
        fill=WHITE,
        outline=BORDER_COLOR,
        width=3,
        tags="timer_parts")
    # 남은 시간에 따른 호(Arc) 강조
    extent = 360.0 * pct
    if extent > 0:
        canvas.create_arc(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            start=90,
            extent=-extent,
            fill="",
            outline=ACCENT_ORANGE,
            width=6,
            style="arc",
            tags="timer_parts")
    # 상단 버튼 형상
    canvas.create_rectangle(
        cx - 8,
        cy - r - 8,
        cx + 8,
        cy - r,
        fill=GRAY_TEXT,
        outline="",
        tags="timer_parts")
    canvas.create_oval(
        cx - 4,
        cy - r - 12,
        cx + 4,
        cy - r - 8,
        fill=ACCENT_ORANGE,
        outline="",
        tags="timer_parts")


def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius=8, **kwargs):
    """
    [함수 역할] 캔버스에 둥근 카드를 그리기 위한 베지에 코너 연산 기반 범용 그리기 함수입니다.
    """
    points = [x1 +
              radius, y1, x1 +
              radius, y1, x2 -
              radius, y1, x2 -
              radius, y1, x2, y1, x2, y1 +
              radius, x2, y1 +
              radius, x2, y2 -
              radius, x2, y2 -
              radius, x2, y2, x2 -
              radius, y2, x2 -
              radius, y2, x1 +
              radius, y2, x1 +
              radius, y2, x1, y2, x1, y2 -
              radius, x1, y2 -
              radius, x1, y1 +
              radius, x1, y1 +
              radius, x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)


def draw_experience_bar(canvas, xp_value):
    """
    [함수 역할] 상단 진행바 영역에 주황색 둥근 프로그레스 바를 렌더링합니다.
    """
    canvas.delete("bar_layer")
    w = 340
    h = 28
    pct = int((xp_value / 1000.0) * 100)
    pct = min(100, max(0, pct))

    # 트랙 배경
    draw_rounded_rectangle(
        canvas,
        2,
        2,
        w - 2,
        h - 2,
        radius=10,
        fill="#E6D7C8",
        outline="",
        tags="bar_layer")

    # 충전 바
    if pct > 0:
        bar_w = int((pct / 100.0) * (w - 4))
        bar_w = max(20, bar_w)
        draw_rounded_rectangle(
            canvas,
            2,
            2,
            bar_w,
            h - 2,
            radius=10,
            fill=ACCENT_ORANGE,
            outline="",
            tags="bar_layer")
        txt_x = bar_w - 24 if bar_w > 60 else 30
        canvas.create_text(txt_x, h // 2, text=f"{pct}%",
                           fill=WHITE if bar_w > 60 else TEXT_BROWN,
                           font=(FONT_NAME, 12, "bold"), tags="bar_layer")
    else:
        canvas.create_text(
            w // 2,
            h // 2,
            text="0%",
            fill=GRAY_TEXT,
            font=(
                FONT_NAME,
                12,
                "bold"),
            tags="bar_layer")

# =========================================================================
# 5. AI 자연어 입력 일정 분석 파서 (AI Quest Parser Heuristics - Removed)
# =========================================================================


# =========================================================================
# 6. 헤더 및 홈 대시보드 뷰 그리기
# =========================================================================

def create_header(parent):
    """
    [함수 역할] 상단 헤더 프레임을 구축합니다. (게임 요소 제거, 심플한 디데이 스케줄러 스타일)
    """
    header_frame = tk.Frame(parent, bg=BG_COLOR, pady=12, padx=15)
    header_frame.pack(fill="x")

    # 왼쪽 스케줄러 제목
    title_lbl = tk.Label(
        header_frame,
        text="SLO 스케줄러",
        font=(
            "맑은 고딕",
            16,
            "bold"),
        fg=TEXT_BROWN,
        bg=BG_COLOR)
    title_lbl.pack(side="left")

    # 우측: 오늘 할 일 완료 현황 요약 배지
    stat_badge = tk.Frame(
        header_frame,
        bg=CARD_BG,
        highlightthickness=0,
        bd=0,
        padx=12,
        pady=4)
    stat_badge.pack(side="right")

    app_state["root"].stat_label = tk.Label(
        stat_badge, text="", font=(
            "맑은 고딕", 11, "bold"), fg=TEXT_BROWN, bg=CARD_BG)
    app_state["root"].stat_label.pack()
    update_badges()


def draw_home_view(parent):
    """
    [함수 역할] 홈 메인 대시보드 일정 요약 및 캐릭터 마스코트 상태를 렌더링합니다.
    """
    home_wrap = tk.Frame(parent, bg=BG_COLOR)
    home_wrap.pack(fill="both", expand=True)

    # A. 상단 요약 카드 (슬로 캐릭터 마스코트 + 진행 상황)
    summary_card = tk.Frame(
        home_wrap,
        bg=WHITE,
        padx=15,
        pady=15,
        highlightthickness=0,
        bd=0)
    summary_card.pack(fill="x", padx=12, pady=(10, 4))

    # 캐릭터 연출을 위해 가로 배열
    content_frame = tk.Frame(summary_card, bg=WHITE)
    content_frame.pack(fill="x")

    # 1. 나무늘보 캐릭터 캔버스 배치 (왼쪽)
    sloth_status = get_sloth_status()
    sloth_canvas = tk.Canvas(
        content_frame,
        width=130,
        height=120,
        bg=WHITE,
        highlightthickness=0)
    sloth_canvas.pack(side="left", padx=(10, 15))
    draw_vector_sloth(sloth_canvas, 65, 60, scale=1.0, status=sloth_status)

    # 2. 진행 상태 텍스트 및 프로그레스바 (오른쪽)
    right_frame = tk.Frame(content_frame, bg=WHITE)
    right_frame.pack(side="left", fill="both", expand=True)

    # 할 일 요약 계산
    total_quests = len(app_state["quest_list"])
    completed_quests = sum(
        1 for q in app_state["quest_list"] if q["is_completed"])

    title_lbl = tk.Label(
        right_frame,
        text="전체 일정 진행 상황",
        font=FONT_BOLD,
        fg=TEXT_BROWN,
        bg=WHITE)
    title_lbl.pack(anchor="w", pady=(5, 2))

    # 상태 메시지
    if sloth_status == "dead":
        msg_text = "기한 초과 일정이 있어\nSlo가 지쳐 쓰러졌습니다!"
        msg_color = RED_DANGER
    elif sloth_status == "angry":
        msg_text = "마감이 오늘인(D-Day)\n과제가 있습니다! 서두르세요!"
        msg_color = RED_DANGER
    elif sloth_status == "nervous":
        msg_text = "마감이 하루 남은(D-1)\n과제가 있습니다. 집중하세요!"
        msg_color = ACCENT_ORANGE
    elif sloth_status == "happy_heart":
        msg_text = "모든 과제를 끝냈습니다!\n정말 대단해요!"
        msg_color = "#2E7D32"
    else:
        if not app_state.get("quest_list", []):
            msg_text = "과제가 없습니다!\n지금 당장 여유를 즐기세요."
        else:
            msg_text = "아주 평화롭습니다!\n여유롭게 과제를 해보세요."
        msg_color = "#2E7D32"

    status_msg_lbl = tk.Label(
        right_frame,
        text=msg_text,
        font=(
            FONT_NAME,
            9,
            "bold"),
        fg=msg_color,
        bg=WHITE,
        justify="left")
    status_msg_lbl.pack(anchor="w", pady=(0, 4))

    prog_text = f"완료: {completed_quests} / {total_quests}"
    tk.Label(
        right_frame,
        text=prog_text,
        font=FONT_SMALL,
        fg=GRAY_TEXT,
        bg=WHITE).pack(
        anchor="w")

    # 프로그레스 바
    prog_canvas = tk.Canvas(
        right_frame,
        width=180,
        height=12,
        bg=WHITE,
        highlightthickness=0)
    prog_canvas.pack(anchor="w", pady=(4, 0))
    pct = int((completed_quests / total_quests * 100)
              ) if total_quests > 0 else 0
    draw_rounded_rectangle(
        prog_canvas,
        2,
        2,
        178,
        10,
        radius=4,
        fill="#EADBCD")
    if pct > 0:
        bar_w = int(pct / 100.0 * 176)
        draw_rounded_rectangle(
            prog_canvas,
            2,
            2,
            bar_w,
            10,
            radius=4,
            fill=ACCENT_ORANGE)

    # B. 오늘의 퀘스트 목록 및 연체 퀘스트 목록
    draw_quests_section(home_wrap)


# =========================================================================
# 7. Slo's Timer (집중 뽀모도로 타이머 구현 탭)
# =========================================================================

def draw_timer_view(parent):
    """
    [함수 역할] 3번째 탭(타이머)에 연계된 과제 맞춤 집중 타이머를 담당합니다.
    """
    timer_wrap = tk.Frame(parent, bg=BG_COLOR)
    timer_wrap.pack(fill="both", expand=True)

    # 모든 미완료 과제들 리스트업하여 연동
    unfinished_quests = [
        q for q in app_state["quest_list"] if not q["is_completed"]]

    if not unfinished_quests:
        tk.Label(
            timer_wrap,
            text="집중할 예정 일정이 없습니다.\n먼저 일정을 생성해주세요!",
            font=FONT_MAIN,
            fg=GRAY_TEXT,
            bg=BG_COLOR,
            justify="center",
            pady=50).pack()
        return

    # ── 1. 상단: 집중 과제명 강조 카드 ──
    quest_options = {q["title"]: q["id"] for q in unfinished_quests}
    selected_quest_name = tk.StringVar(value=list(quest_options.keys())[0])

    target_card = tk.Frame(
        timer_wrap,
        bg=WHITE,
        padx=16,
        pady=16,
        highlightthickness=0,
        bd=0)
    target_card.pack(fill="x", padx=16, pady=(12, 4))

    # Sub-widgets for selection mode (not running)
    select_title = tk.Label(
        target_card,
        text="지금 집중할 일정",
        font=FONT_BOLD,
        fg=TEXT_BROWN,
        bg=WHITE)
    quest_combo = ttk.Combobox(
        target_card, textvariable=selected_quest_name, values=list(
            quest_options.keys()), state="readonly", font=(
            FONT_NAME, 13, "bold"), justify="center")

    # Sub-widgets for lock mode (running)
    locked_lbl = tk.Label(
        target_card,
        font=(
            FONT_NAME,
            14,
            "bold"),
        fg=TEXT_BROWN,
        bg=WHITE,
        wraplength=340)

    def show_select_mode():
        locked_lbl.pack_forget()
        select_title.pack(anchor="center", pady=(0, 4))
        quest_combo.pack(fill="x", ipady=5)

    def show_lock_mode():
        select_title.pack_forget()
        quest_combo.pack_forget()
        locked_lbl.configure(text=f"지금 집중할 일정: [{selected_quest_name.get()}]")
        locked_lbl.pack(anchor="center", pady=6)

    # Initialize mode
    if app_state["timer_running"]:
        show_lock_mode()
    else:
        show_select_mode()

    # ── 2. 중앙: 스톱워치 캔버스 ──
    focus_canvas = tk.Canvas(
        timer_wrap,
        width=160,
        height=150,
        bg=BG_COLOR,
        highlightthickness=0)
    focus_canvas.pack(pady=(12, 0))
    draw_vector_stopwatch(focus_canvas, 1.0)

    # ── 3. 압도적 크기 타이머 숫자 (고딕체 48pt) ──
    time_display = tk.Label(
        timer_wrap,
        text="25:00",
        font=(
            FONT_NAME,
            48,
            "bold"),
        fg=ACCENT_ORANGE,
        bg=BG_COLOR)
    time_display.pack(pady=(2, 0))

    # 시간 선택 버튼
    duration_var = tk.IntVar(value=1500)

    def set_duration(secs, label_txt):
        if app_state["timer_running"]:
            return
        duration_var.set(secs)
        time_display.configure(text=label_txt)

    dur_row = tk.Frame(timer_wrap, bg=BG_COLOR)
    dur_row.pack(pady=2)
    for label, secs, txt in [("10초 데모", 10, "00:10"),
                             ("5분", 300, "05:00"), ("25분", 1500, "25:00")]:
        tk.Button(
            dur_row,
            text=label,
            font=FONT_SMALL,
            fg=GRAY_TEXT,
            bg=BG_COLOR,
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground=BG_COLOR,
            command=lambda s=secs,
            t=txt: set_duration(
                s,
                t)).pack(
            side="left",
            padx=6)

    # ── 4. 집중 위반 경고 둥근 배지 ──
    warn_canvas = tk.Canvas(
        timer_wrap,
        width=240,
        height=36,
        bg=BG_COLOR,
        highlightthickness=0)
    warn_canvas.pack(pady=4)

    def update_warn_badge():
        warn_canvas.delete("all")
        count = app_state["warning_count"]
        # 연한 빨간색 둥근 배경 (#FADBD8)
        draw_rounded_rectangle(
            warn_canvas,
            2,
            2,
            238,
            34,
            radius=12,
            fill="#FADBD8",
            outline="")
        # 진한 빨간색 경고 메시지 (#C0392B)
        warn_canvas.create_text(120, 18, text=f"집중 위반 경고: {count} / 3",
                                fill="#C0392B", font=(FONT_NAME, 11, "bold"))

    update_warn_badge()

    # 타이머 틱 동적 처리기
    def timer_tick():
        if not app_state["timer_running"]:
            return
        app_state["timer_seconds"] -= 1
        mins = app_state["timer_seconds"] // 60
        secs = app_state["timer_seconds"] % 60
        time_display.configure(text=f"{mins:02d}:{secs:02d}")

        # 경고 배지 실시간 갱신
        update_warn_badge()

        # 1초마다 스톱워치 캔버스 진행률 호 갱신
        total_duration = duration_var.get()
        pct = app_state["timer_seconds"] / \
            total_duration if total_duration > 0 else 0
        draw_vector_stopwatch(focus_canvas, pct)

        if app_state["timer_seconds"] <= 0:
            app_state["timer_running"] = False
            perform_timer_completion(quest_options[selected_quest_name.get()])
        else:
            app_state["timer_job"] = app_state["root"].after(1000, timer_tick)

    def start_timer():
        if app_state["timer_running"]:
            return
        app_state["timer_running"] = True
        app_state["timer_seconds"] = duration_var.get()
        app_state["timer_target_id"] = quest_options[selected_quest_name.get()]
        show_lock_mode()
        _start_monitor_thread()  # 집중 모드 창 감지 백그라운드 스레드 시작
        timer_tick()
        draw_start_btn()

    def stop_timer():
        app_state["timer_running"] = False
        _stop_monitor_thread()  # 집중 모드 창 감지 백그라운드 스레드 종료
        if app_state["timer_job"]:
            app_state["root"].after_cancel(app_state["timer_job"])
        time_display.configure(text="25:00")
        draw_vector_stopwatch(focus_canvas, 1.0)
        show_select_mode()
        update_warn_badge()
        draw_start_btn()

    # ── 5. 하단: 오렌지색 라운드 버튼 ──
    btn_canvas = tk.Canvas(
        timer_wrap,
        width=380,
        height=52,
        bg=BG_COLOR,
        highlightthickness=0,
        cursor="hand2")
    btn_canvas.pack(padx=16, pady=(16, 4))

    def draw_start_btn():
        btn_canvas.delete("all")
        fill_col = "#FFC580" if app_state["timer_running"] else ACCENT_ORANGE
        btn_txt = "집중 중 (클릭 시 중단)" if app_state["timer_running"] else "집중 개시"
        draw_rounded_rectangle(
            btn_canvas,
            2,
            2,
            378,
            50,
            radius=15,
            fill=fill_col,
            outline="")
        btn_canvas.create_text(
            190, 26, text=btn_txt, font=(
                FONT_NAME, 14, "bold"), fill=WHITE)

    draw_start_btn()

    def handle_btn_click(e):
        if app_state["timer_running"]:
            stop_timer()
        else:
            start_timer()

    btn_canvas.bind("<Button-1>", handle_btn_click)

    def on_btn_enter(e):
        btn_canvas.delete("all")
        if app_state["timer_running"]:
            draw_rounded_rectangle(
                btn_canvas,
                2,
                2,
                378,
                50,
                radius=15,
                fill="#FF8A8A",
                outline="")
            btn_canvas.create_text(
                190, 26, text="집중 중단하기", font=(
                    FONT_NAME, 14, "bold"), fill=WHITE)
        else:
            draw_rounded_rectangle(
                btn_canvas,
                2,
                2,
                378,
                50,
                radius=15,
                fill="#FFAC33",
                outline="")
            btn_canvas.create_text(
                190, 26, text="집중 개시", font=(
                    FONT_NAME, 14, "bold"), fill=WHITE)

    def on_btn_leave(e):
        draw_start_btn()

    btn_canvas.bind("<Enter>", on_btn_enter)
    btn_canvas.bind("<Leave>", on_btn_leave)

    # 포기 링크를 우측 하단 구석에 배치하여 '포기 심리' 차단
    abandon_frame = tk.Frame(timer_wrap, bg=BG_COLOR)
    abandon_frame.pack(fill="x", side="bottom", pady=(0, 12))

    stop_lbl = tk.Label(
        abandon_frame,
        text="포기하기",
        font=(
            FONT_NAME,
            8),
        fg="#B3B3B3",
        bg=BG_COLOR,
        cursor="hand2")
    stop_lbl.pack(side="right", padx=20)

    def on_abandon_click(e):
        if not app_state["timer_running"]:
            return
        if messagebox.askyesno("집중 포기", "정말로 지금 집중을 포기하시겠습니까?"):
            stop_timer()

    stop_lbl.bind("<Button-1>", on_abandon_click)


def perform_timer_completion(quest_id):
    """
    [함수 역할] 집중 타이머 만료 시 주황색 프로그레스 바 충전 시각 효과 애니메이션을 돌린 뒤 과제를 클리어 처리합니다.
    """
    try:
        # 애니메이션용 팝업 윈도우 생성
        anim_win = tk.Toplevel(app_state["root"])
        anim_win.title("집중 달성 성공!")
        anim_win.geometry("360x150")
        anim_win.configure(bg=BG_COLOR)
        anim_win.resizable(False, False)
        anim_win.transient(app_state["root"])
        anim_win.grab_set()

        tk.Label(
            anim_win,
            text="집중 과제를 완수하셨습니다!",
            font=FONT_BOLD,
            fg=TEXT_BROWN,
            bg=BG_COLOR).pack(
            pady=15)

        bar_canvas = tk.Canvas(
            anim_win,
            width=320,
            height=25,
            bg=BG_COLOR,
            highlightthickness=0)
        bar_canvas.pack(pady=10)

        # 1초간 애니메이션으로 주황색 프로그레스 채우기 시각화 구현
        def animate_step(step=0):
            if step <= 100:
                bar_canvas.delete("all")
                draw_rounded_rectangle(
                    bar_canvas, 2, 2, 318, 23, radius=8, fill="#E6D7C8")
                fill_w = int((step / 100.0) * 316)
                if fill_w > 16:
                    draw_rounded_rectangle(
                        bar_canvas, 2, 2, fill_w, 23,
                        radius=8, fill=ACCENT_ORANGE)
                app_state["root"].after(10, lambda: animate_step(step + 2))
            else:
                # 퀘스트 상태 완료 업데이트
                _stop_monitor_thread()  # 타임아웃 완료 시 창 감지 스레드 안전 종료
                anim_win.destroy()
                toggle_quest_status(quest_id)
                messagebox.showinfo("퀘스트 달성 성공", "경험치를 무사히 획득했습니다!")

        animate_step()
    except Exception as e:
        print(f"애니메이션 연동 에러: {e}")

# =========================================================================
# 8. 달력(Calendar) 화면 및 Google Calendar API / Local API 연동 로직
# =========================================================================


def draw_calendar_view(parent):
    """
    [함수 역할] 4번째 달력 탭 활성화 시 나타날 대화형 연/월 캘린더 그리드 및 일별 세부 퀘스트 조회를 조립합니다.
    """

    cal_wrap = tk.Frame(parent, bg=BG_COLOR, padx=15, pady=5)
    cal_wrap.pack(fill="both", expand=True)

    # A. 연/월 네비게이션용 탑 바
    ctrl_row = tk.Frame(cal_wrap, bg=BG_COLOR)
    ctrl_row.pack(fill="x", pady=5)

    def slide_prev():
        global cal_month, cal_year
        cal_month -= 1
        if cal_month < 1:
            cal_month = 12
            cal_year -= 1
        switch_tab(3)

    def slide_next():
        global cal_month, cal_year
        cal_month += 1
        if cal_month > 12:
            cal_month = 1
            cal_year += 1
        switch_tab(3)

    tk.Button(
        ctrl_row,
        text="◀",
        font=(
            "맑은 고딕",
            11,
            "bold"),
        fg=TEXT_BROWN,
        bg=BG_COLOR,
        relief="flat",
        bd=0,
        activebackground=CARD_BG,
        command=slide_prev).pack(
            side="left",
        padx=10)
    tk.Label(
        ctrl_row,
        text=f"{cal_year}년 {cal_month}월",
        font=(
            "맑은 고딕",
            13,
            "bold"),
        fg=TEXT_BROWN,
        bg=BG_COLOR).pack(
            side="left",
            expand=True,
        fill="x")
    tk.Button(
        ctrl_row,
        text="▶",
        font=(
            "맑은 고딕",
            11,
            "bold"),
        fg=TEXT_BROWN,
        bg=BG_COLOR,
        relief="flat",
        bd=0,
        activebackground=CARD_BG,
        command=slide_next).pack(
            side="right",
        padx=10)

    # B. 요일 이정표
    wk_frame = tk.Frame(cal_wrap, bg=BG_COLOR)
    wk_frame.pack(fill="x", pady=(5, 2))
    wk_labels = ["일", "월", "화", "수", "목", "금", "토"]
    for i, day_name in enumerate(wk_labels):
        wk_frame.columnconfigure(i, weight=1)
        w_lbl = tk.Label(
            wk_frame, text=day_name, font=(
                "맑은 고딕", 9, "bold"), bg=BG_COLOR)
        if i == 0:
            w_lbl.configure(fg="#D05A5A")
        elif i == 6:
            w_lbl.configure(fg="#5A90D0")
        else:
            w_lbl.configure(fg=TEXT_BROWN)
        w_lbl.grid(row=0, column=i, sticky="ew")

    # C. 날짜 격자 그리드 구현 (테두리 제거)
    grid_box = tk.Frame(
        cal_wrap,
        bg=WHITE,
        highlightthickness=0,
        bd=0,
        padx=8,
        pady=8)
    grid_box.pack(fill="x", pady=5)
    for i in range(7):
        grid_box.columnconfigure(i, weight=1)

    calendar.setfirstweekday(calendar.SUNDAY)
    month_matrix = calendar.monthcalendar(cal_year, cal_month)
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    if not app_state["selected_date"]:
        app_state["selected_date"] = today_str

    def tap_date(date_string):
        app_state["selected_date"] = date_string
        switch_tab(3)

    row_count = 0
    for week in month_matrix:
        for col_idx, val in enumerate(week):
            if val == 0:
                tk.Label(
                    grid_box,
                    text="",
                    bg=WHITE,
                    height=2).grid(
                    row=row_count,
                    column=col_idx,
                    sticky="nsew",
                    padx=1,
                    pady=1)
            else:
                curr_date = f"{cal_year}-{cal_month:02d}-{val:02d}"
                day_quests = [q for q in app_state["quest_list"]
                              if q["due_date"] == curr_date]
                is_streak_completed = len(day_quests) > 0 and all(
                    q["is_completed"] for q in day_quests)

                is_sel = curr_date == app_state["selected_date"]
                is_tod = curr_date == today_str

                day_cell = tk.Frame(grid_box, bg=WHITE)
                day_cell.grid(
                    row=row_count,
                    column=col_idx,
                    sticky="nsew",
                    padx=1,
                    pady=1)

                if is_streak_completed:
                    lbl = tk.Label(
                        day_cell,
                        text=str(val),
                        font=(
                            "맑은 고딕",
                            9,
                            "bold"),
                        fg=WHITE,
                        bg=ACCENT_ORANGE,
                        width=3,
                        height=1,
                        cursor="hand2")
                elif is_sel:
                    lbl = tk.Label(
                        day_cell,
                        text=str(val),
                        font=(
                            "맑은 고딕",
                            9,
                            "bold"),
                        fg=TEXT_BROWN,
                        bg="#F3E5D8",
                        width=3,
                        height=1,
                        relief="flat",
                        bd=0,
                        cursor="hand2")
                elif is_tod:
                    lbl = tk.Label(
                        day_cell,
                        text=str(val),
                        font=(
                            "맑은 고딕",
                            9,
                            "bold",
                            "underline"),
                        fg=ACCENT_ORANGE,
                        bg=WHITE,
                        width=3,
                        height=1,
                        cursor="hand2")
                else:
                    fg_color = TEXT_BROWN
                    if col_idx == 0:
                        fg_color = "#D05A5A"
                    if col_idx == 6:
                        fg_color = "#5A90D0"
                    lbl = tk.Label(
                        day_cell,
                        text=str(val),
                        font=(
                            "맑은 고딕",
                            9),
                        fg=fg_color,
                        bg=WHITE,
                        width=3,
                        height=1,
                        cursor="hand2")

                lbl.pack(pady=3)
                lbl.bind(
                    "<Button-1>",
                    lambda e,
                    d_str=curr_date: tap_date(d_str))
                day_cell.bind(
                    "<Button-1>",
                    lambda e,
                    d_str=curr_date: tap_date(d_str))
        row_count += 1

    # D. 선택일 세부 패널
    focus_date = app_state["selected_date"]
    try:
        parsed_dt = datetime.datetime.strptime(focus_date, "%Y-%m-%d")
        kor_date_title = parsed_dt.strftime("%Y년 %m월 %d일")
    except BaseException:
        kor_date_title = focus_date

    detail_panel = tk.Frame(cal_wrap, bg=BG_COLOR)
    detail_panel.pack(fill="both", expand=True, pady=8)

    is_today_view = (focus_date == today_str)
    is_past_view = (focus_date < today_str)
    lock_hint = " [조회 전용 (과거 날짜)]" if is_past_view else (
        " [오늘 - 완료 체크 가능]" if is_today_view else " [미래 날짜]")
    hdr_color = GRAY_TEXT if is_past_view else (
        GREEN_ALIVE if is_today_view else ACCENT_BLUE)
    tk.Label(
        detail_panel,
        text=f"{kor_date_title} 퀘스트 목록{lock_hint}",
        font=FONT_BOLD,
        fg=hdr_color,
        bg=BG_COLOR,
        anchor="w").pack(
        fill="x",
        pady=(
            0,
             4))

    filtered_quests = [q for q in app_state["quest_list"]
                       if q["due_date"] == focus_date]

    if not filtered_quests:
        tk.Label(
            detail_panel,
            text="이 일자에 배정된 과제가 없습니다.",
            font=FONT_MAIN,
            fg=GRAY_TEXT,
            bg=BG_COLOR,
            anchor="w",
            pady=10).pack(
            fill="x")
    else:
        for q in filtered_quests:
            item_bar = tk.Frame(
                detail_panel,
                bg=WHITE,
                highlightthickness=0,
                bd=0,
                padx=10,
                pady=5)
            item_bar.pack(fill="x", pady=2)

            chk_icon = "✓" if q["is_completed"] else "○"
            chk_col = ACCENT_ORANGE if q["is_completed"] else GRAY_TEXT

            icon_lbl = tk.Label(
                item_bar, text=chk_icon, font=(
                    "맑은 고딕", 10), fg=chk_col, bg=WHITE)
            icon_lbl.pack(side="left", padx=(0, 5))

            # 오직 오늘 날짜에만 바인딩
            if focus_date == today_str:
                icon_lbl.configure(cursor="hand2")
                icon_lbl.bind(
                    "<Button-1>",
                    lambda e,
                    q_id=q["id"]: toggle_quest_status(q_id))

            font_opt = (
                "맑은 고딕",
                10,
                "overstrike") if q["is_completed"] else (
                "맑은 고딕",
                10)
            txt_color = GRAY_TEXT if q["is_completed"] else TEXT_BROWN
            tk.Label(
                item_bar,
                text=q["title"],
                font=font_opt,
                fg=txt_color,
                bg=WHITE,
                anchor="w").pack(
                side="left",
                fill="x",
                expand=True)

            level_tag = "COMPLETED" if q["is_completed"] else f"{
                q['difficulty']} • {
                q['xp_reward']}XP"
            level_color = GRAY_TEXT if q["is_completed"] else (
                "#D05A5A" if q["difficulty"] == "Hard" else "#5A90D0")
            tk.Label(
                item_bar,
                text=level_tag,
                font=(
                    "맑은 고딕",
                    7,
                    "bold"),
                fg=level_color,
                bg=CARD_BG,
                padx=4).pack(
                side="right")

    # E. 하단 액션 버튼 바
    action_row = tk.Frame(cal_wrap, bg=BG_COLOR)
    action_row.pack(side="bottom", fill="x", pady=(2, 5))

    sim_btn = tk.Button(
        action_row,
        text="하루 경과 시뮬레이션",
        font=(
            "맑은 고딕",
            9,
            "bold"),
        fg="#D05A5A",
        bg=WHITE,
        activebackground=CARD_BG,
        relief="flat",
        bd=0,
        padx=12,
        pady=6,
        command=simulate_next_day)
    sim_btn.pack(anchor="center")


def simulate_next_day():
    """
    [함수 역할] 하루가 지나 날짜가 바뀌었을 때의 모의 시뮬레이터입니다.
    어제 미완료 일정이 있다면 날짜가 지나 D+1 등으로 밀려나는 연체 상태를 시뮬레이션합니다.
    """
    try:
        if not messagebox.askyesno("시뮬레이터 작동", "하루가 경과한 상황을 모의로 테스트해보시겠습니까?"):
            return

        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")
        yesterday_str = (
            today -
            datetime.timedelta(
                days=1)).strftime("%Y-%m-%d")

        # 1. 오늘 퀘스트를 어제 날짜 퀘스트로 강제 이동하여 마감 기한 초과(연체) 상태 모의
        shifted = 0
        for q in app_state["quest_list"]:
            if q["due_date"] == today_str:
                q["due_date"] = yesterday_str
                shifted += 1

        # 어제 미완수 퀘스트 건수 확인
        yesterday_quests = [
            q for q in app_state["quest_list"]
            if q["due_date"] == yesterday_str
        ]
        incomplete_count = sum(
            1 for q in yesterday_quests if not q["is_completed"])

        if incomplete_count > 0:
            messagebox.showwarning(
                "일정 연체 발생!",
                f"어제 마감이었으나 완료되지 않은 일정 {incomplete_count}개가 연체 상태로 전환되었습니다.\n"
                f"대시보드에서 빨간색 연체 배지로 표시됩니다!"
            )
        else:
            messagebox.showinfo(
                "어제 일정 완료!",
                "어제 일정을 모두 안전하게 정복 완료하셨습니다!"
            )

        # 2. 오늘 날짜용 새로운 샘플 퀘스트 발급
        app_state["quest_list"].append({
            "id": f"q_sim1_{int(datetime.datetime.now().timestamp())}",
            "title": "알고리즘 기출 풀이",
            "difficulty": "Hard",
            "due_date": today_str,
            "xp_reward": 200,
            "is_completed": False
        })
        app_state["quest_list"].append({
            "id": f"q_sim2_{int(datetime.datetime.now().timestamp())}",
            "title": "스케줄러 코드 리팩토링 완료하기",
            "difficulty": "Medium",
            "due_date": today_str,
            "xp_reward": 100,
            "is_completed": False
        })

        app_state["selected_date"] = today_str
        save_data()
        update_badges()
        switch_tab(app_state["current_tab"])
    except Exception as e:
        messagebox.showerror("시뮬레이션 예외", f"에러: {e}")


def update_badges():
    """
    [함수 역할] 상단 오늘 과제 현황을 실시간 재작성합니다. (게임 배지 제거)
    """
    try:
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        today_quests = [q for q in app_state["quest_list"]
                        if q["due_date"] == today_str]
        total_today = len(today_quests)
        completed_today = sum(1 for q in today_quests if q["is_completed"])

        status_text = f"오늘 할 일 {completed_today}/{total_today}"
        if hasattr(
                app_state["root"],
                "stat_label") and app_state["root"].stat_label:
            app_state["root"].stat_label.configure(text=status_text)
    except Exception as e:
        print(f"뱃지 업데이트 실패: {e}")


# =========================================================================
# 10. AI 자연어 일정 추가 팝업 및 퀘스트 제어 로직
# =========================================================================

def open_add_quest_modal():
    """
    [함수 역할] 새로운 일정 추가 창을 띄웁니다.
    마감일은 기본적으로 달력의 선택된 날짜(selected_date)로 채워지며, 직접 수정할 수 있습니다.
    """
    try:
        modal = tk.Toplevel(app_state["root"])
        modal.title("일정 추가")
        modal.geometry("380x420")
        modal.configure(bg=BG_COLOR)
        modal.resizable(False, False)
        modal.transient(app_state["root"])
        modal.grab_set()

        tk.Label(
            modal,
            text="새 일정 추가",
            font=FONT_TITLE,
            fg=TEXT_BROWN,
            bg=BG_COLOR).pack(
            pady=(
                20,
                15))

        # 1. 과제 내용 입력 필드
        tk.Label(
            modal,
            text="과제 내용",
            font=FONT_BOLD,
            fg=TEXT_BROWN,
            bg=BG_COLOR).pack(
            anchor="w",
            padx=30,
            pady=(
                10,
                2))
        title_bg = tk.Frame(modal, bg=WHITE, padx=10, pady=6)
        title_bg.pack(fill="x", padx=30)
        title_entry = tk.Entry(
            title_bg,
            font=(
                "맑은 고딕",
                11),
            bg=WHITE,
            fg=TEXT_BROWN,
            relief="flat",
            bd=0)
        title_entry.pack(fill="x")
        title_entry.focus()

        # 2. 마감일 입력 필드
        tk.Label(
            modal,
            text="마감일 (YYYY-MM-DD)",
            font=FONT_BOLD,
            fg=TEXT_BROWN,
            bg=BG_COLOR).pack(
            anchor="w",
            padx=30,
            pady=(
                15,
                2))
        due_bg = tk.Frame(modal, bg=WHITE, padx=10, pady=6)
        due_bg.pack(fill="x", padx=30)

        # 기본 날짜 설정
        default_date = app_state.get("selected_date", "")
        if not default_date:
            default_date = datetime.date.today().strftime("%Y-%m-%d")

        due_entry = tk.Entry(
            due_bg,
            font=(
                "맑은 고딕",
                11),
            bg=WHITE,
            fg=TEXT_BROWN,
            relief="flat",
            bd=0)
        due_entry.insert(0, default_date)
        due_entry.pack(fill="x")

        # 3. 난이도 선택 필드
        tk.Label(
            modal,
            text="난이도",
            font=FONT_BOLD,
            fg=TEXT_BROWN,
            bg=BG_COLOR).pack(
            anchor="w",
            padx=30,
            pady=(
                15,
                2))

        # 콤보박스 스타일 정의
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'TCombobox',
            fieldbackground=WHITE,
            background=WHITE,
            foreground=TEXT_BROWN,
            selectbackground=ACCENT_ORANGE)

        diff_var = tk.StringVar(value="Medium")
        diff_combo = ttk.Combobox(
            modal,
            textvariable=diff_var,
            values=[
                "Easy",
                "Medium",
                "Hard"],
            state="readonly",
            font=(
                "맑은 고딕",
                11))
        diff_combo.pack(fill="x", padx=30, ipady=4)

        def confirm_registration():
            title = title_entry.get().strip()
            due_date = due_entry.get().strip()
            difficulty = diff_var.get()

            # 입력 검증
            if not title:
                messagebox.showwarning("입력 누락", "과제 내용을 입력해주세요.", parent=modal)
                return

            # 날짜 정규식 검증 YYYY-MM-DD
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', due_date):
                messagebox.showwarning(
                    "날짜 형식 오류",
                    "마감일 형식을 YYYY-MM-DD로 입력해주세요.\n예: 2026-06-09",
                    parent=modal)
                return

            try:
                # 실제로 올바른 날짜인지 확인
                datetime.datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "날짜 오류", "올바른 날짜를 입력해주세요.", parent=modal)
                return

            # 난이도에 따른 XP 설정
            xp_rewards = {"Easy": 50, "Medium": 100, "Hard": 200}
            xp_reward = xp_rewards.get(difficulty, 100)

            unique_id = f"q_{int(datetime.datetime.now().timestamp() * 1000)}"

            # JSON 퀘스트 리스트에 가산
            app_state["quest_list"].append({
                "id": unique_id,
                "title": title,
                "difficulty": difficulty,
                "due_date": due_date,
                "xp_reward": xp_reward,
                "is_completed": False
            })

            save_data()
            switch_tab(app_state["current_tab"])

            modal.destroy()
            messagebox.showinfo(
                "퀘스트 등록",
                f"'{title}' 일정이 등록되었습니다!",
                parent=app_state["root"])

        # 조작 버튼 바
        btn_bar = tk.Frame(modal, bg=BG_COLOR)
        btn_bar.pack(fill="x", pady=25)

        tk.Button(
            btn_bar,
            text="취소",
            font=FONT_MAIN,
            bg="#E0D4C9",
            fg=TEXT_BROWN,
            relief="flat",
            bd=0,
            padx=20,
            pady=6,
            command=modal.destroy).pack(
            side="left",
            padx=(
                60,
                10))
        tk.Button(
            btn_bar,
            text="등록",
            font=FONT_BOLD,
            bg=ACCENT_ORANGE,
            fg=WHITE,
            relief="flat",
            bd=0,
            padx=20,
            pady=6,
            command=confirm_registration).pack(
            side="right",
            padx=(
                10,
                60))

    except Exception as ex:
        messagebox.showerror("AI 모달 구동 실패", f"오류: {ex}")


def draw_task_item(parent, q):
    """
    [함수 역할] 일정 항목 하나를 카드 형태로 아름답게 렌더링합니다. D-Day 정보와 상태 체크가 포함됩니다.
    """
    is_done = q["is_completed"]

    # 카드 프레임
    card = tk.Frame(
        parent,
        bg=WHITE if not is_done else CARD_BG,
        highlightthickness=0,
        bd=0,
        padx=12,
        pady=8)
    card.pack(fill="x", pady=3)

    # 토글 체크 박스
    chk_char = "✓" if is_done else "○"
    chk_col = ACCENT_ORANGE if is_done else GRAY_TEXT

    chk_lbl = tk.Label(
        card,
        text=chk_char,
        font=(
            FONT_NAME,
            16,
            "bold"),
        fg=chk_col,
        bg=card["bg"],
        cursor="hand2")
    chk_lbl.pack(side="left", padx=(0, 10))
    chk_lbl.bind(
        "<Button-1>",
        lambda e,
        q_id=q["id"]: toggle_quest_status(q_id))

    # 텍스트 정보 컬럼
    info_column = tk.Frame(card, bg=card["bg"])
    info_column.pack(side="left", fill="x", expand=True)

    f_style = (FONT_NAME, 11, "overstrike") if is_done else (FONT_NAME, 11)
    c_style = GRAY_TEXT if is_done else TEXT_BROWN
    title_lbl = tk.Label(
        info_column,
        text=q["title"],
        font=f_style,
        fg=c_style,
        bg=card["bg"],
        anchor="w")
    title_lbl.pack(anchor="w")

    # D-Day 및 마감일 라벨 표시
    dday_str = get_d_day_string(q["due_date"])

    # D-Day 상태에 따라 색상 분기
    if is_done:
        dday_bg, dday_fg = "#E6DCD2", GRAY_TEXT
    else:
        if dday_str.startswith("D+") or "Overdue" in dday_str:
            dday_bg, dday_fg = "#FFEAEA", RED_DANGER
        elif dday_str == "D-Day":
            dday_bg, dday_fg = "#FFF3E0", ACCENT_ORANGE
        else:
            dday_bg, dday_fg = "#E0F0FF", ACCENT_BLUE

    tag_row = tk.Frame(info_column, bg=card["bg"])
    tag_row.pack(anchor="w", pady=(2, 0))

    dday_lbl = tk.Label(
        tag_row,
        text=dday_str,
        font=(
            FONT_NAME,
            8,
            "bold"),
        bg=dday_bg,
        fg=dday_fg,
        padx=6,
        pady=1)
    dday_lbl.pack(side="left")

    due_lbl = tk.Label(
        tag_row,
        text=f"마감: {
            q['due_date']}",
        font=(
            FONT_NAME,
            8),
        bg=card["bg"],
        fg=GRAY_TEXT)
    due_lbl.pack(side="left", padx=6)

    # 우측 삭제 단추
    del_lbl = tk.Label(
        card,
        text="✕",
        font=(
            FONT_NAME,
            10),
        fg="#E57373",
        bg=card["bg"],
        cursor="hand2")
    del_lbl.pack(side="right", padx=5)
    del_lbl.bind("<Button-1>", lambda e, q_id=q["id"]: delete_quest(q_id))

    # 마우스 호버 효과
    widgets_to_hover = [
        chk_lbl,
        info_column,
        title_lbl,
        tag_row,
        dday_lbl,
        due_lbl,
        del_lbl]

    def make_hover_handlers(c_widget, w_list, done_flag):
        def enter(e):
            hover_bg = "#FFF8F3" if not done_flag else "#F5EDE4"
            c_widget.configure(bg=hover_bg)
            for w in w_list:
                if w != dday_lbl:  # Keep D-Day badge bg
                    w.configure(bg=hover_bg)

        def leave(e):
            normal_bg = WHITE if not done_flag else CARD_BG
            c_widget.configure(bg=normal_bg)
            for w in w_list:
                if w != dday_lbl:  # Keep D-Day badge bg
                    w.configure(bg=normal_bg)
        c_widget.bind("<Enter>", enter)
        c_widget.bind("<Leave>", leave)
        for w in w_list:
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)

    make_hover_handlers(card, widgets_to_hover, is_done)


def draw_quests_section(parent):
    """
    [함수 역할] 홈 대시보드에 오늘 일정 및 연체된 일정을 정밀 렌더링합니다.
    """
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    section_wrap = tk.Frame(parent, bg=BG_COLOR, padx=12)
    section_wrap.pack(fill="both", expand=True, pady=(5, 5))

    # 1. 연체된 일정 (Overdue)
    overdue_quests = [q for q in app_state["quest_list"]
                      if q["due_date"] < today_str and not q["is_completed"]]
    if overdue_quests:
        overdue_hdr = tk.Frame(section_wrap, bg=BG_COLOR)
        overdue_hdr.pack(fill="x", pady=(5, 2))
        tk.Label(
            overdue_hdr,
            text="기한 초과 일정",
            font=FONT_BOLD,
            fg=RED_DANGER,
            bg=BG_COLOR).pack(
            side="left")

        for q in overdue_quests:
            draw_task_item(section_wrap, q)

    # 2. 앞으로 해야 할 일정 (Upcoming Tasks)
    upcoming_quests = [q for q in app_state["quest_list"]
                       if q["due_date"] >= today_str and not q["is_completed"]]
    upcoming_quests = sorted(upcoming_quests, key=lambda x: x["due_date"])
    rem_count = len(upcoming_quests)

    upcoming_hdr = tk.Frame(section_wrap, bg=BG_COLOR)
    upcoming_hdr.pack(fill="x", pady=(10, 2))
    tk.Label(
        upcoming_hdr,
        text="앞으로 해야 할 일정",
        font=FONT_BOLD,
        fg=TEXT_BROWN,
        bg=BG_COLOR).pack(
        side="left")

    lbl_text = f"{rem_count}개 남음" if rem_count > 0 else "예정된 일정 완료"
    lbl_color = ACCENT_ORANGE if rem_count > 0 else "#2E7D32"
    tk.Label(
        upcoming_hdr,
        text=lbl_text,
        font=FONT_BOLD,
        fg=lbl_color,
        bg=BG_COLOR).pack(
        side="right")

    if not upcoming_quests:
        tk.Label(
            section_wrap,
            text="앞으로 해야 할 일정이 없습니다.\n+ 버튼을 눌러 새로운 일정을 추가해보세요.",
            font=FONT_MAIN,
            fg=GRAY_TEXT,
            bg=BG_COLOR,
            justify="center",
            pady=15).pack()
    else:
        for q in upcoming_quests:
            draw_task_item(section_wrap, q)


def toggle_quest_status(quest_id):
    """
    [함수 역할] 과제 상태 토글 처리 및 경험치를 더한 뒤 레벨업 검증을 실행합니다.
    어제 날짜 혹은 과거 날짜 퀘스트의 완료 체크를 원천 차단합니다.
    """
    try:
        target = None
        for q in app_state["quest_list"]:
            if q["id"] == quest_id:
                target = q
                break
        if not target:
            return

        # 기동일 기준 과거 날짜의 퀘스트 완료 체크 차단 🔒
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        if target["due_date"] < today_str:
            messagebox.showwarning("완료 변경 제한",
                                   "과거 날짜의 퀘스트는 이미 어제 날짜 경과 패널티를 받았으므로\n"
                                   "더 이상 완료 여부를 변경할 수 없습니다!")
            return

        now_val = not target["is_completed"]
        target["is_completed"] = now_val

        xp_gain = target["xp_reward"]

        if now_val:
            app_state["user"]["xp"] += xp_gain
            # 레벨업 체크 진행
            check_level_up(xp_gain)
        else:
            app_state["user"]["xp"] = max(0, app_state["user"]["xp"] - xp_gain)

        save_data()
        check_and_update_streak()

        # 현재 화면에 맞춰 강제 새로고침
        switch_tab(app_state["current_tab"])
    except Exception as ex:
        messagebox.showerror("토글 처리 에러", f"오류: {ex}")


def delete_quest(quest_id):
    try:
        if not messagebox.askyesno("삭제 여부 확인", "선택하신 RPG 퀘스트를 목록에서 지우시겠습니까?"):
            return
        app_state["quest_list"] = [
            q for q in app_state["quest_list"] if q["id"] != quest_id]
        save_data()
        check_and_update_streak()

        switch_tab(app_state["current_tab"])
    except Exception as err:
        messagebox.showerror("삭제 오류", f"처리 중 실패: {err}")

# =========================================================================
# 11. 최하단 네비게이션 및 동적 탭 전환 장치
# =========================================================================


def switch_tab(tab_idx):
    try:
        app_state["current_tab"] = tab_idx

        for idx, (btn, dot) in enumerate(app_state["tab_buttons"]):
            if idx == tab_idx:
                btn.configure(fg=ACCENT_ORANGE)
                dot.configure(text="•")
            else:
                btn.configure(fg=GRAY_TEXT)
                dot.configure(text=" ")

        for widget in app_state["main_container"].winfo_children():
            widget.destroy()

        if tab_idx == 0:
            draw_home_view(app_state["main_container"])
        elif tab_idx == 1:
            draw_quest_list_view(app_state["main_container"])
        elif tab_idx == 2:
            draw_timer_view(app_state["main_container"])
        elif tab_idx == 3:
            draw_calendar_view(app_state["main_container"])
        elif tab_idx == 4:
            draw_stats_view(app_state["main_container"])
        else:
            draw_coming_soon_view(app_state["main_container"], tab_idx)

    except Exception as e:
        print(f"화면 전환 실행 실패: {e}")


def create_bottom_nav(parent):
    # 테두리 완전 제거
    nav_frame = tk.Frame(parent, bg=WHITE, highlightthickness=0, bd=0, pady=8)
    nav_frame.pack(side="bottom", fill="x")

    for i in range(5):
        nav_frame.columnconfigure(i, weight=1)

    icon_manifest = [("홈", 0), ("일정", 1), ("타이머", 2), ("달력", 3), ("통계", 4)]
    app_state["tab_buttons"] = []

    for idx, (char, code) in enumerate(icon_manifest):
        active_color = (
            ACCENT_ORANGE if code == app_state["current_tab"] else GRAY_TEXT)

        col_wrap = tk.Frame(nav_frame, bg=WHITE)
        col_wrap.grid(row=0, column=idx, sticky="ew")
        lbl = tk.Label(
            col_wrap,
            text=char,
            font=(
                FONT_NAME,
                12,
                "bold"),
            fg=active_color,
            bg=WHITE,
            cursor="hand2")
        lbl.pack()
        dot_lbl = tk.Label(
            col_wrap,
            text="•" if code == app_state["current_tab"] else " ",
            font=(
                FONT_NAME,
                10,
                "bold"),
            fg=ACCENT_ORANGE,
            bg=WHITE)
        dot_lbl.pack()
        lbl.bind("<Button-1>", lambda e, c=code: switch_tab(c))
        dot_lbl.bind("<Button-1>", lambda e, c=code: switch_tab(c))
        # 튜플 형태로 (라벨, 점) 보관하여 switch_tab에서 참조
        app_state["tab_buttons"].append((lbl, dot_lbl))


def draw_quest_list_view(parent):
    """
    [함수 역할] 1번 탭(일정) - 전체 일정 목록을 렌더링합니다. (과거, 오늘, 미래의 모든 일정 조회 및 관리 가능)
    """
    wrap = tk.Frame(parent, bg=BG_COLOR)
    wrap.pack(fill="both", expand=True)

    # 상단 타이틀
    title_frame = tk.Frame(wrap, bg=BG_COLOR, padx=15, pady=10)
    title_frame.pack(fill="x")
    tk.Label(
        title_frame,
        text="전체 일정 목록",
        font=FONT_TITLE,
        fg=TEXT_BROWN,
        bg=BG_COLOR).pack(
        side="left")

    # 일정 추가 버튼을 상단 우측에도 조그맣게 배치
    add_btn = tk.Button(
        title_frame,
        text="+ 새 일정 추가",
        font=FONT_BOLD,
        fg=WHITE,
        bg=ACCENT_ORANGE,
        relief="flat",
        bd=0,
        padx=10,
        pady=4,
        command=open_add_quest_modal)
    add_btn.pack(side="right")

    # 전체 일정을 날짜순으로 정렬
    sorted_quests = sorted(
        app_state["quest_list"],
        key=lambda x: x["due_date"])

    # 메인 카드 프레임
    card = tk.Frame(
        wrap,
        bg=WHITE,
        padx=15,
        pady=15,
        highlightthickness=0,
        bd=0)
    card.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    if not sorted_quests:
        tk.Label(
            card,
            text="등록된 일정이 전혀 없습니다.\n새로운 일정을 추가해보세요!",
            font=FONT_MAIN,
            fg=GRAY_TEXT,
            bg=WHITE,
            justify="center",
            pady=50).pack()
        return

    # Tkinter 스크롤뷰 구현
    canvas = tk.Canvas(card, bg=WHITE, highlightthickness=0)
    scrollbar = ttk.Scrollbar(card, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=WHITE)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame,
                         anchor="nw", width=340)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 날짜별 그룹화하여 표시
    current_date_group = None
    for q in sorted_quests:
        # 날짜 구분선 표시
        if q["due_date"] != current_date_group:
            current_date_group = q["due_date"]
            group_lbl = tk.Label(
                scrollable_frame,
                text=f"{current_date_group} ({
                    get_d_day_string(current_date_group)})",
                font=FONT_BOLD,
                fg=TEXT_BROWN,
                bg=WHITE,
                anchor="w",
                pady=6)
            group_lbl.pack(fill="x", pady=(8, 2))

        draw_task_item(scrollable_frame, q)


def draw_stats_view(parent):
    """
    [함수 역할] 4번 탭 - 일정 완료 통계 및 완료율 분석 리포트를 렌더링합니다.
    """
    wrap = tk.Frame(parent, bg=BG_COLOR)
    wrap.pack(fill="both", expand=True)

    # 상단 타이틀
    tk.Label(
        wrap,
        text="일정 관리 통계 리포트",
        font=FONT_TITLE,
        fg=TEXT_BROWN,
        bg=BG_COLOR).pack(
        pady=(
            20,
            10))

    # 통계용 카드
    card = tk.Frame(
        wrap,
        bg=WHITE,
        padx=20,
        pady=25,
        highlightthickness=0,
        bd=0)
    card.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    # 통계 계산
    total = len(app_state["quest_list"])
    completed = sum(1 for q in app_state["quest_list"] if q["is_completed"])
    incomplete = total - completed
    completion_rate = int((completed / total) * 100) if total > 0 else 0

    # 통계 항목 레이아웃
    tk.Label(
        card,
        text="누적 통계",
        font=FONT_BOLD,
        fg=TEXT_BROWN,
        bg=WHITE).pack(
        anchor="w",
        pady=(
            0,
            10))

    stats_frame = tk.Frame(card, bg=WHITE)
    stats_frame.pack(fill="x", pady=5)

    items = [
        ("총 등록된 일정", f"{total} 개"),
        ("완료된 일정", f"{completed} 개"),
        ("진행 중인 일정", f"{incomplete} 개"),
        ("평균 일정 달성률", f"{completion_rate} %")
    ]

    for label, val in items:
        row = tk.Frame(stats_frame, bg=WHITE, pady=4)
        row.pack(fill="x")
        tk.Label(
            row,
            text=label,
            font=FONT_MAIN,
            fg=GRAY_TEXT,
            bg=WHITE).pack(
            side="left")
        tk.Label(
            row,
            text=val,
            font=FONT_BOLD,
            fg=TEXT_BROWN,
            bg=WHITE).pack(
            side="right")

    # 구분선
    tk.Frame(card, height=1, bg=BORDER_COLOR).pack(fill="x", pady=15)

    # 진행률 비주얼 막대
    tk.Label(
        card,
        text="달성률 분석",
        font=FONT_BOLD,
        fg=TEXT_BROWN,
        bg=WHITE).pack(
        anchor="w",
        pady=(
            0,
            10))

    chart_canvas = tk.Canvas(
        card,
        width=280,
        height=40,
        bg=CARD_BG,
        highlightthickness=0)
    chart_canvas.pack(pady=10)
    draw_rounded_rectangle(
        chart_canvas,
        2,
        2,
        278,
        38,
        radius=8,
        fill="#EADBCD")
    if completion_rate > 0:
        fill_w = int((completion_rate / 100.0) * 276)
        draw_rounded_rectangle(
            chart_canvas,
            2,
            2,
            fill_w,
            38,
            radius=8,
            fill=ACCENT_ORANGE)
    chart_canvas.create_text(
        140,
        20,
        text=f"완료율 {completion_rate}%",
        fill=WHITE if completion_rate > 50 else TEXT_BROWN,
        font=(
            FONT_NAME,
            10,
            "bold"))


def draw_coming_soon_view(parent, tab_idx):
    soon_wrap = tk.Frame(parent, bg=BG_COLOR, pady=80)
    soon_wrap.pack(fill="both", expand=True)

    tk.Label(
        soon_wrap,
        text="준비 중",
        font=(
            "맑은 고딕",
            14,
            "bold"),
        fg=TEXT_BROWN,
        bg=BG_COLOR).pack(
            pady=10)
    desc_str = "이 기능은 다음 업데이트에 연동될 예정입니다!\n천천히, 꾸준히 매일의 과제들을 클리어해주세요."
    tk.Label(
        soon_wrap,
        text=desc_str,
        font=FONT_MAIN,
        fg=GRAY_TEXT,
        bg=BG_COLOR,
        justify="center").pack(
        pady=10)

# =========================================================================
# 12. 메인 부트스트랩 진입점
# =========================================================================


def check_level_up(gained_xp):
    """
    [함수 역할] 레벨업 기능 비활성화로 더미 함수로 전환되었습니다.
    """
    pass


def main():
    try:
        root = tk.Tk()
        root.title("SLO퀘스트 - RPG 듀오링고 스케줄러")
        root.geometry("414x850")
        root.configure(bg=BG_COLOR)
        root.resizable(False, False)
        app_state["root"] = root

        # JSON 데이터베이스 로드 및 스트릭/하트 정리
        load_data()

        # 1. 기동 시 날짜 비교 및 미완료 일정 알림 로직
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        last_date = app_state["user"]["last_date"]
        if last_date != today_str and last_date != "":
            # 어제 미완수 퀘스트 체크
            yesterday_quests = [
                q for q in app_state["quest_list"]
                if q["due_date"] == last_date
            ]
            all_done = (
                all(q["is_completed"] for q in yesterday_quests)
                if yesterday_quests else True
            )

            if not all_done:
                messagebox.showwarning(
                    "미완료 일정 알림",
                    "어제 완료하지 못한 일정이 있습니다.\n일정 상세 및 연체 목록을 확인해보세요!"
                )
            app_state["user"]["last_date"] = today_str
            save_data()

        create_header(root)
        create_bottom_nav(root)

        app_state["main_container"] = tk.Frame(root, bg=BG_COLOR)
        app_state["main_container"].pack(fill="both", expand=True)

        switch_tab(0)

        # FAB + 버튼 배치
        fab_canvas = tk.Canvas(
            root,
            width=58,
            height=58,
            bg=BG_COLOR,
            highlightthickness=0,
            cursor="hand2")
        fab_canvas.place(x=332, y=695)

        fab_circle = fab_canvas.create_oval(
            3,
            3,
            55,
            55,
            fill=ACCENT_ORANGE,
            outline="#C47300",
            width=2,
            tags="fab_trigger")
        fab_canvas.create_text(
            29,
            29,
            text="+",
            font=(
                "맑은 고딕",
                22,
                "bold"),
            fill=WHITE,
            tags="fab_trigger")

        fab_canvas.tag_bind(
            "fab_trigger",
            "<Button-1>",
            lambda e: open_add_quest_modal())

        def hover_in(e): fab_canvas.itemconfig(fab_circle, fill="#FFAC33")
        def hover_out(e): fab_canvas.itemconfig(fab_circle, fill=ACCENT_ORANGE)
        fab_canvas.bind("<Enter>", hover_in)
        fab_canvas.bind("<Leave>", hover_out)

        root.mainloop()
    except Exception as fatal_err:
        print(f"치명적 구동 에러: {fatal_err}")
        err_box = tk.Tk()
        err_box.withdraw()
        messagebox.showerror(
            "구동 중단 알림",
            f"슬로퀘스트 초기화 도중 치명적인 문제가 감지되었습니다:\n{fatal_err}")
        err_box.destroy()


if __name__ == "__main__":
    main()
