import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import yfinance as yf

# ==========================================
# 0. AI 세팅
# ==========================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

st.set_page_config(page_title="앤트리치 미주 실적 요약기", page_icon="🇺🇸")

# ==========================================
# 🚨 블로그 우회 접속 차단기
# ==========================================
if "passed" not in st.session_state:
    st.session_state.passed = False

if st.query_params.get("from") == "blog":
    st.session_state.passed = True
    st.query_params.clear()

if not st.session_state.passed:
    st.error("🚨 비정상적인 접근입니다!")
    st.write("이 **[미국 주식 실적발표 요약기]**는 블로그 방문자 전용 프리미엄 기능입니다.")
    st.write("아래 버튼을 눌러 블로그를 통해 정식으로 접속해 주세요! 🐜")
    st.link_button("👉 앤트리치 블로그로 이동하기", "https://blog.naver.com/antrich10")
    st.stop()
# ==========================================

st.title("🇺🇸 영어 1도 몰라도 OK! 미주 실적 요약기")
st.write("영어 기사 번역기 돌리느라 지치셨죠? 앤트리치 AI가 실제 재무 데이터와 월가 뉴스를 종합해 핵심만 한글 표로 정리해 드립니다.")
st.divider()

# ==========================================
# 🧠 AI 두뇌 (재무 데이터 + 핵심 지표 + 뉴스 결합)
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_earnings_summary(ticker):
    # ----------------------------------------
    # [1단계] yfinance로 '숫자' 캐내기 (PER, PBR, 순이익 추가!)
    # ----------------------------------------
    try:
        stock = yf.Ticker(ticker)
        
        # 1. EPS 및 매출 데이터
        eps_df = stock.earnings_dates
        eps_data = eps_df.head(3).to_string() if eps_df is not None and not eps_df.empty else "N/A"
        
        inc_stmt = stock.quarterly_income_stmt
        rev_data = inc_stmt.iloc[:5, :2].to_string() if inc_stmt is not None and not inc_stmt.empty else "N/A"
        
        # 💡 2. 대표적인 재무/가치평가 지표 (PER, PBR, PSR, 순이익) 추출
        info = stock.info
        per = info.get('trailingPE', 'N/A')
        pbr = info.get('priceToBook', 'N/A')
        psr = info.get('priceToSalesTrailing12Months', 'N/A')
        
        try:
            # 최근 분기 순이익 (Net Income)
            net_income_raw = inc_stmt.loc['Net Income'].iloc[0]
            net_income = f"$ {net_income_raw:,.0f}" if isinstance(net_income_raw, (int, float)) else "N/A"
        except:
            net_income = "N/A"
            
        financial_db = f"""[yfinance 공식 재무 데이터]
- EPS 히스토리:\n{eps_data}
- 최근 분기 재무제표:\n{rev_data}
- 핵심 지표: PER={per}, PBR={pbr}, PSR={psr}, 최근 분기 순이익={net_income}"""

    except Exception as e:
        financial_db = f"재무 데이터 수집 오류: {e}"

    # ----------------------------------------
    # [2단계] 구글 뉴스로 '가이던스 및 반응' 캐내기
    # ----------------------------------------
    news_results = []
    try:
        url = f"https://news.google.com/rss/search?q={ticker}+latest+quarter+earnings+guidance&hl=en-US&gl=US&ceid=US:en"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        for news in soup.find_all("item")[:10]:
            title = news.title.text if news.title else ""
            desc = BeautifulSoup(news.description.text, "html.parser").get_text(separator=" ", strip=True) if news.description else ""
            news_results.append(f"[뉴스 제목]: {title}\n[내용 요약]: {desc}")
    except:
        pass
        
    news_text = "\n\n".join(news_results) if news_results else "최근 뉴스를 찾을 수 없습니다."

    # ----------------------------------------
    # [3단계] 제미나이 프롬프트 지시 (표 2개로 분리!)
    # ----------------------------------------
    prompt = f"""
    당신은 '앤트리치' 블로그의 수석 주식 분석가입니다.
    아래 제공된 [{ticker}]의 데이터를 바탕으로 한국인 투자자를 위한 실적 요약을 작성하세요.

    1. [실제 재무 데이터]: 매출, EPS, 그리고 PER, PBR, PSR, 순이익 숫자를 찾아 표에 넣으세요.
    {financial_db}
    
    2. [최신 뉴스 반응]: 향후 가이던스와 종합 평가를 분석하세요.
    {news_text}

    [출력 양식 (반드시 아래 마크다운 표 형식을 유지할 것)]
    ### 📊 [{ticker}] 최신 실적 요약
    | 항목 | 발표 수치 및 결과 | 
    |---|---|
    | 💰 매출 (Revenue) | (예: 약 251억 달러 기록 / 지난 분기 대비 증가/감소) |
    | 💵 주당순이익 (EPS) | (예: 0.71달러 기록 / 시장 예상치 하회) |
    | 🏦 최근 분기 순이익 | (데이터에 있는 Net Income 수치를 읽기 쉽게 원화나 달러 단위로 변환해서 기재) |

    ### 🧮 핵심 가치평가(Valuation) 지표
    | 지표 | 현재 수치 | 앤트리치 코멘트 |
    |---|---|---|
    | PER (주가수익비율) | (수치) | (이 수치를 바탕으로 고평가/저평가 여부나 동종업계 대비 느낌을 한 줄로 코멘트) |
    | PBR (주가순자산비율)| (수치) | (가치 투자 관점에서의 한 줄 코멘트) |
    | PSR (주가매출비율) | (수치) | (매출 대비 주가 수준 코멘트) |

    ### 🔮 향후 가이던스 (Guidance)
    - (뉴스에서 파악된 다음 분기/연간 전망 1~2줄. 모르면 '명확히 확인되지 않음' 기재)

    ### 🎯 앤트리치 3줄 요약 (종합 평가)
    1. (핵심 포인트 1)
    2. (핵심 포인트 2)
    3. (주가 흐름 및 밸류에이션을 고려한 투자자 유의사항)
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except ResourceExhausted:
        return "ERROR_LIMIT"
    except Exception as e:
        return "ERROR_UNKNOWN"

# ==========================================
# 1. 사용자 입력 받기
# ==========================================
ticker_input = st.text_input("🔍 궁금한 미국 주식의 '티커(Ticker)'를 영어로 입력하세요 (예: TSLA, AAPL, NVDA)", placeholder="TSLA")

# ==========================================
# 2. 버튼 클릭 시 실행
# ==========================================
if st.button("실적 요약 🚀", use_container_width=True):
    if not ticker_input:
        st.warning("종목 티커를 먼저 입력해 주세요!")
    else:
        target_ticker = ticker_input.upper().strip() 
        
        with st.spinner(f"월가에서 [{target_ticker}]의 실제 재무제표와 뉴스를 분석 중입니다... 🕵️‍♂️ (약 5~10초)"):
            
            result_text = get_earnings_summary(target_ticker)
            
            if result_text == "ERROR_LIMIT":
                st.error("🚨 앗! AI가 생각할 시간을 달래요. 딱 1분만 기다리셨다가 다시 버튼을 눌러주세요!")
            elif result_text == "ERROR_UNKNOWN":
                st.error("🚨 알 수 없는 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
            else:
                st.success(f"✅ [{target_ticker}] 실적 분석 완료! (1시간 동안 캐시가 유지되어 빠르게 뜹니다.)")
                with st.container(border=True):
                    st.markdown(result_text)

# ==========================================
# 3. 블로그 트래픽 유도용 하단 버튼
# ==========================================
st.divider()
st.caption("실적 발표 후, 이 종목을 사야 할까 팔아야 할까? 앤트리치의 심층 분석을 확인하세요!")
st.link_button("👉 앤트리치 블로그 바로가기", "https://blog.naver.com/antrich10", use_container_width=True)
