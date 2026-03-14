import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

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
st.write("영어 기사 번역기 돌리느라 지치셨죠? 앤트리치 AI가 월가의 영문 실적 기사를 방금 읽고, 가장 중요한 핵심만 한글 표로 정리해 드립니다.")
st.divider()

# ==========================================
# 🧠 AI 두뇌 (실적 기사 심층 스캔)
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_earnings_summary(ticker):
    news_results = []
    try:
        # 💡 개선점 1: when:7d 삭제. EPS, Revenue 등의 핵심 키워드 추가!
        url = f"https://news.google.com/rss/search?q={ticker}+latest+quarter+earnings+EPS+revenue+beat+miss&hl=en-US&gl=US&ceid=US:en"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 💡 개선점 2: 상위 10개 기사의 '제목' + '기사 본문 요약(숫자 포함)'까지 싹쓸이!
        for news in soup.find_all("item")[:10]:
            title = news.title.text if news.title else ""
            desc_html = news.description.text if news.description else ""
            # HTML 찌꺼기 제거하고 깔끔한 텍스트만 추출
            desc_text = BeautifulSoup(desc_html, "html.parser").get_text(separator=" ", strip=True)
            news_results.append(f"[제목]: {title}\n[요약]: {desc_text}")
    except:
        return "ERROR_NEWS"
        
    if not news_results:
        return "NO_NEWS"
        
    news_text = "\n\n".join(news_results)
    
    # 💡 개선점 3: 프롬프트를 더 강력하게 압박! (무조건 숫자를 찾아내라고 지시)
    prompt = f"""
    You are an expert Wall Street financial analyst writing for a Korean audience ('Antrich' blog).
    Here are the news headlines and snippets for the latest earnings report of [{ticker}].
    
    {news_text}

    Carefully extract the exact numbers for Revenue and EPS from the text above. 
    Based on this information, provide a clear, concise earnings summary entirely in KOREAN.
    You MUST format the output exactly like this structure:

    ### 📊 [{ticker}] 최신 실적 요약 (AI 분석)
    | 항목 | 발표 수치 및 시장 예상치 비교 | 
    |---|---|
    | 💰 매출 (Revenue) | (예: 251억 달러 기록 / 예상치 256억 달러 하회) |
    | 💵 주당순이익 (EPS) | (예: 0.71달러 기록 / 예상치 0.74달러 하회) |

    ### 🔮 향후 가이던스 (Guidance)
    - (회사에서 발표한 다음 분기나 연간 전망을 1~2줄로 요약. 기사에 없으면 '언급되지 않음'으로 처리)

    ### 🎯 앤트리치 3줄 요약 (종합 평가)
    1. (핵심 포인트 1)
    2. (핵심 포인트 2)
    3. (시장의 반응이나 주가 향방에 대한 짧은 코멘트)

    명심하세요: 숫자가 포함된 팩트를 최우선으로 찾아서 표에 넣으세요!
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
        
        with st.spinner(f"월가에서 [{target_ticker}] 영문 실적 발표 자료를 가져와 번역/분석 중입니다... 🕵️‍♂️ (약 5~10초 소요)"):
            
            result_text = get_earnings_summary(target_ticker)
            
            if result_text == "ERROR_LIMIT":
                st.error("🚨 앗! AI가 생각할 시간을 달래요. 딱 1분만 기다리셨다가 다시 버튼을 눌러주세요!")
            elif result_text == "ERROR_NEWS":
                st.error("🚨 뉴스 데이터를 불러오는 데 실패했습니다.")
            elif result_text == "NO_NEWS":
                st.info(f"앗! [{target_ticker}]의 실적 발표 뉴스를 찾을 수 없습니다. 티커가 틀렸는지 확인해 주세요!")
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
