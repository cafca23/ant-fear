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
# 🚨 [업그레이드] 입장권 파쇄기 탑재! (주소창 숨김)
# ==========================================
# 1. 앤트리치 방문증(세션) 발급 확인
if "passed" not in st.session_state:
    st.session_state.passed = False

# 2. 주소창에 암호가 있으면 방문증에 '합격' 도장을 찍고, 암호를 파쇄합니다!
if st.query_params.get("from") == "blog":
    st.session_state.passed = True
    st.query_params.clear()  # 💡 마법의 코드: 주소창에서 '?from=blog'를 즉시 지워버립니다!

# 3. 방문증이 없는 불법 침입자 차단
if not st.session_state.passed:
    st.error("🚨 비정상적인 접근입니다!")
    st.write("이 **[앤트리치 종목 이유 판독기]**는 블로그 방문자 전용 프리미엄 기능입니다.")
    st.write("아래 버튼을 눌러 블로그를 통해 정식으로 접속해 주세요! 🐜")
    st.link_button("👉 앤트리치 블로그로 이동하기", "https://blog.naver.com/antrich10")
    st.stop() # 🛑 여기서 프로그램 멈춤
# ==========================================

st.title("🚨 대체 이거 왜 올라/떨어져?!")
# ... (이 아래는 기존 코드와 동일하게 쭉 진행됩니다!) ...

st.title("🚨이 종목 왜 상승 / 하락 했지?")
st.write("앤트리치가 방금 뜬 뉴스를 싹쓸이해서 급등락 이유를 딱 3줄로 요약해 드립니다.")
st.divider()

# ==========================================
# 1. 사용자 입력 받기
# ==========================================
stock_name = st.text_input("🔍 궁금한 종목명을 입력하세요 (예: 삼성전자, 에코프로, 테슬라)", placeholder="종목명을 입력하고 엔터를 치거나 버튼을 누르세요!")

# ==========================================
# 2. 뉴스 수집 및 AI 분석 실행
# ==========================================
if st.button("이유 찾기 🚀", use_container_width=True):
    if not stock_name:
        st.warning("종목명을 먼저 입력해 주세요!")
    else:
        with st.spinner(f"인터넷을 뒤져서 [{stock_name}] 최신 뉴스를 싹쓸이 분석 중입니다... 🕵️‍♂️ (약 5초 소요)"):
            
            # [1단계] 구글 뉴스에서 해당 종목의 최신(최근 1일) 뉴스 15개 긁어오기
            news_results = []
            try:
                # 검색어에 '주식'을 붙여서 연예/사회 등 엉뚱한 뉴스 필터링
                url = f"https://news.google.com/rss/search?q={stock_name} 주식 when:1d&hl=ko&gl=KR&ceid=KR:ko"
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.text, "html.parser")
                
                for news in soup.find_all("item")[:15]:
                    news_results.append(f"- {news.title.text}")
            except:
                st.error("뉴스 데이터를 불러오는 데 실패했습니다.")
            
            # [2단계] 뉴스가 있으면 AI에게 분석 명령 내리기
            if not news_results:
                st.info(f"앗! 최근 24시간 동안 [{stock_name}]에 대한 특별한 뉴스가 없습니다. 잔잔한 하루인가 보네요!")
            else:
                news_text = "\n".join(news_results)
                
                prompt = f"""
                당신은 '앤트리치' 블로그의 수석 주식 분석가입니다.
                다음은 방금 수집된 [{stock_name}] 주식의 최신 뉴스 제목들입니다.
                
                {news_text}

                이 뉴스들을 종합적으로 분석해서, 지금 이 종목의 주가가 움직이는(오르거나 내리거나 이슈가 있는) 핵심 이유를 딱 '3가지 팩트'로만 요약해 주세요.

                [작성 규칙]
                1. 쓸데없는 인사말이나 서론은 무조건 빼고, 바로 1, 2, 3번 번호를 매겨서 이유만 설명하세요.
                2. 바쁜 현대인들이 스마트폰으로 3초 만에 읽고 이해할 수 있도록 아주 쉽고 명확하게 작성하세요.
                3. 마지막 줄에는 "💡 앤트리치 코멘트:"를 달고, 이 이슈가 단기적인 테마인지, 장기적인 실적에 영향을 줄 것인지 분석가의 의견을 딱 한 줄로 덧붙여 주세요.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.success("✅ 원인 분석 완료!")
                    
                    # 결과를 예쁜 박스 안에 담아서 보여주기
                    with st.container(border=True):
                        st.markdown(f"### 🎯 [{stock_name}] 주가 변동 요인 3줄 요약")
                        st.markdown(response.text)
                        
                except ResourceExhausted:
                    st.error("🚨 앗! AI가 생각할 시간을 달래요. 딱 1분만 기다리셨다가 다시 버튼을 눌러주세요!")
                except Exception as e:
                    st.error(f"🚨 알 수 없는 오류가 발생했습니다: {e}")

# ==========================================
# 3. 블로그 트래픽 유도용 하단 버튼
# ==========================================
st.divider()
st.caption("더 깊이 있는 종목 분석과 매매 타점이 궁금하다면?")
st.link_button("👉 앤트리치 블로그 바로가기", "https://blog.naver.com/antrich10", use_container_width=True)
