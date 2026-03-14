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

st.set_page_config(page_title="앤트리치 종목 이유 판독기", page_icon="🚨")

# ==========================================
# 🚨 [최종 진화] 암살자 모드 파쇄기 가동! (화면 깜빡임 없이 조용히 지우기)
# ==========================================
# 1. 앤트리치 방문증(세션) 발급 확인
if "passed" not in st.session_state:
    st.session_state.passed = False

# 2. 주소창에 암호가 있으면 방문증에 '합격' 도장을 찍고, 암호를 조용히 지웁니다.
if st.query_params.get("from") == "blog":
    st.session_state.passed = True
    st.query_params.clear()  # 💡 암호 지우기 끝! (여기에 있던 st.rerun()을 삭제해서 딜레이를 없앴습니다)

# 3. 방문증이 없는 불법 침입자 차단
if not st.session_state.passed:
    st.error("🚨 비정상적인 접근입니다!")
    st.write("이 **[앤트리치 종목 이유 판독기]**는 블로그 방문자 전용 프리미엄 기능입니다.")
    st.write("아래 버튼을 눌러 블로그를 통해 정식으로 접속해 주세요! 🐜")
    st.link_button("👉 앤트리치 블로그로 이동하기", "https://blog.naver.com/antrich10")
    st.stop() # 🛑 여기서 프로그램 작동을 완전히 멈춥니다!
# ==========================================

st.title("🚨 이 종목 왜 상승 / 하락 했지?")
st.write("앤트리치가 방금 뜬 뉴스를 싹쓸이해서 급등락 이유를 딱 3줄로 요약해 드립니다.")
st.divider()

# ==========================================
# 🧠 [핵심 마법] 1시간 기억하는 AI 두뇌 (캐싱)
# ==========================================
# ttl=3600 은 '3600초(1시간) 동안 이 정답을 기억해라!' 라는 뜻입니다.
@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_reason(stock_keyword):
    # 1. 뉴스 긁어오기
    news_results = []
    try:
        url = f"https://news.google.com/rss/search?q={stock_keyword} 주식 when:1d&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        
        for news in soup.find_all("item")[:15]:
            news_results.append(f"- {news.title.text}")
    except:
        return "ERROR_NEWS"
        
    if not news_results:
        return "NO_NEWS"
        
    # 2. AI에게 분석 지시
    news_text = "\n".join(news_results)
    prompt = f"""
    당신은 '앤트리치' 블로그의 수석 주식 분석가입니다.
    다음은 방금 수집된 [{stock_keyword}] 주식의 최신 뉴스 제목들입니다.
    
    {news_text}

    이 뉴스들을 종합적으로 분석해서, 지금 이 종목의 주가가 움직이는(오르거나 내리거나 이슈가 있는) 핵심 이유를 딱 '3가지 팩트'로만 요약해 주세요.

    [작성 규칙]
    1. 쓸데없는 인사말이나 서론은 무조건 빼고, 바로 1, 2, 3번 번호를 매겨서 이유만 설명하세요.
    2. 바쁜 현대인들이 스마트폰으로 3초 만에 읽고 이해할 수 있도록 아주 쉽고 명확하게 작성하세요.
    3. 마지막 줄에는 "💡 앤트리치 코멘트:"를 달고, 이 이슈가 단기적인 테마인지, 장기적인 실적에 영향을 줄 것인지 분석가의 의견을 딱 한 줄로 덧붙여 주세요.
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
stock_name = st.text_input("🔍 궁금한 종목명을 입력하세요 (예: 삼성전자, 에코프로, 테슬라)", placeholder="종목명을 입력하고 엔터를 치거나 버튼을 누르세요!")

# ==========================================
# 2. 버튼 클릭 시 실행
# ==========================================
if st.button("이유 찾기 🚀", use_container_width=True):
    if not stock_name:
        st.warning("종목명을 먼저 입력해 주세요!")
    else:
        with st.spinner(f"[{stock_name}] 최신 뉴스를 싹쓸이 분석 중입니다..."):
            
            # 여기서 방금 만든 마법의 함수를 부릅니다!
            result_text = get_stock_reason(stock_name)
            
            # 결과에 따라 알맞은 화면 보여주기
            if result_text == "ERROR_LIMIT":
                st.error("🚨 앗! AI가 생각할 시간을 달래요. 딱 1분만 기다리셨다가 다시 버튼을 눌러주세요!")
            elif result_text == "ERROR_NEWS":
                st.error("🚨 뉴스 데이터를 불러오는 데 실패했습니다.")
            elif result_text == "NO_NEWS":
                st.info(f"앗! 최근 24시간 동안 [{stock_name}]에 대한 특별한 뉴스가 없습니다. 잔잔한 하루인가 보네요!")
            elif result_text == "ERROR_UNKNOWN":
                st.error("🚨 알 수 없는 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
            else:
                st.success(f"✅ [{stock_name}] 원인 분석 완료! (1시간 동안 결과가 초고속으로 유지됩니다.)")
                with st.container(border=True):
                    st.markdown(f"### 🎯 [{stock_name}] 주가 변동 요인 3줄 요약")
                    st.markdown(result_text)

# ==========================================
# 3. 블로그 트래픽 유도용 하단 버튼
# ==========================================
st.divider()
st.caption("더 깊이 있는 종목 분석과 매매 타점이 궁금하다면?")
st.link_button("👉 앤트리치 블로그 바로가기", "https://blog.naver.com/antrich10", use_container_width=True)
