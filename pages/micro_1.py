"""
UN Comtrade + Amazon SerpApi 통합 분석 모듈
아마존 진출 전략 솔루션 대시보드 + 경쟁사 분석

구성:
1. [기반] 품목명으로 HS Code 찾기
2. [STEP 1] 거시적 시장 분석 (UN Comtrade 수출입 통계)
3. [STEP 2] 미시적 현지 분석 (Amazon 실시간 가격 조사)
4. [STEP 3] 경쟁사 Top 15 상세 분석 (신규 추가)
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv
from plotly.subplots import make_subplots
from urllib.parse import quote
import re
import openai
from openai import OpenAI

# ==================== 설정 및 상수 ====================

CACHE_EXPIRY_DAYS = 7
AMAZON_CACHE_FILE = "amazon_cache.json"

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
HS_CODE_CSV_PATH = os.path.join(MODULE_DIR, "HScode_customs.csv")


CATEGORY_HINTS = {
    "화장품": ["3303", "3304", "3305", "3306", "3307"],
    "코스메틱": ["3303", "3304", "3305", "3306", "3307"],
    "향수": ["3303"],
    "메이크업": ["3304"],
    "스킨케어": ["3304"],
    "샴푸": ["3305"],
    "치약": ["3306"],
    "비누": ["3401"],
    "세제": ["3402"],
}

PACKAGING_NEGATIVE_KEYWORDS = [
    "포장", "포장용", "원지", "카톤", "상자", "필름", "라벨", "용기", "병", "캡", "뚜껑",
    "케이스", "스티커", "박스", "포장재", "봉투"
]

# ==================== 환경 설정 ====================

def _get_env_or_session(key: str) -> Optional[str]:
    if key in st.session_state and st.session_state.get(key):
        return str(st.session_state.get(key)).strip()
    env_val = os.getenv(key)
    if env_val:
        return str(env_val).strip()
    return None


def get_settings() -> Dict[str, Optional[str]]:
    load_dotenv()
    
    primary = _get_env_or_session("UN_COMTRADE_KEY")
    if not primary:
        primary = _get_env_or_session("UN_API_KEY")
        
    secondary = _get_env_or_session("UN_SECOND_API_KEY")
    openai_key = _get_env_or_session("OPENAI_API_KEY")
    serpapi = _get_env_or_session("SERPAPI_KEY")  # ✅ 수정: RAINFOREST_API → SERPAPI_KEY
    
    cache_dir = _get_env_or_session("CACHE_DIR") or "./comtrade_cache"
    cache_dir = str(cache_dir)
    
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir, exist_ok=True)
        except Exception:
            cache_dir = "./comtrade_cache_temp"
            os.makedirs(cache_dir, exist_ok=True)
    
    return {
        "PRIMARY_KEY": primary,
        "SECONDARY_KEY": secondary,
        "OPENAI_KEY": openai_key,
        "SERPAPI": serpapi,  # ✅ 수정
        "CACHE_DIR": cache_dir,
    }

# ==================== OpenAI 호출 함수 ====================

def generate_openai_response(prompt: str) -> str:
    """OpenAI API를 사용하여 분석 리포트를 생성합니다."""
    settings = get_settings()
    api_key = settings.get("OPENAI_KEY")
    
    if not api_key:
        return "❌ OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요."
    
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 글로벌 이커머스 및 무역 전문 컨설턴트입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI 리포트 생성 중 오류 발생: {str(e)}"

# ==================== 수량 추출 및 가성비 분석 ====================

def extract_quantity_val(title: str) -> int:
    """제품명에서 수량 정보를 '숫자'로만 추출하여 가성비 계산에 활용합니다."""
    match = re.search(r'(\d+)\s?(?:Pack|Count|Pairs|Items|Pcs|Units)', title, re.IGNORECASE)
    
    if match:
        return int(match.group(1))
    
    nums = re.findall(r'\d+', title)
    if nums:
        val = int(nums[-1])
        return val if val > 0 else 1
        
    return 1

def summarize_description_backup(asin: str, product_title: str, price: float) -> dict:
    """제품 상세 정보로 가성비 및 한국 진출 전략 분석 (더미 데이터 모드)"""
    
    domain = st.session_state.get("amazon_amazon_domain", "amazon.com")
    
    # 더미 제품 특징 데이터
    dummy_features = [
        "Premium quality ingredients for best results",
        "Long-lasting formula that stays fresh all day",
        "Dermatologist tested and approved",
        "Suitable for all skin types",
        "Easy to apply with smooth texture",
        "Paraben-free and cruelty-free formula",
        "Travel-friendly packaging included"
    ]
    
    bullets = "\n".join(dummy_features)
    
    qty = extract_quantity_val(product_title)
    safe_price = price if price and price > 0 else 0
    unit_price = safe_price / qty if qty > 0 else 0
    
    country_info = {
        "amazon.com": {"name": "미국", "focus": "성분 투명성, FDA 규정, 대용량 가성비, 다양한 인종별 피부톤 대응"},
        "amazon.co.jp": {"name": "일본", "focus": "패키징 디자인의 정교함, 후생노동성(MHLW) 규정, 미백/보습 세분화, 소량 패키지 선호"},
        "amazon.co.uk": {"name": "영국", "focus": "친환경/비건 인증, 유럽 화장품 규정(CPNP), 전통적 브랜드 신뢰도, 지속 가능한 포장"},
        "amazon.de": {"name": "독일", "focus": "더마테스트(Dermatest) 인증 중요도, 유기농 성분, 실용적 패키징, 성분 분석 결과 중시"}
    }
    
    selected_country = country_info.get(domain, {"name": "해외", "focus": "현지 규정 및 소비자 선호도"})

    prompt = f"""
    당신은 한국 기업의 {selected_country['name']} 아마존 진출을 돕는 수출 전략 컨설턴트입니다.
    현지 1위 제품을 '정복해야 할 타겟'으로 설정하여 아래 데이터를 분석하세요.

    [분석 데이터]
    - 진출 대상국: {selected_country['name']} (플랫폼: {domain})
    - 현지 시장 특성 및 규제: {selected_country['focus']}
    - 경쟁사 제품명: {product_title}
    - 현지 판매가: ${safe_price} ({qty}개입, 개당 ${unit_price:.2f})
    - 경쟁사 제품 특징: {bullets[:500]}

    [수출 전략 리포트 구성 가이드라인]
    1. {selected_country['name']} 시장 1위 비결: 이 제품의 현지 성공 공식 분석
    2. 한국 기업의 기회: 경쟁사 제품 대비 한국 제품이 가질 수 있는 우위(성분, 디자인, 리뷰 약점 공략)
    3. 수출 가격 포지셔닝: 경쟁사 단가(${unit_price:.2f}) 기준, 한국 기업의 적정 수출가 제안
    4. 현지화 및 규제 대응: {selected_country['name']} 수출 시 필수 인증(FDA, MHLW, CPNP 등) 및 패키징 조언
    """
        
    analysis_report = generate_openai_response(prompt)
    
    return {
        "analysis": analysis_report,
        "unit_price": unit_price,
        "qty": qty
    }
    
# ==================== 텍스트 유틸 ====================

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = str(s).lower()
    s = re.sub(r"[\(\)\[\]\{\}]", " ", s)
    s = re.sub(r"[^0-9a-zA-Z가-힣\s·ㆍ\-_]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def has_any(text: str, keywords: List[str]) -> bool:
    return any(k in text for k in keywords)


# ==================== 헬퍼 함수 (Comtrade) ====================

# def get_country_name_comtrade(code) -> str:
    if pd.isna(code):
        return "알 수 없음"
    try:
        code = int(code)
        return COUNTRY_CODE_MAP.get(code, f"국가코드 {code}")
    except Exception:
        return "알 수 없음"


# ==================== 캐싱 (Comtrade) ====================

def get_cache_filename(cache_dir: str, hs_code: str, reporter_code: str, flow_code: str, data_type: str) -> str:
    return os.path.join(cache_dir, f"{hs_code}_{reporter_code}_{flow_code}_{data_type}.json")


def is_cache_valid(cache_file: str) -> bool:
    if not os.path.exists(cache_file):
        return False
    file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
    return datetime.now() - file_time < timedelta(days=CACHE_EXPIRY_DAYS)


def load_from_cache(cache_file: str) -> Optional[pd.DataFrame]:
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data:
                return pd.DataFrame(data)
    except Exception:
        return None
    return None


def save_to_cache(cache_file: str, df: pd.DataFrame) -> bool:
    try:
        if df is not None and len(df) > 0:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(df.to_dict("records"), f, ensure_ascii=False)
            return True
    except Exception:
        return False
    return False


def get_cache_info(cache_dir: str) -> Dict[str, float]:
    if not os.path.exists(cache_dir):
        return {"count": 0, "size_mb": 0.0}
    files = [f for f in os.listdir(cache_dir) if f.endswith(".json")]
    total_size = sum(os.path.getsize(os.path.join(cache_dir, f)) for f in files)
    return {"count": len(files), "size_mb": round(total_size / (1024 * 1024), 2)}


def clear_cache(cache_dir: str) -> bool:
    try:
        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                if file.endswith(".json"):
                    os.remove(os.path.join(cache_dir, file))
        return True
    except Exception:
        return False


# ==================== Amazon SerpApi ====================

def get_dummy_amazon_data(query: str, amazon_domain: str = "amazon.com") -> List[dict]:
    """검색어와 도메인에 따른 더미 데이터 생성"""
    
    # 도메인별 통화 및 가격 배율
    domain_config = {
        "amazon.com": {"currency": "$", "multiplier": 1.0, "lang": "en"},
        "amazon.co.jp": {"currency": "¥", "multiplier": 150.0, "lang": "jp"},
        "amazon.co.uk": {"currency": "£", "multiplier": 0.8, "lang": "en"},
        "amazon.de": {"currency": "€", "multiplier": 0.9, "lang": "de"},
    }
    
    config = domain_config.get(amazon_domain, domain_config["amazon.com"])
    
    # 카테고리별 더미 제품 데이터
    dummy_products = {
        "cosmetic": [
            {"name": "SHEGLAM Color Bloom Liquid Blush Makeup Set", "brand": "SHEGLAM", "base_price": 15.99, "rating": 4.5, "reviews": 12847, "asin": "B0BXYZ1234"},
            {"name": "Maybelline New York Instant Age Rewind Set", "brand": "Maybelline", "base_price": 24.99, "rating": 4.4, "reviews": 89234, "asin": "B0BXYZ1235"},
            {"name": "e.l.f. Cosmetics Flawless Finish Foundation Kit", "brand": "e.l.f.", "base_price": 18.00, "rating": 4.3, "reviews": 45621, "asin": "B0BXYZ1236"},
            {"name": "NYX Professional Makeup Ultimate Set 16 Colors", "brand": "NYX", "base_price": 22.00, "rating": 4.6, "reviews": 34521, "asin": "B0BXYZ1237"},
            {"name": "COVERGIRL Clean Fresh Skincare Set", "brand": "COVERGIRL", "base_price": 29.99, "rating": 4.2, "reviews": 23456, "asin": "B0BXYZ1238"},
            {"name": "L'Oreal Paris True Match Foundation Set", "brand": "L'Oreal", "base_price": 32.99, "rating": 4.4, "reviews": 67890, "asin": "B0BXYZ1239"},
            {"name": "Revlon ColorStay Makeup Collection", "brand": "Revlon", "base_price": 27.50, "rating": 4.1, "reviews": 54321, "asin": "B0BXYZ1240"},
            {"name": "Neutrogena Hydro Boost Skincare Set", "brand": "Neutrogena", "base_price": 35.99, "rating": 4.5, "reviews": 78901, "asin": "B0BXYZ1241"},
            {"name": "CeraVe Daily Skincare Routine Bundle", "brand": "CeraVe", "base_price": 42.00, "rating": 4.7, "reviews": 123456, "asin": "B0BXYZ1242"},
            {"name": "The Ordinary Skincare Starter Set", "brand": "The Ordinary", "base_price": 38.00, "rating": 4.6, "reviews": 98765, "asin": "B0BXYZ1243"},
            {"name": "Clinique 3-Step Skincare System", "brand": "Clinique", "base_price": 45.00, "rating": 4.3, "reviews": 34567, "asin": "B0BXYZ1244"},
            {"name": "Olay Regenerist Micro-Sculpting Set", "brand": "Olay", "base_price": 48.99, "rating": 4.4, "reviews": 56789, "asin": "B0BXYZ1245"},
            {"name": "Korean Beauty 10-Step Skincare Kit", "brand": "K-Beauty", "base_price": 55.00, "rating": 4.5, "reviews": 23456, "asin": "B0BXYZ1246"},
            {"name": "Fenty Beauty Soft Matte Foundation Set", "brand": "Fenty Beauty", "base_price": 52.00, "rating": 4.6, "reviews": 87654, "asin": "B0BXYZ1247"},
            {"name": "Charlotte Tilbury Magic Set", "brand": "Charlotte Tilbury", "base_price": 65.00, "rating": 4.7, "reviews": 45678, "asin": "B0BXYZ1248"},
        ],
        "shampoo": [
            {"name": "Pantene Pro-V Daily Moisture Renewal Shampoo", "brand": "Pantene", "base_price": 12.99, "rating": 4.5, "reviews": 45678, "asin": "B0CSHP1234"},
            {"name": "Head & Shoulders Clinical Strength Shampoo", "brand": "Head & Shoulders", "base_price": 15.99, "rating": 4.4, "reviews": 67890, "asin": "B0CSHP1235"},
            {"name": "OGX Biotin & Collagen Shampoo Set", "brand": "OGX", "base_price": 18.99, "rating": 4.3, "reviews": 34521, "asin": "B0CSHP1236"},
            {"name": "Dove Nutritive Solutions Shampoo Bundle", "brand": "Dove", "base_price": 14.50, "rating": 4.2, "reviews": 89012, "asin": "B0CSHP1237"},
            {"name": "TRESemmé Keratin Smooth Shampoo Pack", "brand": "TRESemmé", "base_price": 16.99, "rating": 4.1, "reviews": 23456, "asin": "B0CSHP1238"},
            {"name": "Moroccanoil Hydrating Shampoo", "brand": "Moroccanoil", "base_price": 28.00, "rating": 4.6, "reviews": 56789, "asin": "B0CSHP1239"},
            {"name": "Olaplex No.4 Bond Maintenance Shampoo", "brand": "Olaplex", "base_price": 30.00, "rating": 4.7, "reviews": 78901, "asin": "B0CSHP1240"},
            {"name": "Aussie Miracle Moist Shampoo 3-Pack", "brand": "Aussie", "base_price": 19.99, "rating": 4.3, "reviews": 34567, "asin": "B0CSHP1241"},
            {"name": "Herbal Essences Bio:Renew Shampoo Set", "brand": "Herbal Essences", "base_price": 17.50, "rating": 4.2, "reviews": 45678, "asin": "B0CSHP1242"},
            {"name": "Redken All Soft Shampoo for Dry Hair", "brand": "Redken", "base_price": 25.00, "rating": 4.5, "reviews": 23456, "asin": "B0CSHP1243"},
            {"name": "Briogeo Don't Despair Repair Shampoo", "brand": "Briogeo", "base_price": 36.00, "rating": 4.6, "reviews": 12345, "asin": "B0CSHP1244"},
            {"name": "Living Proof Full Shampoo", "brand": "Living Proof", "base_price": 32.00, "rating": 4.4, "reviews": 34567, "asin": "B0CSHP1245"},
            {"name": "Pureology Hydrate Shampoo", "brand": "Pureology", "base_price": 38.00, "rating": 4.5, "reviews": 45678, "asin": "B0CSHP1246"},
            {"name": "Function of Beauty Custom Shampoo", "brand": "Function of Beauty", "base_price": 29.99, "rating": 4.3, "reviews": 56789, "asin": "B0CSHP1247"},
            {"name": "Kérastase Nutritive Shampoo", "brand": "Kérastase", "base_price": 42.00, "rating": 4.7, "reviews": 23456, "asin": "B0CSHP1248"},
        ],
        "default": [
            {"name": f"Premium {query.title()} Product Set - Professional Grade", "brand": "TopBrand", "base_price": 29.99, "rating": 4.5, "reviews": 15678, "asin": "B0CDEF1234"},
            {"name": f"Essential {query.title()} Collection - Best Seller", "brand": "EssentialCo", "base_price": 24.99, "rating": 4.4, "reviews": 23456, "asin": "B0CDEF1235"},
            {"name": f"Deluxe {query.title()} Bundle - Value Pack", "brand": "DeluxeBrand", "base_price": 34.99, "rating": 4.3, "reviews": 12345, "asin": "B0CDEF1236"},
            {"name": f"Professional {query.title()} Kit - Complete Set", "brand": "ProLine", "base_price": 39.99, "rating": 4.6, "reviews": 34567, "asin": "B0CDEF1237"},
            {"name": f"Natural {query.title()} Organic Collection", "brand": "NaturalCo", "base_price": 27.50, "rating": 4.2, "reviews": 8901, "asin": "B0CDEF1238"},
            {"name": f"Budget {query.title()} Starter Pack", "brand": "ValueBrand", "base_price": 15.99, "rating": 4.1, "reviews": 45678, "asin": "B0CDEF1239"},
            {"name": f"Luxury {query.title()} Premium Edition", "brand": "LuxuryLine", "base_price": 55.00, "rating": 4.7, "reviews": 7890, "asin": "B0CDEF1240"},
            {"name": f"Everyday {query.title()} Daily Use Set", "brand": "DailyBrand", "base_price": 19.99, "rating": 4.3, "reviews": 56789, "asin": "B0CDEF1241"},
            {"name": f"Advanced {query.title()} Formula Plus", "brand": "AdvancedCo", "base_price": 32.00, "rating": 4.4, "reviews": 23456, "asin": "B0CDEF1242"},
            {"name": f"Classic {query.title()} Traditional Set", "brand": "ClassicBrand", "base_price": 22.50, "rating": 4.2, "reviews": 12345, "asin": "B0CDEF1243"},
            {"name": f"Modern {query.title()} Innovation Series", "brand": "ModernCo", "base_price": 42.00, "rating": 4.5, "reviews": 34567, "asin": "B0CDEF1244"},
            {"name": f"Eco-Friendly {query.title()} Green Edition", "brand": "EcoBrand", "base_price": 28.99, "rating": 4.4, "reviews": 8901, "asin": "B0CDEF1245"},
            {"name": f"Travel Size {query.title()} Mini Set", "brand": "TravelCo", "base_price": 14.99, "rating": 4.1, "reviews": 45678, "asin": "B0CDEF1246"},
            {"name": f"Family {query.title()} Mega Pack", "brand": "FamilyBrand", "base_price": 48.00, "rating": 4.3, "reviews": 23456, "asin": "B0CDEF1247"},
            {"name": f"Sensitive {query.title()} Gentle Care", "brand": "GentleCo", "base_price": 26.50, "rating": 4.5, "reviews": 12345, "asin": "B0CDEF1248"},
        ]
    }
    
    # 검색어에 따른 제품 선택
    query_lower = query.lower()
    if "cosmetic" in query_lower or "makeup" in query_lower or "beauty" in query_lower or "skin" in query_lower:
        products = dummy_products["cosmetic"]
    elif "shampoo" in query_lower or "hair" in query_lower or "conditioner" in query_lower:
        products = dummy_products["shampoo"]
    else:
        products = dummy_products["default"]
    
    # 결과 생성
    results = []
    for p in products:
        adjusted_price = round(p["base_price"] * config["multiplier"], 2)
        results.append({
            "제품명": p["name"],
            "브랜드": p["brand"],
            "가격": adjusted_price,
            "별점": p["rating"],
            "리뷰수": p["reviews"],
            "asin": p["asin"],
            "링크": f"https://{amazon_domain}/dp/{p['asin']}",
        })
    
    return results


def fetch_amazon_market_data(query: str, amazon_domain: str = "amazon.com") -> Optional[List[dict]]:
    """아마존 제품 검색 (더미 데이터 모드)"""
    
    cache_key = f"{amazon_domain}_{query}"
    
    # 캐시 확인
    if os.path.exists(AMAZON_CACHE_FILE):
        try:
            with open(AMAZON_CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}
    else:
        cache = {}
    
    if cache_key in cache:
        st.info("✅ 아마존 데이터 캐시에서 로드!")
        return cache[cache_key]
    
    # 더미 데이터 사용
    st.info("🔄 더미 데이터 모드로 실행 중... (SerpApi 비활성화)")
    
    try:
        results = get_dummy_amazon_data(query, amazon_domain)
        
        # 캐시 저장
        cache[cache_key] = results
        with open(AMAZON_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        
        st.success(f"✅ {len(results)}개 제품 데이터 로드 완료!")
        return results
    
    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류: {e}")
        return None


def get_dummy_reviews() -> List[dict]:
    """더미 리뷰 데이터 생성"""
    dummy_reviews = [
        {"rating": 5, "title": "Excellent product!", "body": "This is the best product I've ever used. Great quality and fast shipping. Love it! Works perfectly and lasts long.", "verified": True},
        {"rating": 5, "title": "Highly recommend", "body": "Amazing product! Exceeded my expectations. The quality is excellent and it arrived quickly.", "verified": True},
        {"rating": 4, "title": "Good value for money", "body": "Very good product overall. Works well and the price is reasonable. Would buy again.", "verified": True},
        {"rating": 5, "title": "Perfect!", "body": "Exactly what I was looking for. Great quality, perfect size, and amazing results.", "verified": True},
        {"rating": 4, "title": "Nice product", "body": "Good quality product. A bit expensive but worth it. Shipping was fast.", "verified": True},
        {"rating": 3, "title": "It's okay", "body": "Product is decent but not as good as I expected. Average quality.", "verified": True},
        {"rating": 5, "title": "Love this!", "body": "Best purchase I've made in a while. Works great and the quality is superb.", "verified": True},
        {"rating": 2, "title": "Disappointed", "body": "Not what I expected. Quality is poor and it doesn't work as advertised.", "verified": False},
        {"rating": 4, "title": "Good but could be better", "body": "Overall satisfied with the product. Works well but packaging could be improved.", "verified": True},
        {"rating": 5, "title": "5 stars!", "body": "Amazing! Perfect for my needs. Would definitely recommend to others.", "verified": True},
        {"rating": 1, "title": "Terrible", "body": "Worst product ever. Broke after one use. Waste of money. Don't buy this.", "verified": False},
        {"rating": 4, "title": "Pretty good", "body": "Good product for the price. Does what it's supposed to do. Happy with my purchase.", "verified": True},
        {"rating": 5, "title": "Outstanding quality", "body": "The quality is excellent. Best product in this category. Highly recommend!", "verified": True},
        {"rating": 3, "title": "Average", "body": "It's an average product. Nothing special but gets the job done.", "verified": True},
        {"rating": 4, "title": "Satisfied customer", "body": "Good product overall. Fast delivery and works as expected. Would recommend.", "verified": True},
        {"rating": 2, "title": "Not great", "body": "Product arrived late and quality is not as good as shown in pictures. Disappointed.", "verified": True},
        {"rating": 5, "title": "Fantastic!", "body": "Absolutely love this product! Great value, amazing quality. Will buy again.", "verified": True},
        {"rating": 4, "title": "Recommended", "body": "Good purchase. Product works well and shipping was quick. Happy customer.", "verified": True},
        {"rating": 3, "title": "Just okay", "body": "Product is just okay. Not bad but not great either. Expected better quality.", "verified": False},
        {"rating": 5, "title": "Perfect gift", "body": "Bought this as a gift and they loved it! Great quality and beautiful packaging.", "verified": True},
    ]
    return dummy_reviews


def fetch_product_reviews(asin: str, amazon_domain: str = "amazon.com") -> Optional[List[dict]]:
    """제품 리뷰 가져오기 (더미 데이터 모드)"""
    
    REVIEWS_CACHE_FILE = "amazon_reviews_cache.json"
    
    cache_key = f"{amazon_domain}_{asin}_reviews"
    
    # 캐시 확인
    if os.path.exists(REVIEWS_CACHE_FILE):
        try:
            with open(REVIEWS_CACHE_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}
    else:
        cache = {}
    
    if cache_key in cache:
        st.info("✅ 리뷰 캐시에서 로드!")
        return cache[cache_key]
    
    # 더미 데이터 사용
    st.info(f"🔄 더미 리뷰 데이터 로드 중... (ASIN: {asin})")
    
    try:
        reviews = get_dummy_reviews()
        
        # 캐시 저장
        cache[cache_key] = reviews
        with open(REVIEWS_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        
        st.success(f"✅ {len(reviews)}개 리뷰 데이터 로드 완료!")
        return reviews
    
    except Exception as e:
        st.error(f"❌ 리뷰 로드 중 오류: {str(e)}")
        return None


def summarize_reviews(reviews: List[dict]) -> dict:
    """리뷰를 분석하여 핵심 인사이트 추출 (수출 기업 대응용)"""
    
    if not reviews:
        return {
            "positive": ["데이터 없음"],
            "negative": ["데이터 없음"],
            "summary": "리뷰 데이터를 불러올 수 없습니다."
        }
    
    high_rated = [r for r in reviews if r.get('rating', 0) >= 4]
    low_rated = [r for r in reviews if r.get('rating', 0) <= 2]
    
    positive_keywords = {}
    negative_keywords = {}
    
    positive_words = ['great', 'good', 'excellent', 'love', 'best', 'perfect', 'amazing', 'works', 'warm', 'hot', 'last', 'long']
    negative_words = ['bad', 'poor', 'worst', 'terrible', 'not', 'don\'t', 'cold', 'short', 'leak', 'broke', 'waste']
    
    for review in high_rated:
        body = (review.get('body') or '').lower()
        for word in positive_words:
            if word in body:
                positive_keywords[word] = positive_keywords.get(word, 0) + 1
    
    for review in low_rated:
        body = (review.get('body') or '').lower()
        for word in negative_words:
            if word in body:
                negative_keywords[word] = negative_keywords.get(word, 0) + 1
    
    top_positive = sorted(positive_keywords.items(), key=lambda x: x[1], reverse=True)[:5]
    top_negative = sorted(negative_keywords.items(), key=lambda x: x[1], reverse=True)[:5]
    
    positive_insights = []
    negative_insights = []
    
    if top_positive:
        positive_insights = [f"'{word}' 언급 {count}회" for word, count in top_positive]
    else:
        positive_insights = ["긍정적인 리뷰 키워드를 찾을 수 없습니다."]
    
    if top_negative:
        negative_insights = [f"'{word}' 언급 {count}회" for word, count in top_negative]
    else:
        negative_insights = ["부정적인 리뷰가 거의 없습니다."]
    
    total = len(reviews)
    high_pct = len(high_rated) / total * 100 if total > 0 else 0
    low_pct = len(low_rated) / total * 100 if total > 0 else 0

    return {
        "positive": positive_insights,
        "negative": negative_insights,
        "summary": f"총 {total}개 리뷰 분석: 현지 만족도 {high_pct:.0f}% 수준",
        "high_rated_count": len(high_rated),
        "low_rated_count": len(low_rated),
    }


def get_amazon_cache_info() -> Dict[str, int]:
    if not os.path.exists(AMAZON_CACHE_FILE):
        return {"count": 0}
    
    try:
        with open(AMAZON_CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
            return {"count": len(cache)}
    except Exception:
        return {"count": 0}


def clear_amazon_cache() -> bool:
    try:
        if os.path.exists(AMAZON_CACHE_FILE):
            os.remove(AMAZON_CACHE_FILE)
        return True
    except Exception:
        return False



# ==================== 아마존 경쟁사 분석 섹션 ====================

def render_amazon_research(key_prefix: str = "amazon") -> None:
    """STEP 2: 아마존 실시간 가격 조사"""
    
    def k(name: str) -> str:
        return f"{key_prefix}_{name}"
    
    st.markdown("## 아마존 실시간 마켓 펄스")
    
    if k("search_query") not in st.session_state:
        st.session_state[k("search_query")] = ""
    if k("amazon_domain") not in st.session_state:
        st.session_state[k("amazon_domain")] = "amazon.com"
    if k("results") not in st.session_state:
        st.session_state[k("results")] = None
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "아마존 검색어 입력",
            key=k("search_query"),
            placeholder="예: hand warmer, shampoo 500ml, cosmetic set",
            help="검색하고 싶은 제품명을 영어로 입력하세요"
        )
    
    with col2:
        amazon_domain = st.selectbox(
            "아마존 도메인",
            ["amazon.com", "amazon.co.uk", "amazon.de", "amazon.co.jp"],
            key=k("amazon_domain")
        )

        country_tips = {
            "amazon.com": "🇺🇸 미국 수출 시 FDA 시설 등록 및 성분 검토가 최우선입니다.",
            "amazon.co.jp": "🇯🇵 일본 수출 시 '의약외품(Quasi-drugs)' 분류 여부를 반드시 확인하세요.",
            "amazon.co.uk": "🇬🇧 영국 수출 시 유통기한 및 책임자(RP) 지정이 필수입니다.",
            "amazon.de": "🇩🇪 독일 수출 시 환경 부담금(EPR) 및 인증 마크 획득이 중요합니다."
        }

        st.caption(country_tips.get(amazon_domain, ""))
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🔍 검색", use_container_width=True, key=k("search_btn"))
    
    with st.expander("아마존 캐시 관리"):
        cache_info = get_amazon_cache_info()
        st.metric("저장된 검색어", f"{cache_info['count']}개")
        st.caption(f"캐시 파일: `{AMAZON_CACHE_FILE}`")
        
        if st.button("🗑️ 아마존 캐시 삭제", key=k("clear_cache")):
            if clear_amazon_cache():
                st.success("아마존 캐시 삭제 완료!")
                st.rerun()
    
    if search_btn:
        if not search_query:
            st.warning("검색어를 입력해주세요.")
            return
        
        with st.spinner("🔄 아마존 데이터 수집 중..."):
            results = fetch_amazon_market_data(search_query, amazon_domain)
            st.session_state[k("results")] = results
    
    results = st.session_state.get(k("results"))
    
    if not results:
        st.info("💡 검색어를 입력하고 '검색' 버튼을 클릭하세요.")
        return
    
    st.markdown("---")
    
    # ✅ 수정: 실시간 가격 지표와 가격대 분포를 통합
    st.markdown("### 💰 아마존 실시간 가격 분석")
    
    prices = [r["가격"] for r in results if r["가격"] is not None]
    ratings = [r["별점"] for r in results if r["별점"] is not None]
    
    if prices:
        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        min_price = min(prices)
    else:
        avg_price = max_price = min_price = 0
    
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
    else:
        avg_rating = 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("평균 가격", f"${avg_price:.2f}")
    col2.metric("최고가", f"${max_price:.2f}")
    col3.metric("최저가", f"${min_price:.2f}")
    col4.metric("평균 별점", f"{avg_rating:.1f} ⭐")
    
    # ✅ 가격대 분포 차트 추가
    if prices:
        st.markdown("#### 가격대 분포 (Top 15)")
        df_results = pd.DataFrame(results)
        
        min_p = min(prices)
        max_p = max(prices)
        range_p = max_p - min_p
        
        bins = []
        bin_size = range_p / 5
        for i in range(5):
            low = min_p + (i * bin_size)
            high = min_p + ((i + 1) * bin_size)
            bins.append(f"${low:.0f}-${high:.0f}")
        
        price_dist = {bin_name: 0 for bin_name in bins}
        
        for price in prices:
            idx = min(int((price - min_p) / bin_size), 4)
            bin_name = bins[idx]
            price_dist[bin_name] += 1
        
        fig_price = go.Figure(data=[
            go.Bar(
                x=list(price_dist.keys()),
                y=list(price_dist.values()),
                marker=dict(
                    color='rgba(139, 92, 246, 0.8)',
                    line=dict(width=0)
                ),
                text=list(price_dist.values()),
                textposition='outside',
                width=0.4,
            )
        ])
        fig_price.update_layout(
            xaxis_title="가격대",
            yaxis_title="제품 수",
            height=350,
            showlegend=False,
            yaxis=dict(
                showgrid=True, 
                gridcolor='rgba(128, 128, 128, 0.2)',
                range=[0, max(price_dist.values()) * 1.15]
            ),
            margin=dict(t=20, b=60, l=60, r=40)
        )
        st.plotly_chart(fig_price, use_container_width=True)
        
        most_common_price = max(price_dist, key=price_dist.get)
        st.info(f"**핵심 인사이트**: 가장 많은 제품이 **{most_common_price}** 가격대에 위치")
    
    st.markdown("---")
    
    # 🏆 경쟁사 Top 15 테이블
    st.markdown("### 🏆 경쟁사 Top 15 제품 목록")
    
    df_results = pd.DataFrame(results)
    df_results.insert(0, "순위", range(1, len(df_results) + 1))
    
    df_results["Amazon 링크"] = df_results.apply(
        lambda row: f"https://www.amazon.com/dp/{row['asin']}" if row.get('asin') else "", 
        axis=1
    )
    
    df_results["가격_표시"] = df_results["가격"].apply(lambda x: f"${x:.2f}" if x else "N/A")
    
    display_df = df_results[["순위", "제품명", "가격_표시", "별점", "리뷰수"]].copy()
    display_df.columns = ["순위", "제품명", "가격", "별점", "리뷰수"]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=550,
        hide_index=True,
        column_config={
            "순위": st.column_config.NumberColumn("순위", width="small"),
            "제품명": st.column_config.TextColumn("제품명", width="large"),
            "가격": st.column_config.TextColumn("가격", width="small"),
            "별점": st.column_config.NumberColumn("별점", format="%.1f ⭐", width="small"),
            "리뷰수": st.column_config.NumberColumn("리뷰수", format="%d", width="small"),
        }
    )
    
    # 경쟁 구도 분석
    if results:
        df_results = pd.DataFrame(results)
        
        st.markdown("### 📊 시장 경쟁 구도 분석(Top 15)")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 경쟁사 가격대 분포")
            
            # 가격 데이터 추출
            chart_prices = [r['가격'] for r in results if r.get('가격') and r['가격'] > 0]
            
            if chart_prices:
                # 히스토그램 생성
                fig_hist = px.histogram(
                    x=chart_prices,
                    nbins=8,
                    color_discrete_sequence=['#22c55e']
                )
                fig_hist.update_layout(
                    xaxis_title="가격 ($)",
                    yaxis_title="count",
                    height=400,
                    showlegend=False,
                    bargap=0.1,
                    margin=dict(t=20, b=60, l=60, r=40)
                )
                fig_hist.update_traces(
                    marker_line_width=0,
                    opacity=0.9
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.warning("가격 데이터가 없습니다.")
        
        with col2:
            st.markdown("#### 주요 브랜드 점유율")

            if '브랜드' in df_results.columns:
                brand_counts = df_results['브랜드'].value_counts().head(5)
                fig_brand = px.pie(values=brand_counts.values, 
                                    names=brand_counts.index, 
                                    hole=0.4, 
                                    color_discrete_sequence=px.colors.sequential.Greens_r)
                fig_brand.update_layout(
                    height=400,
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                fig_brand.update_traces(
                    textposition='inside',
                    textinfo='percent',
                    textfont_size=12
                )
                st.plotly_chart(fig_brand, use_container_width=True)
            else:
                st.warning("브랜드 데이터를 찾을 수 없습니다.")

        # Top 1 제품 전략 분석
        st.markdown("---")
        st.markdown("### 📝 Champion Analysis: 1위 제품 정복 가이드")
        top_product = results[0]
        
        with st.expander(f"현재 1위 제품: {top_product['제품명'][:60]}...", expanded=True):
            if st.button("전략적 상세 분석 실행"):
                with st.spinner("단가 및 수출 진출 전략을 분석 중입니다..."):
                    analysis_data = summarize_description_backup(
                        top_product['asin'], 
                        top_product['제품명'], 
                        top_product['가격']
                    )

                    reviews = fetch_product_reviews(top_product['asin'])

                    st.markdown("#### 실시간 제품구성 및 단가 분석")
                    col_q, col_p = st.columns(2)
                    col_q.metric("추출된 수량", f"{analysis_data['qty']} 개입")
                    col_p.metric("개당 가격", f"${analysis_data['unit_price']:.2f}")
                    st.markdown("---")

                    if reviews:
                        summary = summarize_reviews(reviews)
                      
                                            
                    st.success(analysis_data['analysis'])

    with st.expander("제품 링크 보기"):
        for idx, row in df_results.iterrows():
            if row.get("asin"):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"{idx + 1}. {row['제품명'][:80]}...") 
                with col2:
                    st.link_button("상품 페이지", f"https://www.amazon.com/dp/{row['asin']}", use_container_width=True)


# ==================== 메인 실행 ====================

def main():
    st.set_page_config(
        page_title="SY 글로벌 커넥트",
        page_icon="🚀",
        layout="wide",
    )

    # ==================== 🔽 여기에 사이드바 코드 삽입! ====================
    import base64
    
    # 사이드바 CSS
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"] { display: none; }
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
                  <div style="font-size:1.15rem; font-weight:900; color:#0f172a;">🚀 SEO Suite</div>
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
    

    st.markdown("""
    <style>
    .block-container{ padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

    # 1. 최상위 통합 카테고리 타이틀 추가
    st.markdown("# 🚢 해외진출 전략 허브")
    
    # 2. 구분선
    st.markdown("---")
    
    # 3. 미시적 분석 섹션 호출 (이 함수 내부에서 'Micro Dynamics' 제목이 나옵니다)
    render_amazon_research(key_prefix="amazon")

if __name__ == "__main__":
    main()

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #718096; font-size: 0.9em;'>
    <p>Global E-commerce All In One Solution</p>
    <p>Developed by Seyeon Global Connect</p>
</div>
""", unsafe_allow_html=True)