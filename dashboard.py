import streamlit as st
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

st.set_page_config(page_title="앤트리치 시황판", page_icon="📊", layout="wide")

# ==========================================
# 🚨 [업그레이드] 초고속 입장권 파쇄기 가동! (0.1초 컷)
# ==========================================
# 1. 방문증(세션) 발급 확인
if "passed" not in st.session_state:
    st.session_state.passed = False

# 2. 주소창에 암호가 있는지 검사합니다.
if st.query_params.get("from") == "blog":
    st.session_state.passed = True
    st.query_params.clear() # 암호 지우기!
    st.rerun() # 💡 핵심 부스터: 화면을 그리기도 전에 0.1초 만에 강제 새로고침해서 흔적을 완벽히 날립니다!

# 3. 방문증이 없는 불법 침입자 철통 방어
if not st.session_state.passed:
    st.error("🚨 비정상적인 접근입니다!")
    st.write("이 **[앤트리치 3대 공포/탐욕 지수 현황판]**은 블로그 방문자 전용 프리미엄 기능입니다.")
    st.write("아래 버튼을 눌러 블로그를 통해 정식으로 접속해 주세요! 🐜")
    st.link_button("👉 앤트리치 블로그로 이동하기", "https://blog.naver.com/antrich10")
    st.stop() # 🛑 여기서 프로그램 작동 정지!
# ==========================================

st.title("📊 앤트리치 3대 공포/탐욕 지수 현황판")
st.write("투자의 나침반! 현재 시장의 분위기를 한눈에 파악하고 매매 타이밍을 잡으세요.")
st.divider()

# ==========================================
# [상단] 3대 심리 지표 (VIX, CNN, V-KOSPI)
# ==========================================
col1, col2, col3 = st.columns(3)

# 1. 미국 VIX 지수 (왼쪽 칸)
with col1:
    try:
        vix = yf.Ticker("^VIX")
        vix_hist = vix.history(period="5d")['Close']
        vix_price = float(vix_hist.iloc[-1])
        vix_prev = float(vix_hist.iloc[-2])
        vix_diff = vix_price - vix_prev
        vix_pct = (vix_diff / vix_prev) * 100
        
        if vix_price < 15:
            vix_state = "🟢 극도의 탐욕 & 매도"
        elif vix_price < 20:
            vix_state = "🟡 탐욕 & 매도"
        elif vix_price < 25:
            vix_state = "⚪ 중립 & 중립"
        elif vix_price < 40:
            vix_state = "🟠 공포 & 매수"
        else:
            vix_state = "🔴 극도의 공포 & 매수"
            
        st.metric(label="🇺🇸 미국 VIX (공포 지수)", value=f"{vix_price:.2f}", 
                  delta=f"{vix_diff:.2f} ({vix_pct:.2f}%)", delta_color="inverse")
        st.markdown(f"**현재 상태: {vix_state}**")
        
    except Exception as e:
        st.metric(label="🇺🇸 미국 VIX", value="불러오기 실패")

    with st.expander("📌 VIX 지수 해석 가이드"):
        st.markdown("""
        * **15 미만 (극도의 탐욕 & 매도)** : 하락 우려 없이 대중이 상승에 취해있는 상태
        * **15 ~ 20 (탐욕 & 매도)** : 경제가 안정적이며 주가가 꾸준히 우상향하는 구간
        * **20 ~ 25 (중립 & 중립)** : 금리, 전쟁 등 악재 뉴스로 변동성이 커지는 구간
        * **25 ~ 40 (공포 & 매수)** : 지수 하락이 눈에 띄며 시장에 공포 심리가 확산
        * **40 이상 (극도의 공포 & 매수)** : 2008년 금융위기(80), 2020년 코로나(82) 수준의 패닉장
        """)

# 2. 미국 CNN 공포/탐욕 지수 (가운데 칸)
with col2:
    try:
        url_cnn = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
        res_cnn = requests.get(url_cnn, headers=headers)
        data_cnn = res_cnn.json()
        
        score_cnn = float(data_cnn['fear_and_greed']['score'])
        prev_cnn = float(data_cnn['fear_and_greed']['previous_close'])
        cnn_diff = score_cnn - prev_cnn
        
        if score_cnn <= 25:
            cnn_state = "🔴 극도의 공포 & 매수"
        elif score_cnn <= 45:
            cnn_state = "🟠 공포 & 매수"
        elif score_cnn <= 55:
            cnn_state = "⚪ 중립 & 중립"
        elif score_cnn <= 75:
            cnn_state = "🟡 안정 & 매도"
        else:
            cnn_state = "🟢 극도의 탐욕 & 매도"
            
        st.metric(label="🦅 미국 CNN 지수", value=f"{score_cnn:.1f}", delta=f"{cnn_diff:.1f}")
        st.markdown(f"**현재 상태: {cnn_state}**")
        
    except Exception as e:
        st.metric(label="🦅 미국 CNN 지수", value="불러오기 실패")

    with st.expander("📌 CNN 지수 해석 가이드"):
        st.markdown("""
        * **0 ~ 25 (극도의 공포 & 매수)** : 대중의 강력한 투매가 일어나는 최고의 매수 기회
        * **25 ~ 45 (공포 & 매수)** : 투자자들이 몸을 사리며 현금을 관망하는 구간
        * **45 ~ 55 (중립 & 중립)** : 수급과 심리가 균형을 이룬 평온한 시장
        * **55 ~ 75 (안정 & 매도)** : 수익 소문이 돌며 대중의 매수세가 몰리는 구간
        * **75 ~ 100 (극도의 탐욕 & 매도)** : FOMO 절정 및 거품 붕괴 경고 (현금 확보 및 익절)
        """)

# 3. 한국 KOSPI 공포 지수 (오른쪽 칸)
with col3:
    try:
        url_vkospi = "https://kr.investing.com/indices/kospi-volatility"
        inv_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        res_vkospi = requests.get(url_vkospi, headers=inv_headers)
        soup_vkospi = BeautifulSoup(res_vkospi.text, "html.parser")
