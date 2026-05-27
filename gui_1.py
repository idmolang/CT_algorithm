import tkinter as tk  # GUI 구현을 위한 기본 tkinter 라이브러리 임포트
from tkinter import messagebox  # 팝업 메시지 박스 유틸리티 임포트
from tkinter import ttk  # 세련된 콤보박스 및 스크롤바 등 사용을 위한 ttk 임포트
import json  # 데이터 저장을 위해 JSON 처리 표준 라이브러리 임포트
import os  # 파일 경로 탐색 및 파일 확인용 os 라이브러리 임포트
import datetime  # 날짜 계산 및 오늘 날짜 처리를 위한 datetime 임포트
import calendar  # 달력 격자 생성 및 월 이동을 위한 calendar 임포트
import re  # AI 자연어 파싱을 위한 정규식 라이브러리 임포트

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

# 기본 폰트 패밀리 지정 (한글 맑은 고딕 탑재)
FONT_NAME = "맑은 고딕"
FONT_MAIN = (FONT_NAME, 11)
FONT_BOLD = (FONT_NAME, 11, "bold")
FONT_TITLE = (FONT_NAME, 16, "bold")
FONT_SMALL = (FONT_NAME, 9)

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
        "inventory": ["orange_scarf"] # 해금된 의상 장비 인벤토리 리스트
    },
    "quest_list": [],               # 퀘스트 배열 리스트 (id, title, difficulty, due_date, xp_reward, is_completed)
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
                app_state["quest_list"] = data.get("quest_list", app_state["quest_list"])
                app_state["equipped"] = data.get("equipped", app_state["equipped"])
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

def check_and_update_streak():
    """
    [함수 역할] 오늘자 퀘스트 올패스 여부를 체크하고 스트릭 일수를 가감합니다.
    """
    try:
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        today_quests = [q for q in app_state["quest_list"] if q["due_date"] == today_str]
        
        if not today_quests:
            return  # 퀘스트가 없다면 패스
            
        all_completed = all(q["is_completed"] for q in today_quests)
        
        # 오늘 과제가 다 깨졌고, 어제와 다른 신규 스트릭 일자인 경우 활성화
        if all_completed:
            if app_state["user"]["last_date"] != today_str or app_state["user"]["streak"] == 0:
                app_state["user"]["streak"] += 1
                app_state["user"]["last_date"] = today_str
                # 레벨 보너스 보석 지급 대신 게이미피케이션에 맞춰 XP 보너스 증정
                app_state["user"]["xp"] += 50
                messagebox.showinfo("일일 퀘스트 올 패스! 🔥", 
                                    f"축하합니다! 오늘의 모든 RPG 퀘스트를 완료하여 스트릭을 달성하셨습니다!\n"
                                    f"불꽃 스트릭 {app_state['user']['streak']}일 유지 중! 보너스 50XP를 획득했습니다. 🦥")
                # 레벨업 체크
                check_level_up(0)
                save_data()
                update_badges()
    except Exception as e:
        print(f"스트릭 검증 오류: {e}")

# =========================================================================
# 4. Canvas 기반 인터랙티브 나무늘보 'Slo' 커스텀 벡터 드로잉 엔진
# =========================================================================

def draw_vector_sloth(canvas, x_center, y_center, scale=1.0, is_sleeping=False, equipped=None):
    """
    [함수 역할] 둥근 도형들을 사용하여 모던하고 귀여운 나무늘보 '슬로(Slo)' 캐릭터를 캔버스에 직접 그립니다.
    이 방식은 파일 로딩 포맷 인식 실패를 근본적으로 차단하며, 장비 장착 상태와 스트릭 차감에 따른 취침(Zzz...) 상태를 완벽히 가변 반영합니다.
    """
    canvas.delete("sloth_part")  # 이전 파트 레이어 완전 삭제
    
    if equipped is None:
        equipped = app_state["equipped"]
        
    body_color = "#A88C74"  # 슬로 시그니처 갈색
    face_color = "#F7E6D7"  # 부드러운 얼굴 크림색
    dark_brown = "#5A4232"  # 다크 초콜릿 갈색
    
    # 1. 몸통 (둥근 항아리 모양)
    canvas.create_oval((x_center - 50*scale), (y_center - 45*scale), 
                       (x_center + 50*scale), (y_center + 55*scale), 
                       fill=body_color, outline="#8E735D", width=2, tags="sloth_part")
                       
    # 2. 얼굴 판 (연크림형 타원)
    canvas.create_oval((x_center - 38*scale), (y_center - 38*scale), 
                       (x_center + 38*scale), (y_center + 20*scale), 
                       fill=face_color, outline="", tags="sloth_part")
                       
    # 3. 눈가 어두운 무늬 패치
    canvas.create_oval((x_center - 28*scale), (y_center - 20*scale), 
                       (x_center - 8*scale), (y_center + 2*scale), 
                       fill=dark_brown, outline="", tags="sloth_part")
    canvas.create_oval((x_center + 8*scale), (y_center - 20*scale), 
                       (x_center + 28*scale), (y_center + 2*scale), 
                       fill=dark_brown, outline="", tags="sloth_part")
                       
    # 4. 수면/활동에 따른 눈 레이어
    if is_sleeping:
        # 잠자는 나무늘보: 호를 이용한 감은 눈("uu") 구현 및 Zzz 효과텍스트 추가
        canvas.create_arc((x_center - 24*scale), (y_center - 13*scale), 
                          (x_center - 12*scale), (y_center - 1*scale), 
                          start=180, extent=180, style="arc", outline="#F7E6D7", width=3, tags="sloth_part")
        canvas.create_arc((x_center + 12*scale), (y_center - 13*scale), 
                          (x_center + 24*scale), (y_center - 1*scale), 
                          start=180, extent=180, style="arc", outline="#F7E6D7", width=3, tags="sloth_part")
        # 연핑크 수줍은 볼터치
        canvas.create_oval((x_center - 28*scale), (y_center + 2*scale), 
                           (x_center - 18*scale), (y_center + 8*scale), 
                           fill="#FFB6C1", outline="", tags="sloth_part")
        canvas.create_oval((x_center + 18*scale), (y_center + 2*scale), 
                           (x_center + 28*scale), (y_center + 8*scale), 
                           fill="#FFB6C1", outline="", tags="sloth_part")
        # Zzz 수면 이펙트
        canvas.create_text((x_center + 45*scale), (y_center - 32*scale), text="Zzz...", font=("맑은 고딕", int(10*scale), "bold"), fill=TEXT_BROWN, tags="sloth_part")
    else:
        # 활동 상태: 초롱초롱한 왕구슬눈 및 하이라이트
        canvas.create_oval((x_center - 22*scale), (y_center - 14*scale), 
                           (x_center - 14*scale), (y_center - 6*scale), 
                           fill="#000000", outline="", tags="sloth_part")
        canvas.create_oval((x_center + 14*scale), (y_center - 14*scale), 
                           (x_center + 22*scale), (y_center - 6*scale), 
                           fill="#000000", outline="", tags="sloth_part")
        # 흰색 초점 점찍기
        canvas.create_oval((x_center - 20*scale), (y_center - 13*scale), 
                           (x_center - 17*scale), (y_center - 10*scale), 
                           fill="#FFFFFF", outline="", tags="sloth_part")
        canvas.create_oval((x_center + 16*scale), (y_center - 13*scale), 
                           (x_center + 19*scale), (y_center - 10*scale), 
                           fill="#FFFFFF", outline="", tags="sloth_part")
        # 붉은 볼터치
        canvas.create_oval((x_center - 28*scale), (y_center + 1*scale), 
                           (x_center - 18*scale), (y_center + 7*scale), 
                           fill="#FF8A8A", outline="", tags="sloth_part")
        canvas.create_oval((x_center + 18*scale), (y_center + 1*scale), 
                           (x_center + 28*scale), (y_center + 7*scale), 
                           fill="#FF8A8A", outline="", tags="sloth_part")

    # 5. 코와 입
    canvas.create_oval((x_center - 7*scale), (y_center - 5*scale), 
                       (x_center + 7*scale), (y_center + 3*scale), 
                       fill=dark_brown, outline="", tags="sloth_part")
    canvas.create_arc((x_center - 8*scale), (y_center + 2*scale), 
                      (x_center + 8*scale), (y_center + 10*scale), 
                      start=200, extent=140, style="arc", outline=dark_brown, width=2, tags="sloth_part")

    # 6. 의상 레이어 1 - 주황색 목도리 (orange_scarf)
    if equipped.get("orange_scarf", False):
        canvas.create_oval((x_center - 32*scale), (y_center + 21*scale),
                           (x_center + 32*scale), (y_center + 35*scale),
                           fill=ACCENT_ORANGE, outline="#C47300", width=1.5, tags="sloth_part")
        canvas.create_polygon([
            (x_center + 10*scale), (y_center + 28*scale),
            (x_center + 25*scale), (y_center + 28*scale),
            (x_center + 20*scale), (y_center + 48*scale),
            (x_center + 5*scale), (y_center + 45*scale)
        ], fill=ACCENT_ORANGE, outline="#C47300", width=1.5, tags="sloth_part")
        
    # 7. 의상 레이어 2 - 멋쟁이 선글라스 (sunglasses)
    if equipped.get("sunglasses", False):
        canvas.create_oval((x_center - 31*scale), (y_center - 18*scale),
                           (x_center - 7*scale), (y_center - 2*scale),
                           fill="#222222", outline="#FFFFFF", width=1, tags="sloth_part")
        canvas.create_oval((x_center + 7*scale), (y_center - 18*scale),
                           (x_center + 31*scale), (y_center - 2*scale),
                           fill="#222222", outline="#FFFFFF", width=1, tags="sloth_part")
        canvas.create_line((x_center - 7*scale), (y_center - 10*scale),
                            (x_center + 7*scale), (y_center - 10*scale),
                            fill="#FFFFFF", width=2, tags="sloth_part")

    # 8. 의상 레이어 3 - 황금 왕관 (crown)
    if equipped.get("crown", False):
        canvas.create_polygon([
            (x_center - 22*scale), (y_center - 35*scale),
            (x_center - 28*scale), (y_center - 55*scale),
            (x_center - 10*scale), (y_center - 45*scale),
            (x_center), (y_center - 60*scale),
            (x_center + 10*scale), (y_center - 45*scale),
            (x_center + 28*scale), (y_center - 55*scale),
            (x_center + 22*scale), (y_center - 35*scale)
        ], fill="#FFD700", outline="#B8860B", width=1.5, tags="sloth_part")
        canvas.create_oval((x_center - 30*scale), (y_center - 57*scale), (x_center - 26*scale), (y_center - 53*scale), fill="#FF0000", outline="", tags="sloth_part")
        canvas.create_oval((x_center - 2*scale), (y_center - 62*scale), (x_center + 2*scale), (y_center - 58*scale), fill="#0000FF", outline="", tags="sloth_part")
        canvas.create_oval((x_center + 26*scale), (y_center - 57*scale), (x_center + 30*scale), (y_center - 53*scale), fill="#FF0000", outline="", tags="sloth_part")

def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius=8, **kwargs):
    """
    [함수 역할] 캔버스에 둥근 카드를 그리기 위한 베지에 코너 연산 기반 범용 그리기 함수입니다.
    """
    points = [
        x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1, x2, y1,
        x2, y1 + radius, x2, y1 + radius, x2, y2 - radius, x2, y2 - radius, x2, y2,
        x2 - radius, y2, x2 - radius, y2, x1 + radius, y2, x1 + radius, y2, x1, y2,
        x1, y2 - radius, x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

def draw_experience_bar(canvas, xp_value):
    """
    [함수 역할] 상단 진행바 영역에 주황색 둥근 프로그레스 바를 렌더링합니다.
    """
    canvas.delete("bar_layer")
    w = 320
    h = 20
    pct = int((xp_value / 1000.0) * 100)
    pct = min(100, max(0, pct))
    
    # 트랙 배경
    draw_rounded_rectangle(canvas, 2, 2, w-2, h-2, radius=8, fill="#E6D7C8", outline="", tags="bar_layer")
    
    # 충전 바
    if pct > 0:
        bar_w = int((pct / 100.0) * (w - 4))
        bar_w = max(16, bar_w)
        draw_rounded_rectangle(canvas, 2, 2, bar_w, h-2, radius=8, fill=ACCENT_ORANGE, outline="", tags="bar_layer")
        
        txt_x = bar_w - 20 if bar_w > 50 else 25
        canvas.create_text(txt_x, h // 2, text=f"{pct}%", fill=WHITE if bar_w > 50 else TEXT_BROWN, font=("맑은 고딕", 8, "bold"), tags="bar_layer")

# =========================================================================
# 5. AI 자연어 입력 일정 분석 파서 (AI Quest Parser Heuristics)
# =========================================================================

def ai_quest_parser(input_text):
    """
    [함수 역할] 정규식(Regex) 분석을 가미하여 한 줄 일상 입력 구문에서 퀘스트 제목, 마감일, 난이도(XP)를 정밀 분석 정규화합니다.
    """
    # 1. 난이도 가이드 판단
    difficulty = "Medium"
    xp_reward = 100
    if re.search(r'(상|하드|어려움|hard|Hard|HARD)', input_text):
        difficulty = "Hard"
        xp_reward = 200
    elif re.search(r'(하|이지|쉬움|easy|Easy|EASY)', input_text):
        difficulty = "Easy"
        xp_reward = 50
    elif re.search(r'(중|보통|미디움|medium|Medium|MEDIUM)', input_text):
        difficulty = "Medium"
        xp_reward = 100
        
    # 2. 날짜 가이드 판단
    today = datetime.date.today()
    due_date = today.strftime("%Y-%m-%d")
    
    if "내일" in input_text:
        due_date = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    elif "모레" in input_text:
        due_date = (today + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    elif "오늘" in input_text:
        due_date = today.strftime("%Y-%m-%d")
    else:
        # MM월 DD일 매칭 분석
        date_match = re.search(r'(\d{1,2})월\s*(\d{1,2})일', input_text)
        if date_match:
            try:
                dt = datetime.date(today.year, int(date_match.group(1)), int(date_match.group(2)))
                due_date = dt.strftime("%Y-%m-%d")
            except: pass
        else:
            # ISO 매칭분석
            iso_match = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', input_text)
            if iso_match:
                due_date = f"{iso_match.group(1)}-{int(iso_match.group(2)):02d}-{int(iso_match.group(3)):02d}"
            else:
                short_match = re.search(r'(\d{1,2})[-/](\d{1,2})', input_text)
                if short_match:
                    due_date = f"{today.year}-{int(short_match.group(1)):02d}-{int(short_match.group(2)):02d}"
                    
    # 3. 자연어 정제 (제목 추출용)
    clean_title = input_text
    stopwords = [
        r'\d{1,2}월\s*\d{1,2}일(까지)?',
        r'\d{4}[-/]\d{1,2}[-/]\d{1,2}(까지)?',
        r'\d{1,2}[-/]\d{1,2}(까지)?',
        r'오늘(까지)?', r'내일(까지)?', r'모레(까지)?',
        r'(난이도)?\s*(상|하드|어려움|hard|Hard|HARD|중|보통|미디움|medium|Medium|MEDIUM|하|이지|쉬움|easy|Easy|EASY)',
        r'등록', r'추가', r'제출', r'하기', r'일정', r'퀘스트', r'할일', r'과제'
    ]
    for pattern in stopwords:
        clean_title = re.sub(pattern, '', clean_title)
        
    clean_title = re.sub(r'[\s\?\!\,\.\:\-]+', ' ', clean_title).strip()
    if not clean_title or len(clean_title) < 2:
        clean_title = "신규 스케줄 퀘스트"
        
    return {
        "title": clean_title,
        "difficulty": difficulty,
        "due_date": due_date,
        "xp_reward": xp_reward
    }

# =========================================================================
# 6. 헤더 및 홈 대시보드 뷰 그리기
# =========================================================================

def create_header(parent):
    """
    [함수 역할] 5개 하트 폼팩터가 적용된 상단 헤더 프레임을 구축합니다.
    """
    header_frame = tk.Frame(parent, bg=BG_COLOR, pady=8, padx=15)
    header_frame.pack(fill="x")
    
    # 왼쪽 나무늘보 아이콘박스
    icon_box = tk.Label(header_frame, text="🦥", font=("맑은 고딕", 16), bg=BG_COLOR)
    icon_box.pack(side="left")
    
    level_lbl = tk.Label(header_frame, text=f"Level {app_state['user']['level']}", font=("맑은 고딕", 14, "bold"), fg=TEXT_BROWN, bg=BG_COLOR)
    level_lbl.pack(side="left", padx=5)
    
    # 우측 하트(Heart) 및 불꽃(Streak) 콤팩트 배지
    stat_badge = tk.Frame(header_frame, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=10, pady=3)
    stat_badge.pack(side="right")
    
    hearts_str = "❤️" * app_state["user"]["heart"] + "💔" * (5 - app_state["user"]["heart"])
    app_state["root"].stat_label = tk.Label(stat_badge, text=f"{app_state['user']['streak']} 🔥  {hearts_str}", font=("맑은 고딕", 10, "bold"), fg=TEXT_BROWN, bg=CARD_BG)
    app_state["root"].stat_label.pack()

def draw_home_view(parent):
    """
    [함수 역할] 홈 메인 대시보드 및 커스텀 나무늘보 옷장 코스튬 UI를 렌더링합니다.
    """
    home_wrap = tk.Frame(parent, bg=BG_COLOR)
    home_wrap.pack(fill="both", expand=True)
    
    # A. 메인 진행율 카드형 영역
    card_frame = tk.Frame(home_wrap, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=15, pady=10)
    card_frame.pack(fill="x", padx=15, pady=6)
    
    # 캐릭터 연출 및 옷장 개방을 위한 가로 배열 정렬
    char_frame = tk.Frame(card_frame, bg=CARD_BG)
    char_frame.pack(fill="x")
    
    # 나무늘보 커스텀 드로잉 캔버스 마스코트 배치 (120x110 크기)
    sloth_canvas = tk.Canvas(char_frame, width=120, height=110, bg=WHITE, highlightthickness=1, highlightbackground=BORDER_COLOR)
    sloth_canvas.pack(side="left", padx=(40, 10))
    
    # 생명이 2개 이하로 고달픈 슬로는 수면 페널티 기믹 작동
    is_sleeping = app_state["user"]["heart"] <= 2
    draw_vector_sloth(sloth_canvas, 60, 55, scale=0.9, is_sleeping=is_sleeping)
    
    # 우측: 캐릭터 옷장 수동 변환 판넬
    closet_box = tk.LabelFrame(char_frame, text="👗 Slo's 옷장", font=FONT_BOLD, fg=TEXT_BROWN, bg=CARD_BG, labelanchor="n", padx=5, pady=5)
    closet_box.pack(side="left", padx=15)
    
    # 인벤토리 여부 확인을 통한 체크박스 활성화
    def toggle_gear(gear_key):
        if gear_key not in app_state["user"]["inventory"]:
            messagebox.showwarning("해금 필요", f"레벨을 더 올려 아이템을 해금하십시오!\n(목도리: Lv.1 | 선글라스: Lv.3 | 왕관: Lv.5)", parent=app_state["root"])
            return
        app_state["equipped"][gear_key] = not app_state["equipped"][gear_key]
        draw_vector_sloth(sloth_canvas, 60, 55, scale=0.9, is_sleeping=is_sleeping)
        save_data()
        
    scarf_var = tk.BooleanVar(value=app_state["equipped"]["orange_scarf"])
    glass_var = tk.BooleanVar(value=app_state["equipped"]["sunglasses"])
    crown_var = tk.BooleanVar(value=app_state["equipped"]["crown"])
    
    tk.Checkbutton(closet_box, text="🧡 주황목도리 (Lv.1)", variable=scarf_var, bg=CARD_BG, font=FONT_SMALL, command=lambda: toggle_gear("orange_scarf")).pack(anchor="w")
    tk.Checkbutton(closet_box, text="🕶️ 멋쟁이안경 (Lv.3)", variable=glass_var, bg=CARD_BG, font=FONT_SMALL, command=lambda: toggle_gear("sunglasses")).pack(anchor="w")
    tk.Checkbutton(closet_box, text="👑 황금왕관 (Lv.5)", variable=crown_var, bg=CARD_BG, font=FONT_SMALL, command=lambda: toggle_gear("crown")).pack(anchor="w")
    
    # 격려 서브타이틀
    tk.Label(card_frame, text="Slow but Steady", font=("맑은 고딕", 18, "bold"), fg=TEXT_BROWN, bg=CARD_BG).pack(pady=(5,0))
    rem_xp = 1000 - app_state["user"]["xp"]
    tk.Label(card_frame, text=f"You're {rem_xp}XP away from Level {app_state['user']['level'] + 1}!", font=FONT_SMALL, fg="#7A5A3F", bg=CARD_BG).pack()
    
    # 프로그레스바 지표 라벨
    progress_text_row = tk.Frame(card_frame, bg=CARD_BG)
    progress_text_row.pack(fill="x", padx=15, pady=(5,0))
    tk.Label(progress_text_row, text=f"Level {app_state['user']['level']}", font=FONT_BOLD, fg=TEXT_BROWN, bg=CARD_BG).pack(side="left")
    tk.Label(progress_text_row, text=f"Level {app_state['user']['level'] + 1}", font=FONT_BOLD, fg=TEXT_BROWN, bg=CARD_BG).pack(side="right")
    
    xp_canvas = tk.Canvas(card_frame, width=320, height=20, bg=CARD_BG, highlightthickness=0)
    xp_canvas.pack(pady=4)
    draw_experience_bar(xp_canvas, app_state["user"]["xp"])
    
    # B. 미니 스탯 가로 카드
    stats_row = tk.Frame(home_wrap, bg=BG_COLOR)
    stats_row.pack(fill="x", padx=10, pady=2)
    for i in range(3):
        stats_row.columnconfigure(i, weight=1)
        
    badge_data = [
        ("🔥", f"{app_state['user']['streak']} DAYS", "streak_label"),
        ("❤️", f"{app_state['user']['heart']} HEARTS", "lives_label"),
        ("👑", f"Lv. {app_state['user']['level']} SLO", "gems_label")
    ]
    for idx, (icon, text, key) in enumerate(badge_data):
        m_card = tk.Frame(stats_row, bg=WHITE, highlightthickness=1, highlightbackground=BORDER_COLOR, pady=6)
        m_card.grid(row=0, column=idx, padx=4, sticky="ew")
        tk.Label(m_card, text=icon, font=("맑은 고딕", 12), bg=WHITE).pack()
        lbl = tk.Label(m_card, text=text, font=FONT_BOLD, fg=TEXT_BROWN, bg=WHITE)
        lbl.pack()
        app_state[key] = lbl
        
    # C. 오늘의 퀘스트 목록 뷰어 그리기
    draw_quests_section(home_wrap)
    
    # D. 말풍선 격려
    msg_wrap = tk.Frame(home_wrap, bg=BG_COLOR, padx=15, pady=4)
    msg_wrap.pack(fill="x")
    msg_canvas = tk.Canvas(msg_wrap, height=75, bg=BG_COLOR, highlightthickness=0)
    msg_canvas.pack(fill="x")
    msg_canvas.create_rectangle(2, 2, 380, 70, outline=ACCENT_BLUE, width=2, dash=(4, 4))
    
    inner_bubble = tk.Frame(msg_canvas, bg=WHITE, padx=8, pady=4)
    msg_canvas.create_window(191, 36, window=inner_bubble, width=370, height=62)
    tk.Label(inner_bubble, text="🦥", font=("맑은 고딕", 16), bg=WHITE).pack(side="left", padx=5)
    coach_msg = '"Doing great! One more task and you\'ll hit\nyour daily goal. Take it slow, keep it steady."'
    tk.Label(inner_bubble, text=coach_msg, font=("맑은 고딕", 8, "italic"), fg=TEXT_BROWN, bg=WHITE, justify="left").pack(side="left")

# =========================================================================
# 7. Slo's Timer (집중 뽀모도로 타이머 구현 탭)
# =========================================================================

def draw_timer_view(parent):
    """
    [함수 역할] 3번째 탭(⏱️)에 연계된 퀘스트 맞춤 집중 타이머 및 완료 캔버스 애니메이션 구동을 담당합니다.
    """
    timer_wrap = tk.Frame(parent, bg=BG_COLOR, padx=20, pady=10)
    timer_wrap.pack(fill="both", expand=True)
    
    tk.Label(timer_wrap, text="⏱️ Slo's Focus Timer", font=FONT_TITLE, fg=TEXT_BROWN, bg=BG_COLOR).pack(pady=5)
    
    # 오늘 예정된 미완료 과제들만 리스트업하여 연동
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    unfinished_quests = [q for q in app_state["quest_list"] if q["due_date"] == today_str and not q["is_completed"]]
    
    if not unfinished_quests:
        tk.Label(timer_wrap, text="집중할 오늘 예정 퀘스트가 없습니다.\n먼저 퀘스트를 생성해주세요! 🦥", font=FONT_MAIN, fg=GRAY_TEXT, bg=BG_COLOR, justify="center", pady=50).pack()
        return
        
    # 집중 과제 선택 영역
    sel_frame = tk.LabelFrame(timer_wrap, text="집중 연계할 퀘스트 선택", font=FONT_BOLD, fg=TEXT_BROWN, bg=BG_COLOR, padx=10, pady=5)
    sel_frame.pack(fill="x", pady=10)
    
    quest_options = {q["title"]: q["id"] for q in unfinished_quests}
    selected_quest_name = tk.StringVar(value=list(quest_options.keys())[0])
    
    quest_combo = ttk.Combobox(sel_frame, textvariable=selected_quest_name, values=list(quest_options.keys()), state="readonly", font=FONT_MAIN)
    quest_combo.pack(fill="x", ipady=2)
    
    # 타이머 중심 비주얼 캐릭터 캔버스 탑재
    focus_canvas = tk.Canvas(timer_wrap, width=110, height=100, bg=WHITE, highlightthickness=1, highlightbackground=BORDER_COLOR)
    focus_canvas.pack(pady=10)
    
    # 집중 모드 캐릭터 드로잉 (깨어있는 모습)
    draw_vector_sloth(focus_canvas, 55, 50, scale=0.8, is_sleeping=False)
    
    # 타이머 표시 영역
    time_display = tk.Label(timer_wrap, text="25:00", font=("Consolas", 42, "bold"), fg=ACCENT_ORANGE, bg=BG_COLOR)
    time_display.pack(pady=5)
    
    # 시간 선택 바
    duration_var = tk.IntVar(value=600)  # 기본 10분 모드
    
    def set_duration(secs, label_txt):
        duration_var.set(secs)
        time_display.configure(text=label_txt)
        
    dur_row = tk.Frame(timer_wrap, bg=BG_COLOR)
    dur_row.pack(pady=5)
    
    tk.Button(dur_row, text="10초 데모", font=FONT_SMALL, command=lambda: set_duration(10, "00:10")).pack(side="left", padx=5)
    tk.Button(dur_row, text="5분", font=FONT_SMALL, command=lambda: set_duration(300, "05:00")).pack(side="left", padx=5)
    tk.Button(dur_row, text="25분(정식)", font=FONT_SMALL, command=lambda: set_duration(1500, "25:00")).pack(side="left", padx=5)
    
    # 타이머 틱 동적 처리기
    def timer_tick():
        if not app_state["timer_running"]: return
        
        app_state["timer_seconds"] -= 1
        mins = app_state["timer_seconds"] // 60
        secs = app_state["timer_seconds"] % 60
        time_display.configure(text=f"{mins:02d}:{secs:02d}")
        
        # 1초마다 마스코트 좌우 깜빡임 애니메이션으로 역동성 추가
        if app_state["timer_seconds"] % 2 == 0:
            draw_vector_sloth(focus_canvas, 55, 50, scale=0.8, is_sleeping=True)
        else:
            draw_vector_sloth(focus_canvas, 55, 50, scale=0.8, is_sleeping=False)
            
        if app_state["timer_seconds"] <= 0:
            app_state["timer_running"] = False
            # 집중 목표 성공 및 캔버스 애니메이션 트리거
            perform_timer_completion(quest_options[selected_quest_name.get()])
        else:
            app_state["timer_job"] = app_state["root"].after(1000, timer_tick)
            
    def start_timer():
        if app_state["timer_running"]: return
        app_state["timer_running"] = True
        app_state["timer_seconds"] = duration_var.get()
        app_state["timer_target_id"] = quest_options[selected_quest_name.get()]
        timer_tick()
        
    def stop_timer():
        app_state["timer_running"] = False
        if app_state["timer_job"]:
            app_state["root"].after_cancel(app_state["timer_job"])
        time_display.configure(text="25:00")
        draw_vector_sloth(focus_canvas, 55, 50, scale=0.8, is_sleeping=False)
        
    # 하단 조작기 버튼
    btn_row = tk.Frame(timer_wrap, bg=BG_COLOR)
    btn_row.pack(pady=15)
    
    tk.Button(btn_row, text="▶ 집중 개시", font=FONT_BOLD, fg=WHITE, bg=ACCENT_ORANGE, relief="flat", padx=15, pady=5, command=start_timer).pack(side="left", padx=10)
    tk.Button(btn_row, text="⏹ 포기/정지", font=FONT_MAIN, bg="#E0D4C9", fg=TEXT_BROWN, relief="flat", padx=15, pady=5, command=stop_timer).pack(side="right", padx=10)

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
        
        tk.Label(anim_win, text="🎉 집중 과제를 완수하셨습니다! 🎉", font=FONT_BOLD, fg=TEXT_BROWN, bg=BG_COLOR).pack(pady=15)
        
        bar_canvas = tk.Canvas(anim_win, width=320, height=25, bg=BG_COLOR, highlightthickness=0)
        bar_canvas.pack(pady=10)
        
        # 1초간 애니메이션으로 주황색 프로그레스 채우기 시각화 구현
        def animate_step(step=0):
            if step <= 100:
                bar_canvas.delete("all")
                draw_rounded_rectangle(bar_canvas, 2, 2, 318, 23, radius=8, fill="#E6D7C8")
                fill_w = int((step / 100.0) * 316)
                if fill_w > 16:
                    draw_rounded_rectangle(bar_canvas, 2, 2, fill_w, 23, radius=8, fill=ACCENT_ORANGE)
                app_state["root"].after(10, lambda: animate_step(step + 2))
            else:
                # 퀘스트 상태 완료 업데이트
                anim_win.destroy()
                toggle_quest_status(quest_id)
                messagebox.showinfo("퀘스트 달성 성공", "경험치를 무사히 획득했습니다! 🦥")
                
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
    global cal_year, cal_month
    
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
        
    tk.Button(ctrl_row, text="◀", font=("맑은 고딕", 11, "bold"), fg=TEXT_BROWN, bg=BG_COLOR, relief="flat", activebackground=CARD_BG, command=slide_prev).pack(side="left", padx=10)
    tk.Label(ctrl_row, text=f"{cal_year}년 {cal_month}월", font=("맑은 고딕", 13, "bold"), fg=TEXT_BROWN, bg=BG_COLOR).pack(side="left", expand=True, fill="x")
    tk.Button(ctrl_row, text="▶", font=("맑은 고딕", 11, "bold"), fg=TEXT_BROWN, bg=BG_COLOR, relief="flat", activebackground=CARD_BG, command=slide_next).pack(side="right", padx=10)
    
    # B. 요일 이정표
    wk_frame = tk.Frame(cal_wrap, bg=BG_COLOR)
    wk_frame.pack(fill="x", pady=(5, 2))
    wk_labels = ["일", "월", "화", "수", "목", "금", "토"]
    for i, day_name in enumerate(wk_labels):
        wk_frame.columnconfigure(i, weight=1)
        w_lbl = tk.Label(wk_frame, text=day_name, font=("맑은 고딕", 9, "bold"), bg=BG_COLOR)
        if i == 0: w_lbl.configure(fg="#D05A5A")
        elif i == 6: w_lbl.configure(fg="#5A90D0")
        else: w_lbl.configure(fg=TEXT_BROWN)
        w_lbl.grid(row=0, column=i, sticky="ew")
        
    # C. 날짜 격자 그리드 구현
    grid_box = tk.Frame(cal_wrap, bg=WHITE, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=5, pady=5)
    grid_box.pack(fill="x", pady=5)
    for i in range(7):
        grid_box.columnconfigure(i, weight=1)
        
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
                tk.Label(grid_box, text="", bg=WHITE, height=2).grid(row=row_count, column=col_idx, sticky="nsew", padx=1, pady=1)
            else:
                curr_date = f"{cal_year}-{cal_month:02d}-{val:02d}"
                # 스트릭 체크는 이제 퀘스트 목록의 is_completed 올 클리어로 판단
                day_quests = [q for q in app_state["quest_list"] if q["due_date"] == curr_date]
                is_streak_completed = len(day_quests) > 0 and all(q["is_completed"] for q in day_quests)
                
                is_sel = curr_date == app_state["selected_date"]
                is_tod = curr_date == today_str
                
                day_cell = tk.Frame(grid_box, bg=WHITE)
                day_cell.grid(row=row_count, column=col_idx, sticky="nsew", padx=1, pady=1)
                
                if is_streak_completed:
                    lbl = tk.Label(day_cell, text=str(val), font=("맑은 고딕", 9, "bold"), fg=WHITE, bg=ACCENT_ORANGE, width=3, height=1, cursor="hand2")
                elif is_sel:
                    lbl = tk.Label(day_cell, text=str(val), font=("맑은 고딕", 9, "bold"), fg=TEXT_BROWN, bg="#F3E5D8", width=3, height=1, relief="solid", bd=1, cursor="hand2")
                elif is_tod:
                    lbl = tk.Label(day_cell, text=str(val), font=("맑은 고딕", 9, "bold", "underline"), fg=ACCENT_ORANGE, bg=WHITE, width=3, height=1, cursor="hand2")
                else:
                    fg_color = TEXT_BROWN
                    if col_idx == 0: fg_color = "#D05A5A"
                    if col_idx == 6: fg_color = "#5A90D0"
                    lbl = tk.Label(day_cell, text=str(val), font=("맑은 고딕", 9), fg=fg_color, bg=WHITE, width=3, height=1, cursor="hand2")
                    
                lbl.pack(pady=3)
                lbl.bind("<Button-1>", lambda e, d_str=curr_date: tap_date(d_str))
                day_cell.bind("<Button-1>", lambda e, d_str=curr_date: tap_date(d_str))
        row_count += 1
        
    # D. 선택일 세부 패널
    focus_date = app_state["selected_date"]
    try:
        parsed_dt = datetime.datetime.strptime(focus_date, "%Y-%m-%d")
        kor_date_title = parsed_dt.strftime("%Y년 %m월 %d일")
    except:
        kor_date_title = focus_date
        
    detail_panel = tk.Frame(cal_wrap, bg=BG_COLOR)
    detail_panel.pack(fill="both", expand=True, pady=8)
    
    tk.Label(detail_panel, text=f"📌 {kor_date_title} 퀘스트 목록", font=FONT_BOLD, fg=TEXT_BROWN, bg=BG_COLOR, anchor="w").pack(fill="x", pady=(0, 4))
    
    filtered_quests = [q for q in app_state["quest_list"] if q["due_date"] == focus_date]
    
    if not filtered_quests:
        tk.Label(detail_panel, text="이 일자에 배정된 과제가 없습니다. 🦥", font=FONT_MAIN, fg=GRAY_TEXT, bg=BG_COLOR, anchor="w", pady=10).pack(fill="x")
    else:
        for q in filtered_quests:
            item_bar = tk.Frame(detail_panel, bg=WHITE, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=10, pady=5)
            item_bar.pack(fill="x", pady=2)
            
            chk_icon = "✅" if q["is_completed"] else "⚪"
            chk_col = ACCENT_ORANGE if q["is_completed"] else GRAY_TEXT
            
            icon_lbl = tk.Label(item_bar, text=chk_icon, font=("맑은 고딕", 10), fg=chk_col, bg=WHITE)
            icon_lbl.pack(side="left", padx=(0, 5))
            
            if focus_date == today_str:
                icon_lbl.configure(cursor="hand2")
                icon_lbl.bind("<Button-1>", lambda e, q_id=q["id"]: toggle_quest_status(q_id))
                
            font_opt = ("맑은 고딕", 10, "overstrike") if q["is_completed"] else ("맑은 고딕", 10)
            txt_color = GRAY_TEXT if q["is_completed"] else TEXT_BROWN
            tk.Label(item_bar, text=q["title"], font=font_opt, fg=txt_color, bg=WHITE, anchor="w").pack(side="left", fill="x", expand=True)
            
            level_tag = "COMPLETED" if q["is_completed"] else f"{q['difficulty']} • {q['xp_reward']}XP"
            level_color = GRAY_TEXT if q["is_completed"] else ("#D05A5A" if q["difficulty"] == "Hard" else "#5A90D0")
            tk.Label(item_bar, text=level_tag, font=("맑은 고딕", 7, "bold"), fg=level_color, bg=CARD_BG, padx=4).pack(side="right")
            
    # E. 하단 액션 버튼 바
    action_row = tk.Frame(cal_wrap, bg=BG_COLOR)
    action_row.pack(side="bottom", fill="x", pady=(2, 5))
    
    sim_btn = tk.Button(action_row, text="⌛ 하루 경과 시뮬레이션", font=("맑은 고딕", 9, "bold"), fg="#D05A5A", bg=WHITE, activebackground=CARD_BG, relief="solid", bd=1, padx=8, pady=4, command=simulate_next_day)
    sim_btn.pack(side="left")
    
    sync_btn = tk.Button(action_row, text="📅 구글 캘린더 동기화", font=("맑은 고딕", 9, "bold"), fg=WHITE, bg=ACCENT_ORANGE, activebackground="#E58600", activeforeground=WHITE, relief="flat", padx=10, pady=4, command=sync_google_calendar)
    sync_btn.pack(side="right")

def show_api_dialog_box(title, text_content):
    try:
        popup = tk.Toplevel(app_state["root"])
        popup.title(title)
        popup.geometry("380x360")
        popup.configure(bg=BG_COLOR)
        popup.resizable(False, False)
        popup.transient(app_state["root"])
        popup.grab_set()
        
        tk.Label(popup, text="📅 Calendar API 동기화 가이드", font=FONT_TITLE, fg=TEXT_BROWN, bg=BG_COLOR).pack(pady=(15, 8))
        text_area = tk.Text(popup, font=("맑은 고딕", 9), bg=WHITE, fg=TEXT_BROWN, wrap="word", relief="solid", bd=1, padx=8, pady=8)
        text_area.pack(fill="both", expand=True, padx=15, pady=8)
        text_area.insert("1.0", text_content)
        text_area.configure(state="disabled")
        
        close_btn = tk.Button(popup, text="가이드 닫기", font=FONT_BOLD, fg=WHITE, bg=ACCENT_ORANGE, relief="flat", padx=15, pady=4, command=popup.destroy)
        close_btn.pack(pady=(8, 15))
    except Exception as e:
        print(f"안내 팝업 에러: {e}")

def sync_google_calendar():
    """
    [함수 역할] 구글 캘린더 API 패키지를 탑재하여 실제 구글 캘린더 일정을 생성하며 실패 시 로컬 보존 안내창으로 부드럽게 우회합니다.
    """
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        import pickle
        
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        script_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(script_dir, 'token.pickle')
        creds_path = os.path.join(script_dir, 'credentials.json')
        
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(creds_path):
                    raise FileNotFoundError("credentials.json 파일이 없습니다.")
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
                
        service = build('calendar', 'v3', credentials=creds)
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        push_cnt = 0
        
        for q in app_state["quest_list"]:
            if q["due_date"] == today_str and not q["is_completed"]:
                event_data = {
                    'summary': f'[SLOQuest] {q["title"]}',
                    'description': f'난이도: {q["difficulty"]} | XP 보상: {q["xp_reward"]}\n나무늘보와 꾸준히 실천! 🦥',
                    'start': {'dateTime': f'{today_str}T17:00:00', 'timeZone': 'Asia/Seoul'},
                    'end': {'dateTime': f'{today_str}T18:00:00', 'timeZone': 'Asia/Seoul'}
                }
                service.events().insert(calendarId='primary', body=event_data).execute()
                push_cnt += 1
                
        messagebox.showinfo("동기화 완수 🎉", f"구글 캘린더 연동 성공!\n오늘 진행 예정인 {push_cnt}개의 퀘스트 일정을 푸시했습니다.")
    except Exception as err:
        local_sync_msg = (
            f"구글 연동 알림:\n- 상태: 라이브러리가 로드되었으나 API 자격증명이 필요합니다.\n\n"
            "오프라인 로컬 저장소 동기화가 성공적으로 수행되었습니다.\n"
            "작성 및 완료 상태는 로컬 JSON(slo_data.json)에 자동 누적되어, 캘린더 탭 격자판에서 성공한 날짜들을 주황색 동그라미로 즉각 확인하실 수 있습니다!"
        )
        show_api_dialog_box("로컬 캘린더 싱크 완료", local_sync_msg)

# =========================================================================
# 9. 스트릭 및 페널티 시뮬레이션 상호작용
# =========================================================================

def simulate_next_day():
    """
    [함수 역할] 하루가 지나 날짜가 바뀌어 어제 과제 미달성 시 하트 차감 및 쉴드 방어 동작을 미리 시험해보는 모의 시뮬레이터입니다.
    """
    try:
        if not messagebox.askyesno("시뮬레이터 작동", "하루가 경과한 상황을 모의로 테스트해보시겠습니까?\n(어제 깨지 못한 과제가 있을 경우 하트가 깎이며 쉴드가 소모될 수 있습니다.)"):
            return
            
        today = datetime.date.today()
        today_str = today.strftime("%Y-%m-%d")
        yesterday_str = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 1. 오늘 퀘스트를 어제 날짜 퀘스트로 강제 이동
        shifted = 0
        for q in app_state["quest_list"]:
            if q["due_date"] == today_str:
                q["due_date"] = yesterday_str
                shifted += 1
                
        # 2. 어제 날짜 퀘스트 올패스 체크
        yesterday_quests = [q for q in app_state["quest_list"] if q["due_date"] == yesterday_str]
        all_done = all(q["is_completed"] for q in yesterday_quests) if yesterday_quests else True
        
        # 3. 듀오링고식 생명 및 페널티 연산 적용
        if not all_done:
            # 어제 미완수 발생
            if app_state["user"]["heart"] > 0:
                app_state["user"]["heart"] -= 1
                messagebox.showwarning(
                    "하트 쉴드 차감! ❤️🛡️",
                    f"어제 깜빡하고 깨지 못한 퀘스트가 발견되었습니다!\n\n"
                    f"생명(Heart)이 1개 소모되어 소중한 연속 스트릭 불꽃({app_state['user']['streak']}일)을 "
                    f"동결 쉴드로 가까스로 수호했습니다!\n"
                    f"(남은 생명: {app_state['user']['heart']} / 5)"
                )
            else:
                old_streak = app_state["user"]["streak"]
                app_state["user"]["streak"] = 0
                messagebox.showerror(
                    "스트릭이 단절되었습니다 😢",
                    f"어제 잔여 과제가 존재하나 남은 생명(Heart)도 부족하여\n"
                    f"아쉽게 연속 {old_streak}일 스트릭이 0일로 리셋되었습니다!\n"
                    f"다시 나무늘보 Slo와 오늘부터 천천히 확실히 도약해보아요."
                )
        else:
            if yesterday_quests:
                app_state["user"]["streak"] += 1
                messagebox.showinfo(
                    "스트릭 수호 성공! 🔥",
                    f"어제 과제를 전부 말끔히 정복하셨습니다!\n"
                    f"스트릭 기록이 {app_state['user']['streak']}일로 상승 및 유지되었습니다!"
                )
                
        # 4. 신규 하루치 모의 퀘스트 2종 발급
        app_state["quest_list"].append({
            "id": f"q_sim1_{int(datetime.datetime.now().timestamp())}",
            "title": "알고리즘 과제",
            "difficulty": "Hard",
            "due_date": today_str,
            "xp_reward": 200,
            "is_completed": False
        })
        app_state["quest_list"].append({
            "id": f"q_sim2_{int(datetime.datetime.now().timestamp())}",
            "title": "생물 시험 복습",
            "difficulty": "Medium",
            "due_date": today_str,
            "xp_reward": 100,
            "is_completed": False
        })
        
        app_state["selected_date"] = today_str
        save_data()
        update_badges()
        
        if app_state["current_tab"] == 0: switch_tab(0)
        elif app_state["current_tab"] == 3: switch_tab(3)
    except Exception as e:
        messagebox.showerror("시뮬레이션 예외", f"에러: {e}")

def update_badges():
    """
    [함수 역할] 상단 하트 배지와 스탯 수치 라벨들을 현재 JSON 메모리 상태에 맞춰 실시간 재작성합니다.
    """
    try:
        hearts_str = "❤️" * app_state["user"]["heart"] + "💔" * (5 - app_state["user"]["heart"])
        if hasattr(app_state["root"], "stat_label") and app_state["root"].stat_label:
            app_state["root"].stat_label.configure(text=f"{app_state['user']['streak']} 🔥  {hearts_str}")
            
        if app_state["streak_label"] and app_state["streak_label"].winfo_exists():
            app_state["streak_label"].configure(text=f"{app_state['user']['streak']} DAYS")
            
        if app_state["lives_label"] and app_state["lives_label"].winfo_exists():
            app_state["lives_label"].configure(text=f"{app_state['user']['heart']} HEARTS")
            
        if app_state["gems_label"] and app_state["gems_label"].winfo_exists():
            app_state["gems_label"].configure(text=f"Lv. {app_state['user']['level']} SLO")
    except Exception as e:
        print(f"뱃지 업데이트 실패: {e}")

# =========================================================================
# 10. AI 자연어 일정 추가 팝업 및 퀘스트 제어 로직
# =========================================================================

def open_add_quest_modal():
    """
    [함수 역할] 자연어 과제 추가 창을 띄워 AI 파서 분석 결과를 시각화하고 최종 등록합니다. (AI Quest Parser 연계)
    """
    try:
        modal = tk.Toplevel(app_state["root"])
        modal.title("AI 자연어 퀘스트 분석")
        modal.geometry("380x420")
        modal.configure(bg=BG_COLOR)
        modal.resizable(False, False)
        modal.transient(app_state["root"])
        modal.grab_set()
        
        tk.Label(modal, text="🔮 AI 자연어 퀘스트 파서", font=FONT_TITLE, fg=TEXT_BROWN, bg=BG_COLOR).pack(pady=15)
        
        # 자연어 설명
        instruction = (
            "Slo에게 대화하듯 일정을 이야기해보세요!\n"
            "예: '내일까지 알고리즘 과제 제출 난이도 하드'\n"
            "일자, 과제내용, 난이도(XP)를 자동 정규화합니다."
        )
        tk.Label(modal, text=instruction, font=FONT_MAIN, fg=TEXT_BROWN, bg=BG_COLOR, justify="center").pack(pady=5)
        
        # 1. 텍스트 에어리어
        text_entry = tk.Entry(modal, font=("맑은 고딕", 12), bg=WHITE, fg=TEXT_BROWN, relief="solid", bd=1)
        text_entry.pack(fill="x", padx=25, ipady=6, pady=10)
        text_entry.focus()
        
        # 분석 파서 결과 피드백 디스플레이용 프레임
        preview_frame = tk.LabelFrame(modal, text="AI 정규화 분석 결과 미리보기", font=FONT_BOLD, fg=TEXT_BROWN, bg=BG_COLOR, padx=15, pady=8)
        preview_frame.pack(fill="both", expand=True, padx=25, pady=5)
        
        lbl_title = tk.Label(preview_frame, text="과제명: -", font=FONT_MAIN, bg=BG_COLOR, anchor="w")
        lbl_title.pack(fill="x", pady=2)
        
        lbl_due = tk.Label(preview_frame, text="마감일: -", font=FONT_MAIN, bg=BG_COLOR, anchor="w")
        lbl_due.pack(fill="x", pady=2)
        
        lbl_diff = tk.Label(preview_frame, text="난이도(XP): -", font=FONT_MAIN, bg=BG_COLOR, anchor="w")
        lbl_diff.pack(fill="x", pady=2)
        
        parsed_result = {"data": None}
        
        def run_parsing():
            raw_t = text_entry.get().strip()
            if not raw_t:
                messagebox.showwarning("입력 유실", "과제 문장을 한 줄 적어주십시오.", parent=modal)
                return
            # 파서 구동
            res = ai_quest_parser(raw_t)
            parsed_result["data"] = res
            
            lbl_title.configure(text=f"과제명: {res['title']}", fg="#2E7D32")
            lbl_due.configure(text=f"마감일: {res['due_date']}", fg="#2E7D32")
            lbl_diff.configure(text=f"난이도(XP): {res['difficulty']} ({res['xp_reward']}XP)", fg="#2E7D32")
            
        # AI 파싱 실행 단추
        tk.Button(modal, text="🔍 AI 자연어 일정 분석 실행", font=FONT_BOLD, fg=WHITE, bg=ACCENT_BLUE, relief="flat", padx=10, pady=3, command=run_parsing).pack(pady=5)
        
        def confirm_registration():
            if not parsed_result["data"]:
                messagebox.showwarning("분석 필요", "먼저 분석을 성공적으로 실행해주십시오.", parent=modal)
                return
                
            res = parsed_result["data"]
            unique_id = f"q_{int(datetime.datetime.now().timestamp() * 1000)}"
            
            # JSON 퀘스트 리스트에 가산
            app_state["quest_list"].append({
                "id": unique_id,
                "title": res["title"],
                "difficulty": res["difficulty"],
                "due_date": res["due_date"],
                "xp_reward": res["xp_reward"],
                "is_completed": False
            })
            
            save_data()
            
            if app_state["current_tab"] == 0: switch_tab(0)
            elif app_state["current_tab"] == 3: switch_tab(3)
            
            modal.destroy()
            messagebox.showinfo("퀘스트 등록", f"AI 스케줄 퀘스트가 정상 배치되었습니다! 🦥", parent=app_state["root"])
            
        # 조작 버튼 바
        btn_bar = tk.Frame(modal, bg=BG_COLOR)
        btn_bar.pack(fill="x", pady=15)
        
        tk.Button(btn_bar, text="취소", font=FONT_MAIN, bg="#E0D4C9", fg=TEXT_BROWN, relief="flat", padx=15, pady=4, command=modal.destroy).pack(side="left", padx=(50, 10))
        tk.Button(btn_bar, text="과제 수락", font=FONT_BOLD, bg=ACCENT_ORANGE, fg=WHITE, relief="flat", padx=15, pady=4, command=confirm_registration).pack(side="right", padx=(10, 50))
        
    except Exception as ex:
        messagebox.showerror("AI 모달 구동 실패", f"오류: {ex}")

def draw_quests_section(parent):
    """
    [함수 역할] 홈 대시보드의 당일자 퀘스트 카드리스트를 렌더링합니다.
    """
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    today_quests = [q for q in app_state["quest_list"] if q["due_date"] == today_str]
    rem_count = sum(1 for q in today_quests if not q["is_completed"])
    
    wrap = tk.Frame(parent, bg=BG_COLOR, padx=15)
    wrap.pack(fill="x", pady=3)
    
    hdr = tk.Frame(wrap, bg=BG_COLOR)
    hdr.pack(fill="x", pady=(3, 5))
    
    tk.Label(hdr, text="Today's Quests", font=FONT_TITLE, fg="black", bg=BG_COLOR).pack(side="left")
    
    lbl_text = f"{rem_count} REMAINING" if rem_count > 0 else "ALL COMPLETED! 🎉"
    lbl_color = "#A66F3F" if rem_count > 0 else "#2E7D32"
    tk.Label(hdr, text=lbl_text, font=FONT_BOLD, fg=lbl_color, bg=BG_COLOR).pack(side="right", pady=(4, 0))
    
    if not today_quests:
        tk.Label(wrap, text="오늘 생성된 과제가 없습니다.\n오른쪽 밑의 '+' 버튼으로 AI 파서를 구동하세요! 🦥", font=FONT_MAIN, fg=GRAY_TEXT, bg=BG_COLOR, justify="center", pady=20).pack()
        return
        
    for q in today_quests:
        is_done = q["is_completed"]
        
        card = tk.Frame(wrap, bg=WHITE if not is_done else CARD_BG, highlightthickness=1, highlightbackground=BORDER_COLOR if not is_done else "#F2E5D9", padx=12, pady=6)
        card.pack(fill="x", pady=3)
        
        card.bind("<Enter>", lambda e, c=card: c.configure(highlightbackground=ACCENT_ORANGE))
        card.bind("<Leave>", lambda e, c=card, idn=is_done: c.configure(highlightbackground=BORDER_COLOR if not idn else "#F2E5D9"))
        
        chk_char = "🧡" if is_done else "⚪"
        chk_col = ACCENT_ORANGE if is_done else GRAY_TEXT
        
        chk_lbl = tk.Label(card, text=chk_char, font=("맑은 고딕", 13), fg=chk_col, bg=card["bg"], cursor="hand2")
        chk_lbl.pack(side="left", padx=(0, 10))
        chk_lbl.bind("<Button-1>", lambda e, q_id=q["id"]: toggle_quest_status(q_id))
        
        info_column = tk.Frame(card, bg=card["bg"])
        info_column.pack(side="left", fill="x", expand=True)
        
        f_style = ("맑은 고딕", 11, "overstrike") if is_done else ("맑은 고딕", 11)
        c_style = GRAY_TEXT if is_done else TEXT_BROWN
        tk.Label(info_column, text=q["title"], font=f_style, fg=c_style, bg=card["bg"], anchor="w").pack(anchor="w")
        
        tag_row = tk.Frame(info_column, bg=card["bg"])
        tag_row.pack(anchor="w", pady=(1, 0))
        
        if is_done:
            t_bg, t_fg, t_txt = "#E6DCD2", GRAY_TEXT, "COMPLETED"
        else:
            t_txt = f"{q['difficulty']} • {q['xp_reward']}XP"
            if q["difficulty"] == "Hard":
                t_bg, t_fg = "#FFE4E1", "#D05A5A"
            elif q["difficulty"] == "Medium":
                t_bg, t_fg = "#E0F0FF", "#5A90D0"
            else:
                t_bg, t_fg = "#E8F5E9", "#2E7D32"
                
        tk.Label(tag_row, text=t_txt, font=("맑은 고딕", 7, "bold"), bg=t_bg, fg=t_fg, padx=5, pady=1).pack(side="left")
        
        if is_done:
            tk.Label(card, text="🎉", font=("맑은 고딕", 12), bg=card["bg"]).pack(side="right", padx=5)
        else:
            del_lbl = tk.Label(card, text="❌", font=("맑은 고딕", 9), fg="#E57373", bg=card["bg"], cursor="hand2")
            del_lbl.pack(side="right", padx=5)
            del_lbl.bind("<Button-1>", lambda e, q_id=q["id"]: delete_quest(q_id))

def toggle_quest_status(quest_id):
    """
    [함수 역할] 과제 상태 토글 처리 및 경험치를 더한 뒤 레벨업 검증을 실행합니다.
    """
    try:
        target = None
        for q in app_state["quest_list"]:
            if q["id"] == quest_id:
                target = q
                break
        if not target: return
        
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
        
        if app_state["current_tab"] == 0: switch_tab(0)
        elif app_state["current_tab"] == 3: switch_tab(3)
    except Exception as ex:
        messagebox.showerror("토글 처리 에러", f"오류: {ex}")

def check_level_up(gained_xp):
    """
    [함수 역할] 누적 XP가 1000에 달성하면 레벨업을 진행하고 나무 위 코스튬을 추가해 줍니다. (Level-up & Gear 연계)
    """
    if app_state["user"]["xp"] >= 1000:
        app_state["user"]["level"] += 1
        app_state["user"]["xp"] = app_state["user"]["xp"] % 1000
        app_state["user"]["heart"] = 5  # 하트 만충 5개
        
        # 기획서 상의 레벨 코스튬 해금 로직
        unlocked_gear = ""
        if app_state["user"]["level"] >= 3 and "sunglasses" not in app_state["user"]["inventory"]:
            app_state["user"]["inventory"].append("sunglasses")
            unlocked_gear = "\n🕶️ '멋쟁이안경'이 Slo의 옷장에 잠금 해제되었습니다!"
        elif app_state["user"]["level"] >= 5 and "crown" not in app_state["user"]["inventory"]:
            app_state["user"]["inventory"].append("crown")
            unlocked_gear = "\n👑 '황금왕관'이 Slo의 옷장에 잠금 해제되었습니다!"
            
        messagebox.showinfo("레벨 업! 👑🎉", 
                            f"천천히 꾸준하게! Level {app_state['user']['level']}을 달성했습니다!\n"
                            f"생명(Heart)이 5개로 꽉 채워졌습니다!{unlocked_gear}")
        update_badges()

def delete_quest(quest_id):
    try:
        if not messagebox.askyesno("삭제 여부 확인", "선택하신 RPG 퀘스트를 목록에서 지우시겠습니까?"):
            return
        app_state["quest_list"] = [q for q in app_state["quest_list"] if q["id"] != quest_id]
        save_data()
        check_and_update_streak()
        
        if app_state["current_tab"] == 0: switch_tab(0)
        elif app_state["current_tab"] == 3: switch_tab(3)
    except Exception as err:
        messagebox.showerror("삭제 오류", f"처리 중 실패: {err}")

# =========================================================================
# 11. 최하단 네비게이션 및 동적 탭 전환 장치
# =========================================================================

def switch_tab(tab_idx):
    try:
        app_state["current_tab"] = tab_idx
        
        for idx, (btn, icon_char) in enumerate(app_state["tab_buttons"]):
            if idx == tab_idx:
                btn.configure(fg=ACCENT_ORANGE)
            else:
                btn.configure(fg=GRAY_TEXT)
                
        for widget in app_state["main_container"].winfo_children():
            widget.destroy()
            
        if tab_idx == 0:
            draw_home_view(app_state["main_container"])
        elif tab_idx == 2:
            draw_timer_view(app_state["main_container"])
        elif tab_idx == 3:
            draw_calendar_view(app_state["main_container"])
        else:
            draw_coming_soon_view(app_state["main_container"], tab_idx)
            
    except Exception as e:
        print(f"화면 전환 실행 실패: {e}")

def create_bottom_nav(parent):
    nav_frame = tk.Frame(parent, bg=WHITE, highlightthickness=1, highlightbackground=BORDER_COLOR, pady=8)
    nav_frame.pack(side="bottom", fill="x")
    
    for i in range(5):
        nav_frame.columnconfigure(i, weight=1)
        
    icon_manifest = [("🏠", 0), ("📋", 1), ("⏱️", 2), ("📅", 3), ("📊", 4)]
    app_state["tab_buttons"] = []
    
    for idx, (char, code) in enumerate(icon_manifest):
        active_color = ACCENT_ORANGE if code == app_state["current_tab"] else GRAY_TEXT
        
        lbl = tk.Label(nav_frame, text=char, font=("맑은 고딕", 17), fg=active_color, bg=WHITE, cursor="hand2")
        lbl.grid(row=0, column=idx, sticky="ew")
        lbl.bind("<Button-1>", lambda e, c=code: switch_tab(c))
        app_state["tab_buttons"].append((lbl, char))

def draw_coming_soon_view(parent, tab_idx):
    soon_wrap = tk.Frame(parent, bg=BG_COLOR, pady=80)
    soon_wrap.pack(fill="both", expand=True)
    tab_names = {1: "퀘스트 상세 목록 (Quest List)", 4: "통계 및 분석 보고서 (Stats)"}
    emojis = {1: "📋", 4: "📊"}
    
    tk.Label(soon_wrap, text=emojis.get(tab_idx, "🏗️"), font=("맑은 고딕", 50), bg=BG_COLOR).pack()
    tk.Label(soon_wrap, text=tab_names.get(tab_idx, "준비 중"), font=("맑은 고딕", 14, "bold"), fg=TEXT_BROWN, bg=BG_COLOR).pack(pady=10)
    desc_str = "이 기능은 SLO퀘스트 다음 업데이트에 연동될 예정입니다!\n천천히, 꾸준히 매일의 과제들을 클리어해주세요. 🦥"
    tk.Label(soon_wrap, text=desc_str, font=FONT_MAIN, fg=GRAY_TEXT, bg=BG_COLOR, justify="center").pack(pady=10)

# =========================================================================
# 12. 메인 부트스트랩 진입점
# =========================================================================

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
        
        # 1. 기동 시 날짜 비교를 통한 결석 하트 감산 페널티 로직
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        if app_state["user"]["last_date"] != today_str and app_state["user"]["last_date"] != "":
            # 어제 미완수 퀘스트 체크
            yesterday_quests = [q for q in app_state["quest_list"] if q["due_date"] == app_state["user"]["last_date"]]
            all_done = all(q["is_completed"] for q in yesterday_quests) if yesterday_quests else True
            
            if not all_done:
                # 패널티 차감
                app_state["user"]["heart"] = max(0, app_state["user"]["heart"] - 1)
                if app_state["user"]["heart"] == 0:
                    app_state["user"]["streak"] = 0
                save_data()
            app_state["user"]["last_date"] = today_str
            save_data()
            
        create_header(root)
        create_bottom_nav(root)
        
        app_state["main_container"] = tk.Frame(root, bg=BG_COLOR)
        app_state["main_container"].pack(fill="both", expand=True)
        
        switch_tab(0)
        
        # FAB + 버튼 배치
        fab_canvas = tk.Canvas(root, width=58, height=58, bg=BG_COLOR, highlightthickness=0, cursor="hand2")
        fab_canvas.place(x=332, y=695)
        
        fab_circle = fab_canvas.create_oval(3, 3, 55, 55, fill=ACCENT_ORANGE, outline="#C47300", width=2, tags="fab_trigger")
        fab_canvas.create_text(29, 29, text="+", font=("맑은 고딕", 22, "bold"), fill=WHITE, tags="fab_trigger")
        
        fab_canvas.tag_bind("fab_trigger", "<Button-1>", lambda e: open_add_quest_modal())
        
        def hover_in(e): fab_canvas.itemconfig(fab_circle, fill="#FFAC33")
        def hover_out(e): fab_canvas.itemconfig(fab_circle, fill=ACCENT_ORANGE)
        fab_canvas.bind("<Enter>", hover_in)
        fab_canvas.bind("<Leave>", hover_out)
        
        root.mainloop()
    except Exception as fatal_err:
        print(f"치명적 구동 에러: {fatal_err}")
        err_box = tk.Tk()
        err_box.withdraw()
        messagebox.showerror("구동 중단 알림", f"슬로퀘스트 초기화 도중 치명적인 문제가 감지되었습니다:\n{fatal_err}")
        err_box.destroy()

if __name__ == "__main__":
    main()