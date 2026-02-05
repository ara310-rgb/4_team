import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import os
import re
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2
import xml.etree.ElementTree as ET  # [추가] XML 파싱용 라이브러리

# ==========================================
# 0. 설정 및 API 키 로드
# ==========================================
st.set_page_config(page_title="KOTRA AX 수출 솔루션", page_icon="🚀", layout="wide")

# .env 파일 로드 (로컬 환경용)
load_dotenv()

# API 키 설정 (환경변수에서 가져오거나 직접 입력)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RAINFOREST_API_KEY = os.getenv("RAINFOREST_API_KEY") # 아마존 데이터용
SERPAPI_KEY = os.getenv("SERPAPI_KEY")               # 구글 검색용
UTRADEHUB_KEY = os.getenv("UTRADEHUB_API_KEY")       # 무역정보용 (추후확장)
UN_COMTRADE_KEY = os.getenv("UN_COMTRADE_KEY")       # UN 무역통계
CUSTOMS_KEY = os.getenv("CUSTOMS_ITEMS_COUNTRY")     # 관세청 통계

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# 파일 경로 설정
REPORT_FOLDER = "pdfs"
SITE_CSV_FILE = os.path.join("data", "overseas_site_search.csv")

# 국가별 수출입 데이터 파일 매핑 (업로드된 파일명 기준)
ITEM_DATA_FILES = {
    "중국": "kotra_items.xlsx - 1 중국.csv",
    "미국": "kotra_items.xlsx - 2 미국.csv",
    "베트남": "kotra_items.xlsx - 3 베트남.csv",
    "일본": "kotra_items.xlsx - 4 일본.csv",
    "홍콩": "kotra_items.xlsx - 5 홍콩.csv",
    "대만": "kotra_items.xlsx - 6 대만.csv",
    "싱가포르": "kotra_items.xlsx - 7 싱가포르.csv",
    "인도": "kotra_items.xlsx - 8 인도.csv",
    "호주": "kotra_items.xlsx - 9 호주.csv",
    "멕시코": "kotra_items.xlsx - 10 멕시코.csv"
}

# CSS 스타일링 (SY Global Connect 브랜드 톤 적용)
st.markdown("""
<style>
    /* 메인 제목: 검정색으로 변경 및 크기 조절 */
    .main-header { 
        font-size: 24px; 
        font-weight: 700; 
        color: #000000; 
        margin-bottom: 15px; 
        border-bottom: 2px solid #e5e7eb; 
        padding-bottom: 10px;
    }
    /* 서브 제목: 브랜드 다크 그레이 적용 */
    .sub-header { 
        font-size: 20px; 
        font-weight: 600; 
        color: #2c3e50; 
        margin-top: 25px; 
        margin-bottom: 10px;
    }
    /* 인사이트 박스: 좀 더 신뢰감 있는 배경색 */
    .insight-box { 
        background-color: #f8f9fa; 
        border-left: 5px solid #764ba2; 
        padding: 20px; 
        border-radius: 8px; 
        margin-bottom: 20px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
    }
    .traffic-light { font-size: 3rem; text-align: center; }
    /* 버튼 스타일: 브랜드 보라색 그라디언트 느낌 */
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        background-color: #ffffff;
        color: #764ba2;
        border: 1px solid #764ba2;
    }
    .stButton>button:hover {
        background-color: #764ba2;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 데이터 로더 및 유틸리티 함수
# ==========================================

# 1-1. PDF 텍스트 추출
def extract_text_from_pdf(file_path, max_pages=15):
    try:
        if not os.path.exists(file_path):
            return None
        text = ""
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            read_limit = min(num_pages, max_pages) 
            for i in range(read_limit):
                page = reader.pages[i]
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# 1-2. CSV 로드 (인코딩 처리)
@st.cache_data
def load_csv_data(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        return pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            return pd.read_csv(file_path, encoding='cp949')
        except:
            return None

# ==========================================
# [New] HS Code 데이터 로드 및 전처리 함수
# ==========================================
@st.cache_data
def load_hs_code_library():
    file_path = os.path.join("data", "HScode_customs.csv")
    if not os.path.exists(file_path):
        return pd.DataFrame() # 파일 없으면 빈 껍데기 반환
    
    try:
        # CSV 읽기 (인코딩 에러 방지)
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp949')
        
        # 데이터 전처리: 검색하기 편하게 '코드 - 품목명' 형태로 컬럼 생성
        # HS부호가 숫자형일 수 있으므로 문자열로 변환
        df['HS부호'] = df['HS부호'].astype(str)
        # 검색용 라벨 만들기 (예: "3304990000 - 기초화장품")
        df['Label'] = df['HS부호'] + "| " + df['한글품목명']
        return df[['HS부호', '한글품목명', 'Label']]
    except Exception as e:
        return pd.DataFrame()


# 1-3. URL 추출 정규식
def extract_url(text):
    if pd.isna(text): return None
    pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    urls = re.findall(pattern, str(text))
    if urls:
        url = urls[0].rstrip('.,)]}>"\'')
        if not url.startswith(('http://', 'https://')):
            url = "https://" + url
        return url
    return None

# ==========================================
# 2. 외부 API 연동 함수 (Rainforest, SerpApi, Customs)
# ==========================================

# ==========================================
# [수정] 2-1. Amazon 가격 분석 (Rainforest API + Failover)
# ==========================================

# 국가별 아마존 도메인 매핑
COUNTRY_TO_AMAZON = {
    "미국": "amazon.com", "일본": "amazon.co.jp", "독일": "amazon.de",
    "영국": "amazon.co.uk", "프랑스": "amazon.fr", "이탈리아": "amazon.it",
    "스페인": "amazon.es", "인도": "amazon.in", "호주": "amazon.com.au",
    "캐나다": "amazon.ca", "멕시코": "amazon.com.mx", "브라질": "amazon.com.br",
    "싱가포르": "amazon.sg", "아랍에미리트": "amazon.ae"
}

def get_amazon_pricing(keyword, target_country):
    """
    Rainforest API를 호출하되, 실패 시 가상 데이터(Mock)를 반환하여
    대시보드가 멈추지 않게 함.
    """
    api_key = os.getenv("RAINFOREST_API_KEY")
    domain = COUNTRY_TO_AMAZON.get(target_country, "amazon.com") # 기본값은 미국

# ---------------------------------------------
    # [Case 1] 실제 API 호출 시도
    # ---------------------------------------------
    if api_key:
        try:
            params = {
                "api_key": api_key,
                "type": "search",
                "amazon_domain": domain,
                "search_term": keyword,
                "sort_by": "featured" # 관련도순
            }
            
            # 타임아웃 5초 설정 (너무 오래 걸리면 스킵)
            response = requests.get("https://api.rainforestapi.com/request", params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                products = []
                prices = []
                
                if "search_results" in data:
                    for item in data["search_results"][:5]: # 상위 5개만
                        if "price" in item and "value" in item["price"]:
                            price_val = item["price"]["value"]
                            prices.append(price_val)
                            products.append({
                                "title": item.get("title", "No Title")[:50] + "...",
                                "price": price_val,
                                "currency": item["price"].get("currency", "USD"),
                                "link": item.get("link", "#"),
                                "image": item.get("image", None)
                            })
                
                if products:
                    return {
                        "status": "SUCCESS",
                        "average": sum(prices) / len(prices),
                        "min": min(prices),
                        "max": max(prices),
                        "products": products,
                        "currency": products[0]['currency']
                    }
            else:
                # 에러 로그 출력 (디버깅용)
                print(f"Rainforest API Error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"Rainforest Connection Error: {e}")

    # ---------------------------------------------
    # [Case 2] API 실패/없음 -> 가상 데이터(Mock) 생성
    # ---------------------------------------------
    # 키워드를 보고 가격대를 그럴싸하게 난수 생성
    base_price = random.uniform(15.0, 50.0) # 기본 15~50달러 사이
    mock_currency = "USD"
    if target_country == "일본": mock_currency = "JPY"; base_price *= 100
    elif target_country == "유럽": mock_currency = "EUR"; base_price *= 0.9

    mock_products = [
        {"title": f"[Competitor] {keyword} Premium A", "price": base_price * 1.2, "currency": mock_currency, "link": "#"},
        {"title": f"[Competitor] {keyword} Standard B", "price": base_price, "currency": mock_currency, "link": "#"},
        {"title": f"[Competitor] {keyword} Basic C", "price": base_price * 0.8, "currency": mock_currency, "link": "#"},
        {"title": f"[Competitor] Top Rated {keyword}", "price": base_price * 1.5, "currency": mock_currency, "link": "#"},
        {"title": f"[Competitor] Eco-friendly {keyword}", "price": base_price * 1.1, "currency": mock_currency, "link": "#"},
    ]
    prices = [p['price'] for p in mock_products]

    return {
        "status": "MOCK_DATA", # 상태 표시
        "average": sum(prices) / len(prices),
        "min": min(prices),
        "max": max(prices),
        "products": mock_products,
        "currency": mock_currency
    }

# 2-2. Google 검색 (SerpApi)
def get_google_buyers(query, api_key):
    """
    SerpApi를 사용하여 구글 검색 결과를 가져옵니다.
    """
    if not api_key:
        return [] # 키 없으면 빈 리스트
    
    try:
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": 5
        }
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()
        
        results = []
        if "organic_results" in data:
            for item in data["organic_results"]:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet")
                })
        return results
    except Exception as e:
        return []
# ==========================================
# KOTRA 해외인증정보 API 연동 함수
# 기존 코드 266번째 줄 이후에 추가
# ==========================================

@st.cache_data(ttl=86400)
def fetch_kotra_certification_info(target_country, product_category=""):
    """
    KOTRA 해외인증정보 API 호출 (XML 방식)
    """
    api_key = os.getenv("OVERSEAS_CERTI")
    if not api_key:
        return []
    
    url = "http://apis.data.go.kr/1451000/OverseasCertiInfoService/getOverseasCertiInfoList"
    params = {
        "serviceKey": requests.utils.unquote(api_key),
        "natnNm": target_country,
        "numOfRows": 50,
        "pageNo": 1,
        "resultType": "xml"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.content)
                items = root.findall('.//item')

                # [수정] 들여쓰기 교정 완료 (items 변수와 줄 맞춤)
                if not items:
                    return []

                cert_list = []
                for item in items:
                    item_category = item.findtext("prdlstNm") or ""
                    if product_category and product_category not in item_category:
                        continue

                    cert_data = {
                        "cert_name": item.findtext("certiNm") or "인증명 없음",
                        "product_category": item_category or "품목 정보 없음",
                        "test_agency": item.findtext("testInsttNm") or "정보 없음",
                        "cert_procedure": item.findtext("certiPrcs") or "상세 절차 정보 없음",
                        "system_content": item.findtext("sysCn"),
                        "remarks": item.findtext("rm")
                    }
                    cert_list.append(cert_data)
                    
                return cert_list
            except ET.ParseError:
                return []
        else:
            return []
    except Exception as e:
        return []
            
            



# ==========================================
# [수정] 2-3. UN Comtrade API 연동 (시장규모/경쟁사 분석)
# ==========================================

# UN Comtrade용 국가 코드 (ISO 3166-1 numeric code)
# 한국: 410, 세계: 0
COUNTRY_TO_COMTRADE = {
    "미국": "840", "중국": "156", "일본": "392", "베트남": "704",
    "홍콩": "344", "대만": "490", "인도": "356", "싱가포르": "702",
    "호주": "036", "멕시코": "484", "독일": "276", "프랑스": "250",
    "영국": "826", "러시아": "643", "브라질": "076", "캐나다": "124",
    "인도네시아": "360", "태국": "764", "필리핀": "608", "아랍에미리트": "784",
    "이탈리아": "380", "스페인": "724", "네덜란드": "528", "한국": "410", "세계": "0"
}

@st.cache_data(ttl=3600)
def fetch_un_comtrade_data(hs_code, target_country):
    """
    UN Comtrade API 호출 
    1. Primary/Secondary 키 자동 전환
    2. 타겟 국가가 파트너 목록에 있으면 제거 (Self-reference 방지)
    3. 6단위 조회 실패 시 4단위로 자동 재시도 (Failover)
    """
    keys_to_try = []
    key1 = os.getenv("UN_COMTRADE_KEY")
    key2 = os.getenv("UN_COMTRADE_SECONDARY_KEY")
    if key1: keys_to_try.append(key1)
    if key2: keys_to_try.append(key2)
    
    if not keys_to_try:
        return None, "API_KEY_MISSING"

    target_code = COUNTRY_TO_COMTRADE.get(target_country)
    if not target_code:
        return None, f"'{target_country}'은(는) 지원되지 않는 국가 코드입니다."

    # [수정 1] 파트너 리스트 관리 (자기 자신 제외)
    # 기본 파트너: 세계(0), 한국(410), 중국(156), 미국(840), 독일(276), 일본(392)
    default_partners = ["0", "410", "156", "840", "276", "392"]
    
    # 만약 타겟 국가가 파트너 리스트에 있다면 제거 (예: 미국 조회 시 파트너에서 미국 제외)
    if target_code in default_partners:
        default_partners.remove(target_code)
    
    partner_str = ",".join(default_partners)

    # [수정 2] 6단위 시도 후 실패하면 4단위 시도할 수 있도록 리스트 구성
    # 예: [330499, 3304]
    hs_codes_to_try = [hs_code]
    if len(hs_code) > 4:
        hs_codes_to_try.append(hs_code[:4]) # 4자리 코드 추가

    url = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
    
    # --- 이중 루프: HS코드(6->4) 반복 -> API키 반복 ---
    for current_hs in hs_codes_to_try:
        params = {
            "reporterCode": target_code,     
            "partnerCode": partner_str, 
            "period": "2023",           # 2개년도 동시 요청
            "cmdCode": current_hs,              
            "flowCode": "M",                 
            "motCode": "0",                  
            "freqCode": "A",                 
            "format": "json"
        }

        for i, api_key in enumerate(keys_to_try):
            headers = {"Ocp-Apim-Subscription-Key": api_key}
            
            try:
                response = requests.get(url, params=params, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and len(data['data']) > 0:
                        df = pd.DataFrame(data['data'])
                        
                        # [핵심 수정 2] 숫자 코드(partnerCode)와 연도(refYear) 컬럼 확보
                        cols_to_keep = ['partnerCode', 'partnerDesc', 'primaryValue', 'refYear']
                        if all(col in df.columns for col in cols_to_keep):
                            df = df[cols_to_keep]
                            df['primaryValue'] = pd.to_numeric(df['primaryValue'], errors='coerce').fillna(0)
                            
                            # [핵심 수정 3] 최신 연도 데이터만 필터링
                            # 데이터에 있는 연도 중 가장 큰 값(최신)을 찾음
                            latest_year = df['refYear'].max()
                            df_latest = df[df['refYear'] == latest_year].copy()
                            
                            # 국가명 한글 매핑 (시각화용)
                            # partnerCode: 0(세계), 410(한국), 156(중국), 840(미국), 276(독일), 392(일본)
                            code_map = {0: '전세계(시장규모)', 410: '한국', 156: '중국', 
                                        840: '미국', 276: '독일', 392: '일본'}
                            
                            # map 함수를 써서 안전하게 변환
                            df_latest['partnerDesc'] = df_latest['partnerCode'].map(code_map).fillna(df_latest['partnerDesc'])
                            
                            # 4자리로 찾았을 경우 메시지에 표시
                            success_msg = f"SUCCESS({latest_year})"
                            if len(current_hs) == 4:
                                success_msg += "_4DIGIT" # 4자리로 찾았음을 표시

                            return df_latest, success_msg

                    # 데이터가 없으면(NO_DATA) -> 다음 키 시도하지 말고, 다음 HS 코드로 넘어감(break)
                    # 왜냐하면 키 문제가 아니라 데이터 문제니까.
                    else:
                        break

                elif response.status_code in [401, 403, 429]:
                    continue 
                else:
                    # 기타 서버 에러면 다음 키 시도
                    continue

            except Exception as e:
                continue
        # 내부 for문(키 순환)이 끝났는데도 리턴이 안 됐다면 -> 다음 HS 코드(current_hs)로 넘어감
    return None, "ALL_KEYS_FAILED"
# ==========================================
# 3. 로직: 권역 및 국가 정보 매핑
# ==========================================
def get_region_info(target_country):
    """국가별 PDF 파일 및 메타데이터 매핑 (최신 버전 반영)"""
    
    # 1. 북미
    if target_country == "미국":
        return {"region": "북미(미국)", "file": f"{REPORT_FOLDER}/USA.pdf", "trend": "공급망 재편, 웰니스, 트럼프 2기", "growth": "2.1%"}
    elif target_country == "캐나다":
        return {"region": "북미", "file": f"{REPORT_FOLDER}/CANADA.pdf", "trend": "에너지 전환, 인프라 투자, 이민 확대", "growth": "1.5%"}
    
    # 2. 아시아 (동북아/동남아/대양주/서남아)
    elif target_country == "중국":
        return {"region": "아시아(동북아)", "file": f"{REPORT_FOLDER}/CHINA.pdf", "trend": "경제권 구축(재세계화), 기술 자립(Red Tech)", "growth": "4.5%"}
    elif target_country == "일본":
        return {"region": "아시아(동북아)", "file": f"{REPORT_FOLDER}/JAPAN.pdf", "trend": "GX/DX 혁신, 시니어 이코노미, 구조적 한류", "growth": "0.8%"}
    elif target_country == "대만":
        return {"region": "아시아(동북아)", "file": f"{REPORT_FOLDER}/TAIWAN.pdf", "trend": "반도체/AI 초격차, 에너지 안보", "growth": "2.8%"}
    elif target_country == "베트남":
        return {"region": "동남아", "file": f"{REPORT_FOLDER}/VIETNAM.pdf", "trend": "미국 관세 대응, 산업 고도화, 녹색 전환", "growth": "6.0%"}
    elif target_country == "인도네시아":
        return {"region": "동남아", "file": f"{REPORT_FOLDER}/INDONESIA.pdf", "trend": "경제안보, 교역 다변화, 신수도 이전", "growth": "4.4%"}
    elif target_country == "태국":
        return {"region": "동남아", "file": f"{REPORT_FOLDER}/THAILAND.pdf", "trend": "전기차 허브, 인프라 신성장", "growth": "1.6%"}
    elif target_country == "필리핀":
        return {"region": "동남아", "file": f"{REPORT_FOLDER}/PHILIPPINES.pdf", "trend": "신정부조달법, 디지털 결제 확산", "growth": "6.1%"}
    elif target_country == "싱가포르":
        return {"region": "동남아", "file": f"{REPORT_FOLDER}/SINGAPORE.pdf", "trend": "녹색금융 허브, 2050 넷제로", "growth": "1.5%"}
    elif target_country == "인도":
        return {"region": "서남아", "file": f"{REPORT_FOLDER}/INDIA.pdf", "trend": "Make in India, 디지털 전환, 소비혁명", "growth": "6.8%"}
    elif target_country == "호주":
        return {"region": "대양주", "file": f"{REPORT_FOLDER}/AUSTRALIA.pdf", "trend": "Future Made in Australia, 청정에너지", "growth": "2.2%"}

    # 3. 유럽
    elif target_country == "독일":
        return {"region": "유럽", "file": f"{REPORT_FOLDER}/GERMANY.pdf", "trend": "공급망 재편, 방산 투자, 가치소비 2.0", "growth": "1.3%"}
    elif target_country == "프랑스":
        return {"region": "유럽", "file": f"{REPORT_FOLDER}/FRANCE.pdf", "trend": "전력망/방산 투자, K-뷰티 열풍", "growth": "1.1%"}
    elif target_country == "영국":
        return {"region": "유럽", "file": f"{REPORT_FOLDER}/UK.pdf", "trend": "신산업 전략(IS-8), 넷제로, 디지털 헬스", "growth": "1.3%"}
    elif target_country == "이탈리아":
        return {"region": "유럽", "file": f"{REPORT_FOLDER}/ITALY.pdf", "trend": "제조업 혁신, 방산/안보, 고령화 대응", "growth": "0.7%"}
    elif target_country == "스페인":
        return {"region": "유럽", "file": f"{REPORT_FOLDER}/SPAIN.pdf", "trend": "재생에너지 인프라, 전기차 산업", "growth": "1.9%"}
    elif target_country == "네덜란드":
        return {"region": "유럽", "file": f"{REPORT_FOLDER}/NETHERLANDS.pdf", "trend": "ESG/공급망 실사, 방산 협력, DX", "growth": "1.4%"}
    elif target_country in ["스위스", "오스트리아", "벨기에", "스웨덴", "포르투갈", "불가리아"]:
        # 파일명이 국가명과 동일한 경우 처리
        return {"region": "유럽", "file": f"{REPORT_FOLDER}/{target_country.upper()}.pdf", "trend": "EU 역내 협력, 친환경, 에너지 안보", "growth": "1~2%"}

    # 4. 중남미
    elif target_country == "멕시코":
        return {"region": "중남미", "file": f"{REPORT_FOLDER}/MEXICO.pdf", "trend": "니어쇼어링, USMCA 대응", "growth": "2.0%"}
    elif target_country == "브라질":
        return {"region": "중남미", "file": f"{REPORT_FOLDER}/BRAZIL.pdf", "trend": "무역장벽 강화, 인프라 프로젝트", "growth": "1.9%"}

    # 5. 중동/CIS
    elif target_country == "아랍에미리트":
        return {"region": "중동", "file": f"{REPORT_FOLDER}/UAE.pdf", "trend": "AI/디지털 산업, 비석유 부문 육성", "growth": "5.0%"}
    elif target_country == "이란":
        return {"region": "중동", "file": f"{REPORT_FOLDER}/IRAN.pdf", "trend": "경제 제재 대응, 자원 활용", "growth": "1.1%"}
    elif target_country in ["튀르키예", "터키"]:
        return {"region": "중동/유럽", "file": f"{REPORT_FOLDER}/TURKIYE.pdf", "trend": "인플레 완화, 방산 협력", "growth": "3.8%"}
    elif target_country == "러시아":
        return {"region": "CIS", "file": f"{REPORT_FOLDER}/RUSSIA.pdf", "trend": "제재 대응, 동방정책, 물류 재편", "growth": "2.5%"}
    elif target_country == "우크라이나":
        return {"region": "CIS", "file": f"{REPORT_FOLDER}/UKRANIA.pdf", "trend": "전후 재건, EU 통합", "growth": "2~3%"}
    elif target_country == "몽골":
        return {"region": "CIS", "file": f"{REPORT_FOLDER}/MONGOLIA.pdf", "trend": "자원 개발, 경제 회랑", "growth": "5.0%"}

    # 그 외 (권역별 파일 매핑)
    else:
        return {"region": "기타", "file": None, "trend": "글로벌 트렌드 참조", "growth": "-"}

# ==========================================
# 4. 사이드바 (Storytelling Menu)
# ==========================================
def render_sidebar():
    with st.sidebar:
        st.header("🚀 SY GLOBAL TRADING")
        st.caption("AI & Data-Driven Export Strategy")
        st.divider()
        
        # 1. 타겟 설정
        st.subheader("🎯 타겟 설정")
        
        # 국가 선택
        country_list = sorted(list(set(ITEM_DATA_FILES.keys()) | {"영국", "프랑스", "독일", "러시아", "이란", "튀르키예", "브라질", "캐나다"}))
        if "미국" in country_list:
            country_list.insert(0, country_list.pop(country_list.index("미국"))) # 미국을 맨 위로
        
        target_country = st.selectbox("진출 희망 국가", country_list)

   
# -------------------------------------------------------
        # [수정] HS Code 검색 및 6자리 자동 입력 로직
        # -------------------------------------------------------
        
        # 1) 세션 상태 초기화 (값 저장소)
        if 'hs_code_val' not in st.session_state:
            st.session_state['hs_code_val'] = "330499"
         # 2) HS Code 검색창 (접었다 폈다 할 수 있게)
        hs_df = load_hs_code_library()

        # 3. 검색창 (Expander로 작게 숨기기)
        with st.expander("🔍 HS Code 품목명으로 찾기"):
            if not hs_df.empty:
                # 검색용 Selectbox
                search_selection = st.selectbox(
                    "품목명을 검색하세요 (예: 화장품, 반도체)",
                    options=hs_df['Label'].tolist(),
                    index=None,
                    placeholder="키워드 입력..."
                )
                
                # 사용자가 선택을 했을 경우
                if search_selection:
                    # "3304990000 | 기초화장품" 에서 앞의 코드만 추출
                    full_code = search_selection.split(" | ")[0]
                    short_code = full_code[:6]  # 앞 6자리만 추출
                    
                    # 값이 다를 때만 업데이트 (무한 루프 방지)
                    if st.session_state['hs_code_val'] != short_code:
                        st.session_state['hs_code_val'] = short_code
                        st.rerun() # 화면 즉시 새로고침
            else:
                st.warning("HS Code 데이터(CSV)가 없습니다.")

        # 4. 메인 입력란 (위의 검색 결과와 연동됨)
        hs_code = st.text_input(
            "HS Code (6단위)", 
            value=st.session_state['hs_code_val'],
            # key="hs_code_widget", # 위젯 키 설정
            help="위 검색창에서 품목을 찾으면 자동으로 입력됩니다."
        )
        
        # 입력란을 직접 수정했을 때 세션 상태 업데이트 (양방향 동기화)
        if hs_code != st.session_state['hs_code_val']:
            st.session_state['hs_code_val'] = hs_code
        # -------------------------------------------------------
        
        st.divider()
        
        # 2. 시나리오 선택 (질문형)
        st.subheader("📂 수출 전략 시나리오")
        scenario = st.radio(
            "확인하고 싶은 내용은?",
            [
                "1️⃣ 시장성 ➡️ 내 물건, 시장성이 있을까?",
                "2️⃣ 진입장벽 ➡️ 관세와 규제, 뚫을 수 있나? ",
                "3️⃣ 가격전략 ➡️ 얼마에 팔아야 남을까?",
                "4️⃣ 바이어/유통 ➡️ 누구에게 팔까?"
            ]
        )
        
        st.divider()
        
        # 3. AI 무역 비서 (RAG)
        st.subheader("🤖 AI 무역비서")
        user_query = st.text_input("질문 입력", placeholder="예: 미국 화장품 인증 절차는?")
        
        if st.button("전송"):
            if not OPENAI_API_KEY:
                st.error("⚠️ OPENAI_API_KEY가 필요합니다.")
            else:
                with st.spinner("AI가 분석 중입니다..."):
                    # PDF 정보 가져오기
                    region_info = get_region_info(target_country)
                    pdf_context = ""
                    if region_info['file']:
                        pdf_context = extract_text_from_pdf(region_info['file'])
                        if pdf_context:
                            pdf_context = pdf_context[:3000] # 토큰 제한 고려
                    
                    # GPT 호출
                    try:
                        system_msg = f"당신은 KOTRA의 20년차 무역 전문가입니다. {target_country} 시장에 대해 답변하세요."
                        prompt = f"참고 문서:\n{pdf_context}\n\n질문: {user_query}\n\n문서 내용을 바탕으로 구체적으로 답변해줘."
                        
                        response = client.chat.completions.create(
                            model="gpt-4o", # 모델명 확인
                            messages=[
                                {"role": "system", "content": system_msg},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        st.info(response.choices[0].message.content)
                    except Exception as e:
                        st.error(f"AI 호출 오류: {e}")

    return scenario, target_country, hs_code

# ==========================================
# 5. 메인 콘텐츠 (Scenario Handlers)
# ==========================================

# [시나리오 1] 시장성 분석
def render_market_analysis(target_country, hs_code):
    info = get_region_info(target_country)
    
    st.markdown(f'<div class="main-header">📊 1. 시장성 분석: "이 시장, 들어갈 자리가 있나?"</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="insight-box">
        <h4>💡 KOTRA 2026 {target_country} 진출 전망</h4>
        <p style="font-size: 1.1rem;">
        "2026년 <strong>{target_country}</strong> 시장의 핵심 키워드는 <strong>'{info['trend']}'</strong>입니다.<br>
        예상 경제 성장률은 <strong>{info['growth']}</strong>로 전망됩니다."
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    df_trade = None
    status = "INIT"
    market_share = 0

    with col1:
        with st.spinner(f"UN Comtrade에서 {target_country} 시장 데이터를 분석 중..."):
            df_trade, status = fetch_un_comtrade_data(hs_code, target_country)
            
            # (A) API 데이터 성공 시
            if "SUCCESS" in status and df_trade is not None and not df_trade.empty:
                # 상태 메시지에서 연도 추출 (예: "SUCCESS(2023)")
                data_year = status.replace("SUCCESS(", "").replace(")", "")
                st.success(f"✅ 글로벌 무역 데이터 로드 성공 (기준년도: {data_year}, HS: {hs_code})")
                
                # [핵심 수정 4] 문자열 대신 정확한 'partnerCode' 숫자(0, 410)로 데이터 찾기
                # 전세계(0) 데이터 찾기
                world_rows = df_trade[df_trade['partnerCode'] == 0]
                world_val = world_rows['primaryValue'].sum() if not world_rows.empty else 0
                
                # 한국(410) 데이터 찾기
                korea_rows = df_trade[df_trade['partnerCode'] == 410]
                korea_val = korea_rows['primaryValue'].sum() if not korea_rows.empty else 0
                
                # 점유율 계산
                market_share = (korea_val / world_val * 100) if world_val > 0 else 0
                
                # 차트 그리기
                fig = px.bar(
                    df_trade, 
                    x='partnerDesc', 
                    y='primaryValue',
                    title=f"{data_year}년 {target_country} 수입 시장 점유율 (단위: USD)",
                    labels={'primaryValue': '수입액($)', 'partnerDesc': '수출국'},
                    color='partnerDesc',
                    text_auto='.2s',
                    height=600
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                if world_val > 0:
                    st.markdown(f"""
                    <div style='background-color:#f0f9ff; padding:15px; border-radius:10px; margin-top:10px;'>
                        <p style='font-size:1.2rem; margin-bottom:5px;'>
                            🌏 <strong>{target_country}</strong>에서는 이 품목을 전 세계에서 
                            <span style='color:#1e3a8a; font-weight:900; font-size:1.4rem;'>${world_val:,.0f}</span> 수입합니다.
                        </p>
                        <p style='font-size:1.2rem; margin-bottom:0;'>
                            그 중 한국 제품은 
                            <span style='color:#dc2626; font-weight:900; font-size:1.4rem;'>${korea_val:,.0f} ({market_share:.2f}%)</span> 입니다.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ 전세계 수입 데이터가 0으로 집계되었습니다. (데이터 누락 가능성)")

            # (B) API 실패 시 -> KOTRA CSV 사용
            else:
                if status == "API_KEY_MISSING":
                    st.warning("⚠️ UN_COMTRADE_KEY가 없습니다. CSV 데이터를 사용합니다.")
                else:
                    st.warning(f"⚠️ 실시간 데이터 호출 실패 ({status}). KOTRA 내부 데이터를 표시합니다.")
                
                file_key = ITEM_DATA_FILES.get(target_country)
                df_csv = load_csv_data(file_key) if file_key else None
                
                if df_csv is not None:
                     val_cols = [c for c in df_csv.columns if '수출금액' in c or 'Value' in c]
                     if val_cols:
                        top_items = df_csv.head(10)
                        x_col = df_csv.columns[3] if len(df_csv.columns) > 3 else df_csv.columns[0]
                        fig = px.bar(top_items, x=x_col, y=val_cols[0], 
                                     title=f"대{target_country} 주요 수출 품목 (KOTRA 데이터)",
                                     color=val_cols[0],
                                     height=500)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("표시할 KOTRA 데이터가 없습니다.")

    # [수정] 점유율에 따른 동적 멘트 설정
        if "SUCCESS" in status and df_trade is not None:
             # 점유율 구간별 메시지 로직
             if market_share >= 20:
                 share_msg = "🏆 시장 주도 (압도적)"
                 color = "normal" # 초록색
             elif market_share >= 10:
                 share_msg = "🚀 주요 수출국 (상위권)"
                 color = "normal"
             elif market_share >= 5:
                 share_msg = "📈 성장세 (안정권)"
                 color = "normal"
             elif market_share >= 1:
                 share_msg = "진입 초기 (확대 필요)"
                 color = "off" # 회색
             else:
                 share_msg = "미미함 (개척 필요)"
                 color = "inverse" # 빨간색

             st.metric(label="한국 제품 시장 점유율", value=f"{market_share:.2f}%", delta=share_msg, delta_color=color)
        else:
             st.metric(label="시장 점유율", value="-", delta="데이터 없음")
        
        st.markdown("---")
        st.caption(f"📂 분석 리포트: {info['file']}")
        if info['file'] and os.path.exists(info['file']):
            with open(info['file'], "rb") as pdf_file:
                st.download_button(label="PDF 원문 다운로드", data=pdf_file, file_name=os.path.basename(info['file']))


# [시나리오 2] 진입장벽 & 전략
def render_barriers_strategy(target_country, hs_code):
    info = get_region_info(target_country)
    st.markdown(f'<div class="main-header">2. Risk Guard: AI SWOT & 규제 리스크 분석</div>', unsafe_allow_html=True)
    
    # -------------------------------------------------------------
    # 1. AI 분석 로직
    # -------------------------------------------------------------
    
    # 기본값
    analysis_result = {
        "risk_color": "🟡",
        "risk_level": "분석 대기",
        "risk_reason": "AI가 규제 데이터를 정밀 분석 중입니다...",
        "tip": "<b>현지 규정 교차 검증 필요</b><br>관세청 및 인증 기관의 최신 정보를 확인하세요.",
        "swot": {
            "S": "<b>품질 경쟁력 보유</b><br>한국 제품에 대한 긍정적 인식 활용 가능",
            "W": "<b>가격 경쟁 심화</b><br>물류비 및 관세로 인한 가격 상승 부담",
            "O": "<b>시장 트렌드 부합</b><br>현지 소비자의 니즈와 일치하는 특성",
            "T": "<b>통상 규제 불확실성</b><br>환율 변동 및 정책 변화 리스크"
        }
    }

    if OPENAI_API_KEY:
        try:
            pdf_context = "관련 보고서 없음"
            if info['file']:
                pdf_context = extract_text_from_pdf(info['file'], max_pages=3)
                if pdf_context: pdf_context = pdf_context[:1500]

            prompt = f"""
            당신은 까다로운 'SY 글로벌 커넥트'의 수석 무역 컨설턴트입니다. 아래 정보를 바탕으로 {target_country}에 {hs_code} 품목을 수출할 때의 전략을 HTML 태그를 섞어서 작성하세요. 수출 난이도를 엄격하게 평가하세요.
            
            [분석 대상]
            - 국가: {target_country}
            - HS Code: {hs_code}
            - 국가 트렌드: {info['trend']}
            - 보고서 내용: {pdf_context}

            [지시사항]
            1. **진입장벽 평가(엄격하게)**: 
               - 인증(FDA, CE, 할랄 등), 관세, 비관세 장벽이 조금이라도 복잡하면 '🟡(보통)' 또는 '🔴(높음)'으로 판정하세요.
               - 아무 규제 없이 누구나 팔 수 있는 경우에만 '🟢(낮음)'을 주세요.
            2. **맞춤형 Tip**: 
               - 입력된 HS Code({hs_code})에 딱 맞는 구체적인 조언을 1줄 작성하세요.
               - 첫 줄: 무엇을 준비해야 하는지 핵심을 <b>태그로 감싸서 볼드체</b>로 작성.
               - 그 뒤: <br>태그를 2번 사용하여 줄을 바꾸고, 구체적인 실행 정보 3줄 작성.

            3. **SWOT 분석**: 
               - 각 항목(S,W,O,T)의 첫 줄: 핵심 내용을 <b>태그로 감싸서 볼드체</b>로 작성.
               - 그 뒤: <br>태그로 줄을 바꾸고, 2~3줄의 상세 부연 설명 추가.

            [출력 포맷 (JSON)]
            {{
                "risk_color": "🔴" or "🟡" or "🟢",
                "risk_level": "진입장벽 높음/보통/낮음",
                "risk_reason": "판단 근거 (한 문장)",
                "tip": "<b>핵심준비사항</b><br><br>상세내용 1... 상세내용 2...",
                "swot": {{
                    "S": "<b>핵심강점입니다.</b><br>상세설명...",
                    "W": "<b>핵심약점입니다.</b><br>상세설명...",
                    "O": "<b>핵심기회입니다.</b><br>상세설명...",
                    "T": "<b>핵심위협입니다.</b><br>상세설명..."
                }}
            }}
            """
            
            with st.spinner(f"{target_country}의 법령 및 규제 데이터를 교차 검증 중입니다..."):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                analysis_result = json.loads(response.choices[0].message.content)

        except Exception as e:
            st.warning(f"AI 분석 중 오류가 발생하여 기본 정보를 표시합니다. ({str(e)})")
    else:
        st.warning("⚠️ OPENAI_API_KEY가 없습니다. 정확한 분석을 위해 키를 설정해주세요.")

    # -------------------------------------------------------------
    # 2. UI 렌더링 (신호등 & Tip)
    # -------------------------------------------------------------
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="sub-header">🚦 진입 신호등</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"""
            <div style='text-align: center; margin: 10px 0;'>
                <span style='font-size: 4rem;'>{analysis_result.get('risk_color', '🟡')}</span>
                <h3 style='margin-top:0;'>{analysis_result.get('risk_level', '분석 대기')}</h3>
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"📝 **판단 근거:** {analysis_result.get('risk_reason', '-')}")

    with col2:
        st.markdown(f'<div class="sub-header">💡 {hs_code} 맞춤형 전략</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background-color: #e8f0fe; padding: 20px; border-radius: 10px; border-left: 5px solid #4285f4;">
            <strong style="color: #1967d2; font-size: 1.1em;">[SY 글로벌 커넥트의 조언]</strong>
            <div style="margin-top: 10px; line-height: 1.6;">
                {analysis_result.get('tip', '-')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: right; margin-top: 5px;'>
            <small style='color:grey'>
            * 규제 정보 교차 확인: <a href='https://dream.kotra.or.kr/' target='_blank'>KOTRA 해외시장뉴스</a>
            </small>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 3. UI 렌더링 (SWOT)
    # -------------------------------------------------------------
    st.markdown("---")
    st.markdown('<div class="sub-header">SWOT 정밀 분석</div>', unsafe_allow_html=True)
    
    swot = analysis_result.get('swot', {})
    
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    with row1_col1:
        with st.container(border=True):
            st.markdown("#### 💪 Strength (강점)")
            st.markdown(f"<div style='background-color:#e3f2fd; padding:15px; border-radius:5px; color:#0d47a1; line-height:1.5;'>{swot.get('S', '-')}</div>", unsafe_allow_html=True)

    with row1_col2:
        with st.container(border=True):
            st.markdown("#### 🔻 Weakness (약점)")
            st.markdown(f"<div style='background-color:#fff3e0; padding:15px; border-radius:5px; color:#e65100; line-height:1.5;'>{swot.get('W', '-')}</div>", unsafe_allow_html=True)

    with row2_col1:
        with st.container(border=True):
            st.markdown("#### 🚀 Opportunity (기회)")
            st.markdown(f"<div style='background-color:#e8f5e9; padding:15px; border-radius:5px; color:#1b5e20; line-height:1.5;'>{swot.get('O', '-')}</div>", unsafe_allow_html=True)

    with row2_col2:
        with st.container(border=True):
            st.markdown("#### ⚠️ Threat (위협)")
            st.markdown(f"<div style='background-color:#ffebee; padding:15px; border-radius:5px; color:#b71c1c; line-height:1.5;'>{swot.get('T', '-')}</div>", unsafe_allow_html=True)

# [시나리오 3] 가격 전략
def render_pricing(target_country, hs_code):
    st.markdown(f'<div class="main-header">💰 3. 가격 전략: "얼마에 팔아야 남을까?"</div>', unsafe_allow_html=True)
    st.info(f"💡 **{target_country}**의 대표 이커머스(Amazon) 데이터를 분석하여 최적 가격을 제안합니다.")
    
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        keyword = st.text_input("상품 검색 키워드 (영문)", "Korean Cosmetics")
    with col_btn:
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True) # 버튼 줄맞춤
        search_btn = st.button("가격 분석 시작", use_container_width=True)

    if search_btn:
        with st.spinner(f"Amazon({COUNTRY_TO_AMAZON.get(target_country, 'Global')})에서 경쟁사 가격을 스캔 중..."):
            
            # API 호출 (혹은 Mock 데이터 반환)
            data = get_amazon_pricing(keyword, target_country)
            
            # 상태에 따른 알림 표시
            if data['status'] == "SUCCESS":
                st.success(f"✅ 실시간 Amazon 데이터 분석 완료 ({len(data['products'])}개 상품)")
            else:
                st.warning("⚠️ Amazon API 연결이 원활하지 않아 '예상 시뮬레이션 데이터'를 표시합니다.")

            # 1. 가격 지표 카드
            curr = data['currency']
            c1, c2, c3 = st.columns(3)
            c1.metric("최저가 (Low)", f"{data['min']:.2f} {curr}", delta="- 경쟁 우위")
            c2.metric("평균가 (Avg)", f"{data['average']:.2f} {curr}")
            c3.metric("최고가 (High)", f"{data['max']:.2f} {curr}", delta="+ 프리미엄")
            
            # 2. 가격 분포 차트
            st.subheader("📊 경쟁 제품 가격 포지셔닝")
            df_price = pd.DataFrame(data['products'])
            
            fig = px.bar(
                df_price, 
                x='title', 
                y='price', 
                color='price',
                text_auto='.2s',
                title=f"'{keyword}' 경쟁사 가격 분포 ({curr})",
                labels={'price': f'가격 ({curr})', 'title': '상품명'},
                height=500
            )
            fig.update_xaxes(showticklabels=False) # 상품명이 너무 길어서 X축 라벨 숨김
            st.plotly_chart(fig, use_container_width=True)
            
            # 3. 상세 리스트 (Expander)
            with st.expander("📦 경쟁 제품 상세 리스트 보기", expanded=True):
                # 데이터프레임 표시 (링크는 클릭 가능하게)
                st.dataframe(
                    df_price[['title', 'price', 'currency']],
                    use_container_width=True,
                    hide_index=True
                )

# [시나리오 4] 바이어 & 실행
def render_action_plan(target_country):
    st.markdown(f'<div class="main-header">🤝 4. 실행 전략: "누구를 만나야 하나?"</div>', unsafe_allow_html=True)
    
    st.subheader("🏢 유력 바이어 발굴 채널")
    
    # 1. CSV 기반 사이트 추천
    df_sites = load_csv_data(SITE_CSV_FILE)
    matched_sites = pd.DataFrame()
    if df_sites is not None:
        # 국가명이 포함된 데이터 필터링
        matched_sites = df_sites[df_sites['국가'].astype(str).str.contains(target_country, na=False)]
    
    if not matched_sites.empty:
        for idx, row in matched_sites.iterrows():
            title = row.get('제목', 'Unknown')
            content = row.get('본문내용', '')
            url = extract_url(content)
            
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{title}**")
                    with st.expander("상세 정보"):
                        st.write(content)
                with c2:
                    if url:
                        st.link_button("사이트 이동", url)
                    else:
                        st.button("URL 없음", disabled=True, key=f"btn_{idx}")
    else:
        st.info(f"'{target_country}' 관련 등록된 로컬 사이트가 없습니다. 구글 검색을 활용하세요.")

    st.divider()
    
    # 2. 구글 실시간 검색 (SerpApi)
    st.subheader("🔍 구글 실시간 바이어 검색")
    search_query = st.text_input("구글 검색어", f"{target_country} importers distributors cosmetics")
    
    if st.button("바이어 검색 (SerpApi)"):
        results = get_google_buyers(search_query, SERPAPI_KEY)
        if results:
            for res in results:
                st.markdown(f"- **[{res['title']}]({res['link']})**")
                st.caption(res['snippet'])
        else:
            if not SERPAPI_KEY:
                st.warning("⚠️ SERPAPI_KEY가 설정되지 않아 검색할 수 없습니다.")
            else:
                st.warning("검색 결과가 없습니다.")

# ==========================================
# 6. Main Function
# ==========================================
def main():
    scenario, target_country, hs_code = render_sidebar()
    
    if "1️⃣" in scenario:
        render_market_analysis(target_country, hs_code)
    elif "2️⃣" in scenario:
        render_barriers_strategy(target_country, hs_code)
    elif "3️⃣" in scenario:
        render_pricing(target_country, hs_code)
    elif "4️⃣" in scenario:
        render_action_plan(target_country)

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #718096; font-size: 0.9em;'>
        <p>Global E-commerce SEO & Marketing Solution</p>
        <p>Developed by <strong>Seyeon Global Connect</strong> | Powered by KOTRA AX</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

