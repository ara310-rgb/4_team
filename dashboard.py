import os
import random
import base64
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup
from streamlit_option_menu import option_menu
from openai import OpenAI
from dotenv import load_dotenv
import runpy
from pathlib import Path
import yfinance as yf


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

NAVER_URL = "https://news.naver.com/breakingnews/section/101/262"


BASE_DIR = Path(__file__).resolve().parent
if "route" not in st.session_state:
    st.session_state.route = "__HOME__"

if "current_page" in st.session_state:
    cp = st.session_state.get("current_page")
    if cp == "dashboard.py":
        st.session_state.route = "__HOME__"
    elif isinstance(cp, str) and cp.endswith(".py"):
        st.session_state.route = cp

if st.session_state.route != "__HOME__":
    target = (BASE_DIR / st.session_state.route).resolve()
    if not target.exists():
        st.error(f"파일을 찾을 수 없습니다: {st.session_state.route}")
        st.session_state.route = "__HOME__"
        st.stop()
    runpy.run_path(str(target), run_name="__main__")
    st.stop()

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "dashboard.py"
PAGES = {
    "junghyun.py": Path(__file__).parent / "junghyun.py",
}
page = st.session_state["current_page"]
if page != "dashboard.py":
    runpy.run_path(str(PAGES[page]), run_name="__main__")
    st.stop()

st.set_page_config(
    page_title="SY Global Connect",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>

/* Streamlit 기본 멀티페이지 네비게이션 제거 */
[data-testid="stSidebarNav"] {
    display: none;
}

.block-container{
  padding: 2rem 8rem 5rem !important;
}

:root{
  --bg:#ffffff;
  --card:#ffffff;
  --line:#e5e7eb;
  --line-2:#d1d5db;
  --soft:#f3f4f6;
  --soft-2:#f8fafc;

  --text:#0f172a;
  --muted:#64748b;

  --accent:#051161;
  --accent-weak: rgba(5,17,97,0.10);
  --accent-weak-2: rgba(5,17,97,0.16);

  --danger:#ef4444;
  --warn:#f59e0b;
}

.main { background: var(--bg); }
[data-testid="stAppViewContainer"] { background: var(--bg); }
[data-testid="stSidebar"] { background: var(--bg); border-right: 1px solid var(--line); }

h1,h2,h3 { color: var(--text); text-shadow: none !important; }
h1 { font-weight: 800; font-size: 2.2rem; margin-bottom: 0.25rem; }
h2 { font-weight: 700; font-size: 1.4rem; }
h3 { font-weight: 650; font-size: 1.1rem; }

.small-muted{ color: var(--muted); font-size: 0.92rem; }

.stButton>button{
  background: var(--accent);
  color: #ffffff;
  border: none;
  border-radius: 12px;
  padding: 10px 14px;
  font-weight: 800;
  box-shadow: none !important;
}
.stButton>button:hover{
  background: rgba(5,17,97,0.65);
  box-shadow: none !important;
}
.stButton>button:active{
  filter: brightness(0.96);
  box-shadow: none !important;
}

[data-testid="stMetric"]{
  background: var(--card);
  border-radius: 14px;
  padding: 14px 16px;
  box-shadow: none !important;
  border: 1px solid var(--line);
}
[data-testid="stMetricValue"]{
  color: var(--text);
  font-weight: 900;
  font-size: 24px;
}
[data-testid="stMetricLabel"]{
  color: var(--muted);
  font-weight: 700;
}

.stProgress > div > div > div > div{
  background: var(--accent) !important;
  box-shadow: none !important;
}
.stProgress > div > div{
  background: var(--soft) !important;
  box-shadow: none !important;
  border-radius: 999px;
}
.stProgress > div{ border-radius: 999px; }

.streamlit-expanderHeader{
  background: var(--card) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
}
.streamlit-expanderHeader:hover{
  border-color: var(--line-2) !important;
  background: var(--soft-2) !important;
}

.logo-box{
  background: rgba(255,255,255,0.6);
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 14px 12px;
  margin-bottom: 10px;
  text-align:center;
}

.logo-img{
  max-width: 150px;
  width: 100%;
  height: auto;
  display:block;
  margin: 0 auto;
}

div[data-testid="stHorizontalBlock"] > div{
  gap: 14px;
}

.login-wrap{
  width: 400px;
  height: 200px;
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px;
  box-sizing: border-box;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.login-title{
  font-size: 16px;
  font-weight: 900;
  color: var(--text);
  margin-bottom: 10px;
}

div[data-testid="stVerticalBlockBorderWrapper"]{
  border-radius: 16px !important;
  border: 1px solid var(--line) !important;
  background: var(--card) !important;
  box-shadow: none !important;
}

.quick-stack{
  display:flex;
  flex-direction:column;
  gap:10px;
}

.quick-stack a.quick-pill{
  display:flex;
  align-items:center;
  justify-content:center;

  width:100%;
  height:54px;

  background:#051161;
  color:#ffffff !important;

  border-radius:16px;
  font-size:17px;
  font-weight:700;
  letter-spacing:-0.2px;

  text-decoration:none !important;
  cursor:pointer;
  transition: all .15s ease;
}

.quick-stack a.quick-pill:hover{
  background: rgba(5,17,97,0.85);
  transform: translateY(-1px);
}

.us-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.us-card:hover {
  border-color: var(--accent);
  box-shadow: 0 4px 12px rgba(5,17,97,0.1);
  transform: translateY(-2px);
}

.us-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  display: block;
}

.us-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent);
  margin-bottom: 12px;
}

.us-content {
  font-size: 1.05rem;
  line-height: 1.8;
  color: var(--text);
  word-break: keep-all;
}

</style>
""",
    unsafe_allow_html=True,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": "https://news.naver.com/",
}


@st.cache_data(ttl=60)
def fetch_headlines(url: str, limit: int = 5):
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    for li in soup.select("li.sa_item"):
        title_node = li.select_one("a.sa_text_title strong.sa_text_strong")
        link_node = li.select_one("a.sa_text_title")
        thumb_img = li.select_one("a.sa_thumb_link img")

        if not title_node or not link_node:
            continue

        title = title_node.get_text(strip=True)

        href = (link_node.get("href") or "").strip()
        if href.startswith("/"):
            href = "https://news.naver.com" + href

        img_url = ""
        if thumb_img:
            img_url = (thumb_img.get("src") or thumb_img.get("data-src") or "").strip()

        items.append({"title": title, "url": href, "img": img_url})
        if len(items) >= limit:
            break

    return items


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def render_naver_ticker(items):
    cards = []
    for it in items:
        img = it.get("img") or ""
        url = it.get("url") or ""
        title = it.get("title") or ""

        thumb_html = ""
        if img:
            thumb_html = f"""
            <div class="thumb-wrap">
              <img src="{esc(img)}" alt="" />
            </div>
            """

        cards.append(
            f"""
        <div class="review-card">
          <a class="headline-link" href="{esc(url)}" target="_blank" rel="noreferrer">
            {thumb_html}
            <div class="text-wrap">
              <div class="review-title">{esc(title)}</div>
              <div class="review-meta">Naver 경제/증권 속보</div>
            </div>
          </a>
        </div>
        """
        )

    track = "".join(cards) * 2

    html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
:root {{
  --accent: #051161;
  --line: #e5e7eb;
  --soft: #f3f4f6;
  --muted: rgba(0,0,0,0.55);
}}

body {{
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

.review-ticker-wrap {{
  width: 100%;
  overflow: hidden;
  border-radius: 16px;
  background: rgba(255,255,255,0.95);
  border: none;
  box-shadow: none;
  padding: 14px 10px 18px;
  box-sizing: border-box;
}}

.review-ticker-track {{
  display: flex;
  gap: 14px;
  width: max-content;
  animation: tickerMove 28s linear infinite;
  align-items: stretch;
  will-change: transform;
  transform: translateZ(0);
}}

.review-ticker-wrap:hover .review-ticker-track {{
  animation-play-state: paused;
}}

.review-card {{
  width: 450px;
  flex: 0 0 auto;
  border-radius: 14px;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.10);
  box-shadow: none;
  overflow: hidden;
  box-sizing: border-box;
}}

.headline-link {{
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 14px;
  text-decoration: none;
  color: inherit;
  box-sizing: border-box;
}}

.headline-link:hover {{
  background: rgba(5,17,97,0.06);
}}

.thumb-wrap {{
  width: 110px;
  height: 75px;
  flex-shrink: 0;
  border-radius: 12px;
  overflow: hidden;
  background: var(--soft);
}}

.thumb-wrap img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}}

.text-wrap {{
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}}

.review-title {{
  font-size: 14px;
  font-weight: 800;
  line-height: 1.45;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: keep-all;
  overflow-wrap: break-word;
}}

.headline-link:hover .review-title {{
  color: var(--accent);
  text-decoration: underline;
}}

.review-meta {{
  font-size: 12px;
  color: var(--muted);
}}

@keyframes tickerMove {{
  0% {{ transform: translateX(-50%); }}
  100% {{ transform: translateX(0); }}
}}
</style>
</head>
<body>
  <div class="review-ticker-wrap">
    <div class="review-ticker-track">
      {track}
    </div>
  </div>
</body>
</html>
"""
    st.components.v1.html(html, height=130, scrolling=False)


def init_chat_state(
    greeting: str = "안녕하세요! 무역 전문 AI 챗봇입니다. HS 코드, 관세, 통관 규정에 대해 무엇이든 물어보세요!"
) -> None:
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [{"role": "assistant", "content": greeting}]
    if "chat_draft" not in st.session_state:
        st.session_state.chat_draft = ""


def get_openai_response(user_text: str, system_message: str) -> str:
    if client is None:
        return "OPENAI_API_KEY가 없습니다. .env 또는 시스템 환경변수에 OPENAI_API_KEY를 설정해주세요."
    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_text},
            ],
            temperature=0.2,
        )
        return (r.choices[0].message.content or "").strip()
    except Exception as e:
        return f"AI 호출 오류: {e}"


def render_chat_widget(
    get_openai_response_fn,
    title: str = "💬 AI 챗봇",
    header: str = "#### 💬 AI 무역 챗봇",
    caption: str = "HS 코드, 관세, 통관 규정 질문을 입력하세요.",
    placeholder: str = "예: HS 3304 미국 수입 관세가 궁금해요",
    system_message: str = (
        "당신은 국제 무역과 관세 전문가입니다. "
        "HS 코드, 통관 규정, 필요 서류, 관세율에 대해 정확하고 상세한 답변을 한국어로 제공합니다."
    ),
    popover_width: str = "stretch",
) -> None:
    key_prefix = "chat_widget"
    draft_key = f"{key_prefix}_draft"
    send_key = f"{key_prefix}_send"
    reset_key = f"{key_prefix}_reset"

    with st.popover(title, width=popover_width):
        st.markdown(header)
        st.caption(caption)

        chat_box = st.container(height=200, border=True)
        with chat_box:
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        st.session_state.chat_draft = st.text_input(
            "질문 입력",
            value=st.session_state.chat_draft,
            placeholder=placeholder,
            key=draft_key,
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button("전송", key=send_key, use_container_width=True):
                user_text = (st.session_state.chat_draft or "").strip()
                if user_text:
                    st.session_state.chat_messages.append({"role": "user", "content": user_text})
                    with st.spinner("AI가 답변을 생성 중입니다..."):
                        resp = get_openai_response_fn(user_text, system_message)
                    st.session_state.chat_messages.append({"role": "assistant", "content": resp})
                    st.session_state.chat_draft = ""
                    st.rerun()

        with c2:
            if st.button("대화 초기화", key=reset_key, use_container_width=True):
                first_msg = "안녕하세요!"
                if st.session_state.chat_messages:
                    first_msg = st.session_state.chat_messages[0].get("content", first_msg)
                st.session_state.chat_messages = [{"role": "assistant", "content": first_msg}]
                st.session_state.chat_draft = ""
                st.rerun()


def init_exchange_state(default_rate: float = 1320.0):
    """환율 계산기 세션 상태 초기화"""
    if "exchange_rate" not in st.session_state:
        st.session_state.exchange_rate = default_rate
    if "selected_currency" not in st.session_state:
        st.session_state.selected_currency = "USD"
    if "last_fetch_time" not in st.session_state:
        st.session_state.last_fetch_time = None


def get_live_exchange_rate(currency_code: str) -> float:
    """실시간 환율 가져오기"""
    ticker_map = {
        "USD": "USDKRW=X",
        "JPY": "JPYKRW=X", 
        "EUR": "EURKRW=X",
        "CNY": "CNYKRW=X",
        "GBP": "GBPKRW=X",
        "AUD": "AUDKRW=X",
        "CAD": "CADKRW=X"
    }
    
    ticker = ticker_map.get(currency_code, "USDKRW=X")
    
    try:
        data = yf.download(ticker, period="1d", interval="1d", progress=False)
        if not data.empty:
            rate = float(data['Close'].iloc[-1])
            return rate * 100 if currency_code == "JPY" else rate
        return None
    except:
        return None


def render_exchange_widget(
    title: str = "💵 환율",
    popover_width: str = "stretch"
) -> None:
    """Popover 형태의 환율 계산기 위젯 렌더링"""
    
    key_prefix = "ex_widget"
    
    with st.popover(title, width=popover_width):
        header_col1, header_col2 = st.columns([3, 1])
        
        with header_col1:
            st.markdown("#### 💵 실시간 환율 계산기")
        
        with header_col2:
            if st.button("🔄", key=f"{key_prefix}_refresh", help="환율 새로고침"):
                selected = st.session_state.selected_currency
                new_rate = get_live_exchange_rate(selected)
                
                if new_rate:
                    st.session_state.exchange_rate = new_rate
                    st.session_state.last_fetch_time = pd.Timestamp.now()
                    st.success("✅ 최신 환율 반영!")
                    st.rerun()
                else:
                    st.error("환율 조회 실패")
        
        st.caption("yfinance 기반 실시간 환율")
        
        currency_options = {
            "USD (미국 달러)": "USD",
            "JPY (일본 엔 - 100엔)": "JPY",
            "EUR (유로)": "EUR",
            "CNY (중국 위안)": "CNY",
            "GBP (영국 파운드)": "GBP",
            "AUD (호주 달러)": "AUD",
            "CAD (캐나다 달러)": "CAD"
        }
        
        selected_label = st.selectbox(
            "통화 선택",
            options=list(currency_options.keys()),
            key=f"{key_prefix}_currency",
            index=list(currency_options.values()).index(st.session_state.selected_currency)
        )
        
        selected_currency = currency_options[selected_label]
        
        if selected_currency != st.session_state.selected_currency:
            st.session_state.selected_currency = selected_currency
            new_rate = get_live_exchange_rate(selected_currency)
            if new_rate:
                st.session_state.exchange_rate = new_rate
                st.session_state.last_fetch_time = pd.Timestamp.now()
                st.rerun()
        
        rate = st.session_state.exchange_rate
        
        rate_unit = "100엔" if selected_currency == "JPY" else f"1 {selected_currency}"
        st.metric("적용 환율", f"{rate:,.2f} KRW / {rate_unit}")
        
        if st.session_state.last_fetch_time:
            time_diff = pd.Timestamp.now() - st.session_state.last_fetch_time
            minutes_ago = int(time_diff.total_seconds() / 60)
            st.caption(f"🕐 {minutes_ago}분 전 업데이트")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            foreign_val = st.number_input(
                f"입력 ({selected_currency})", 
                min_value=0.0, 
                format="%.2f",
                key=f"{key_prefix}_foreign"
            )
            
        with col2:
            krw_result = foreign_val * rate
            st.metric("변환 결과", f"{krw_result:,.0f} 원")

        st.info(f"💡 {rate_unit} = {rate:,.2f} KRW")
        
        if st.button("계산 초기화", key=f"{key_prefix}_reset", use_container_width=True):
            st.rerun()


def ensure_user_store():
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", "users.csv")
    if not os.path.exists(path):
        pd.DataFrame(columns=["user_id", "email", "password"]).to_csv(path, index=False, encoding="utf-8-sig")
    return path


def upsert_user(user_id: str, email: str, password: str):
    path = ensure_user_store()
    df = pd.read_csv(path, dtype=str).fillna("")
    user_id = (user_id or "").strip()
    email = (email or "").strip()
    password = (password or "").strip()

    if user_id in df["user_id"].values:
        df.loc[df["user_id"] == user_id, ["email", "password"]] = [email, password]
    else:
        df = pd.concat(
            [df, pd.DataFrame([{"user_id": user_id, "email": email, "password": password}])],
            ignore_index=True,
        )

    df.to_csv(path, index=False, encoding="utf-8-sig")
    st.session_state.users_df = df


def render_login_page():
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"
    if "users_df" not in st.session_state:
        path = ensure_user_store()
        st.session_state.users_df = pd.read_csv(path, dtype=str).fillna("")
    if "nav" not in st.session_state:
        st.session_state.nav = "Home"

    st.markdown("<br>", unsafe_allow_html=True)

    left, mid, right = st.columns([2, 3, 2])

    with mid:
        box = st.container(height=270, border=True)

        with box:
            if st.session_state.auth_view == "login":
                st.markdown("#### 🔐 Login")

                with st.form("login_form", clear_on_submit=False):
                    user_id = st.text_input("아이디", placeholder="예) kita123", label_visibility="collapsed")
                    user_pw = st.text_input(
                        "비밀번호",
                        type="password",
                        placeholder="********",
                        label_visibility="collapsed",
                    )

                    b1, b2 = st.columns(2)
                    with b1:
                        login_clicked = st.form_submit_button("로그인", use_container_width=True)
                    with b2:
                        signup_clicked = st.form_submit_button("회원가입", use_container_width=True)

                if signup_clicked:
                    st.session_state.auth_view = "signup"
                    st.rerun()

                if login_clicked:
                    user_id = (user_id or "").strip()
                    user_pw = (user_pw or "").strip()

                    if not user_id or not user_pw:
                        st.error("아이디/비밀번호를 입력하세요.")
                    else:
                        df = st.session_state.users_df
                        ok = False
                        if len(df) > 0:
                            hit = df[(df["user_id"] == user_id) & (df["password"] == user_pw)]
                            ok = len(hit) > 0

                        if ok:
                            st.session_state.auth_user = user_id
                            st.session_state.nav = "Home"
                            st.rerun()
                        else:
                            st.error("가입된 정보가 없거나 비밀번호가 일치하지 않습니다.")
            else:
                st.markdown("#### 🧾 회원가입")

                with st.form("signup_form", clear_on_submit=False):
                    new_id = st.text_input("아이디", placeholder="아이디", label_visibility="collapsed")
                    new_email = st.text_input("이메일", placeholder="이메일", label_visibility="collapsed")
                    new_pw = st.text_input("비밀번호", type="password", placeholder="비밀번호", label_visibility="collapsed")

                    b1, b2 = st.columns(2)
                    with b1:
                        submit_signup = st.form_submit_button("가입 완료", use_container_width=True)
                    with b2:
                        back_login = st.form_submit_button("로그인으로", use_container_width=True)

                if back_login:
                    st.session_state.auth_view = "login"
                    st.rerun()

                if submit_signup:
                    new_id = (new_id or "").strip()
                    new_email = (new_email or "").strip()
                    new_pw = (new_pw or "").strip()

                    if not new_id or not new_email or not new_pw:
                        st.error("아이디/이메일/비밀번호를 모두 입력하세요.")
                    elif "@" not in new_email or "." not in new_email:
                        st.error("이메일 형식이 올바르지 않습니다.")
                    else:
                        upsert_user(new_id, new_email, new_pw)
                        st.success("회원가입 완료! 로그인 화면으로 이동합니다.")
                        st.session_state.auth_view = "login"
                        st.rerun()


if 'tasks' not in st.session_state:
    st.session_state.tasks = pd.DataFrame([
        {"카테고리": "📝 수출 서류 준비", "항목": "인보이스 작성", "완료": True},
        {"카테고리": "🚢 물류 처리", "항목": "포워더 예약", "완료": False},
        {"카테고리": "💼 바이어 매칭", "항목": "바이어 리스트 작성", "완료": False},
    ])


def get_prog(cat_name):
    subset = st.session_state.tasks[st.session_state.tasks["카테고리"] == cat_name]
    if len(subset) == 0:
        return 0.0
    return len(subset[subset["완료"] == True]) / len(subset)


def render_task_page():
    col1, col2, col3 = st.columns(3)

    with col1:
        p1 = get_prog("📝 수출 서류 준비")
        st.metric("📝 수출 서류 준비", f"{int(p1*100)}%")
        st.progress(p1)

    with col2:
        p2 = get_prog("🚢 물류 처리")
        st.metric("🚢 물류 처리", f"{int(p2*100)}%")
        st.progress(p2)

    with col3:
        p3 = get_prog("💼 바이어 매칭")
        st.metric("💼 바이어 매칭", f"{int(p3*100)}%")
        st.progress(p3)

    st.markdown("---")

    st.subheader("업무 목록 편집")
    edited_df = st.data_editor(
        st.session_state.tasks,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "완료": st.column_config.CheckboxColumn("완료 여부"),
            "카테고리": st.column_config.SelectboxColumn(
                "카테고리 지정", 
                options=["📝 수출 서류 준비", "🚢 물류 처리", "💼 바이어 매칭"]
            )
        },
        key="task_editor"
    )

    if st.button("💾 변경사항 저장", use_container_width=True, key="save_task_btn"):
        st.session_state.tasks = edited_df
        st.success("✅ 데이터가 저장되었습니다!")
        st.rerun()


def render_us_page():
    st.markdown(
        """
        <div class="us-card">
            <span class="us-icon">🏢</span>
            <div class="us-title">회사 소개</div>
            <div class="us-content">
                세연글로벌커넥트는 AI 기술을 기반으로 글로벌 무역 데이터를 분석하여<br> 해외 시장 진출을 지원하는 무역 인텔리전스 기업입니다.<br>
                전문가의 도움 없이도 신뢰도 높은 해외 시장 분석과 의사결정을 가능하게 합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div class="us-card">
            <span class="us-icon">💼</span>
            <div class="us-title">솔루션 소개</div>
            <div class="us-content">
                세연글로벌커넥트는 관세청 및 세관 신고 데이터를 연동하여 1,000만 개 이상의 기업 수출입 정보를 분석합니다.<br>
                해외 바이어 발굴, 경쟁사 거래 분석, 시장 동향 파악까지 하나의 플랫폼에서 제공합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div class="us-card">
            <span class="us-icon">🤖</span>
            <div class="us-title">AI 마케팅 자동화</div>
            <div class="us-content">
                세연글로벌커넥트의 AI 분석 시스템은 4억 건 이상의 무역 데이터를 실시간으로 처리합니다.<br>
                이를 통해 맞춤형 해외 시장 조사와 빠른 글로벌 마케팅 전략 수립을 자동화합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.subheader("Contact")
    contact_col1, contact_col2, contact_col3 = st.columns(3)
    
    with contact_col1:
        st.metric("Email", "contact@syglobal.com")
    
    with contact_col2:
        st.metric("Phone", "+82-2-1234-5678")
    
    with contact_col3:
        st.metric("Address", "서울특별시 강남구")


init_chat_state()
init_exchange_state()

header_left, header_right = st.columns([7, 3])

with header_left:
    st.title("세연 글로벌 커넥트")
    st.markdown(
        '<div class="small-muted">무역 서류, 마케팅, 환율까지 관리하는 올인원 서비스</div>',
        unsafe_allow_html=True,
    )

with header_right:
    b1, b2 = st.columns(2)
    with b1:
        render_exchange_widget(
            title="**💵 환율**",
            popover_width="stretch"
        )
    with b2:
        render_chat_widget(
            get_openai_response_fn=get_openai_response,
            title="**💬 챗봇**",
            popover_width="stretch",
        )

if "nav" not in st.session_state:
    st.session_state.nav = "Home"

menu_items = ["Home", "Task", "With Us", "Settings"]
menu_icons = ["house-fill", "list-task", "palette-fill", "gear-fill"]

selected = option_menu(
    menu_title=None,
    options=menu_items,
    icons=menu_icons,
    menu_icon="cast",
    default_index=menu_items.index(st.session_state.nav),
    orientation="horizontal",
    key="top_nav",
    styles={
        "container": {
            "padding": "4px!important",
            "background": "#ffffff",
            "border-radius": "16px",
        },
        "icon": {"color": "#051161", "font-size": "20px"},
        "nav-link": {
            "font-size": "15px",
            "text-align": "center",
            "margin": "4px",
            "padding": "10px 14px",
            "border-radius": "12px",
            "color": "#0f172a",
            "font-weight": "650",
            "background": "#ffffff",
            "border": "1px solid #e5e7eb",
        },
        "nav-link-selected": {
            "background": "rgba(5,17,97,0.10)",
            "color": "#051161",
            "font-weight": "850",
            "border": "1px solid #051161",
        },
    },
)
st.session_state.nav = selected

with st.sidebar:
    with st.expander("1) 해외진출 전략 허브", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("시장동향", use_container_width=True, key="nav_cn_1"):
                st.switch_page("pages/macro_1.py")
        with col2:
            if st.button("전략분석", use_container_width=True, key="nav_cn_2"):
                st.switch_page("pages/micro_1.py")
        with col3:
            if st.button("규제진단", use_container_width=True, key="nav_cn_3"):
                st.switch_page("pages/mac_mic_1.py")

    with st.expander("2) SEO 서비스", expanded=False):
        if st.button("바로가기", use_container_width=True, key="nav_news"):
            st.switch_page("pages/junghyun.py")

    with st.expander("3) AI 바이어 매칭 서비스", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("바이어 찾기", use_container_width=True, key="nav_ai_1"):
                st.switch_page("pages/03_ai_chatbot.py")
        with col2:
            if st.button("전시회 일정", use_container_width=True, key="nav_ai_2"):
                st.switch_page("pages/buyer_maps.py")

    with st.expander("4) 환율 정보 확인", expanded=False):
        if st.button("바로가기", use_container_width=True, key="nav_ex"):
            st.switch_page("pages/exchange_rate.py")

    with st.expander("5) 무역 서류 자동 완성", expanded=False):
        if st.button("바로가기", use_container_width=True, key="nav_fx"):
            st.switch_page("pages/auto_docs.py")

    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        try:
            logo_b64 = base64.b64encode(open(logo_path, "rb").read()).decode()
            st.markdown(
                f"""
                <div class="logo-box">
                  <img class="logo-img" src="data:image/png;base64,{logo_b64}" alt="logo"/>
                  <div class="small-muted" style="margin-top:8px; text-align:center;">
                    KITA AX MASTER TEAM4
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"로고 로드 실패: {e}")
    else:
        st.markdown(
            """
            <div class="logo-box">
              <div style="font-size:1.15rem; font-weight:900; color:#0f172a;">🚀 SY Global Connect</div>
              <div class="small-muted" style="margin-top:6px;">KITA AX MASTER TEAM4</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

if selected == "Task":
    render_task_page()
    st.stop()

if selected == "With Us":
    render_us_page()
    st.stop()

if selected == "Settings":
    render_login_page()
    st.stop()

st.markdown("<br>", unsafe_allow_html=True)

with st.container():
    items = fetch_headlines(NAVER_URL, 5)
    if not items:
        items = [{"title": "헤드라인을 불러오지 못했습니다.", "url": NAVER_URL, "img": ""}]
    render_naver_ticker(items)

st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("#### 📝 수출 서류 준비")
    progress1 = get_prog("📝 수출 서류 준비")
    st.progress(progress1)
    st.metric("진행률", f"{int(progress1*100)}%")

with c2:
    st.markdown("#### 🚢 물류 처리")
    progress2 = get_prog("🚢 물류 처리")
    st.progress(progress2)
    st.metric("진행률", f"{int(progress2*100)}%")

with c3:
    st.markdown("#### 💼 바이어 매칭")
    progress3 = get_prog("💼 바이어 매칭")
    st.progress(progress3)
    st.metric("진행률", f"{int(progress3*100)}%")

with c4:
    st.markdown(
        """
        <div class="quick-stack">
          <a class="quick-pill" href="https://www.smes.go.kr/exportcenter/" target="_blank" rel="noreferrer">
            수출지원센터
          </a>
          <a class="quick-pill" href="https://tradetestingteam4.streamlit.app/" target="_blank" rel="noreferrer">
            수출역량진단 테스트
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
st.markdown("""
<div style='text-align: center; color: #718096; font-size: 0.9em;'>
    <p>Global E-commerce All In One Solution</p>
    <p>Developed by Seyeon Global Connect</p>
</div>
""", unsafe_allow_html=True)