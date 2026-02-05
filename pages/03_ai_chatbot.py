import streamlit as st
import pandas as pd
import unicodedata
import glob
import csv
import re
import base64
from io import StringIO
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os

# ==================== 환경 변수 & OpenAI 초기화 ====================
load_dotenv()

try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_api_key) if openai_api_key else None
except Exception:
    client = None

# ==================== Streamlit 기본 설정 ====================
st.set_page_config(
    page_title="AI 바이어 매칭 & 이메일 생성",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== CSS ====================
st.markdown("""
<style>
/* Streamlit 기본 멀티페이지 네비게이션 제거 */
[data-testid="stSidebarNav"] {
    display: none;
}

/* ── 색상 변수 ── */
:root {
  --bg:            #ffffff;
  --card:          #ffffff;
  --line:          #e2e8f0;
  --text:          #0f172a;
  --muted:         #64748b;
  --indigo:        #051161;          /* 메인 액센트 변경 */
  --indigo-hover:  rgba(5,17,97,0.85);
  --indigo-light:  #eef2ff;
  --indigo-border: #a5b4fc;
  --danger:        #ef4444;
}

/* ── 앱 배경 ── */
.main,
[data-testid="stAppViewContainer"] { background: var(--bg); }

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
  background: var(--bg);
  border-right: 1px solid var(--line);
}

/* ── 타이포그래피 ── */
h1 {
  font-weight: 900 !important;
  font-size: 2.65rem !important;
  line-height: 1.12 !important;
  color: var(--text);
  margin: 0.2rem 0 0.35rem 0 !important;
}
h2 { font-weight: 800; font-size: 1.45rem !important; color: var(--text); }
h3 { font-weight: 700; font-size: 1.08rem !important; color: var(--text); }

/* ── 사이드바 로고 박스 ── */
.logo-box {
  background: rgba(255,255,255,0.6);
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 14px 12px;
  margin-bottom: 10px;
  text-align:center;
}
.logo-img {
  max-width: 150px;
  width: 100%;
  height: auto;
  display:block;
  margin: 0 auto;
}
.small-muted {
  color:#64748b;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.2px;
}

/* ── 사이드바 nav expander ── */
[data-testid="stSidebar"] .streamlit-expanderHeader {
  background: var(--card) !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
  font-weight: 650 !important;
  font-size: 0.93rem !important;
}

/* ── 페이지 헤더: 박스/테두리/그림자 제거 ── */
.page-header {
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  padding: 0 !important;
  margin-top: 0.35rem !important;
  margin-bottom: 1.1rem !important;
  box-shadow: none !important;
}
.page-header .sub {
  color: var(--muted);
  font-size: 1.02rem;
  font-weight: 600;
  margin-top: 6px;
}

/* ── 버튼: 기본(인디고) ── */
.stButton > button {
  background: var(--indigo) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px;
  padding: 9px 16px;
  font-weight: 700;
  font-size: 0.92rem;
  box-shadow: 0 2px 6px rgba(5,17,97,.3) !important;
  transition: background .15s;
}
.stButton > button:hover {
  background: var(--indigo-hover) !important;
}

/* ── 사이드바 내 버튼은 좀 더 작게 ── */
[data-testid="stSidebar"] .stButton > button {
  padding: 7px 12px;
  font-size: 0.88rem;
  box-shadow: 0 1px 3px rgba(5,17,97,.2) !important;
}

/* ── 로딩 완료 배지 (인디고) ── */
.loading-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--indigo-light);
  border: 1px solid var(--indigo-border);
  border-radius: 12px;
  padding: 10px 16px;
  margin-bottom: 1rem;
}
.loading-badge .icon { font-size: 1.2rem; }
.loading-badge .txt { font-size: 0.92rem; color: var(--indigo); font-weight: 650; }

/* ── 결과 카드 (expander) ── */
.streamlit-expanderHeader {
  background: var(--card) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  font-weight: 650 !important;
}

/* ── 배지 ── */
.badge-ok {
  display: inline-block;
  background: var(--indigo-light);
  color: var(--indigo);
  font-size: 0.78rem;
  font-weight: 700;
  padding: 2px 10px;
  border-radius: 999px;
}
.badge-warn {
  display: inline-block;
  background: #fef3c7;
  color: #92400e;
  font-size: 0.78rem;
  font-weight: 700;
  padding: 2px 10px;
  border-radius: 999px;
}

/* ── form 내 submit 버튼도 인디고 ── */
[data-testid="stForm"] {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
  padding: 0 !important;
}
.stFormSubmitButton > button {
  background: var(--indigo) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px;
  font-weight: 700;
  box-shadow: 0 2px 6px rgba(5,17,97,.3) !important;
  transition: background .15s;
}
.stFormSubmitButton > button:hover {
  background: var(--indigo-hover) !important;
}

/* ── 메인 콘텐츠 패딩 ── */
.block-container { padding: 3.2rem 2.5rem 4rem !important; }
</style>
""", unsafe_allow_html=True)


# ==================== 상수: 국가 옵션 ====================
COUNTRY_OPTIONS = [
    "United States", "Canada", "Mexico",
    "Brazil", "Argentina", "Chile",
    "United Kingdom", "Germany", "France", "Italy", "Spain", "Netherlands",
    "Sweden", "Norway", "Denmark", "Poland",
    "Turkey", "Russia",
    "United Arab Emirates", "Saudi Arabia", "Qatar", "Kuwait",
    "South Africa", "Egypt", "Nigeria",
    "China", "Japan", "South Korea", "Taiwan", "Hong Kong",
    "Singapore", "Malaysia", "Thailand", "Vietnam", "Indonesia", "Philippines", "India",
    "Australia", "New Zealand",
]

# ==================== 상수: CSV 파일명 매핑 ====================
CSV_BUYER_FILES = {
    "KOTRA_해외바이어현황_20240829":           "대한무역투자진흥공사_해외바이어 현황_20240829.csv",
    "중진공_해외바이어구매오퍼_20241231":       "중소벤처기업진흥공단_해외바이어 구매오퍼 정보_20241231.csv",
    "중진공_해외바이어인콰이어리_20241230":     "중소벤처기업진흥공단_해외바이어 인콰이어리 신청_20241230.csv",
    "무보_화장품바이어_20200812":              "한국무역보험공사_화장품 바이어 정보_20200812.csv",
    "중진공_고비즈코리아거래처_20250523":       "중소벤처기업진흥공단_고비즈코리아 거래처정보_20250523.csv",
}

# ==================== 상수: 산업 키워드 매핑 ====================
INDUSTRY_KEYWORDS = {
    "화장품/뷰티": [
        "cosmetics", "beauty", "skincare", "skin care", "makeup", "personal care",
        "lotion", "cream", "serum", "toner", "cleanser", "sunscreen", "mask", "fragrance",
        "k-beauty", "kbeauty",
    ],
    "전자제품": [
        "electronics", "electronic", "device", "gadget", "semiconductor", "chip",
        "display", "battery", "charger", "adapter", "smart", "iot", "sensor", "led",
    ],
    "식품": [
        "food", "beverage", "snack", "drink", "coffee", "tea", "sauce",
        "noodle", "ramen", "instant", "frozen", "seafood", "meat", "fruit",
    ],
    "섬유/의류": [
        "apparel", "clothing", "garment", "textile", "fabric", "fashion",
        "yarn", "cotton", "polyester", "knit", "denim", "outerwear", "sportswear",
    ],
    "자동차 부품": [
        "auto", "automotive", "car", "vehicle", "spare parts", "parts",
        "engine", "brake", "filter", "tire", "tyre", "transmission", "sensor",
    ],
    "기계/설비": [
        "machinery", "equipment", "industrial", "manufacturing", "factory",
        "pump", "valve", "compressor", "tool", "robot", "automation", "cnc",
    ],
    "의료기기": [
        "medical", "healthcare", "diagnostic", "surgical", "hospital",
        "clinic", "monitor", "disposable", "sterile",
    ],
    "기타": ["import", "export", "trade", "sourcing", "procurement"],
}

# ==================== 소스별 가중치 ====================
SOURCE_WEIGHT = {
    "중진공_해외바이어구매오퍼_20241231":   6,
    "중진공_해외바이어인콰이어리_20241230": 6,
    "무보_화장품바이어_20200812":          8,
    "중진공_고비즈코리아거래처_20250523":   2,
    "KOTRA_해외바이어현황_20240829":       -5,
}

# ============================================================
# OpenAI 호출
# ============================================================
def get_openai_response(prompt: str, system_message: str = "당신은 무역 전문가입니다.") -> str:
    if not client:
        return "⚠️ OpenAI API가 설정되지 않았습니다. .env에 OPENAI_API_KEY를 확인하세요."
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.7,
            max_tokens=900,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ API 오류: {e}"


# ============================================================
# AI 이메일 생성 / 번역
# ============================================================
def generate_buyer_email(
    buyer_name: str,
    country: str,
    industry: str,
    purchase_history: list[str],
    contact_person: str | None = None,
    email: str | None = None,
) -> str:
    prompt = f"""
다음 바이어에게 보낼 비즈니스 이메일을 한국어로 작성해주세요.

- 회사명: {buyer_name}
- 국가: {country}
- 산업: {industry}
- 관심 제품/범주: {', '.join(purchase_history)}
- 담당자(알려진 경우): {contact_person or '미확인'}
- 이메일(알려진 경우): {email or '미확인'}

**중요**: 이메일 본문에서 반드시 "{buyer_name}" 회사명을 명시적으로 언급해주세요.
한국 제품 수출 업체로서 파트너십을 제안하는 전문적이고 간결한 이메일을 작성해주세요.
제목과 본문을 포함해주세요.
"""
    return get_openai_response(prompt, "당신은 국제 비즈니스 커뮤니케이션 전문가입니다.")


def translate_email(email_content: str, target_language: str) -> str:
    prompt = f"""
다음 이메일을 {target_language}로 번역해주세요.
비즈니스 이메일 톤을 유지하세요.

{email_content}
"""
    return get_openai_response(prompt, "당신은 전문 비즈니스 번역가입니다.")


# ============================================================
# CSV 로딩 & 정규화 유틸리티
# ============================================================
def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def _find_local_csv_by_name(filename: str) -> str | None:
    target = _nfc(filename)
    candidates = [
        Path.cwd() / filename,
        Path.cwd() / "data" / filename,
        Path.cwd() / "datasets" / filename,
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    for p in glob.glob("**/*.csv", recursive=True):
        if _nfc(Path(p).name) == target:
            return str(Path(p))
    return None


def _read_csv_bytes_flexible(raw: bytes) -> tuple[pd.DataFrame, str, str]:
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    text, used_enc = None, None
    for enc in encodings:
        try:
            text     = raw.decode(enc)
            used_enc = enc
            break
        except Exception:
            continue
    if text is None:
        text     = raw.decode("cp949", errors="replace")
        used_enc = "cp949(errors=replace)"

    sample = text[:5000]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
        sep = dialect.delimiter
    except Exception:
        sep = ","

    df = pd.read_csv(StringIO(text), sep=sep, engine="python", on_bad_lines="skip")
    if df.shape[1] == 1:
        for alt in [",", ";", "\t", "|"]:
            if alt == sep:
                continue
            df2 = pd.read_csv(StringIO(text), sep=alt, engine="python", on_bad_lines="skip")
            if df2.shape[1] > 1:
                df, sep = df2, alt
                break
    return df, used_enc, sep


def _read_csv_flexible_from_path(path: str) -> tuple[pd.DataFrame, str, str]:
    return _read_csv_bytes_flexible(Path(path).read_bytes())


def _norm_col(s: str) -> str:
    s = re.sub(r"\s+", "", str(s).strip().lower())
    return s.replace("-", "").replace("_", "")


def _infer_col(cols: list[str], keywords: list[str]) -> str | None:
    normed = {c: _norm_col(c) for c in cols}
    for c, nc in normed.items():
        for kw in keywords:
            if kw in nc:
                return c
    return None


def _safe_get(row, col) -> str:
    if not col:
        return ""
    v = row.get(col)
    return "" if pd.isna(v) else str(v).strip()


def _parse_date_any(x: str):
    if not x:
        return None
    for fmt in ["%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d", "%Y%m%d", "%Y-%m", "%Y.%m", "%Y/%m"]:
        try:
            return datetime.strptime(str(x).strip(), fmt)
        except Exception:
            continue
    return None


def _guess_country_from_text(text: str) -> str:
    t = (text or "").lower()
    if not t:
        return ""
    hints = {
        "united states": "United States", "usa": "United States", "u.s.": "United States",
        "canada": "Canada", "japan": "Japan",
        "korea": "South Korea", "republic of korea": "South Korea",
        "china": "China", "vietnam": "Vietnam", "singapore": "Singapore",
        "hong kong": "Hong Kong", "taiwan": "Taiwan",
        "uk": "United Kingdom", "united kingdom": "United Kingdom",
        "germany": "Germany", "france": "France", "italy": "Italy", "spain": "Spain",
        "australia": "Australia", "india": "India",
        "u.a.e": "United Arab Emirates", "uae": "United Arab Emirates",
        "saudi": "Saudi Arabia",
    }
    for k, v in hints.items():
        if k in t:
            return v
    return ""


@st.cache_data(ttl=3600)
def load_and_standardize_buyer_csv(resolved_paths: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, meta = [], []
    for source_name, path in resolved_paths.items():
        if not path:
            meta.append({"source": source_name, "status": "missing", "detail": "path not resolved"})
            continue
        try:
            df, enc, sep = _read_csv_flexible_from_path(path)
        except Exception as e:
            meta.append({"source": source_name, "status": "fail", "detail": str(e)})
            continue

        cols = list(df.columns)
        col_company  = _infer_col(cols, ["상호명", "회사", "기업", "업체", "buyer", "company", "corporation", "기관명", "조직"])
        col_title    = _infer_col(cols, ["제목", "title"])
        col_item     = _infer_col(cols, ["품목명", "품목", "제품", "item", "product", "카테고리", "category", "오퍼", "inquiry"])
        col_country  = _infer_col(cols, ["국가명", "국가", "country", "nation", "소재국", "거주국"])
        col_city     = _infer_col(cols, ["도시", "city", "영문도시", "영문시군구", "시군구", "소재지"])
        col_hs       = _infer_col(cols, ["hs", "hscode", "hs코드", "품목코드", "세번"])
        col_name     = _infer_col(cols, ["담당자", "contact", "name", "성명", "대표자"])
        col_email    = _infer_col(cols, ["이메일", "email", "e-mail", "메일"])
        col_phone    = _infer_col(cols, ["전화", "phone", "tel", "연락처", "mobile", "핸드폰"])
        col_web      = _infer_col(cols, ["웹", "홈페이지", "website", "url", "domain", "사이트"])
        col_addr     = _infer_col(cols, ["주소", "기본주소", "address"])
        col_date     = _infer_col(cols, ["상담일", "신청시작일", "신청종료일", "등록", "신청", "일자", "날짜", "date", "created", "updated"])

        for _, r in df.iterrows():
            company = _safe_get(r, col_company)
            title   = _safe_get(r, col_title)
            item    = _safe_get(r, col_item)
            if not company:
                company = (f"Inquiry/Offer: {title or item}") if (title or item) else "Unknown Company"

            country  = _safe_get(r, col_country)
            addr     = _safe_get(r, col_addr)
            website  = _safe_get(r, col_web)
            email_v  = _safe_get(r, col_email)
            if not country:
                country = _guess_country_from_text(addr) or _guess_country_from_text(website) or _guess_country_from_text(email_v)

            rows.append({
                "company_name":   company,
                "country":        country,
                "city":           _safe_get(r, col_city),
                "product_text":   " ".join(x for x in [item, title] if x),
                "hs_code":        _safe_get(r, col_hs),
                "contact_person": _safe_get(r, col_name),
                "email":          email_v,
                "phone":          _safe_get(r, col_phone),
                "website":        website,
                "address":        addr,
                "date":           _parse_date_any(_safe_get(r, col_date)),
                "date_raw":       _safe_get(r, col_date),
                "source":         source_name,
            })
        meta.append({"source": source_name, "status": "ok", "rows": len(df), "cols": len(cols), "encoding": enc, "sep": sep, "path": path})

    df_all  = pd.DataFrame(rows)
    df_meta = pd.DataFrame(meta)
    if not df_all.empty:
        for c in ["company_name", "country", "city", "product_text", "hs_code",
                  "contact_person", "email", "phone", "website", "address", "date_raw", "source"]:
            df_all[c] = df_all[c].fillna("").astype(str).str.strip()
    return df_all, df_meta


# ============================================================
# 스코어링 & 중복 제거
# ============================================================
def score_buyer_record(
    row: dict,
    industry: str,
    hs_code: str,
    countries_selected: list[str],
    require_email: bool,
) -> int:
    score   = 0
    prod    = (row.get("product_text") or "").lower()
    comp    = (row.get("company_name") or "").lower()
    hs      = (row.get("hs_code") or "").replace(" ", "")
    country = (row.get("country") or "").lower()

    kws = INDUSTRY_KEYWORDS.get(industry, [])
    if any(kw.lower() in prod for kw in kws):  score += 30
    if any(kw.lower() in comp for kw in kws):  score += 10

    if hs_code:
        hk = hs_code.replace(" ", "")
        if hk and hk in hs:
            score += 45

    if countries_selected:
        if any(c.lower() in country for c in countries_selected if c):
            score += 20
        else:
            score -= 15

    if row.get("email"):          score += 20
    if row.get("contact_person"): score += 8
    if row.get("phone"):          score += 6
    if row.get("website"):        score += 6

    if require_email and not row.get("email"):
        score -= 999

    dt = row.get("date")
    if isinstance(dt, datetime):
        days_ago = (datetime.now() - dt).days
        if   days_ago <= 90:  score += 10
        elif days_ago <= 365: score += 5

    score += SOURCE_WEIGHT.get(row.get("source", ""), 0)
    return max(-999, min(100, score))


def dedupe_buyer_candidates(records: list[dict]) -> list[dict]:
    if not records:
        return records
    df = pd.DataFrame(records)
    if df.empty:
        return records

    df["email_key"] = df["email"].fillna("").astype(str).str.lower().str.strip()
    df["cc_key"] = (
        df["company_name"].fillna("").astype(str).str.lower().str.strip()
        + "|"
        + df["country_targets"].apply(lambda x: ",".join(x) if isinstance(x, list) else str(x)).str.lower().str.strip()
    )
    with_email = df[df["email_key"] != ""].sort_values("match_score", ascending=False).drop_duplicates("email_key")
    no_email   = df[df["email_key"] == ""].sort_values("match_score", ascending=False).drop_duplicates("cc_key")
    out = pd.concat([with_email, no_email]).sort_values("match_score", ascending=False)
    return out.drop(columns=["email_key", "cc_key"]).to_dict(orient="records")


# ============================================================
# 세션 스테이트 초기화
# ============================================================
if "matched_buyers" not in st.session_state:
    st.session_state.matched_buyers = []

st.markdown("""
    <style>
    /* Streamlit 기본 네비게이션 숨김 */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* 사이드바 배경 */
    section[data-testid="stSidebar"] { 
        background: #ffffff !important;
        border-right: 1px solid #e5e7eb;
    }
    
    /* 사이드바 버튼 스타일 (✅ hover 효과 추가) */
    .stButton>button {
        background: #051161 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px;
        padding: 10px 14px;
        font-weight: 700;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: rgba(5,17,97,0.85) !important;
        box-shadow: 0 4px 12px rgba(5,17,97,0.3) !important;
    }
    
    /* 사이드바 로고 스타일 */
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
    .small-muted{
        color:#64748b;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.2px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 사이드바 (✅ 새로운 로직 적용)
# ============================================================
with st.sidebar:
    # 1) 국가별 수출입 데이터
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
    # 2) SEO 서비스
    with st.expander("2) SEO 서비스", expanded=False):
        if st.button("바로가기", use_container_width=True, key="nav_news"):
            st.switch_page("pages/junghyun.py")

    # 3) AI 바이어 매칭 서비스
    with st.expander("3) AI 바이어 매칭 서비스", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("바이어 찾기", use_container_width=True, key="nav_ai_1"):
                st.switch_page("pages/03_ai_chatbot.py")
        with col2:
            if st.button("전시회 일정", use_container_width=True, key="nav_ai_2"):
                st.switch_page("pages/buyer_maps.py")

    # 4) 환율 정보 확인
    with st.expander("4) 환율 정보 확인", expanded=False):
        if st.button("바로가기", use_container_width=True, key="nav_ex"):
            st.switch_page("pages/exchange_rate.py")

    # 5) 무역 서류 자동 완성
    with st.expander("5) 무역 서류 자동 완성", expanded=False):
        if st.button("바로가기", use_container_width=True, key="nav_fx"):
            st.switch_page("pages/auto_docs.py")

    # 로고 영역
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()
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
    else:
        st.markdown(
            """
            <div class="logo-box">
              <div style="font-size:1.15rem; font-weight:900; color:#0f172a;">🌐 Trade Suite</div>
              <div class="small-muted" style="margin-top:6px;">KITA AX MASTER TEAM4</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ✅ 홈으로 돌아가기 버튼 (맨 아래)
    if st.button("🏠 홈으로 돌아가기", use_container_width=True, key="go_home_sidebar"):
        st.switch_page("dashboard.py")  # 메인 파일명에 맞게 수정


# ============================================================
# 메인 콘텐츠 — 박스 없이 헤더 표시
# ============================================================
st.markdown("""
<div class="page-header">
  <h1>🚢 AI 바이어 매칭 & 이메일 생성</h1>
  <div class="sub">바이어 후보 발굴 + AI 맞춤 이메일 작성 → 다국어 번역</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# CSV 로딩
# ============================================================
resolved_paths = {k: _find_local_csv_by_name(v) for k, v in CSV_BUYER_FILES.items()}

with st.spinner("📦로딩 중…"):
    df_all, df_meta = load_and_standardize_buyer_csv(resolved_paths)

loaded_count = df_meta[df_meta["status"] == "ok"].shape[0] if not df_meta.empty else 0
total_rows   = len(df_all)

if total_rows > 0:
    st.markdown(f"""
    <div class="loading-badge">
      <span class="icon">✅</span>
      <span class="txt">{total_rows:,}건 바이어 데이터 로딩 완료</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.error("⚠️ CSV 데이터가 비어있습니다. 프로젝트 폴더 또는 data/ 폴더에 CSV 파일을 배치해주세요.")


# ============================================================
# 검색 조건 입력 (2열 — 흰 박스 없이)
# ============================================================
col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown("### 제품 정보")
    industry    = st.selectbox("산업 분야", list(INDUSTRY_KEYWORDS.keys()))
    hs_code     = st.text_input("HS 코드 (선택)", placeholder="예: 3304, 8517")
    max_results = st.slider("최대 후보 수", min_value=10, max_value=300, value=60, step=10)

with col_right:
    st.markdown("### 타겟 국가")
    select_all         = st.checkbox("✅ 전체 선택", value=False, key="country_select_all")
    default_countries  = COUNTRY_OPTIONS if select_all else ["United States"]
    selected_countries = st.multiselect(
        "타겟 국가 (복수 선택 가능)",
        options=COUNTRY_OPTIONS,
        default=default_countries,
        key="country_multiselect",
    )
    require_email = st.checkbox("📧 이메일 있는 후보만", value=False)


# ============================================================
# 검색 실행 버튼
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🔍 바이어 후보 발굴", use_container_width=True, type="primary"):
    if df_all.empty:
        st.error("데이터가 비어있습니다.")
    else:
        df = df_all.copy()
        df["match_score"] = df.apply(
            lambda r: score_buyer_record(
                r.to_dict(),
                industry=industry,
                hs_code=hs_code.strip(),
                countries_selected=selected_countries,
                require_email=require_email,
            ),
            axis=1,
        )

        threshold = 35 if hs_code.strip() else 20
        df = df[df["match_score"] >= threshold].sort_values("match_score", ascending=False)

        buyers = []
        for _, row in df.iterrows():
            website = row.get("website", "")
            email   = row.get("email", "")
            domain  = ""
            if website:
                domain = str(website).strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
            elif email and "@" in str(email):
                domain = str(email).split("@")[-1].strip().lower()

            buyers.append({
                "company_name":      row.get("company_name", "Unknown"),
                "domain":            domain,
                "website":           website or (f"https://{domain}" if domain else ""),
                "industry":          industry,
                "country_targets":   selected_countries,
                "email":             email or (f"info@{domain}" if domain else ""),
                "contact_person":    row.get("contact_person", "") or "미추출",
                "match_score":       int(row.get("match_score", 0)),
                "source":            row.get("source", "CSV"),
                "_raw_country":      row.get("country", ""),
                "_raw_city":         row.get("city", ""),
                "_raw_product_text": row.get("product_text", ""),
                "_raw_hs":           row.get("hs_code", ""),
                "_raw_phone":        row.get("phone", ""),
            })

        buyers = dedupe_buyer_candidates(buyers)[:max_results]
        st.session_state.matched_buyers = buyers

        if buyers:
            st.markdown(f"""
            <div class="loading-badge">
              <span class="icon">🎉</span>
              <span class="txt">{len(buyers)}개의 바이어 후보를 찾았습니다!</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("검색 결과가 없습니다. HS 코드를 입력하거나 산업 분야 / 국가를 바꿔보세요.")


# ============================================================
# 결과 카드 + AI 이메일 생성
# ============================================================
if st.session_state.matched_buyers:
    st.markdown("---")
    st.markdown("### 검색된 바이어 후보 목록")

    for idx, buyer in enumerate(st.session_state.matched_buyers):
        key = f"{buyer.get('domain','') or buyer.get('company_name','')}|{idx}"

        has_real_email = bool(buyer.get("email")) and "@" in buyer.get("email", "")
        has_contact    = buyer.get("contact_person") not in ["", "미추출"]
        badge_html     = (
            '<span class="badge-ok">✅ 연락처 확보</span>'
            if (has_real_email or has_contact)
            else '<span class="badge-warn">🔍 미확인</span>'
        )

        st.markdown(
            f"<div style='margin-top:8px;'>"
            f"{badge_html} "
            # f"<strong style='color:#051161;'>매칭 점수: {buyer['match_score']}점</strong>"
            f"</div>",
            unsafe_allow_html=True,
        )

        with st.expander(
            f"{idx+1}. {buyer['company_name']}  ({buyer.get('domain','') or 'no-domain'})",
            expanded=(idx == 0),
        ):
            col_info, col_action = st.columns([3, 1])

            with col_info:
                st.markdown(f"""
| 항목 | 내용 |
|---|---|
| 🌐 웹사이트 | {buyer.get('website') or 'N/A'} |
| 🏭 산업 | {buyer.get('industry') or 'N/A'} |
| 📧 이메일 | {buyer.get('email') or 'N/A'} |
| ☎️ 전화 | {buyer.get('_raw_phone') or 'N/A'} |
| 📍 국가 | {buyer.get('_raw_country') or 'N/A'} |
""")

            with col_action:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("✉️ AI 이메일 생성", key=f"email_btn_{key}", use_container_width=True):
                    st.session_state[f"generate_email_{key}"] = True
                    st.rerun()

            if st.session_state.get(f"generate_email_{key}", False):
                st.markdown("#### 📧 AI 생성 제안 이메일")

                contact_person = buyer.get("contact_person")
                email_addr     = buyer.get("email")

                interest = [buyer.get("industry", "")]
                if hs_code.strip():
                    interest.append(f"HS {hs_code.strip()}")

                content_key = f"email_content_{key}"
                if content_key not in st.session_state:
                    with st.spinner("AI가 맞춤 이메일을 작성 중입니다…"):
                        st.session_state[content_key] = generate_buyer_email(
                            buyer_name=buyer.get("company_name", ""),
                            country=", ".join(buyer.get("country_targets", [])) or buyer.get("_raw_country", ""),
                            industry=buyer.get("industry", ""),
                            purchase_history=[x for x in interest if x],
                            contact_person=None if contact_person == "미추출" else contact_person,
                            email=email_addr,
                        )

                edit_key = f"email_edit_{key}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = st.session_state[content_key]

                en_state_key = f"trans_en_result_{key}"
                cn_state_key = f"trans_cn_result_{key}"
                submit_en, submit_cn = False, False

                with st.form(key=f"email_form_{key}"):
                    st.text_area(
                        "🇰🇷 한국어 이메일 (수정 가능)",
                        height=280,
                        key=edit_key,
                    )
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        submit_en = st.form_submit_button("🇺🇸 영어로 번역", use_container_width=True)
                    with col_t2:
                        submit_cn = st.form_submit_button("🇨🇳 중국어로 번역", use_container_width=True)

                if submit_en:
                    kr_text = st.session_state.get(edit_key, "").strip()
                    if kr_text:
                        with st.spinner("영어로 번역 중…"):
                            st.session_state[en_state_key] = translate_email(kr_text, "영어")
                    else:
                        st.warning("번역할 내용이 없습니다.")
                    st.rerun()

                if submit_cn:
                    kr_text = st.session_state.get(edit_key, "").strip()
                    if kr_text:
                        with st.spinner("중국어로 번역 중…"):
                            st.session_state[cn_state_key] = translate_email(kr_text, "중국어")
                    else:
                        st.warning("번역할 내용이 없습니다.")
                    st.rerun()

                if en_state_key in st.session_state:
                    st.text_area("🇺🇸 영어 번역", st.session_state[en_state_key], height=280, key=f"email_en_{key}")
                if cn_state_key in st.session_state:
                    st.text_area("🇨🇳 중국어 번역", st.session_state[cn_state_key], height=280, key=f"email_cn_{key}")

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #718096; font-size: 0.9em;'>
    <p>Global E-commerce All In One Solution</p>
    <p>Developed by Seyeon Global Connect</p>
</div>
""", unsafe_allow_html=True)