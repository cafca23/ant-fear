import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

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
# 🚨 [최종 진화] 암살자 모드 파쇄기 가동! 
# ==========================================
if "passed" not in st.session_state:
    st.session_state.passed = False

if st.query_params.get("from") == "blog":
    st.session_state.passed = True
    st.query_params.clear()  # 암호 조용히 지우기

if not st.session_state.passed:
    st.error("🚨 비정상적인 접근입니다!")
    st.write("이 **[미국 주식 실적발표 요약기]**는 블로그 방문자 전용 프리미엄 기능입니다.")
    st.write("아래 버튼을 눌러 블로그를 통해 정식으로 접속해 주세요! 🐜")
    st.link_button("👉 앤트리치 블로그로 이동하기", "https://blog.naver.com/antrich10")
    st.stop()
# ==========================================

st.title("영어 1도 몰라도 OK! 미주 실적 요약기")
st.write("영어 기사 번역기 돌리느라 지치셨죠? 앤트리치 AI가 월가의 영문 실적 기사를 방금 읽고, 가장 중요한 핵심만 한글 표로 정리해 드립니다.")
st.divider()

# ==========================================
# 🧠 [핵심 마법] 1시간 기억하는 AI 두뇌 (캐싱)
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_earnings_summary(ticker):
    # 1. 미국 구글 뉴스에서 해당 티커의 '영문' 실적(Earnings) 기사 긁어오기
    news_results = []
    try:
        # 💡 영어 원문 기사를 정확히 가져오기 위해 검색어를 영어로 세팅!
        url = f"https://news.google.com/rss/search?q={ticker}+earnings+report+OR+results+when:7d&hl=en-US&gl=US&ceid=US:en"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        for news in soup.find_all("item")[:15]:
            news_results.append(f"- {news.title.text}")
    except:
        return "ERROR_NEWS"
        
    if not news_results:
        return "NO_NEWS"
        
    # 2. 제미나이 AI에게 월가 애널리스트 빙의 지시!
    news_text = "\n".join(news_results)
    prompt = f"""
    You are an expert Wall Street financial analyst writing for a Korean audience ('Antrich' blog).
    Here are the latest English news headlines and snippets for the earnings report of [{ticker}].
    
    {news_text}

    Based on this information, please provide a clear, concise earnings summary entirely in KOREAN.
    You MUST format the output exactly like this structure:

    ### 📊 [{ticker}] 최신 실적 요약 (AI 분석)
    | 항목 | 발표 수치 및 결과 | 
    |---|---|
    | 💰 매출 (Revenue) | (매출 수치 기입, 예상치 상회/하회/부합 여부) |
    | 💵 주당순이익 (EPS) | (EPS 수치 기입, 예상치 상회/하회/부합 여부) |

    ### 🔮 향후 가이던스 (Guidance)
    - (회사에서 발표한 다음 분기나 연간 전망을 1~2줄로 요약. 정보가 없으면 '현재 수집된 기사에서는 가이던스 내용이 확인되지 않습니다.'라고 작성)

    ### 🎯 앤트리치 3줄 요약 (종합 평가)
    1. (핵심 포인트 1)
    2. (핵심 포인트 2)
    3. (시장의 반응이나 주가 향방에 대한 짧은 코멘트)

    명심하세요: 모든 답변은 100% 자연스러운 한국어로 작성해야 하며, 표(Table) 형식을 반드시 유지하세요.
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
# 💡 티커(Ticker)를 영어 대문자로 입력받도록 유도합니다.
ticker_input = st.text_input("🔍 궁금한 미국 주식의 '티커(Ticker)'를 영어로 입력하세요 (예: TSLA, AAPL, NVDA)", placeholder="TSLA")

# ==========================================
# 2. 버튼 클릭 시 실행
# ==========================================
if st.button("실적 요약 🚀", use_container_width=True):
    if not ticker_input:
        st.warning("종목 티커를 먼저 입력해 주세요!")
    else:
        # 소문자로 입력해도 대문자로 찰떡같이 바꿔줍니다.
        target_ticker = ticker_input.upper().strip() 
        
        with st.spinner(f"월가에서 [{target_ticker}] 영문 실적 발표 자료를 가져와 번역/분석 중입니다... 🕵️‍♂️ (약 5~10초 소요)"):
            
            result_text = get_earnings_summary(target_ticker)
            
            if result_text == "ERROR_LIMIT":
                st.error("🚨 앗! AI가 생각할 시간을 달래요. 딱 1분만 기다리셨다가 다시 버튼을 눌러주세요!")
            elif result_text == "ERROR_NEWS":
                st.error("🚨 뉴스 데이터를 불러오는 데 실패했습니다.")
            elif result_text == "NO_NEWS":
                st.info(f"앗! 최근 7일 내에 [{target_ticker}]의 굵직한 실적 발표 뉴스가 없습니다. 아직 어닝 시즌이 아니거나 티커가 틀렸을 수 있어요!")
            elif result_text == "ERROR_UNKNOWN":
                st.error("🚨 알 수 없는 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
            else:
                st.success(f"✅ [{target_ticker}] 실적 분석 완료! (1시간 동안 캐시가 유지되어 엄청 빠르게 뜹니다.)")
                with st.container(border=True):
                    st.markdown(result_text)

# ==========================================
# 3. 블로그 트래픽 유도용 하단 버튼
# ==========================================
st.divider()
st.caption("실적 발표 후, 이 종목을 사야 할까 팔아야 할까? 앤트리치의 심층 분석을 확인하세요!")
st.link_button("👉 앤트리치 블로그 바로가기", "https://blog.naver.com/antrich10", use_container_width=True)
