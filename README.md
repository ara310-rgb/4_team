# 🌏 SY Global Connect - AI 기반 글로벌 무역 통합 플랫폼

> 무역 실무자를 위한 올인원 솔루션: 시장 분석부터 바이어 발굴, 물류비 계산, SEO 마케팅, 서류 생성까지

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green)
![License](https://img.shields.io/badge/License-MIT-orange)

---

## 📋 목차

1. [프로젝트 소개](#-프로젝트-소개)
2. [전체 시스템 구조](#-전체-시스템-구조)
3. [주요 모듈](#-주요-모듈)
4. [설치 및 실행](#-설치-및-실행)
5. [사용 가이드](#-사용-가이드)
6. [기술 스택](#-기술-스택)
7. [API 설정](#-api-설정)
8. [FAQ](#-faq)

---

## 🎯 프로젝트 소개

**SY Global Connect**는 한국 중소기업의 글로벌 진출을 지원하는 AI 기반 통합 무역 플랫폼입니다. **KITA AX MASTER TEAM4**가 개발한 이 시스템은 시장 조사부터 바이어 발굴, 물류비 계산, SEO 마케팅, 무역 서류 생성까지 전 과정을 자동화합니다.

### 해결하는 문제
- ❌ 해외 시장 진입장벽 분석에 수일 소요
- ❌ 적합한 바이어 발굴의 어려움
- ❌ 물류비 계산에 2~3시간 소요
- ❌ 무역 서류 작성 시 반복적인 수작업
- ❌ 글로벌 SEO 마케팅 전략 수립의 전문성 부족
- ❌ 실시간 환율 변동 대응 어려움

### 제공하는 솔루션
- ✅ **AI 기반 시장 분석**: SWOT, 진입장벽, 규제 리스크 자동 분석
- ✅ **스마트 바이어 매칭**: 5개 공공기관 DB 통합 (30만+ 바이어), AI 이메일 생성
- ✅ **3분 물류비 견적**: 실시간 환율 반영, 3단계 폴백 시스템
- ✅ **원클릭 서류 생성**: 6종 무역 서류 + AI 리스크 분석
- ✅ **글로벌 SEO 전략**: 60개국 시장별 키워드/콘텐츠 자동 생성
- ✅ **실시간 환율 대시보드**: 4개 주요 통화 모니터링 + 캔들스틱 차트

---

## 🏗️ 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                     SY Global Connect                           │
│               통합 무역 플랫폼 Dashboard                          │
│              (dashboard.py - 메인 허브)                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
    ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
    │          │          │          │          │          │          │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│ 시장  │ │ 바이어 │ │ 물류비 │ │ 서류  │ │  SEO  │ │ 환율  │ │ 전시회 │
│ 분석  │ │ 발굴  │ │ 계산  │ │ 생성  │ │마케팅 │ │모니터 │ │ 정보  │
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘
```

### 대시보드 구성 (dashboard.py)

```
┌─────────────────────────────────────────────────────────────┐
│  헤더                                                        │
│  - 타이틀: 세연 글로벌 커넥트                                │
│  - 위젯: 💵 환율 계산기 | 💬 AI 챗봇 (Popover)               │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  네비게이션 바 (Horizontal Menu)                            │
│  [🏠 Home] [📋 Task] [🎨 With Us] [⚙️ Settings]           │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────┬──────────────────────────────────────┐
│  사이드바            │  메인 콘텐츠 영역                     │
│                      │                                      │
│  1) 해외진출 전략    │  [Home 화면]                         │
│     - 시장동향       │  - 네이버 뉴스 티커                  │
│     - 전략분석       │  - 업무 진행률 (4개 메트릭)          │
│     - 규제진단       │  - 빠른 링크                         │
│                      │                                      │
│  2) SEO 서비스       │  [Task 화면]                         │
│                      │  - 업무 목록 편집 (Data Editor)      │
│  3) AI 바이어 매칭   │  - 진행률 차트                       │
│     - 바이어 찾기    │                                      │
│     - 전시회 일정    │  [With Us 화면]                      │
│                      │  - 회사 소개                         │
│  4) 환율 정보        │  - 솔루션 소개                       │
│                      │  - Contact 정보                      │
│  5) 무역 서류        │                                      │
│                      │  [Settings 화면]                     │
│  로고 영역           │  - 로그인/회원가입                   │
│  (KITA AX MASTER)    │                                      │
└──────────────────────┴──────────────────────────────────────┘
```

---

## 🚀 주요 모듈

### 1️⃣ 해외진출 전략 허브 (Market Analysis)

**파일**: `mac_mic_1.py`, `new_kotra_4.py`, `macro_1.py`, `micro_1.py`, `buyer_maps.py`

#### 핵심 기능

**A) Target Scouting - 시장 탐색**
- HS Code 기반 품목 검색
- 국가별 관세율 조회
- 시장 규모 분석

**B) Risk Guard - 리스크 분석**
- **진입장벽 분석**
  - 관세율 (Tariff)
  - 비관세 장벽 (NTB)
  - 기술 장벽 (TBT)
- **AI SWOT 전략 생성** (GPT-4 기반)
  - Strengths/Weaknesses/Opportunities/Threats
  - 시장 진입 전략 제안

**C) Compliance Navigator - 인증 조회**
- 국가별/품목별 필수 인증 정보
- KOTRA 해외인증정보 API 연동
- 준비 서류 체크리스트

**D) 전시회 정보 - 글로벌 전시회 지도**
- 지역별 전시회 분포 시각화 (Folium)
- 산업분야별 필터링
- 일정 캘린더

#### 주요 함수

```python
# mac_mic_1.py
def load_hs_code_data() -> pd.DataFrame
def search_hs_code_by_product(query: str) -> list

# new_kotra_4.py
def render_barriers_strategy(country: str, hs_code: str)
def get_region_info(country: str) -> dict

# buyer_maps.py
def render_step4_exhibitions()
def load_exhibitions() -> pd.DataFrame
```

#### 사용 예시

```python
# 1. HS Code 검색
search_hs_code_by_product("화장품")
# → [{"code": "3304", "name": "미용 또는 메이크업용 제품"}]

# 2. 진입장벽 분석
render_barriers_strategy(country="United States", hs_code="3304")
# → SWOT 전략 + 관세율 + 규제 정보
```

---

### 2️⃣ AI 바이어 매칭 & 이메일 생성 (Buyer Matching)

**파일**: `03_ai_chatbot.py`, `dashboard.py`

#### 핵심 기능

**A) 스마트 바이어 검색**
- **데이터 소스**: 5개 공공기관 CSV 통합
  - KOTRA 해외바이어 현황 (20만+)
  - 중진공 구매오퍼/인콰이어리 (8만+)
  - 무보 화장품 바이어 (2만+)
  - 고비즈코리아 거래처 (5천+)

**B) 매칭 점수 계산 (0~100점)**

```python
def score_buyer_record(row, industry, hs_code, countries, require_email):
    score = 0
    
    # 1. 국가 일치 (30점)
    if row['country'] in countries:
        score += 30
    
    # 2. 산업 키워드 일치 (20~30점)
    for keyword in INDUSTRY_KEYWORDS[industry]:
        if keyword in row['product_text'].lower():
            score += 30 if len(keyword) > 5 else 20
    
    # 3. HS 코드 일치 (40점)
    if hs_code in row['hs_codes']:
        score += 40
    
    # 4. 이메일 보유 (15점)
    if require_email and row['email']:
        score += 15
    
    # 5. 연락처 정보 (5점)
    if row['contact_person']:
        score += 5
    
    return min(score, 100)
```

**C) AI 이메일 생성**
- GPT-4 기반 맞춤형 제안 이메일
- 한국어 → 영어/중국어 자동 번역
- 실시간 수정 가능

**D) 중복 제거 로직**

```python
def dedupe_buyer_candidates(buyers: list) -> list:
    """도메인 기반 중복 제거 (높은 점수 우선)"""
    seen_domains = {}
    for buyer in buyers:
        domain = normalize_domain(buyer['domain'])
        if domain not in seen_domains or \
           buyer['match_score'] > seen_domains[domain]['match_score']:
            seen_domains[domain] = buyer
    return list(seen_domains.values())
```

#### 산업 분류 (30개 분야)

```python
INDUSTRY_KEYWORDS = {
    "화장품·뷰티": ["cosmetic", "beauty", "skincare"],
    "식품·음료": ["food", "beverage", "농산물"],
    "패션·의류": ["fashion", "apparel", "textile"],
    "전자·IT": ["electronic", "IT", "semiconductor"],
    # ... 총 30개 산업
}
```

#### 워크플로우

```
[사용자 입력]
  ↓
[1. 검색 조건 설정]
  - 산업: 화장품·뷰티
  - HS Code: 3304
  - 국가: United States, Japan
  - 이메일 필수: Yes
  ↓
[2. CSV 데이터 로딩 & 표준화]
  - 5개 파일 통합 (30만+ 레코드)
  - 컬럼 매핑 (company_name, email, etc.)
  ↓
[3. 매칭 점수 계산]
  - 국가 30점 + 키워드 30점 + HS 40점 = 100점
  ↓
[4. 중복 제거 & 정렬]
  - 도메인 기반 deduplication
  - 상위 N개 추출
  ↓
[5. AI 이메일 생성]
  - 바이어별 맞춤 이메일
  - 번역: 한국어 → 영어/중국어
  ↓
[출력]
  - 바이어 카드 (Expander)
  - 편집 가능한 이메일 템플릿
```

---

### 3️⃣ 물류비 자동 계산 (Logistics Calculator)

**파일**: `auto_docs.py` (16.py 통합)

#### 지원 범위

| 항목 | 세부 내용 |
|------|----------|
| **출발 도시** | 구미, 청주, 화성, 수도권, 부산, 대구, 광주, 울산, 창원 (9개) |
| **출발 항만** | 부산항(9개 항로), 인천항(5개 항로), 광양항(3개 항로) |
| **도착 항만** | LA, 뉴욕, 상하이, 함부르크, 로테르담, 싱가포르, 호치민, 도쿄 등 |
| **컨테이너** | 20ft, 40ft, 40hc, LCL (CBM 단위) |

#### 계산 항목

```python
# FCL (Full Container Load)
총 물류비 = (해상운임(USD) × 환율) + 항만부대비용 + 내륙운송비

# 해상운임: KCCI 기반
KCCI_FREIGHT_RATES = {
    "부산-LA": {"20ft": 1200, "40ft": 2400, "40hc": 2600},
    "부산-뉴욕": {"20ft": 2500, "40ft": 5000, "40hc": 5400},
    # ...
}

# 항만 부대비용
PORT_CHARGES = {
    "THC": 150,          # Terminal Handling Charge
    "Wharfage": 50,      # 항만 사용료
    "Doc Fee": 30,       # 서류 수수료
    "Handling": 40,      # 하역비
    "Seal Fee": 10,      # 봉인 수수료
    "Container Tax": 20  # 컨테이너 세
}

# 내륙 운송비 (9×3 매트릭스)
INLAND_TRANSPORT = {
    "구미": {"부산항": 300000, "인천항": 450000, "광양항": 350000},
    "청주": {"부산항": 350000, "인천항": 400000, "광양항": 380000},
    # ...
}
```

#### 환율 조회 (3단계 폴백)

```python
def get_exchange_rate():
    # 1순위: 관세청 API
    try:
        response = requests.get("https://unipass.customs.go.kr/...")
        return float(response.json()['data'][0]['usd_rate'])
    except:
        pass
    
    # 2순위: yfinance
    try:
        import yfinance as yf
        data = yf.download("USDKRW=X", period="1d")
        return float(data['Close'].iloc[-1])
    except:
        pass
    
    # 3순위: 기본값 (.env에서 설정)
    return float(os.getenv("DEFAULT_EXCHANGE_RATE", "1450"))
```

---

### 4️⃣ 무역 서류 자동 생성 + AI 분석 (Smart Documentation)

**파일**: `auto_docs.py` (16.py 통합)

#### 지원 서류 (6종)

| 서류명 | 영문명 | 주요 내용 | 생성 방식 |
|--------|--------|----------|----------|
| 상업송장 | Commercial Invoice | HS Code, 단가, 총액 | python-docx 자동 테이블 |
| 포장명세서 | Packing List | NW/GW/CBM, 포장 단위 | python-docx 자동 테이블 |
| 매매계약서 | Sales Contract | Incoterms, 결제조건 | python-docx 자동 테이블 |
| 견적송장 | Proforma Invoice | 물류비 포함 견적 | python-docx 자동 테이블 |
| 구매주문서 | Purchase Order | 발주번호, 납기일 | python-docx 자동 테이블 |
| L/C 신청서 | L/C Application | 개설은행, 선적조건 | python-docx 자동 테이블 |

#### 듀얼 생성 모드

**모드 A: 표준 양식**
```python
from docx import Document
from docx.shared import Pt, RGBColor

doc = Document()
doc.add_heading('COMMERCIAL INVOICE', 0)

# 테이블 자동 생성
table = doc.add_table(rows=10, cols=4)
table.style = 'Light Grid Accent 1'

# 데이터 입력
table.cell(0, 0).text = "Shipper"
table.cell(0, 1).text = shipper_name
# ...

doc.save("Commercial_Invoice.docx")
```

**모드 B: 자사 양식 (템플릿 치환)**
```python
# 기존 Word 파일 로드
doc = Document("template.docx")

# {{변수}} 치환
for paragraph in doc.paragraphs:
    if "{{shipper}}" in paragraph.text:
        paragraph.text = paragraph.text.replace("{{shipper}}", shipper_name)
    if "{{inv_no}}" in paragraph.text:
        paragraph.text = paragraph.text.replace("{{inv_no}}", invoice_no)
    # ...

doc.save("Filled_Invoice.docx")
```

#### 스마트 자동 계산

```python
# 1. Incoterms별 운임 가산
FREIGHT_RATES = {"AIR": 0.12, "SEA": 0.04}

if incoterms in ["CFR", "CIF", "DDP"]:
    freight_cost = base_price * FREIGHT_RATES[transport_mode]
else:
    freight_cost = 0

# 2. FTA 관세 적용
FTA_RATES = {
    "한-미 FTA": 0.0,
    "한-EU FTA": 0.0,
    "RCEP": 0.05,
    "CPTPP": 0.03,
    "일반": 0.08
}
tariff = base_price * FTA_RATES[fta_agreement]

# 3. 보험료 계산
INSURANCE_RATES = {
    "ICC(A) 전위험담보": 0.008,
    "ICC(B) 한정담보": 0.005,
    "ICC(C) 최소담보": 0.003
}
insurance = (base_price + freight_cost) * INSURANCE_RATES[insurance_type] * 1.1

# 4. 결제 수수료
PAYMENT_FEES = {
    "L/C at Sight": 0.012,
    "T/T": 0.001,
    "D/P": 0.005
}
fee = base_price * PAYMENT_FEES[payment_method]
```

#### AI 거래 분석 (GPT-4o 기반)

```python
def analyze_trade_risk(transaction_data: dict) -> dict:
    """
    5대 리스크 분석 + 영문 특약 조항 생성
    
    Returns:
        {
            "advice": {
                "환율_및_관세_리스크": "...",
                "운송_리스크": "...",
                "법적_및_규제": "...",
                "보험_필요성": "...",
                "사업_연속성": "..."
            },
            "clauses": {
                "Price and Payment Terms": "...",
                "Delivery Terms": "...",
                "Customs and Duties": "...",
                "Insurance": "...",
                "Documentation": "..."
            }
        }
    """
    
    system_prompt = """
    당신은 15년 경력의 국제무역 전문가입니다.
    - Incoterms 2020 전문 컨설턴트
    - FTA 활용 및 환율 헤지 전문가
    
    다음 형식으로 답변하세요:
    
    [ADVICE]
    1. 환율 및 관세 리스크: ...
    2. 운송 리스크: ...
    3. 법적 및 규제 요구사항: ...
    4. 보험 필요성: ...
    5. 사업 연속성: ...
    
    [CLAUSES]
    1. Price and Payment Terms: ...
    2. Delivery Terms: ...
    3. Customs and Duties: ...
    4. Insurance: ...
    5. Documentation: ...
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(transaction_data, ensure_ascii=False)}
        ]
    )
    
    # 파싱 및 반환
    return parse_ai_response(response.choices[0].message.content)
```

---

### 5️⃣ 글로벌 SEO 마케팅 자동화 (Global SEO Pro)

**파일**: `junghyun.py` (seo8.py 통합)

#### 핵심 기능

**A) 시장별 키워드 자동 생성**
- **입력**: 제품명 or HS Code + 타겟 국가 (60개국)
- **출력**: 
  - High-Intent 키워드 10개
  - Long-tail 키워드 8개
  - Google Trends 인기 검색어 (정제)

**B) SerpApi 데이터 수집**

```python
def fetch_comprehensive_serpapi_data(seed_keyword, country_code):
    """
    Google Shopping / Search / Ads / PAA / Related Searches 수집
    """
    params = {
        "engine": "google",
        "q": seed_keyword,
        "gl": country_code,  # 국가 코드 (예: "us", "jp", "kr")
        "hl": get_language_code(country_code),  # 언어 코드
        "api_key": os.getenv("SERPAPI_KEY")
    }
    
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    
    return {
        "shopping_results": data.get("shopping_results", []),
        "ads": data.get("ads", []),
        "organic_results": data.get("organic_results", []),
        "people_also_ask": data.get("related_questions", []),
        "related_searches": data.get("related_searches", [])
    }
```

**C) 키워드 정제 알고리즘**

```python
def extract_high_intent_keywords(serp_data, seed_keyword):
    """
    고의도 키워드 10개 추출 (브랜드/리테일러/용량 제외)
    """
    
    # 제외 규칙
    EXCLUSION_RULES = {
        "brands": ["amazon", "walmart", "ebay", "alibaba"],
        "sizes": ["ml", "oz", "g", "kg", "pack"],
        "info": ["how to", "what is", "guide", "tutorial"]
    }
    
    keywords = []
    
    # 1. Shopping 키워드 추출
    for item in serp_data["shopping_results"]:
        title = item.get("title", "").lower()
        if not any(brand in title for brand in EXCLUSION_RULES["brands"]):
            keywords.append(title)
    
    # 2. 광고 키워드 추출
    for ad in serp_data["ads"]:
        headline = ad.get("title", "").lower()
        if not any(size in headline for size in EXCLUSION_RULES["sizes"]):
            keywords.append(headline)
    
    # 3. 중복 제거 & 점수화
    unique_keywords = list(set(keywords))
    scored = [(kw, calculate_intent_score(kw, seed_keyword)) for kw in unique_keywords]
    
    # 4. 상위 10개 반환
    return [kw for kw, score in sorted(scored, key=lambda x: x[1], reverse=True)[:10]]
```

**D) STP/타겟 분석**

```python
def generate_target_audience_analysis(high_intent_keywords):
    """
    고의도 키워드 기반 타겟 소비층 분석
    """
    prompt = f"""
    다음 고의도 키워드를 분석하여 핵심 타겟 고객을 정의하세요:
    {', '.join(high_intent_keywords)}
    
    출력 형식:
    [DEMOGRAPHICS]
    - 연령대: ...
    - 성별: ...
    - 소득 수준: ...
    
    [PSYCHOGRAPHICS]
    - 라이프스타일: ...
    - 구매 동기: ...
    - 핵심 니즈: ...
    
    [BEHAVIORAL]
    - 검색 패턴: ...
    - 구매 채널: ...
    - 의사결정 요인: ...
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
```

**E) 마케팅 콘텐츠 3종 생성**

```python
def generate_high_quality_content(seed_keyword, target_analysis):
    """
    Amazon Bullet / D2C 상세페이지 / SNS 포스트 생성
    """
    
    # 1. Amazon Bullet Points (5개)
    amazon_prompt = f"""
    제품: {seed_keyword}
    타겟: {target_analysis}
    
    아마존 판매 페이지용 Bullet Point 5개를 작성하세요.
    각 항목은 주요 혜택과 특징을 강조하며, 검색 키워드를 자연스럽게 포함합니다.
    """
    
    # 2. D2C 상세페이지
    d2c_prompt = f"""
    제품: {seed_keyword}
    타겟: {target_analysis}
    
    자사몰용 상세페이지를 작성하세요.
    구성: 헤드라인 → 주요 혜택 → 사용 방법 → CTA
    """
    
    # 3. SNS 포스트
    sns_prompt = f"""
    제품: {seed_keyword}
    타겟: {target_analysis}
    
    인스타그램/페이스북용 포스트를 작성하세요.
    구성: 후크 → 스토리 → 해시태그 (10개)
    """
    
    # GPT 호출 (병렬)
    # ...
    
    return {
        "amazon": amazon_bullets,
        "d2c": d2c_page,
        "sns": sns_post
    }
```

**F) 현지화 번역 (비영어권)**

```python
def translate_with_deepl(text, target_lang):
    """DeepL API 우선 번역"""
    try:
        response = requests.post(
            "https://api-free.deepl.com/v2/translate",
            data={
                "auth_key": os.getenv("DEEPL_API_KEY"),
                "text": text,
                "target_lang": target_lang
            }
        )
        return response.json()["translations"][0]["text"]
    except:
        return translate_with_gpt(text, target_lang)  # 폴백

def translate_with_gpt(text, target_lang):
    """GPT 번역 (DeepL 실패 시)"""
    prompt = f"Translate to {target_lang}:\n{text}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

#### 워크플로우

```
[사용자 입력]
  - 제품: "organic skincare"
  - 국가: Japan (비영어권)
  ↓
[1. Seed Keyword 정규화]
  - 영어: "organic skincare"
  - 일본어: "オーガニックスキンケア"
  ↓
[2. SerpApi 데이터 수집]
  - Shopping: 50개 결과
  - Ads: 20개 키워드
  - PAA: 15개 질문
  - Related: 8개 검색어
  ↓
[3. 키워드 추출 (영어 기준)]
  - High-Intent: ["natural face cream", "organic moisturizer", ...]
  - Long-tail: ["best organic skincare for sensitive skin", ...]
  ↓
[4. 키워드 번역 (개별)]
  - "natural face cream" → "天然フェイスクリーム"
  - "organic moisturizer" → "オーガニック保湿剤"
  ↓
[5. Google Trends]
  - 현지어 인기 검색어: ["韓国スキンケア", "敏感肌 化粧品"]
  - 영어 의미: ["Korean skincare", "sensitive skin cosmetics"]
  ↓
[6. STP/타겟 분석 (영어 키워드만 사용)]
  - Demographics: 25-40세 여성, 중상 소득
  - Psychographics: 자연주의, 건강 중시
  ↓
[7. 콘텐츠 생성 (영어 먼저)]
  - Amazon: 5 bullet points
  - D2C: 500단어 페이지
  - SNS: 150자 포스트
  ↓
[8. 현지화 번역]
  - DeepL 우선 → GPT 폴백
  - English meaning 별도 생성
  ↓
[출력]
  - Excel: 현지어 + 영어 의미 컬럼
  - Word: 현지어 + 영어 의미 섹션
```

---

### 6️⃣ 실시간 환율 모니터링 (Exchange Rate Monitor)

**파일**: `exchange_rate.py`, `dashboard.py`

#### 주요 기능

**A) 실시간 환율 위젯 (Popover)**

```python
def render_exchange_widget(title="💵 환율", popover_width="stretch"):
    """
    Popover 형태의 환율 계산기
    """
    with st.popover(title, width=popover_width):
        # 통화 선택
        selected_currency = st.selectbox(
            "통화 선택",
            ["USD (미국 달러)", "JPY (일본 엔)", "EUR (유로)", "CNY (중국 위안)"]
        )
        
        # 실시간 환율 조회
        rate = get_live_exchange_rate(selected_currency)
        st.metric("적용 환율", f"{rate:,.2f} KRW")
        
        # 환율 계산
        foreign_val = st.number_input("입력 금액", min_value=0.0)
        krw_result = foreign_val * rate
        st.metric("변환 결과", f"{krw_result:,.0f} 원")
```

**B) 캔들스틱 차트 (Plotly)**

```python
import plotly.graph_objects as go

def render_candlestick_chart(currency_pair):
    """
    최근 30일 환율 캔들스틱 차트
    """
    ticker = f"{currency_pair}=X"  # 예: USDKRW=X
    data = yf.download(ticker, period="1mo", interval="1d")
    
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close']
    )])
    
    fig.update_layout(
        title=f"{currency_pair} 환율 추이 (30일)",
        xaxis_title="날짜",
        yaxis_title="환율 (KRW)",
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

**C) 스파크라인 (Sparkline)**

```python
def create_sparkline(data, color="#051161"):
    """
    최근 15일 환율 추이 미니 차트 (데이터프레임 내 표시)
    """
    import base64
    from io import BytesIO
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(2, 0.5))
    plt.plot(data, color=color, linewidth=1.5)
    plt.axis('off')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    
    img_base64 = base64.b64encode(buf.read()).decode()
    return f'<img src="data:image/png;base64,{img_base64}" />'
```

**D) 송금 환율 자동 계산**

```python
def calculate_remittance_rates(base_rate):
    """
    매매기준율 기반 송금 환율 계산
    """
    return {
        "송금_보낼_때": base_rate * 1.01,  # +1%
        "송금_받을_때": base_rate * 0.99   # -1%
    }
```

---

### 7️⃣ 전시회 정보 (Exhibition Information)

**파일**: `buyer_maps.py`

#### 주요 기능

**A) 전시회 지도 시각화**

```python
import folium
from streamlit_folium import st_folium

def render_step4_exhibitions():
    """
    Folium 기반 전시회 지도
    """
    exhibitions = load_exhibitions()
    
    # 지도 생성 (중심: 서울)
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=2)
    
    # 마커 추가
    for _, row in exhibitions.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"<b>{row['전시회명']}</b><br>{row['기간']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
    
    # Streamlit에 표시
    st_folium(m, width=800, height=600)
```

**B) 산업분야별 필터링**

```python
def filter_exhibitions_by_industry(exhibitions, industry):
    """
    산업분야별 전시회 필터링
    """
    return exhibitions[exhibitions['산업분야'].str.contains(industry, na=False)]
```

---

## 💻 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/your-repo/sy-global-connect.git
cd sy-global-connect
```

### 2. 가상환경 생성 (권장)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

**requirements.txt** (통합 버전):

```
streamlit
openai
python-dotenv
pytrends
requests
pandas
openpyxl
python-docx
matplotlib
numpy
yfinance
beautifulsoup4
plotly
streamlit-option-menu
pillow
PyPDF2
folium
streamlit-folium
```

### 4. 환경 변수 설정

프로젝트 루트에 `.env` 파일 생성:

```env
# ========== 필수 API 키 ==========
# OpenAI (SWOT 분석, 바이어 이메일, SEO 콘텐츠, 서류 AI 분석)
OPENAI_API_KEY=sk-proj-your-key-here

# ========== 선택 API 키 ==========
# KOTRA 공공데이터 (진입장벽, 인증 정보)
OVERSEAS_CERTI=your-kotra-cert-key
KOTRA_MARKET_API_KEY=your-kotra-market-key
KOTRA_NTB_API_KEY=your-kotra-ntb-key

# SerpApi (SEO 키워드 분석)
SERPAPI_KEY=your-serpapi-key

# DeepL (번역 품질 향상)
DEEPL_API_KEY=your-deepl-key

# 관세청 환율 API
CUSTOMS_EXCHANGE_RATE_KEY=your-customs-key

# ========== 기본값 설정 ==========
DEFAULT_EXCHANGE_RATE=1450
```

### 5. 데이터 파일 준비

**data/ 폴더 구조**:

```
data/
├── HScode_customs.csv              # HS Code 관세 정보
├── EXHIBITION_PLAN.csv             # 전시회 정보
├── users.csv                       # 사용자 DB (자동 생성)
├── 대한무역투자진흥공사_해외바이어 현황_20240829.csv
├── 중소벤처기업진흥공단_해외바이어 구매오퍼 정보_20241231.csv
├── 중소벤처기업진흥공단_해외바이어 인콰이어리 신청_20241230.csv
├── 한국무역보험공사_화장품 바이어 정보_20200812.csv
└── 중소벤처기업진흥공단_고비즈코리아 거래처정보_20250523.csv
```

### 6. 실행

```bash
# 메인 대시보드 실행
streamlit run dashboard.py
```

브라우저에서 `http://localhost:8501` 자동 오픈

---

## 🎮 사용 가이드

### 대시보드 메인 화면 (Home)

```
1. [헤더 우측] 💵 환율 위젯 클릭
   → 통화 선택: USD
   → 1000 USD 입력
   → 결과: 1,320,000 원

2. [헤더 우측] 💬 AI 챗봇 클릭
   → 질문: "HS 3304 미국 수입 관세율은?"
   → 답변: "HS 3304는 화장품으로, 미국 기본 관세율은 0%입니다. 한-미 FTA 적용 시 추가 혜택..."

3. [뉴스 티커] 스크롤
   → 네이버 경제/증권 속보 자동 스크롤
   → 클릭 시 원문 새 탭 열림

4. [업무 진행률] 메트릭 확인
   - 📝 수출 서류 준비: 67%
   - 🚢 물류 처리: 50%
   - 💼 바이어 매칭: 33%

5. [빠른 링크] 수출지원센터 / 수출역량진단 테스트
```

### Task 화면

```
1. [네비게이션] Task 탭 클릭

2. [업무 목록 편집]
   - 체크박스: 완료 여부 토글
   - 행 추가: "+" 버튼
   - 행 삭제: "-" 버튼
   - 카테고리: 드롭다운 선택

3. [💾 변경사항 저장] 버튼 클릭
   → 세션 상태 업데이트
   → 진행률 자동 재계산
```

### With Us 화면

```
1. [네비게이션] With Us 탭 클릭

2. [회사 소개] 카드
   → AI 무역 인텔리전스 기업 소개

3. [솔루션 소개] 카드
   → 1,000만+ 기업 수출입 정보 분석

4. [AI 마케팅 자동화] 카드
   → 4억+ 무역 데이터 실시간 처리

5. [Contact 정보]
   - Email: contact@syglobal.com
   - Phone: +82-2-1234-5678
```

### Settings 화면 (로그인/회원가입)

```
[로그인 화면]
1. 아이디: kita123
2. 비밀번호: ********
3. [로그인] 버튼 → Home 화면 이동

[회원가입 화면]
1. [회원가입] 버튼 클릭
2. 아이디: newuser
3. 이메일: newuser@example.com
4. 비밀번호: ********
5. [가입 완료] → data/users.csv 저장
6. 로그인 화면 복귀
```

---

### 사이드바 네비게이션

#### 1) 해외진출 전략 허브

```
[시장동향] 버튼 → pages/macro_1.py
- 거시적 무역 지표
- 국가별 GDP/무역량

[전략분석] 버튼 → pages/micro_1.py
- 미시적 산업 분석
- 경쟁사 벤치마킹

[규제진단] 버튼 → pages/mac_mic_1.py
- HS Code 검색
- 진입장벽 분석
- SWOT 전략 생성
```

#### 2) SEO 서비스

```
[바로가기] 버튼 → pages/junghyun.py
1. 입력:
   - 제품: "organic tea"
   - 국가: Japan
2. [🔍 전체 시장 분석 시작]
3. 출력:
   - 타겟 분석
   - 키워드 3종 (High-Intent/Long-tail/Trends)
   - 콘텐츠 3종 (Amazon/D2C/SNS)
   - 📥 Excel/Word 다운로드
```

#### 3) AI 바이어 매칭 서비스

```
[바이어 찾기] 버튼 → pages/03_ai_chatbot.py
1. 산업: 화장품·뷰티
2. HS Code: 3304
3. 국가: United States, Japan
4. [🔍 바이어 검색]
5. 결과:
   - 매칭 점수 85점 이상 상위 10개
   - AI 이메일 자동 생성
   - 영어/중국어 번역 버튼

[전시회 일정] 버튼 → pages/buyer_maps.py
- Folium 지도: 전세계 전시회 분포
- 필터: 산업분야, 기간
```

#### 4) 환율 정보 확인

```
[바로가기] 버튼 → pages/exchange_rate.py
1. [4개 통화 실시간 현황]
   - USD/JPY/EUR/CNY
   - 스파크라인 (15일 추이)
   - 송금 환율 자동 계산

2. [캔들스틱 차트]
   - 통화 선택: USD
   - 기간: 30일
   - 줌/팬 기능
```

#### 5) 무역 서류 자동 완성

```
[바로가기] 버튼 → pages/auto_docs.py

[탭 1: 물류비 계산]
1. 출발 도시: 구미
2. 출발 항만: 부산항
3. 도착 항만: LA
4. 컨테이너: 40ft
5. [💰 물류비 견적 산출]
6. 결과:
   - 총 물류비: ₩5,650,000 (USD $3,896)
   - 비용 구성 차트
   - 절감액: ₩850,000 (13.1%)

[탭 2: 서류 생성]
1. 거래 정보 입력:
   - Shipper: ABC Corp
   - Consignee: XYZ Trading
   - 품목: 전자부품 (HS 8542.39)
   - 수량: 1000 EA @ $15.50

2. 조건 설정:
   - Incoterms: CIF
   - FTA: 한-미 FTA (관세 0%)
   - 보험: ICC(A) 전위험담보
   - 결제: L/C at Sight

3. 서류 선택:
   ☑️ Commercial Invoice
   ☑️ Packing List
   ☑️ Sales Contract
   ☐ Proforma Invoice
   ☐ Purchase Order
   ☐ L/C Application

4. [📝 서류 생성 및 AI 분석]

5. 출력:
   - 6개 Word 파일 다운로드
   - AI 리스크 분석 보고서:
     * [ADVICE] 5대 리스크
     * [CLAUSES] 영문 특약 조항
```

---

## 🔧 기술 스택

### Backend

| 카테고리 | 기술 스택 |
|---------|----------|
| **프레임워크** | Streamlit 1.28+ |
| **AI 엔진** | OpenAI GPT-4o / GPT-4o-mini |
| **데이터 처리** | Pandas, NumPy |
| **웹 스크래핑** | BeautifulSoup4, Requests |
| **API 연동** | yfinance, SerpApi, KOTRA, DeepL |
| **문서 생성** | python-docx, openpyxl |
| **시각화** | Plotly, Matplotlib, Folium |

### Frontend

| 카테고리 | 기술 스택 |
|---------|----------|
| **UI 컴포넌트** | streamlit-option-menu, streamlit-folium |
| **차트** | Plotly (캔들스틱, 스파크라인) |
| **지도** | Folium (전시회 위치) |
| **스타일링** | Custom CSS (디자인 시스템) |

### 디자인 시스템

```css
:root {
  --bg: #ffffff;
  --card: #ffffff;
  --line: #e5e7eb;
  --soft: #f3f4f6;
  --text: #0f172a;
  --muted: #64748b;
  --accent: #051161;
  --accent-weak: rgba(5,17,97,0.10);
}
```

---

## 🔐 API 설정

### API 키 발급 방법

#### 1. OpenAI API (필수)
```
1. https://platform.openai.com/api-keys 접속
2. 회원가입/로그인
3. "Create new secret key" 클릭
4. sk-proj-... 형태의 키 복사
5. .env 파일에 OPENAI_API_KEY=sk-proj-... 추가
```

#### 2. KOTRA 공공데이터 (선택)
```
1. https://www.data.go.kr/ 접속
2. 검색: "해외인증정보", "비관세장벽", "시장 정보"
3. 각 API 활용 신청
4. 발급된 키를 .env에 추가
```

#### 3. SerpApi (선택)
```
1. https://serpapi.com/ 접속
2. 무료 플랜 가입 (100 queries/월)
3. API 키 복사
4. .env에 SERPAPI_KEY=... 추가
```

#### 4. DeepL (선택)
```
1. https://www.deepl.com/pro-api 접속
2. 무료 플랜 가입 (500,000 chars/월)
3. API 키 복사
4. .env에 DEEPL_API_KEY=... 추가
```

#### 5. 관세청 환율 API (선택)
```
1. https://unipass.customs.go.kr 접속
2. 공공데이터포털에서 "환율정보 조회 서비스" 신청
3. 승인 후 키 발급
4. .env에 CUSTOMS_EXCHANGE_RATE_KEY=... 추가
```

---

## ❓ FAQ

### Q1. API 키 없이 사용 가능한가요?
**A.** 부분적으로 가능합니다.
- ✅ 물류비 계산: 가능 (기본 환율 사용)
- ✅ 환율 모니터링: 가능 (yfinance 사용)
- ✅ 전시회 정보: 가능 (CSV 데이터)
- ❌ AI 분석 (SWOT, 이메일, SEO, 서류): OpenAI 키 필수
- ❌ 실시간 SEO 데이터: SerpApi 키 필수

### Q2. 바이어 CSV 파일이 없으면?
**A.** 샘플 데이터로 테스트 가능합니다.
```python
# 03_ai_chatbot.py에서 샘플 데이터 생성
sample_buyers = pd.DataFrame([
    {"company_name": "ABC Trading", "country": "United States", 
     "email": "info@abc.com", "product_text": "cosmetics"},
    # ...
])
```

### Q3. 환율이 실시간으로 업데이트되나요?
**A.** 네, 다음 순서로 조회합니다:
1. 관세청 API (최신)
2. yfinance (실시간)
3. 기본값 (.env 설정)

### Q4. 생성된 서류는 법적 효력이 있나요?
**A.** 본 시스템은 서류 작성을 보조하는 도구입니다. 생성된 서류는 반드시 검토 후 사용하시고, 법적 자문이 필요한 경우 전문가와 상담하세요.

### Q5. 다크 모드를 지원하나요?
**A.** 현재는 라이트 모드만 지원합니다. 향후 업데이트 예정입니다.

### Q6. 모바일에서도 사용 가능한가요?
**A.** Streamlit은 반응형 디자인을 지원하지만, 일부 기능(차트, 지도)은 데스크톱 환경에 최적화되어 있습니다.

### Q7. 커스텀 서류 양식 포맷은?
**A.** `.docx` 형식만 지원합니다. 파일 내에 `{{shipper}}`, `{{consignee}}` 등의 플레이스홀더를 삽입하세요.

### Q8. SEO 키워드가 정확하지 않아요.
**A.** SerpApi 키를 설정하면 실시간 검색 데이터를 기반으로 정확도가 크게 향상됩니다.

---

## 📁 프로젝트 파일 구조

```
sy-global-connect/
├── dashboard.py                    # 메인 대시보드 (Home/Task/With Us/Settings)
├── pages/                          # 서브 페이지
│   ├── macro_1.py                  # 거시적 분석
│   ├── micro_1.py                  # 미시적 분석
│   ├── mac_mic_1.py                # 전략 & 인증
│   ├── new_kotra_4.py              # KOTRA 진입장벽 & SWOT
│   ├── buyer_maps.py               # 전시회 정보
│   ├── junghyun.py                 # SEO 마케팅 (seo8.py 통합)
│   ├── 03_ai_chatbot.py            # AI 바이어 매칭
│   ├── exchange_rate.py            # 환율 모니터링
│   └── auto_docs.py                # 물류비 & 서류 생성 (16.py 통합)
├── data/                           # 데이터 폴더
│   ├── HScode_customs.csv
│   ├── EXHIBITION_PLAN.csv
│   ├── users.csv                   # 사용자 DB (자동 생성)
│   └── [5개 바이어 CSV 파일]
├── assets/                         # 정적 파일
│   └── logo.png                    # 로고 이미지
├── pdf/                            # PDF 리포트 저장
├── .env                            # 환경변수 (API 키)
├── .env.example                    # 환경변수 예시
├── .gitignore
├── requirements.txt                # 패키지 의존성
└── README.md                       # 이 문서
```

---

## 🔄 업데이트 히스토리

### v1.0.0 (2025-02-05)
- ✅ 통합 대시보드 구축 (Home/Task/With Us/Settings)
- ✅ 7대 모듈 통합 (시장 분석, 바이어 매칭, 물류비, 서류, SEO, 환율, 전시회)
- ✅ AI 기능 전면 적용 (GPT-4o 기반)
- ✅ 커스텀 네비게이션 시스템
- ✅ 실시간 환율 위젯 (yfinance)
- ✅ 네이버 뉴스 티커
- ✅ Task 관리 시스템 (Data Editor)
- ✅ 로그인/회원가입 기능

---

## 👥 개발팀

**KITA AX MASTER TEAM4 - Seyeon Global Connect**

| 이름 | 담당 모듈 |
|------|----------|
| 최신비 | AI 바이어 매칭, 대시보드 챗봇 |
| 음정현 | SEO 마케팅 자동화 |
| 김지수 | 물류비 계산, 무역 서류 생성 |
| 박세연 | 환율 모니터링, 캔들스틱 차트 |
| 김가영 | 시장 분석, 전시회 정보 |
| 이아람 | 자료 취합 및 레이아웃 구성 |

---

## 📞 문의 및 지원

- **Email**: contact@syglobal.com
- **Website**: [https://tradetestingteam4.streamlit.app/](https://tradetestingteam4.streamlit.app/)
- **GitHub Issues**: [Report a bug](https://github.com/your-repo/issues)
- **Documentation**: 본 README 파일

---

## 🙏 크레딧

### 데이터 제공
- KOTRA (대한무역투자진흥공사)
- 중소벤처기업진흥공단
- 한국무역보험공사
- 관세청
- KCCI (한국형 컨테이너 운임지수)

### 기술 파트너
- OpenAI (GPT-4o / GPT-4o-mini)
- SerpApi (검색 데이터)
- DeepL (번역 엔진)
- yfinance (금융 데이터)

### 오픈소스
- Streamlit (UI 프레임워크)
- python-docx (문서 생성)
- Plotly (차트 시각화)
- Folium (지도 시각화)

---
