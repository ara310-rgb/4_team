import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
from pathlib import Path
import os
import base64

# ==========================================
# [설정] 페이지 및 스타일
# ==========================================
try:
    st.set_page_config(
        page_title="SY Global Connect - 전시회",
        page_icon="🚢",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except:
    pass

st.markdown("""
<style>
/* Streamlit 기본 네비게이션 숨김 */
[data-testid="stSidebarNav"] {
    display: none;
}

.block-container{padding: 2rem 5rem !important;}
:root{
  --accent:#051161;
  --text:#0f172a;
  --bg:#ffffff;
}

/* 사이드바 배경 */
section[data-testid="stSidebar"] { 
    background: #ffffff !important;
    border-right: 1px solid #e5e7eb;
}

.stButton>button{
  background: var(--accent); 
  color: #ffffff;
  border-radius: 8px; 
  font-weight: 700; 
  border: none;
  transition: 0.3s;
}
.stButton>button:hover{
  background: rgba(5,17,97,0.85);
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


# ==========================================
# [사이드바] 네비게이션
# ==========================================
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
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
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
    else:
        st.markdown(
            """
            <div class="logo-box">
              <div style="font-size:1.15rem; font-weight:900; color:#0f172a;">🎪 Trade Suite</div>
              <div class="small-muted" style="margin-top:6px;">KITA AX MASTER TEAM4</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ✅ 홈으로 돌아가기 버튼
    if st.button("🏠 홈으로 돌아가기", use_container_width=True, key="go_home_sidebar"):
        st.switch_page("dashboard.py")

# ==========================================
# [데이터] 경로 및 좌표 설정
# ==========================================

def find_data_file(filename: str) -> Path | None:
    """
    EXHIBITION_PLAN.csv 같은 파일을
    (현재 파일 위치 -> 상위 폴더들)로 올라가며 자동 탐색해서 찾는다.
    우선순위:
      1) <어딘가>/assets/pages/data/<filename>
      2) <어딘가>/pages/data/<filename>  (예비)
      3) <어딘가>/data/<filename>        (예비)
    """
    here = Path(__file__).resolve()

    candidates_rel = [
        Path("assets/pages/data") / filename,
        Path("pages/data") / filename,
        Path("data") / filename,
    ]

    # __file__ 기준으로 위로 올라가며 탐색
    for parent in [here.parent] + list(here.parents):
        for rel in candidates_rel:
            p = parent / rel
            if p.exists():
                return p

    # 마지막 fallback: 현재 작업 디렉토리 기준도 한 번 더
    cwd = Path.cwd().resolve()
    for rel in candidates_rel:
        p = cwd / rel
        if p.exists():
            return p

    return None


# 주요 도시 위경도 좌표
CITY_COORDS = {
    "밀라노": [45.4642, 9.1900], "모스크바": [55.7558, 37.6173], "상하이": [31.2304, 121.4737],
    "자카르타": [-6.2088, 106.8456], "방콕": [13.7563, 100.5018], "라스베이거스": [36.1699, -115.1398],
    "호치민": [10.8231, 106.6297], "도쿄": [35.6895, 139.6917], "타이베이": [25.0330, 121.5654],
    "싱가포르": [1.3521, 103.8198], "두바이": [25.2048, 55.2708], "리야드": [24.7136, 46.6753],
    "쿠알라룸푸르": [3.1390, 101.6869], "뭄바이": [19.0760, 72.8777], "파리": [48.8566, 2.3522],
    "프랑크푸르트": [50.1109, 8.6821], "홍콩": [22.3193, 114.1694], "바르셀로나": [41.3851, 2.1734],
    "멜버른": [-37.8136, 144.9631], "암스테르담": [52.3676, 4.9041], "뉴욕": [40.7128, -74.0060],
    "멕시코시티": [19.4326, -99.1332], "이스탄불": [41.0082, 28.9784], "마드리드": [40.4168, -3.7038],
    "뮌헨": [48.1351, 11.5820], "베를린": [52.5200, 13.4050], "하노이": [21.0285, 105.8542],
    "시카고": [41.8781, -87.6298], "올랜도": [28.5383, -81.3792]
}

# ==========================================
# [기능] 데이터 로드 및 처리
# ==========================================
@st.cache_data
def load_exhibitions():
    csv_path = find_data_file("EXHIBITION_PLAN.csv")

    if not csv_path:
        st.error("❌ EXHIBITION_PLAN.csv 파일을 찾지 못했습니다.")
        st.info("✅ 파일 위치 예: mini_project/assets/pages/data/EXHIBITION_PLAN.csv")
        return pd.DataFrame()

    # 인코딩 자동 대응
    for enc in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return pd.read_csv(csv_path, encoding=enc)
        except:
            continue

    st.error("❌ CSV 인코딩을 확인할 수 없습니다. (utf-8/utf-8-sig/cp949 모두 실패)")
    return pd.DataFrame()


def parse_date(date_str):
    try:
        d_str = str(date_str)
        if len(d_str) == 7:
            return pd.to_datetime(d_str + "-01")
        return pd.to_datetime(d_str)
    except:
        return pd.NaT


# ==========================================
# [메인] 전시회 렌더링 로직
# ==========================================
def render_step4_exhibitions():
    st.markdown("## 🚢 글로벌 전시회 정보")

    df_exh = load_exhibitions()

    if df_exh.empty:
        st.warning("데이터를 불러오지 못했습니다. CSV 파일 인코딩이나 경로를 확인해주세요.")
        return

    # 날짜 컬럼 처리
    if '개최시작예정일자' in df_exh.columns:
        df_exh['start_dt'] = df_exh['개최시작예정일자'].apply(parse_date)
    else:
        st.error("필수 컬럼 누락: '개최시작예정일자'")
        return

    # 1. 검색 필터
    with st.container():
        st.markdown("##### 전시회 검색 조건")
        col1, col2, col3 = st.columns(3)

        with col1:
            countries = sorted(df_exh['개최국가명'].dropna().unique().tolist()) if '개최국가명' in df_exh.columns else []
            selected_countries = st.multiselect("국가 선택", options=countries, placeholder="국가를 선택하세요")

        with col2:
            date_range = st.date_input("개최 기간", value=[datetime.now(), datetime(2026, 12, 31)])

        with col3:
            industries = set()
            if '산업분야' in df_exh.columns:
                for items in df_exh['산업분야'].dropna():
                    for item in str(items).split(','):
                        industries.add(item.strip())
            selected_industry = st.selectbox("산업 분야", options=['전체'] + sorted(list(industries)))

    # 2. 필터링
    filtered_df = df_exh.copy()

    if selected_countries:
        filtered_df = filtered_df[filtered_df['개최국가명'].isin(selected_countries)]

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_df = filtered_df[(filtered_df['start_dt'] >= start_dt) & (filtered_df['start_dt'] <= end_dt)]

    if selected_industry != '전체':
        filtered_df = filtered_df[filtered_df['산업분야'].str.contains(selected_industry, na=False)]

    # 3. 지도 시각화
    st.markdown("---")
    st.markdown(f"### 전시회 분포 (총 {len(filtered_df)}건)")

    m = folium.Map(location=[20, 10], zoom_start=2, tiles="cartodbpositron")

    if '개최도시명' in filtered_df.columns:
        map_data = filtered_df.dropna(subset=['개최도시명'])
        city_counts = map_data['개최도시명'].value_counts()

        for city, count in city_counts.items():
            if city in CITY_COORDS:
                folium.Marker(
                    location=CITY_COORDS[city],
                    tooltip=f"{city} ({count}건)",
                    popup=folium.Popup(f"<b>{city}</b><br>전시회: {count}건", max_width=200),
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)

    map_output = st_folium(m, width=1200, height=500, key="exhibition_map_main")

    # 4. 결과 테이블
    st.markdown("---")
    clicked_city = map_output.get("last_object_clicked_tooltip")

    if clicked_city:
        clicked_city_name = clicked_city.split(" (")[0]
        st.subheader(f"🏙️ {clicked_city_name} 전시회 목록")
        final_df = filtered_df[filtered_df['개최도시명'] == clicked_city_name]
    else:
        st.subheader("전체 검색 결과")
        final_df = filtered_df

    cols = ['개최시작예정일자', '개최국가명', '개최도시명', '해외전시회명', '산업분야', '전시장명']
    valid_cols = [c for c in cols if c in final_df.columns]

    if not final_df.empty:
        st.dataframe(
            final_df[valid_cols].sort_values('개최시작예정일자') if '개최시작예정일자' in valid_cols else final_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("검색 조건에 맞는 전시회가 없습니다.")


# ==========================================
# [실행 진입점]
# ==========================================
if __name__ == "__main__":
    render_step4_exhibitions()

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #718096; font-size: 0.9em;'>
    <p>Global E-commerce All In One Solution</p>
    <p>Developed by Seyeon Global Connect</p>
</div>
""", unsafe_allow_html=True)