import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import urllib.request
import urllib.parse
import json

# ==========================================
# 0. AI 및 위장 신분증 세팅
# ==========================================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}

st.set_page_config(page_title="앤트리치 테마주 족집게", page_icon="🎯")

# ==========================================
# 🚨 블로그 우회 접속 차단기 (암살자 모드)
# ==========================================
if "passed" not in st.session_state:
    st.session_state.passed = False

if st.query_params.get("from") == "blog":
    st.session_state.passed = True
    st.query_params.clear()

if not st.session_state.passed:
    st.error("🚨 비정상적인 접근입니다!")
    st.write("이 **[앤트리치 테마주 족집게]**는 블로그 방문자 전용 프리미엄 기능입니다.")
    st.write("아래 버튼을 눌러 블로그를 통해 정식으로 접속해 주세요! 🐜")
    st.link_button("👉 앤트리치 블로그로 이동하기", "https://blog.naver.com/antrich10")
    st.stop()
# ==========================================

st.title("🎯 주식 관련주/수혜주 찾기")
st.write("앤트리치가 실시간 뉴스를 싹쓸이 분석해 '진짜 수혜주'만 3초 만에 쏙쏙 골라드립니다.")
st.divider()

# ==========================================
# 🧠 [듀얼 엔진] 네이버 + 구글 뉴스 결합 캐싱
# ==========================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_theme_stocks(theme):
    news_results = []
    
    # ----------------------------------------
    # 엔진 1: 네이버 뉴스 API (실시간 속보 및 찌라시 포착)
    # ----------------------------------------
    try:
        client_id = st.secrets["NAVER_CLIENT_ID"]
        client_secret = st.secrets["NAVER_CLIENT_SECRET"]
        # 검색어 세팅: 테마 이름 + 특징주/대장주
        query = urllib.parse.quote(f"{theme} 특징주 OR 대장주 OR 수혜주")
        url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=10&sort=sim"
        
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        
        response = urllib.request.urlopen(request)
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            for item in data['items']:
                # 네이버 API는 제목에 HTML 태그(<b>)를 섞어서 주므로 깔끔하게 제거
                clean_title = BeautifulSoup(item['title'], 'html.parser').text
                news_results.append(f"[네이버 뉴스] {clean_title}")
    except Exception as e:
        pass # 네이버 에러 나면 조용히 패스하고 구글로 넘어감

    # ----------------------------------------
    # 엔진 2: 구글 뉴스 RSS (글로벌 트렌드 및 거시적 시각 포착)
    # ----------------------------------------
    try:
        url_google = f"https://news.google.com/rss/search?q={theme} 주식 수혜주 when:7d&hl=ko&gl=KR&ceid=KR:ko"
        res_google = requests.get(url_google, headers=headers)
        soup_google = BeautifulSoup(res_google.text, "html.parser")
        
        for news in soup_google.find_all("item")[:10]:
            news_results.append(f"[구글 뉴스] {news.title.text}")
    except Exception as e:
        pass

    # 두 엔진에서 긁어온 뉴스 합치기
    news_text = "\n".join(news_results) if news_results else "최근 뚜렷한 특징주 뉴스가 없습니다. 일반적인 시장 지식을 활용해 답변하세요."

    # ----------------------------------------
