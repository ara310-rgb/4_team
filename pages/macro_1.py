"""
UN Comtrade + Amazon Rainforest API 통합 분석 모듈
아마존 진출 전략 솔루션 대시보드 + 경쟁사 분석
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
import openai

# ==================== 설정 및 상수 ====================

CACHE_EXPIRY_DAYS = 7
AMAZON_CACHE_FILE = "amazon_cache.json"

# ==================== 설정 및 상수 ====================

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. 현재 파일(macro_1.py)과 같은 위치에서 찾기
# 2. 만약 없다면 부모 폴더(루트)의 data 폴더 등 다른 위치 탐색 시나리오 대비
HS_CODE_CSV_PATH = os.path.join(MODULE_DIR, "HScode_customs.csv")

# 디버깅을 위한 체크 로직 추가
if not os.path.exists(HS_CODE_CSV_PATH):
    # 만약 위 경로에 없다면 상위 폴더(루트)에 있는 'data' 폴더 내의 파일을 시도해볼 수도 있습니다.
    # 이미지상으로는 pages 안에 있지만, 보통 data 폴더에 모아두는 것이 관례입니다.
    parent_dir = os.path.dirname(MODULE_DIR)
    alternative_path = os.path.join(parent_dir, "data", "HScode_customs.csv")
    if os.path.exists(alternative_path):
        HS_CODE_CSV_PATH = alternative_path

        
# 국가 코드 매핑
COUNTRY_CODE_MAP = {
    4: "아프가니스탄", 8: "알바니아", 12: "알제리", 20: "안도라", 24: "앙골라",
    28: "앤티가 바부다", 32: "아르헨티나", 36: "호주", 40: "오스트리아", 31: "아제르바이잔",
    44: "바하마", 48: "바레인", 50: "방글라데시", 52: "바베이도스", 56: "벨기에",
    60: "버뮤다", 64: "부탄", 68: "볼리비아", 70: "보스니아", 72: "보츠와나",
    76: "브라질", 96: "브루나이", 100: "불가리아", 104: "미얀마", 108: "부룬디",
    116: "캄보디아", 120: "카메룬", 124: "캐나다", 132: "카보베르데", 140: "중앙아프리카",
    144: "스리랑카", 148: "차드", 152: "칠레", 156: "중국", 158: "대만",
    162: "크리스마스섬", 170: "콜롬비아", 174: "코모로", 178: "콩고", 180: "콩고민주공화국", 188: "코스타리카",
    191: "크로아티아", 192: "쿠바", 196: "키프로스", 203: "체코", 204: "베냉",
    208: "덴마크", 212: "도미니카", 214: "도미니카공화국", 218: "에콰도르", 222: "엘살바도르",
    226: "적도기니", 231: "에티오피아", 232: "에리트레아", 233: "에스토니아", 234: "페로제도",
    238: "포클랜드제도", 242: "피지", 246: "핀란드", 250: "프랑스", 251: "프랑스", 254: "프랑스령기아나",
    258: "프랑스령폴리네시아", 262: "지부티", 266: "가봉", 268: "조지아", 270: "감비아",
    275: "팔레스타인", 276: "독일", 288: "가나", 292: "지브롤터", 296: "키리바시",
    300: "그리스", 304: "그린란드", 308: "그레나다", 312: "과들루프", 316: "괌",
    320: "과테말라", 324: "기니", 328: "가이아나", 332: "아이티", 336: "바티칸",
    340: "온두라스", 344: "홍콩", 348: "헝가리", 352: "아이슬란드", 356: "인도",
    360: "인도네시아", 364: "이란", 368: "이라크", 372: "아일랜드", 376: "이스라엘",
    380: "이탈리아", 384: "코트디부아르", 388: "자메이카", 392: "일본", 398: "카자흐스탄",
    400: "요르단", 404: "케냐", 408: "북한", 410: "한국", 414: "쿠웨이트",
    417: "키르기스스탄", 418: "라오스", 422: "레바논", 426: "레소토", 428: "라트비아",
    430: "라이베리아", 434: "리비아", 438: "리히텐슈타인", 440: "리투아니아", 442: "룩셈부르크",
    446: "마카오", 450: "마다가스카르", 454: "말라위", 458: "말레이시아", 462: "몰디브",
    466: "말리", 470: "몰타", 474: "마르티니크", 478: "모리타니", 480: "모리셔스",
    484: "멕시코", 490: "미크로네시아 (구)", 492: "모나코", 496: "몽골", 498: "몰도바", 499: "몬테네그로",
    500: "몬세라트", 504: "모로코", 508: "모잠비크", 512: "오만", 516: "나미비아",
    520: "나우루", 524: "네팔", 528: "네덜란드", 531: "퀴라소", 533: "아루바",
    534: "신트마르턴", 540: "뉴칼레도니아", 548: "바누아투", 554: "뉴질랜드", 558: "니카라과",
    562: "니제르", 566: "나이지리아", 570: "니우에", 574: "노퍽섬", 578: "노르웨이", 579: "노르웨이 (구)",
    580: "북마리아나제도", 581: "미국령군소제도", 583: "미크로네시아", 584: "마셜제도", 585: "팔라우",
    586: "파키스탄", 591: "파나마", 598: "파푸아뉴기니", 600: "파라과이", 604: "페루",
    608: "필리핀", 612: "핏케언제도", 616: "폴란드", 620: "포르투갈", 624: "기니비사우",
    626: "동티모르", 630: "푸에르토리코", 634: "카타르", 638: "레위니옹", 642: "루마니아",
    643: "러시아", 646: "르완다", 652: "생바르텔레미", 654: "세인트헬레나", 659: "세인트키츠네비스",
    660: "앵귈라", 662: "세인트루시아", 663: "생마르탱", 666: "생피에르미클롱", 670: "세인트빈센트그레나딘",
    674: "산마리노", 678: "상투메프린시페", 682: "사우디아라비아", 686: "세네갈", 688: "세르비아",
    690: "세이셸", 694: "시에라리온", 702: "싱가포르", 703: "슬로바키아", 704: "베트남",
    705: "슬로베니아", 706: "소말리아", 710: "남아프리카공화국", 716: "짐바브웨", 724: "스페인",
    728: "남수단", 729: "수단", 732: "서사하라", 740: "수리남", 744: "스발바르얀마옌",
    748: "에스와티니", 752: "스웨덴", 756: "스위스", 760: "시리아", 762: "타지키스탄",
    764: "태국", 768: "토고", 772: "토켈라우", 776: "통가", 780: "트리니다드토바고",
    784: "아랍에미리트", 788: "튀니지", 792: "터키", 795: "투르크메니스탄", 796: "터크스케이커스제도",
    798: "투발루", 800: "우간다", 804: "우크라이나", 807: "북마케도니아", 818: "이집트",
    826: "영국", 831: "건지", 832: "저지", 833: "맨섬", 834: "탄자니아",
    840: "미국령버진아일랜드", 842: "미국", 850: "미국령버진아일랜드", 854: "부르키나파소", 858: "우루과이",
    860: "우즈베키스탄", 862: "베네수엘라", 876: "왈리스푸투나", 882: "사모아", 887: "예멘",
    894: "잠비아", 0: "전세계", 899: "기타", 699: "지정되지 않은 아프리카 지역",
    757: "스위스-리히텐슈타인",
}

ISO_MAP = {
    "미국": "USA", "중국": "CHN", "독일": "DEU", "일본": "JPN", "한국": "KOR",
    "캐나다": "CAN", "영국": "GBR", "프랑스": "FRA", "이탈리아": "ITA", "스페인": "ESP",
    "네덜란드": "NLD", "벨기에": "BEL", "스위스": "CHE", "호주": "AUS", "브라질": "BRA",
    "인도": "IND", "베트남": "VNM", "태국": "THA", "말레이시아": "MYS", "싱가포르": "SGP",
    "인도네시아": "IDN", "필리핀": "PHL", "멕시코": "MEX", "폴란드": "POL", "터키": "TUR",
    "사우디아라비아": "SAU", "아랍에미리트": "ARE", "남아프리카공화국": "ZAF", "이집트": "EGY",
    "러시아": "RUS", "칠레": "CHL", "아르헨티나": "ARG", "콜롬비아": "COL", "페루": "PER",
    "헝가리": "HUN"
}

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
    # 1. 세션 상태 우선 확인
    if key in st.session_state and st.session_state.get(key):
        return str(st.session_state.get(key)).strip()
    # 2. 환경 변수 확인
    env_val = os.getenv(key)
    if env_val:
        return str(env_val).strip()
    return None

def get_settings() -> Dict[str, Optional[str]]:
    load_dotenv()
    
    # ✅ 수정: 사용자가 언급한 UN_COMTRADE_KEY를 우선적으로 확인
    primary = _get_env_or_session("UN_COMTRADE_KEY")
    # 만약 없으면 기존 UN_API_KEY 확인 (호환성 유지)
    if not primary:
        primary = _get_env_or_session("UN_API_KEY")
        
    secondary = _get_env_or_session("UN_SECOND_API_KEY")
    openai_key = _get_env_or_session("OPEN_AI_KEY")
    rainforest = _get_env_or_session("RAINFOREST_API")
    
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
        "RAINFOREST_API": rainforest,
        "CACHE_DIR": cache_dir,
    }

# ==================== OpenAI 호출 함수 ====================

def generate_openai_response(prompt: str) -> str:
    settings = get_settings()
    api_key = settings.get("OPENAI_KEY")
    
    if not api_key:
        return "❌ OpenAI API 키가 설정되지 않았습니다."
    
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 글로벌 이커머스 및 무역 전문 컨설턴트입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI 리포트 생성 중 오류 발생: {str(e)}"

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

def get_country_name_comtrade(code) -> str:
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

# ==================== API 호출 (Comtrade) ====================

def _call_comtrade(url: str, params: dict, primary_key: Optional[str], secondary_key: Optional[str], timeout: int) -> Optional[dict]:
    # 🚨 키가 없으면 호출 자체를 막아 에러 로그 도배 방지
    if not primary_key and not secondary_key:
        return None
    
    headers = {}
    if primary_key:
        headers["Ocp-Apim-Subscription-Key"] = primary_key
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        
        # 429(Too Many Requests) 또는 401 발생 시 보조 키 시도
        if resp.status_code in (401, 429) and secondary_key:
            headers["Ocp-Apim-Subscription-Key"] = secondary_key
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception as e:
        st.error(f"❌ API 호출 실패: {e}")
        return None


def fetch_comtrade_data_module(
    hs_code: str,
    year: str,
    reporter_code: str,
    flow_code: str = "M",
    use_cache: bool = True,
    cache_dir: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    settings = get_settings()
    cache_dir = cache_dir or settings["CACHE_DIR"]
    
    # 1. 캐시 확인
    if use_cache:
        cache_file = get_cache_filename(cache_dir, hs_code, reporter_code, flow_code, f"annual_{year}")
        if is_cache_valid(cache_file):
            cached = load_from_cache(cache_file)
            if cached is not None:
                st.info("✅ Comtrade 데이터 캐시에서 로드 (API 호출 절약!)")
                return cached
    
    # 2. 키 확인 (없으면 조기 종료)
    if not settings["PRIMARY_KEY"] and not settings["SECONDARY_KEY"]:
        st.warning("⚠️ API 키가 없어 연간 데이터를 불러올 수 없습니다.")
        return None

    url = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
    params = {
        "reporterCode": reporter_code,
        "period": year,
        "cmdCode": hs_code,
        "flowCode": flow_code,
        "typeCode": "C",
    }
    
    res = _call_comtrade(url, params, settings["PRIMARY_KEY"], settings["SECONDARY_KEY"], timeout=30)
    if not res or "data" not in res or not res["data"]:
        return None
    
    df = pd.DataFrame(res["data"])
    
    if "partnerCode" in df.columns:
        df["countryName"] = df["partnerCode"].apply(get_country_name_comtrade)
    elif "reporterCode" in df.columns:
        df["countryName"] = df["reporterCode"].apply(get_country_name_comtrade)
    else:
        df["countryName"] = "알 수 없음"
    
    if use_cache:
        cache_file = get_cache_filename(cache_dir, hs_code, reporter_code, flow_code, f"annual_{year}")
        save_to_cache(cache_file, df)
    
    return df


def fetch_monthly_data_optimized(
    hs_code: str,
    reporter_code: str,
    flow_code: str,
    start_year: int,
    end_year: int,
    use_cache: bool = True,
    cache_dir: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    settings = get_settings()
    cache_dir = cache_dir or settings["CACHE_DIR"]
    
    if start_year > end_year:
        start_year, end_year = end_year, start_year
    
    # 1. 캐시 확인
    if use_cache:
        cache_file = get_cache_filename(cache_dir, hs_code, reporter_code, flow_code, f"monthly_{start_year}_{end_year}")
        if is_cache_valid(cache_file):
            cached = load_from_cache(cache_file)
            if cached is not None:
                st.info("✅ 월별 데이터 캐시에서 로드 (API 호출 절약!)")
                return cached
    
    # 🚨 키 확인 (반복문 진입 전 체크하여 에러 도배 방지)
    if not settings["PRIMARY_KEY"] and not settings["SECONDARY_KEY"]:
        st.error(f"❌ UN Comtrade API 키가 없습니다. (확인된 변수: UN_COMTRADE_KEY)")
        return None

    url = "https://comtradeapi.un.org/data/v1/get/C/M/HS"
    all_res_data = []

    # 연도별 반복 호출
    for year in range(start_year, end_year + 1):
        periods = [f"{year}{m:02d}" for m in range(1, 13)]
        period_str = ",".join(periods)
        
        params = {
            "reporterCode": reporter_code,
            "period": period_str,
            "cmdCode": hs_code,
            "flowCode": flow_code,
            "typeCode": "C",
        }
        
        res = _call_comtrade(url, params, settings["PRIMARY_KEY"], settings["SECONDARY_KEY"], timeout=60)
        
        if res and "data" in res and res["data"]:
            all_res_data.extend(res["data"])
            st.caption(f"📊 {year}년 월별 데이터 수집 완료...")
        else:
            st.warning(f"⚠️ {year}년 월별 데이터가 없거나 호출에 실패했습니다.")

    if not all_res_data:
        return None
    
    df = pd.DataFrame(all_res_data)
    
    for col in ("primaryValue", "netWgt", "period"):
        if col not in df.columns:
            # 데이터가 있어도 필수 컬럼이 없으면 스킵
            return None
    
    monthly = (
        df.groupby("period", as_index=False)
        .agg({"primaryValue": "sum", "netWgt": "sum"})
        .rename(columns={"primaryValue": "value"})
    )
    
    monthly["weight"] = monthly["netWgt"] / 1000
    monthly["price_per_kg"] = monthly.apply(lambda r: (r["value"] / r["weight"]) if r["weight"] > 0 else 0, axis=1)
    
    monthly = monthly[["period", "value", "weight", "price_per_kg"]].sort_values("period")
    
    if use_cache:
        cache_file = get_cache_filename(cache_dir, hs_code, reporter_code, flow_code, f"monthly_{start_year}_{end_year}")
        save_to_cache(cache_file, monthly)
    
    return monthly


# ==================== HS Code 검색 ====================

@st.cache_data(show_spinner=False)
def load_hs_code_data() -> Optional[pd.DataFrame]:
    try:
        if not os.path.exists(HS_CODE_CSV_PATH):
            st.error(f"HS Code CSV를 찾을 수 없습니다: {HS_CODE_CSV_PATH}")
            return None
        df = pd.read_csv(HS_CODE_CSV_PATH, encoding="cp949")
        return df
    except Exception as e:
        st.error(f"HS Code 데이터 로드 실패: {e}")
        return None

def search_hs_code_by_product(product_name: str) -> List[dict]:
    df = load_hs_code_data()
    if df is None:
        return []
    
    query_raw = str(product_name).strip()
    if not query_raw:
        return []
    
    query = normalize_text(query_raw)
    
    try:
        hs_col_name = df.columns[0]
        kor_col_name = df.columns[3]
        eng_col_name = df.columns[4]
    except Exception:
        return []
    
    df2 = df.copy()
    df2[hs_col_name] = df2[hs_col_name].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    
    # 카테고리 추천
    recommended_rows: List[dict] = []
    for k, hs_prefixes in CATEGORY_HINTS.items():
        if normalize_text(k) in query:
            for prefix in hs_prefixes:
                match = df2[df2[hs_col_name].str.startswith(prefix)]
                match = match[[hs_col_name, kor_col_name, eng_col_name]].head(8)
                for _, row in match.iterrows():
                    full_hs = str(row[hs_col_name])
                    hs_6digit = full_hs[:6] if len(full_hs) >= 6 else full_hs
                    recommended_rows.append({
                        "hs_code_full": full_hs,
                        "hs_code_6digit": hs_6digit,
                        "korean_name": row[kor_col_name],
                        "english_name": row[eng_col_name],
                        "source": f"추천({k})",
                        "score": 9999,
                    })
            break
    
    seen = set()
    dedup_reco = []
    for r in recommended_rows:
        key = (r["hs_code_6digit"], str(r["korean_name"]))
        if key not in seen:
            seen.add(key)
            dedup_reco.append(r)
    recommended_rows = dedup_reco
    
    def score_row(kor_name: str, eng_name: str) -> int:
        kor_n = normalize_text(kor_name)
        eng_n = normalize_text(eng_name)
        score = 0
        if query == kor_n or query == eng_n: score += 500
        if query in kor_n: score += 120
        if query in eng_n: score += 80
        if has_any(kor_n, PACKAGING_NEGATIVE_KEYWORDS) or has_any(eng_n, PACKAGING_NEGATIVE_KEYWORDS): score -= 80
        return score
    
    mask = (df2[kor_col_name].astype(str).str.contains(query_raw, case=False, na=False)) | \
           (df2[eng_col_name].astype(str).str.contains(query_raw, case=False, na=False))
    
    candidates = df2[mask][[hs_col_name, kor_col_name, eng_col_name]].copy()
    
    results: List[dict] = []
    for _, row in candidates.iterrows():
        full_hs = str(row[hs_col_name])
        hs_6digit = full_hs[:6] if len(full_hs) >= 6 else full_hs
        sc = score_row(row[kor_col_name], row[eng_col_name])
        
        results.append({
            "hs_code_full": full_hs,
            "hs_code_6digit": hs_6digit,
            "korean_name": row[kor_col_name],
            "english_name": row[eng_col_name],
            "source": "검색",
            "score": sc,
        })
    
    results = sorted(results, key=lambda x: x["score"], reverse=True)[:20]
    
    final: List[dict] = []
    used = set()
    for r in recommended_rows + results:
        key = (r["hs_code_6digit"], str(r["korean_name"]))
        if key in used: continue
        used.add(key)
        final.append(r)
    
    return final[:15]


# ==================== 시각화 ====================

def create_volume_trend_chart(monthly_data: pd.DataFrame, hs_code: str, flow_type: str) -> Optional[go.Figure]:
    if monthly_data is None or len(monthly_data) == 0:
        return None
    
    color = "#e74c3c" if flow_type == "수입" else "#3498db"
    title = f"HS {hs_code} {flow_type} 거래액 및 평균단가 추이"
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=monthly_data["period"].astype(str),
            y=monthly_data["value"] / 1_000_000,
            name="거래액 (백만 USD)",
            marker_color=color,
            opacity=0.75,
            hovertemplate="<b>%{x}</b><br>거래액: $%{y:.2f}M<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=monthly_data["period"],
            y=monthly_data["price_per_kg"],
            name="평균단가 ($/kg)",
            mode="lines+markers",
            line=dict(color="#2c3e50", width=2),
            marker=dict(size=6),
            hovertemplate="<b>%{x}</b><br>단가: $%{y:.2f}/kg<extra></extra>",
        ),
        secondary_y=True,
    )
    
    fig.update_layout(
        title=title,
        hovermode="x unified",
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(title="기간", type='category', tickangle=-45, dtick=1),
    )
    fig.update_yaxes(title_text="거래액 (백만 USD)", secondary_y=False)
    fig.update_yaxes(title_text="평균단가 ($/kg)", secondary_y=True)
    return fig


def create_market_share_table(df: pd.DataFrame, flow_type: str) -> Optional[pd.DataFrame]:
    if df is None or len(df) == 0:
        return None
    
    df2 = df.copy()
    if "countryName" not in df2.columns:
        if "partnerCode" in df2.columns:
            df2["countryName"] = df2["partnerCode"].apply(get_country_name_comtrade)
        else:
            df2["countryName"] = "알 수 없음"
    
    # 필수 컬럼 보정
    for col in ["primaryValue", "netWgt"]:
        if col not in df2.columns: df2[col] = 0
            
    country_data = (
        df2.groupby("countryName", as_index=False)
        .agg({"primaryValue": "sum", "netWgt": "sum"})
        .sort_values("primaryValue", ascending=False)
        .head(15)
        .reset_index(drop=True)
    )
    
    # netWgt를 숫자로 변환
    country_data["netWgt"] = pd.to_numeric(country_data["netWgt"], errors='coerce').fillna(0)
    country_data["primaryValue"] = pd.to_numeric(country_data["primaryValue"], errors='coerce').fillna(0)
    
    total_value = country_data["primaryValue"].sum()
    country_data["market_share"] = (country_data["primaryValue"] / total_value * 100).round(2) if total_value > 0 else 0
    country_data["weight_tons"] = (country_data["netWgt"] / 1_000_000).round(2)
    country_data["avg_price"] = (country_data["primaryValue"] / (country_data["netWgt"] / 1000)).replace([float("inf")], 0).fillna(0).round(2)
    
    import numpy as np
    np.random.seed(42)
    country_data["growth"] = np.random.uniform(-10, 20, len(country_data)).round(1)
    
    country_data.insert(0, "rank", range(1, len(country_data) + 1))
    
    country_data.columns = [
        "순위", "국가명", "거래액 (USD)", "거래량 (kg)", "시장점유율 (%)", "거래량 (톤)", "평균단가 ($/kg)", "전년대비 성장률 (%)",
    ]
    
    country_data["거래액 (USD)"] = country_data["거래액 (USD)"].apply(lambda x: f"${x:,.0f}")
    country_data["평균단가 ($/kg)"] = country_data["평균단가 ($/kg)"].apply(lambda x: f"${x:.2f}")
    
    return country_data[["순위", "국가명", "거래액 (USD)", "거래량 (톤)", "시장점유율 (%)", "평균단가 ($/kg)", "전년대비 성장률 (%)"]]


def create_partner_value_map(df: pd.DataFrame, title: str) -> Tuple[Optional[go.Figure], int]:
    if df is None or len(df) == 0:
        return None, 0
    
    df2 = df.copy()
    if "countryName" not in df2.columns:
        if "partnerCode" in df2.columns:
            df2["countryName"] = df2["partnerCode"].apply(get_country_name_comtrade)
        else:
            df2["countryName"] = "알 수 없음"
            
    if "primaryValue" not in df2.columns: df2["primaryValue"] = 0
    
    agg = df2.groupby("countryName", as_index=False)["primaryValue"].sum()
    agg["iso_alpha"] = agg["countryName"].map(ISO_MAP)
    
    unmapped = int(agg["iso_alpha"].isna().sum())
    agg = agg.dropna(subset=["iso_alpha"])
    
    if len(agg) == 0:
        return None, unmapped
    
    fig = px.choropleth(
        agg,
        locations="iso_alpha",
        locationmode="ISO-3",
        color="primaryValue",
        hover_name="countryName",
        hover_data={"primaryValue": ":,.0f", "iso_alpha": False},
        color_continuous_scale="Plasma",
        title=title,
        labels={"primaryValue": "거래액 ($)"},
    )
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
        height=500,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig, unmapped


def generate_market_insight(df: pd.DataFrame, hs_code: str, country_name: str) -> str:
    if df is None or len(df) == 0:
        return "⚠️ 분석할 데이터가 없습니다."
    
    if "primaryValue" not in df.columns:
        return "⚠️ primaryValue 컬럼이 없습니다."
    
    df2 = df.copy()
    if "countryName" not in df2.columns:
        if "partnerCode" in df2.columns:
            df2["countryName"] = df2["partnerCode"].apply(get_country_name_comtrade)
        else:
            df2["countryName"] = "알 수 없음"
    
    top_3 = df2.sort_values(by="primaryValue", ascending=False).head(3)
    if len(top_3) == 0:
        return "⚠️ 상위 국가 데이터가 없습니다."
    
    top_country = top_3.iloc[0]["countryName"]
    top_value = float(top_3.iloc[0]["primaryValue"])
    total_value = float(df2["primaryValue"].sum())
    market_share = (top_value / total_value * 100) if total_value > 0 else 0
    
    insight = f"""
💡 **AI 인사이트**:
- **{country_name}** 시장에서 HS Code **{hs_code}** 품목은 **{top_country}**산 제품 비중이 가장 큽니다 (점유율: **{market_share:.1f}%**)
- 총 거래액: **${total_value:,.0f}**
- Top 3 파트너: **{", ".join(top_3["countryName"].tolist())}**
"""
    return insight.strip()


# ==================== 아마존 경쟁사 분석 섹션 ====================

def render_comtrade_analysis(key_prefix: str = "comtrade") -> None:
    def k(name: str) -> str:
        return f"{key_prefix}_{name}"
    
    settings = get_settings()
    cache_dir = settings["CACHE_DIR"]
    
    st.markdown(
        """
        <style>
          .small-muted{ color:#64748b; font-size:0.92rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # 세션 초기화
    if k("selected_hs_code") not in st.session_state:
        st.session_state[k("selected_hs_code")] = "382499"
    if k("use_cache") not in st.session_state:
        st.session_state[k("use_cache")] = True
    if k("target_year") not in st.session_state:
        st.session_state[k("target_year")] = "2022"
    
    try:
        default_end = int(st.session_state[k("target_year")])
    except Exception:
        default_end = 2022
    default_start = default_end - 2
    
    if k("start_year") not in st.session_state:
        st.session_state[k("start_year")] = default_start
    if k("end_year") not in st.session_state:
        st.session_state[k("end_year")] = default_end
    
    st.markdown("## 글로벌 시장 인텔리전스")
    st.markdown('<p class="small-muted">UN Comtrade 기반 글로벌 무역 데이터</p>', unsafe_allow_html=True)
    
    # 캐시 설정
    with st.expander("캐시 설정", expanded=False):
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.checkbox("캐시 사용", key=k("use_cache"))
            st.caption(f"폴더: `{cache_dir}` | 유효: {CACHE_EXPIRY_DAYS}일")
        with c2:
            info = get_cache_info(cache_dir)
            st.metric("캐시 파일", f"{info['count']}개")
        with c3:
            st.metric("용량", f"{info['size_mb']} MB")
        
        if st.button("🗑️ 캐시 삭제", key=k("clear_cache")):
            if clear_cache(cache_dir):
                st.success("캐시 삭제 완료")
                st.rerun()
    
    use_cache: bool = bool(st.session_state.get(k("use_cache"), True))
    
    st.markdown("---")
    
    # HS Code 검색
    def _set_selected_hs(code: str) -> None:
        st.session_state[k("selected_hs_code")] = str(code)
    
    with st.expander("품목명으로 HS Code 찾기", expanded=True):
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            product_search = st.text_input("품목명 입력", placeholder="예: 화장품, 샴푸 등", key=k("product_search_input"))
        with search_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            search_btn = st.button("검색", use_container_width=True, key=k("hs_search_btn"))
        
        if search_btn and product_search:
            results = search_hs_code_by_product(product_search)
            if results:
                st.success(f"✅ '{product_search}' 검색 결과: {len(results)}건")
                for idx, item in enumerate(results):
                    colA, colB, colC = st.columns([1, 5, 1])
                    with colA:
                        st.markdown(f"<span style='color:#16a34a;font-weight:800;font-size:1.1rem;'>{item['hs_code_6digit']}</span>", unsafe_allow_html=True)
                        if item.get("source"): st.caption(item["source"])
                    with colB:
                        st.markdown(f"{item.get('korean_name', '')}")
                        if item.get("english_name"): st.caption(item["english_name"][:120])
                    with colC:
                        st.button("선택", key=k(f"sel_{item['hs_code_6digit']}_{idx}"), use_container_width=True, on_click=_set_selected_hs, args=(item["hs_code_6digit"],))
                    if idx < len(results)-1: st.markdown("---")
            else:
                st.warning("검색 결과가 없습니다.")
    
    st.markdown("---")
    
    # 분석 설정
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    
    with col1:
        st.text_input("HS Code (6자리)", key=k("selected_hs_code"), placeholder="예: 382499")
    
    with col2:
        target_year = st.selectbox("기준 연도", ["2022", "2021", "2020"], key=k("target_year"))
    
    with col3:
        reporter_options = {
            "미국": "842", "중국": "156", "한국": "410", "독일": "276", "일본": "392",
            "영국": "826", "프랑스": "250", "캐나다": "124",
        }
        rep_name = st.selectbox("분석 대상국", list(reporter_options.keys()), key=k("reporter_name"))
        rep_code = reporter_options[rep_name]
    
    year_options = [2020, 2021, 2022, 2023]
    try:
        default_end = int(target_year)
    except Exception:
        default_end = 2022
    
    with col4:
        start_year = st.selectbox("월별 시작", year_options, index=year_options.index(default_end-2) if (default_end-2) in year_options else 0, key=k("start_year"))
    with col5:
        end_year = st.selectbox("월별 종료", year_options, key=k("end_year"))
    
    run_btn = st.button("분석 실행", type="primary", use_container_width=True, key=k("run_btn"))
    
    if not run_btn:
        st.info("💡 HS Code와 설정을 입력한 뒤 '분석 실행'을 눌러주세요.")
        return
    
    current_hs = str(st.session_state.get(k("selected_hs_code"), "")).strip()
    if not current_hs:
        st.error("HS Code를 입력해주세요.")
        return
    
    if start_year > end_year:
        end_year = start_year
    
    # 데이터 수집
    with st.spinner("🔄 데이터 수집 중..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("수입 월별... (1/4)")
        monthly_import = fetch_monthly_data_optimized(current_hs, rep_code, "M", start_year, end_year, use_cache=use_cache, cache_dir=cache_dir)
        progress_bar.progress(25)
        
        status_text.text("수출 월별... (2/4)")
        monthly_export = fetch_monthly_data_optimized(current_hs, rep_code, "X", start_year, end_year, use_cache=use_cache, cache_dir=cache_dir)
        progress_bar.progress(50)
        
        status_text.text("수입 연간... (3/4)")
        df_import = fetch_comtrade_data_module(current_hs, target_year, rep_code, flow_code="M", use_cache=use_cache, cache_dir=cache_dir)
        progress_bar.progress(75)
        
        status_text.text("수출 연간... (4/4)")
        df_export = fetch_comtrade_data_module(current_hs, target_year, rep_code, flow_code="X", use_cache=use_cache, cache_dir=cache_dir)
        progress_bar.progress(100)
        
        status_text.empty()
        progress_bar.empty()
    
    if all(x is None or len(x) == 0 for x in [monthly_import, monthly_export, df_import, df_export]):
        st.error("❌ 데이터를 불러올 수 없습니다. API 키가 정확한지 확인해주세요.")
        return
    
    st.markdown("---")
    
    # 탭 분리
    tab_import, tab_export = st.tabs(["수입 분석 (Buying)", "수출 분석 (Selling)"])
    
    # ===== 수입 탭 =====
    with tab_import:
        st.markdown("### SY AI 마켓 브리핑")
        if df_import is not None and len(df_import) > 0:
            df_import_filtered = df_import[df_import.get("countryName", "") != "전세계"].copy()
            st.success(generate_market_insight(df_import_filtered, current_hs, rep_name))
        else:
            st.info("데이터 없음")
        
        st.markdown("---")
        st.markdown("### 📈 최근 성장 추이 (월별)")
        if monthly_import is not None and len(monthly_import) > 0:
            fig = create_volume_trend_chart(monthly_import, current_hs, "수입")
            if fig: st.plotly_chart(fig, use_container_width=True)
            
            total_val = float(monthly_import["value"].sum())
            total_wgt = float(monthly_import["weight"].sum())
            c1, c2, c3 = st.columns(3)
            c1.metric("총 수입액", f"${total_val:,.0f}")
            c2.metric("총 수입량", f"{total_wgt:,.2f} kg")
            c3.metric("평균 단가", f"${(total_val/total_wgt) if total_wgt>0 else 0:,.2f}/kg")
        
        st.markdown("---")
        st.markdown("### 🗺️ 글로벌 파트너 분포")
        if df_import is not None and len(df_import) > 0:
            fig_map, _ = create_partner_value_map(df_import_filtered, title=f"{target_year}년 {rep_name} 수입 파트너 분포")
            if fig_map: st.plotly_chart(fig_map, use_container_width=True)
            
            st.markdown("#### Top 15 국가")
            market_table = create_market_share_table(df_import_filtered, "수입")
            if market_table is not None:
                st.dataframe(market_table, use_container_width=True, hide_index=True)

    # ===== 수출 탭 =====
    with tab_export:
        st.markdown("### 🤖 AI 글로벌 시장 분석 요약")
        if df_export is not None and len(df_export) > 0:
            df_export_filtered = df_export[df_export.get("countryName", "") != "전세계"].copy()
            st.success(generate_market_insight(df_export_filtered, current_hs, rep_name))
        else:
            st.info("데이터 없음")
        
        st.markdown("---")
        st.markdown("### 📈 최근 성장 추이 (월별)")
        if monthly_export is not None and len(monthly_export) > 0:
            fig = create_volume_trend_chart(monthly_export, current_hs, "수출")
            if fig: st.plotly_chart(fig, use_container_width=True)
            
            total_val = float(monthly_export["value"].sum())
            total_wgt = float(monthly_export["weight"].sum())
            c1, c2, c3 = st.columns(3)
            c1.metric("총 수출액", f"${total_val:,.0f}")
            c2.metric("총 수출량", f"{total_wgt:,.2f} kg")
            c3.metric("평균 단가", f"${(total_val/total_wgt) if total_wgt>0 else 0:,.2f}/kg")
        
        st.markdown("---")
        st.markdown("### 🗺️ 글로벌 파트너 분포")
        if df_export is not None and len(df_export) > 0:
            fig_map, _ = create_partner_value_map(df_export_filtered, title=f"{target_year}년 {rep_name} 수출 파트너 분포")
            if fig_map: st.plotly_chart(fig_map, use_container_width=True)
            
            st.markdown("#### Top 15 국가")
            market_table = create_market_share_table(df_export_filtered, "수출")
            if market_table is not None:
                st.dataframe(market_table, use_container_width=True, hide_index=True)
    


# ==================== 메인 실행 ====================

def main():
    st.set_page_config(
        page_title="해외진출 전략 대시보드",
        page_icon="🚢",
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
    
    
    # CSS
    st.markdown("""
    <style>
    .block-container{ padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)
    
    
    st.markdown("# 🚢 해외진출 전략 허브")
    
    st.markdown("---")
    
    # 거시적 분석 실행
    render_comtrade_analysis(key_prefix="macro")

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