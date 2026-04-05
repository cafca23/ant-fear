import streamlit as st
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

# 💡 [보안 우회] 모바일 앱인 척 위장하는 강력한 헤더
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
    'Referer': 'https://m.stock.naver.com/'
}

st.set_page_config(page_title="앤트리치 시황판", page_icon="📊", layout="wide")

# ==========================================
# 🚨 [최종 진화] 암살자 모드 파쇄기 가동! (화면 깜빡임 없이 조용히 지우기)
# ==========================================
if "passed" not in st.session_state:
    st.session_state.passed = False

if st.query_params.get("from") == "blog":
    st.session_state.passed = True
    st.query_params.clear()  

if not st.session_state.passed:
    st.error("🚨 비정상적인 접근입니다!")
    st.write("이 **[앤트리치 3대 공포/탐욕 지수 현황판]**은 블로그 방문자 전용 프리미엄 기능입니다.")
    st.write("아래 버튼을 눌러 블로그를 통해 정식으로 접속해 주세요! 🐜")
    st.link_button("👉 앤트리치 블로그로 이동하기", "https://blog.naver.com/antrich10")
    st.stop() 
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
            
        sign = "+" if vix_diff > 0 else ""
        st.metric(label="🇺🇸 미국 VIX (공포 지수)", value=f"{vix_price:.2f}", 
                  delta=f"{sign}{vix_diff:.2f} ({sign}{vix_pct:.2f}%)", delta_color="inverse")
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
            
        sign = "+" if cnn_diff > 0 else ""
        st.metric(label="🦅 미국 CNN 지수", value=f"{score_cnn:.1f}", delta=f"{sign}{cnn_diff:.1f}")
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
        # 💡 [이중 우회 1순위] 야후 파이낸스 공식 티커 (서버 차단 없음)
        try:
            vkospi = yf.Ticker("^VKOSPI")
            vk_hist = vkospi.history(period="5d")['Close']
            vkospi_value = float(vk_hist.iloc[-1])
            vkospi_prev = float(vk_hist.iloc[-2])
            vkospi_diff = vkospi_value - vkospi_prev
            vkospi_pct = (vkospi_diff / vkospi_prev) * 100
        except:
            # 💡 [이중 우회 2순위] 네이버 모바일 API (PC버전보다 보안이 낮아 뚫림)
            url_vkospi = "https://m.stock.naver.com/api/index/VKOSPI/basic"
            res_vkospi = requests.get(url_vkospi, headers=headers)
            data_vkospi = res_vkospi.json()
            
            vkospi_value = float(str(data_vkospi.get('closePrice', '0')).replace(',', ''))
            diff_raw = data_vkospi.get('compareToPreviousPrice', data_vkospi.get('compareToPreviousClosePrice', '0'))
            vkospi_diff = float(str(diff_raw).replace(',', ''))
            vkospi_pct = float(str(data_vkospi.get('fluctuationsRatio', '0')).replace(',', ''))
            
            if data_vkospi.get('fluctuationsType', {}).get('text') == '하락' or str(data_vkospi.get('fluctuationsRatio', '')).startswith('-'):
                vkospi_diff = -abs(vkospi_diff)
                vkospi_pct = -abs(vkospi_pct)
                
        sign = "+" if vkospi_diff > 0 else ""
        vkospi_delta_str = f"{sign}{vkospi_diff:.2f} ({sign}{vkospi_pct:.2f}%)"
        
        if vkospi_value < 15:
            vkospi_state = "🟢 극도의 탐욕 & 매도"
        elif vkospi_value < 20:
            vkospi_state = "🟡 안정 & 매도"
        elif vkospi_value < 30:
            vkospi_state = "⚪ 경계 & 중립"
        elif vkospi_value < 40:
            vkospi_state = "🟠 극도의 공포 & 매수"
        else:
            vkospi_state = "🔴 역사적 패닉 & 매수"
            
        st.metric(label="🐯 한국 V-KOSPI (공포 지수)", value=f"{vkospi_value:.2f}", 
                  delta=vkospi_delta_str, delta_color="inverse")
        st.markdown(f"**현재 상태: {vkospi_state}**")
        
    except Exception as e:
        st.metric(label="🐯 한국 V-KOSPI", value="불러오기 실패")

    with st.expander("📌 V-KOSPI 해석 가이드"):
        st.markdown("""
        * **15 미만 (극도의 탐욕 & 매도)** : 폭풍 전야. 기습 조정에 대비해 신규 매수 자제
        * **15 ~ 20 (안정 & 매도)** : 이상적인 강세장. 추세를 타며 기존 수익 극대화
        * **20 ~ 30 (경계 & 중립)** : 악재로 인한 변동성 확대. 리스크 관리 및 줍줍 후보 탐색
        * **30 ~ 40 (극도의 공포 & 매수)** : 시스템 위기감에 따른 투매 발생. 바닥 분할 매수 시작
        * **40 이상 (역사적 패닉 & 매수)** : 금융위기, 팬데믹급 패닉. 일생일대의 바닥 매수 찬스
        """)

st.divider()

# ==========================================
# [하단] 거시경제 (Macro) 핵심 지표
# ==========================================
st.header("🌍 거시경제 (Macro) 핵심 지표")
col4, col5 = st.columns(2)

# 4. 달러/원 환율
with col4:
    try:
        usd_krw = yf.Ticker("KRW=X")
        ex_hist = usd_krw.history(period="5d")['Close']
        ex_price = float(ex_hist.iloc[-1])
        ex_prev = float(ex_hist.iloc[-2])
        ex_diff = ex_price - ex_prev
        ex_pct = (ex_diff / ex_prev) * 100
        
        sign = "+" if ex_diff > 0 else ""
        st.metric(label="💵 달러/원 환율 (USD/KRW)", value=f"{ex_price:,.2f} 원", delta=f"{sign}{ex_diff:,.2f} 원 ({sign}{ex_pct:.2f}%)")
    except Exception as e:
        st.metric(label="💵 달러/원 환율", value="불러오기 실패")
        
    with st.expander("📌 환율(USD/KRW) 해석 가이드"):
        st.markdown("""
        * **환율 급등 (원화 약세)** : 외국인 자금 국장 이탈 우려 / 미국 주식 보유자 환차익 발생
        * **환율 급락 (원화 강세)** : 외국인 자금 국장 유입 기대 / 미국 주식 보유자 환차손 주의
        """)

# 5. 미국 10년물 국채 금리
with col5:
    try:
        tnx = yf.Ticker("^TNX")
        tnx_hist = tnx.history(period="5d")['Close']
        tnx_price = float(tnx_hist.iloc[-1])
        tnx_prev = float(tnx_hist.iloc[-2])
        tnx_diff = tnx_price - tnx_prev
        tnx_pct = (tnx_diff / tnx_prev) * 100
        
        sign = "+" if tnx_diff > 0 else ""
        st.metric(label="🏛️ 미국 10년물 국채 금리", value=f"{tnx_price:.3f} %", delta=f"{sign}{tnx_diff:.3f} %p ({sign}{tnx_pct:.2f}%)")
    except Exception as e:
        st.metric(label="🏛️ 미국 10년물 국채 금리", value="불러오기 실패")
        
    with st.expander("📌 10년물 국채 금리 해석 가이드"):
        st.markdown("""
        * **금리 급등 (발작)** : 주식 시장(특히 나스닥 성장주)의 목을 조르는 강력한 악재
        * **금리 안정/하락** : 주식 시장의 호재. 기업 이자 부담 감소 및 위험 자산 선호도 증가
        """)

# ==========================================
# [하단 2] 원자재 & 대체 자산 (인플레이션 및 유동성)
# ==========================================
st.header("🛢️ 원자재 & 대체 자산 (인플레이션 및 유동성)")
col6, col7, col8 = st.columns(3)

# 6. WTI 국제 유가
with col6:
    try:
        wti = yf.Ticker("CL=F")
        wti_hist = wti.history(period="5d")['Close']
        wti_price = float(wti_hist.iloc[-1])
        wti_prev = float(wti_hist.iloc[-2])
        wti_diff = wti_price - wti_prev
        wti_pct = (wti_diff / wti_prev) * 100
        
        sign = "+" if wti_diff > 0 else ""
        st.metric(label="🛢️ WTI 국제 유가", value=f"$ {wti_price:.2f}", delta=f"{sign}{wti_diff:.2f} ({sign}{wti_pct:.2f}%)")
    except Exception as e:
        st.metric(label="🛢️ WTI 국제 유가", value="불러오기 실패")
        
    with st.expander("📌 WTI 유가 해석 가이드"):
        st.markdown("""
        * **유가 급등 (80불 이상)** : 인플레이션 재발 우려. 금리 인하 지연 가능성 증가 (기술주 악재)
        * **유가 하락/안정 (70불 내외)** : 물가 안정 기대감. 증시 상승의 훌륭한 땔감 (호재)
        """)

# 7. 국제 금 (Gold)
with col7:
    try:
        gold = yf.Ticker("GC=F")
        gold_hist = gold.history(period="5d")['Close']
        gold_price = float(gold_hist.iloc[-1])
        gold_prev = float(gold_hist.iloc[-2])
        gold_diff = gold_price - gold_prev
        gold_pct = (gold_diff / gold_prev) * 100
        
        sign = "+" if gold_diff > 0 else ""
        st.metric(label="🥇 국제 금값 (Gold)", value=f"$ {gold_price:,.1f}", delta=f"{sign}{gold_diff:,.1f} ({sign}{gold_pct:.2f}%)")
    except Exception as e:
        st.metric(label="🥇 국제 금값", value="불러오기 실패")
        
    with st.expander("📌 금값 해석 가이드"):
        st.markdown("""
        * **주식 폭락 + 금값 폭등** : 진짜 시스템 위기나 전쟁 발발 (안전 자산 쏠림)
        * **주식 폭락 + 금값 폭락** : 시장의 단순 유동성 경색 (현금 확보 러시)
        * **주식 강세 + 금값 강세** : 화폐 가치 하락(인플레이션)을 방어하려는 움직임
        """)

# 8. 비트코인 (Bitcoin)
with col8:
    try:
        btc = yf.Ticker("BTC-USD")
        btc_hist = btc.history(period="5d")['Close']
        btc_price = float(btc_hist.iloc[-1])
        btc_prev = float(btc_hist.iloc[-2])
        btc_diff = btc_price - btc_prev
        btc_pct = (btc_diff / btc_prev) * 100
        
        sign = "+" if btc_diff > 0 else ""
        st.metric(label="🪙 비트코인 (BTC)", value=f"$ {btc_price:,.0f}", delta=f"{sign}{btc_diff:,.0f} ({sign}{btc_pct:.2f}%)")
    except Exception as e:
        st.metric(label="🪙 비트코인", value="불러오기 실패")
        
    with st.expander("📌 비트코인 해석 가이드"):
        st.markdown("""
        * **시장 선행성** : 가장 공격적인 위험 자산. 증시(특히 나스닥) 방향의 선행 지표 역할
        * **비트코인 급락** : 시장 전반의 위험 선호 심리가 빠르게 식고 있다는 경고등
        """)
        
st.divider()
st.caption("※ 새로고침(F5)을 누르면 실시간 데이터로 업데이트됩니다.")

st.markdown("<br>", unsafe_allow_html=True) 

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

with col_btn2:
    st.link_button("🏠 앤트리치 블로그로 돌아가기 (오늘의 시장 분석 & 종목 보기) 👉", 
                   "https://blog.naver.com/antrich10", 
                   use_container_width=True)
