import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# ==========================================
# 0. AI 및 위장 신분증 기본 세팅
# ==========================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}

st.set_page_config(page_title="앤트리치 테마주 족집게", page_icon="🎯")

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
    st.write("이 **[앤트리치 테마주 족집게]**는 블로그 방문자 전용 프리미엄 기능입니다.")
    st.write("아래 버튼을 눌러 블로그를 통해 정식으로 접속해 주세요! 🐜")
    st.link_button("👉 앤트리치 블로그로 이동하기", "https://blog.naver.com/antrich10")
    st.stop()
# ==========================================

st.title("🎯 그래서 관련주가 뭔데?! (테마주 족집게)")
st.write("광고성 블로그 글 뒤지지 마세요! AI가 뉴스를 싹쓸이 분석해 '진짜 수혜주(대장주)'만 3초 만에 쏙쏙 골라드립니다.")
st.divider()

# ==========================================
# 🧠 [핵심 마법] 1시간 기억하는 AI 두뇌 (캐싱)
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_theme_stocks(theme):
    # 1. 특정 테마의 '특징주/대장주/수혜주' 관련 최신 뉴스 긁어오기
    news_results = []
    try:
        url = f"https://news.google.com/rss/search?q={theme} 주식 특징주 OR 대장주 OR 수혜주 when:7d&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        for news in soup.find_all("item")[:15]:
            news_results.append(f"- {news.title.text}")
    except:
        return "ERROR_NEWS"
        
    news_text = "\n".join(news_results) if news_results else "최근 7일 내의 뚜렷한 특징주 뉴스가 부족합니다. 일반적인 시장 지식을 활용해 답변하세요."

    # 2. AI에게 테마주 전문가 빙의 지시
    prompt = f"""
    당신은 '앤트리치' 주식 블로그의 테마주 발굴 전문가입니다.
    사용자가 궁금해하는 주식 테마는 [{theme}] 입니다.
    다음은 방금 수집된 해당 테마의 최신 뉴스 헤드라인입니다.
    
    {news_text}

    이 뉴스 정보와 당신의 주식 시장 지식을 종합하여, 현재 한국 시장(KOSPI/KOSDAQ) 또는 미국 시장에서 [{theme}] 테마를 이끄는 '대장주(1개)'와 '관련주/2등주(2개)'를 꼽아주세요.

    [작성 규칙]
    1. 불필요한 인사말이나 서론 없이 바로 종목명부터 제시하세요.
    2. 왜 이 종목이 수혜주로 꼽히는지 명확한 팩트 기반의 '1줄 이유'를 반드시 적어주세요.
    3. 아래 마크다운 양식을 정확히 지켜서 출력하세요.

    ### 🥇 [{theme}] 대장주 (Top Pick)
    - **[종목명]**: (이 종목이 대장주인 팩트 1줄 이유)

    ### 🥈 [{theme}] 관련주 / 2등주
    1. **[종목명]**: (수혜주로 꼽히는 팩트 1줄 이유)
    2. **[종목명]**: (수혜주로 꼽히는 팩트 1줄 이유)

    ### 💡 앤트리치 코멘트 (투자 유의사항)
    - (이 테마에 투자할 때 주의할 점이나 재료의 지속성에 대한 분석가 코멘트 1~2줄)
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
theme_input = st.text_input("🔍 궁금한 테마를 입력하세요 (예: 원전, AI 반도체, 전고체 배터리, 비만치료제)", placeholder="테마 키워드를 입력하고 엔터를 치세요!")

# ==========================================
# 2. 버튼 클릭 시 실행
# ==========================================
if st.button("대장주 찾기 🚀", use_container_width=True):
    if not theme_input:
        st.warning("테마 키워드를 먼저 입력해 주세요!")
    else:
        with st.spinner(f"인터넷을 뒤져서 [{theme_input}] 관련 진짜 수혜주를 색출 중입니다... 🕵️‍♂️ (캐시된 테마는 0.1초 컷!)"):
            
            result_text = get_theme_stocks(theme_input)
            
            if result_text == "ERROR_LIMIT":
                st.error("🚨 앗! AI가 생각할 시간을 달래요. 딱 1분만 기다리셨다가 다시 버튼을 눌러주세요!")
            elif result_text == "ERROR_NEWS":
                st.error("🚨 뉴스 데이터를 불러오는 데 실패했습니다.")
            elif result_text == "ERROR_UNKNOWN":
                st.error("🚨 알 수 없는 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
            else:
                st.success(f"✅ [{theme_input}] 테마주 족집게 분석 완료!")
                with st.container(border=True):
                    st.markdown(result_text)

# ==========================================
# 3. 블로그 트래픽 유도용 하단 버튼
# ==========================================
st.divider()
st.caption("테마주 단타 치기 전에 필수 확인! 앤트리치의 시장 분석을 먼저 읽어보세요.")
st.link_button("👉 앤트리치 블로그 바로가기", "https://blog.naver.com/antrich10", use_container_width=True)