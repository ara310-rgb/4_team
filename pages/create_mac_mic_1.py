"""
mac_mic_1.py 생성 스크립트
new_kotra_4.py의 필요한 함수들 + certi_1.py 통합
"""

# 1. new_kotra_4.py 읽기
with open('new_kotra_4.py', 'r', encoding='utf-8') as f:
    kotra_content = f.read()

# 2. certi_1.py 읽기
with open('certi_1.py', 'r', encoding='utf-8') as f:
    certi_content = f.read()

# 3. new_kotra_4.py에서 필요한 부분 추출
# - 모든 import 구문 (1~66줄)
# - 모든 함수 정의 (68~1072줄)
# - main() 제외

kotra_lines = kotra_content.split('\n')

# import 구문 추출 (1~66줄)
imports_section = '\n'.join(kotra_lines[:66])

# 함수들 추출 (68~1072줄 - main() 함수 시작 전까지)
# get_region_info (451줄), render_barriers_strategy (773줄) 등 모두 포함
functions_section = '\n'.join(kotra_lines[67:1072])

# 4. 통합 파일 생성
mac_mic_content = f'''"""
🚀 SY Global Connect - 해외 진출 전략 & 인증
new_kotra_4.py (진입장벽 & SWOT) + certi_1.py (필수 인증)
"""

{imports_section}

# ============ new_kotra_4.py 함수들 ============
{functions_section}

# ============ certi_1.py 인증 조회 함수 ============
def render_certi_info():
    """KOTRA 해외인증정보 조회"""
    import requests
    import pandas as pd
    from urllib.parse import unquote
    import os
    
    OVERSEAS_CERTI_KEY = os.getenv("OVERSEAS_CERTI")
    
    st.markdown("### 필수 인증 정보 ")
    
    # 입력
    col1, col2 = st.columns(2)
    with col1:
        item_nm = st.text_input("품목명 입력", placeholder="예: 프린터", key="certi_item")
    with col2:
        nation_nm = st.text_input("국가명 입력", placeholder="예: 베트남", key="certi_nation")
    
    # 조회 함수
    def fetch_certi_data(key, item, nation):
        url = "http://apis.data.go.kr/B410001/overseasAuthInfo/getOverseasAuthInfo"
        
        params = {{
            'serviceKey': unquote(key) if key else "",
            'pageNo': '1',
            'numOfRows': '100',
            'itemNm': item,
            'nationNm': nation,
            'type': 'json'
        }}
        
        try:
            response = requests.get(url, params=params, verify=False, timeout=15)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"연결 오류: {{e}}")
            return None
    
    # 조회 버튼
    if st.button("🔍 인증 정보 조회", type="primary", key="certi_search"):
        if not OVERSEAS_CERTI_KEY:
            st.error("❌ .env 파일에 OVERSEAS_CERTI 키를 설정하세요.")
        elif not item_nm and not nation_nm:
            st.warning("품목명 또는 국가명을 입력해 주세요.")
        else:
            with st.spinner("KOTRA 서버에서 데이터를 가져오는 중..."):
                result = fetch_certi_data(OVERSEAS_CERTI_KEY, item_nm, nation_nm)
            
            if result:
                try:
                    body = result.get('response', {{}}).get('body', {{}})
                    item_list_obj = body.get('itemList', {{}})
                    
                    if item_list_obj:
                        data_list = item_list_obj.get('item', [])
                        
                        if isinstance(data_list, dict):
                            data_list = [data_list]
                        
                        if data_list:
                            df = pd.DataFrame(data_list)
                            
                            # 필터링
                            if item_nm:
                                df = df[df['nttSj'].str.contains(item_nm, case=False, na=False)]
                            if nation_nm:
                                df = df[df['nat'].str.contains(nation_nm, case=False, na=False)]
                            
                            if not df.empty:
                                st.success(f"✅ 총 {{len(df)}}건의 결과를 찾았습니다.")
                                
                                # 표시
                                display_map = {{
                                    'nat': '국가',
                                    'nttSj': '품목명/제목',
                                    'systName': '인증제도',
                                    'hscd': 'HS코드',
                                    'regDt': '등록일'
                                }}
                                
                                available_cols = [c for c in display_map.keys() if c in df.columns]
                                view_df = df[available_cols].rename(columns=display_map)
                                
                                st.subheader("인증 요약 리스트")
                                st.dataframe(view_df, use_container_width=True, hide_index=True)
                                
                                # 상세 정보
                                st.divider()
                                st.subheader("항목별 상세 정보")
                                for idx, row in df.iterrows():
                                    with st.expander(f"📌 [{{row.get('nat')}}] {{row.get('nttSj')}}"):
                                        c1, c2 = st.columns(2)
                                        with c1:
                                            st.write(f"**인증제도:** {{row.get('systName')}}")
                                            st.write(f"**HS 코드:** {{row.get('hscd', '-')}}")
                                        with c2:
                                            st.write(f"**등록일:** {{row.get('regDt')}}")
                                            st.write(f"**관련 기관:** {{row.get('ovrofInfo', '-')}}")
                                        
                                        st.markdown("---")
                                        st.markdown("**[제도 개요]**")
                                        st.info(row.get('systCn', '내용 없음'))
                                        st.markdown("**[준비 서류]**")
                                        st.warning(row.get('needPapersCn', '내용 없음'))
                            else:
                                st.error(f"⚠️ '{{item_nm}} / {{nation_nm}}'과 일치하는 결과가 없습니다.")
                        else:
                            st.warning("검색된 데이터가 없습니다.")
                    else:
                        st.warning("API 응답에 정보가 없습니다.")
                except Exception as e:
                    st.error(f"데이터 처리 오류: {{e}}")
            else:
                st.error("API 서버와 통신할 수 없습니다.")

# ============ 메인 UI ============
def main():
    st.set_page_config(
        page_title="SY Global Connect - 진출 전략",
        page_icon="🛡️",
        layout="wide"
    )
    
    # CSS
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {{ display: none; }}
    .block-container{{ padding: 2rem 4rem 5rem !important; }}
    </style>
    """, unsafe_allow_html=True)
    
    st.title("SY Global Connect - 진출 전략 & 인증")
    st.caption("진입장벽 분석 + AI SWOT + 필수 인증 정보")
    
    st.markdown("---")
    
    # 입력
    col1, col2 = st.columns(2)
    with col1:
        target_country = st.selectbox(
            "분석 대상국",
                ["미국", "중국", "일본", "독일", "베트남", "몽골", "우크라니아", "러시아", "튀르키예", "이란", "아랍에미리트", "브라질", "멕시코", "스위스", "스웨덴", "네덜란드", "벨기에", "포르투갈", "불가리아", "스페인", "이탈리아", "영국", "프랑스", "호주", "인도", "싱가포르", "필리핀", "인도네시아", "캐나다"],
            key="main_country"
        )
    with col2:
        hs_code = st.text_input(
            "HS Code (6자리)",
            value="330499",
            key="main_hs"
        )
    
    st.markdown("---")
    
    # 진입장벽 & 전략
    render_barriers_strategy(target_country, hs_code)
    
    st.markdown("---")
    
    # 필수 인증 정보
    render_certi_info()
    
    # 푸터
    st.markdown("---")
    st.caption("SY Global Connect | Powered by KOTRA, OpenAI")

if __name__ == "__main__":
    main()
'''

# 저장
with open('mac_mic_1.py', 'w', encoding='utf-8') as f:
    f.write(mac_mic_content)

print("✅ mac_mic_1.py 생성 완료!")
print(f"📊 파일 크기: {len(mac_mic_content)} chars")
print("\n포함된 함수:")
print("  - extract_text_from_pdf")
print("  - load_csv_data")
print("  - load_hs_code_library")
print("  - get_region_info  ← ✅ 이제 포함됨!")
print("  - render_barriers_strategy")
print("  - render_certi_info")
print("\n실행: streamlit run mac_mic_1.py")