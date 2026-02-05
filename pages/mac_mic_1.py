"""
🚀 SY Global Connect - 통합 대시보드
"""

import streamlit as st
import sys
import os
import pandas as pd
import base64

# ========== 1. 페이지 설정 (최상단, 한 번만!) ==========
st.set_page_config(
    page_title="SY 글로벌 커넥트",
    page_icon="🚀",
    layout="wide",
)

# ========== 2. CSS ==========
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none; }
.block-container { padding: 2rem 4rem 5rem !important; }
.stTabs [aria-selected="true"] { background-color: #051161; color: white; }

/* 사이드바 CSS */
section[data-testid="stSidebar"] { 
    background: #ffffff !important;
    border-right: 1px solid #e5e7eb;
}
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

# ========== 3. 사이드바 ==========
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
    st.markdown("---")

    # 홈으로 돌아가기
    if st.button("🏠 홈으로 돌아가기", use_container_width=True, key="go_home_sidebar"):
        st.switch_page("dashboard.py")

# ========== 4. 메인 컨텐츠 ==========
st.markdown("# 🚢 해외진출 전략 허브 : Strategy Playbook")
st.markdown("---")

# 데이터 로드 함수
@st.cache_data
def load_hs_code_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "..", "data", "HScode_customs.csv")
    file_path = os.path.normpath(file_path)
    
    if os.path.exists(file_path):
        encodings = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr', 'latin1']
        
        for enc in encodings:
            try:
                df = pd.read_csv(file_path, encoding=enc)
                return df
            except:
                continue
        
        st.error("❌ 모든 인코딩 시도 실패")
        return None
    return None

df_hs_customs = load_hs_code_data()

def search_hs_code_by_product(query):
    if df_hs_customs is not None and query:
        try:
            hs_col, kor_col, eng_col = df_hs_customs.columns[0], df_hs_customs.columns[3], df_hs_customs.columns[4]
            mask = (df_hs_customs[kor_col].astype(str).str.contains(query, na=False) | 
                    df_hs_customs[eng_col].astype(str).str.contains(query, case=False, na=False))
            results = []
            for _, row in df_hs_customs[mask].head(10).iterrows():
                results.append({
                    "hs_code_6digit": str(row[hs_col])[:6],
                    "korean_name": row[kor_col],
                    "english_name": row[eng_col]
                })
            return results
        except Exception as e:
            st.error(f"검색 중 오류: {e}")
    return []

# 버튼 클릭 시 실행될 콜백 함수
def _set_step3_hs(code: str):
    st.session_state['step3_hs'] = code 
    st.session_state['step3_selected_hs'] = code

# --- UI 부분 시작 ---
st.markdown('<div class="main-header"> 최적 시장 탐색</div>', unsafe_allow_html=True)

# HS Code 검색 UI
with st.expander("🔍 품목명으로 HS Code 찾기", expanded=True):
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        product_search = st.text_input(
            "품목명 입력",
            placeholder="예: 화장품, 샴푸 등",
            key="step3_product_search_main"
        )
    with search_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🔍 검색", use_container_width=True, key="step3_hs_search_main")
            
    if search_btn and product_search:
        results = search_hs_code_by_product(product_search)
        if results:
            st.success(f"✅ '{product_search}' 검색 결과")
            for idx, item in enumerate(results):
                colA, colB, colC = st.columns([1, 5, 1])
                with colA: st.markdown(f"**{item['hs_code_6digit']}**")
                with colB:
                    st.markdown(f"{item['korean_name']}")
                    st.caption(item.get('english_name', ''))
                with colC:
                    st.button("선택", key=f"sel_main_{idx}", on_click=_set_step3_hs, args=(item["hs_code_6digit"],))
        else:
            st.warning("검색 결과가 없습니다.")

st.markdown("---")

# 입력 필드
col_input1, col_input2 = st.columns(2)

with col_input1:
    target_country_step3 = st.selectbox(
        "분석 대상국",
        [
            "미국", "중국", "일본", "독일", "베트남", "몽골", "우크라이나", 
            "러시아", "튀르키예", "이란", "아랍에미리트", "브라질", "멕시코", 
            "스위스", "스웨덴", "네덜란드", "벨기에", "포르투갈", "불가리아", 
            "스페인", "이탈리아", "영국", "프랑스", "호주", "인도", 
            "싱가포르", "필리핀", "인도네시아", "캐나다"
        ],        
        key="step3_country"
    )

with col_input2:
    if 'step3_hs' not in st.session_state:
        st.session_state['step3_hs'] = ""
        
    hs_code_step3 = st.text_input(
        "HS Code (6자리)",
        key="step3_hs"
    )

st.markdown("<br>", unsafe_allow_html=True)

# 분석 시작 버튼
analyze_btn = st.button("🚀 AI 해외진출 전략 분석 시작", type="primary", use_container_width=True)

# 버튼이 클릭되었을 때만 실행
if analyze_btn:
    if not hs_code_step3 or len(hs_code_step3) < 4:
        st.warning("⚠️ 분석을 위해 올바른 HS Code(4~6자리)를 입력해 주세요.")
    else:
        import re
        
        DEBUG_REPLACE = False
        
        try:
            kotra_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "new_kotra_4.py")

            if DEBUG_REPLACE:
                st.caption(f"📌 new_kotra_4.py 로드 경로: {kotra_file_path}")

            with open(kotra_file_path, "r", encoding="utf-8") as f:
                code = f.read()

            # 1) set_page_config 중복 실행 방지
            code = code.replace("st.set_page_config(", "# st.set_page_config(")

            # 2) '필수 인증 정보' 관련 문구 가리기
            code = code.replace('st.markdown("### 📜 국가별/품목별 인증 정보 가이드', '# st.markdown("### 📜 필수 인증 정보 조회')
            code = code.replace('st.warning("⚠️ 해당 국가의 인증정보', '# st.warning("⚠️ 해당 국가의 인증정보')
            code = code.replace('st.info("💡 대안:', '# st.info("💡 대안:')

            # 3) "Risk Guard" / "진입장벽" 등 다양한 원문 케이스를 모두 커버해서 치환
            patterns = [
                r"🛡️\s*2\.\s*진입장벽과\s*SWOT\s*정밀\s*분석",
                r"2\.\s*Risk\s*Guard:\s*AI\s*SWOT\s*&\s*규제\s*리스크\s*분석",
                r"Risk\s*Guard:\s*AI\s*SWOT\s*&\s*규제\s*리스크\s*분석",
                r"진입장벽과\s*SWOT\s*정밀\s*분석",
            ]

            replaced_any = False
            for pat in patterns:
                new_code, n = re.subn(pat, "AI SWOT & 규제 리스크 분석", code)
                if n > 0:
                    replaced_any = True
                    code = new_code

            if DEBUG_REPLACE:
                st.caption(f"✅ 치환 발생 여부: {replaced_any}")
                st.caption(f"✅ 새 문구 포함 여부: {'AI SWOT & 규제 리스크 분석' in code}")

            # 4) main 블록 제거
            if 'if __name__ == "__main__":' in code:
                code = code.split('if __name__ == "__main__":')[0]

            # 5) globals() 오염 방지: 별도 네임스페이스에서 실행
            sandbox = {}
            exec(code, sandbox)

            # 6) 실행된 함수 호출
            if "render_barriers_strategy" in sandbox:
                with st.spinner("AI가 시장 장벽과 SWOT을 정밀 분석 중입니다..."):
                    sandbox["render_barriers_strategy"](target_country_step3, hs_code_step3)
            else:
                st.warning("⚠️ render_barriers_strategy 함수를 찾을 수 없습니다. (new_kotra_4.py 내부 확인 필요)")

        except FileNotFoundError:
            st.error("❌ new_kotra_4.py 파일이 해당 경로에 없습니다.")
        except Exception as e:
            st.error(f"❌ 실행 중 오류 발생: {e}")

st.markdown("---")

# 인증 정보
st.markdown("### 글로벌 인증 길잡이")

try:
    import requests
    import pandas as pd
    from urllib.parse import unquote
    from dotenv import load_dotenv
    
    load_dotenv()
        
    KEY = os.getenv("OVERSEAS_CERTI")
        
    col1, col2 = st.columns(2)
    with col1:
        item = st.text_input("품목명", key="c_i")
    with col2:
        nation = st.text_input("국가명", key="c_n")
        
    def fetch(k, i, n):
        url = "http://apis.data.go.kr/B410001/overseasAuthInfo/getOverseasAuthInfo"
        params = {
            'serviceKey': unquote(k) if k else '',
            'pageNo': '1',
            'numOfRows': '100',
            'itemNm': i,
            'nationNm': n,
            'type': 'json'
        }
        try:
            r = requests.get(url, params=params, verify=False, timeout=15)
            return r.json() if r.status_code == 200 else None
        except:
            return None
    
    if st.button("🔍 조회", key="c_s"):
        if not KEY:
            st.error("❌ OVERSEAS_CERTI 키 필요")
        elif not item and not nation:
            st.warning("입력 필요")
        else:
            with st.spinner("조회 중..."):
                result = fetch(KEY, item, nation)
                    
                if result:
                    try:
                        body = result.get('response', {}).get('body', {})
                        items = body.get('itemList', {}).get('item', [])
                        
                        if isinstance(items, dict):
                            items = [items]
                        
                        if items:
                            df = pd.DataFrame(items)
                                
                            if item:
                                df = df[df['nttSj'].str.contains(item, case=False, na=False)]
                            if nation:
                                df = df[df['nat'].str.contains(nation, case=False, na=False)]
                                
                            if not df.empty:
                                st.success(f"✅ {len(df)}건")
                                    
                                cols = {'nat':'국가', 'nttSj':'품목', 'systName':'인증', 'hscd':'HS', 'regDt':'등록일'}
                                view = df[[c for c in cols.keys() if c in df.columns]].rename(columns=cols)
                                st.dataframe(view, use_container_width=True, hide_index=True)
                                
                                for _, row in df.iterrows():
                                    with st.expander(f"📌 [{row.get('nat')}] {row.get('nttSj')}"):
                                        c1, c2 = st.columns(2)
                                        with c1:
                                            st.write(f"**인증제도:** {row.get('systName')}")
                                            st.write(f"**HS 코드:** {row.get('hscd', '-')}")
                                        with c2:
                                            st.write(f"**등록일:** {row.get('regDt')}")
                                            st.write(f"**관련 기관:** {row.get('ovrofInfo', '-')}")
                                        
                                        st.markdown("---")
                                        st.markdown("**[제도 개요]**")
                                        st.info(row.get('systCn', '내용 없음'))
                                        st.markdown("**[준비 서류]**")
                                        st.warning(row.get('needPapersCn', '내용 없음'))
                            else:
                                st.error("결과 없음")
                    except Exception as e:
                        st.error(f"처리 오류: {e}")

except Exception as e:
    st.error(f"❌ {e}")

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #718096; font-size: 0.9em;'>
    <p>Global E-commerce All In One Solution</p>
    <p>Developed by Seyeon Global Connect</p>
</div>
""", unsafe_allow_html=True)