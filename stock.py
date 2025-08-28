import streamlit as st
import random
import time
import pandas as pd

# --- 페이지 설정 ---
st.set_page_config(
    page_title="실시간 주식 거래 게임",
    page_icon="📈",
    layout="wide"
)

# --- 초기 설정 ---
COMPANIES = [
    "Gemini AI", "스트림릿 솔루션", "데이터 월드", "파이썬 파워",
    "알고리즘 랩스", "클라우드 나인", "AI 비전", "코드 마스터",
    "퀀텀 리프", "빅데이터 Inc."
]
MIN_PRICE = 100
MAX_PRICE = 1_000_000
HISTORY_LIMIT = 100 # 그래프에 표시할 데이터 최대 개수

# --- 게임 상태 관리 함수 ---

def initialize_game():
    """게임 최초 실행 시 모든 상태를 초기화하는 함수"""
    st.session_state.cash = 100_000
    st.session_state.portfolio = {company: 0 for company in COMPANIES}
    
    prices = {}
    price_history = {}
    for company in COMPANIES:
        initial_price = random.randint(1000, 50000)
        prices[company] = initial_price
        price_history[company] = [initial_price]
    
    st.session_state.stock_prices = prices
    st.session_state.previous_prices = prices.copy()
    st.session_state.stock_price_history = price_history

    st.session_state.log = ["게임이 시작되었습니다."]
    st.session_state.asset_history = [100_000]
    st.session_state.initialized = True # 초기화 완료 플래그

def update_prices():
    """두 번째 실행부터 주가를 업데이트하는 함수"""
    st.session_state.previous_prices = st.session_state.stock_prices.copy()
    new_prices = {}
    for company, price in st.session_state.stock_prices.items():
        max_change = int(price * 0.1)
        change = random.randint(-max_change, max_change) if max_change > 0 else 0
        new_price = price + change
        new_price = max(MIN_PRICE, min(MAX_PRICE, new_price))
        new_prices[company] = new_price
        
        history = st.session_state.stock_price_history[company]
        history.append(new_price)
        st.session_state.stock_price_history[company] = history[-HISTORY_LIMIT:]

    st.session_state.stock_prices = new_prices

# --- 스크립트 실행 로직 ---
# 이 부분이 핵심적인 수정사항입니다.
if 'initialized' not in st.session_state:
    initialize_game()
else:
    update_prices()

# --- UI 구성 ---
st.title("📈 실시간 주식 거래 게임")
st.markdown("---")

# --- 자산 현황판 ---
portfolio_value = sum(
    st.session_state.portfolio[c] * st.session_state.stock_prices[c] for c in COMPANIES
)
total_assets = st.session_state.cash + portfolio_value

# 자산 히스토리 업데이트 (최초 실행 시 중복 추가 방지)
if len(st.session_state.asset_history) == 0 or st.session_state.asset_history[-1] != total_assets:
    st.session_state.asset_history.append(total_assets)
    st.session_state.asset_history = st.session_state.asset_history[-HISTORY_LIMIT:]

col1, col2, col3 = st.columns(3)
col1.metric("💰 현금", f"{st.session_state.cash:,.0f} 원")
col2.metric("📊 주식 평가액", f"{portfolio_value:,.0f} 원")
col3.metric("🏦 총 자산", f"{total_assets:,.0f} 원")

# --- 자산 변동 그래프 ---
st.subheader("총 자산 변동 그래프")
chart_data = pd.DataFrame(st.session_state.asset_history, columns=["총 자산"])
st.line_chart(chart_data)
st.markdown("---")

# --- 주식 시장 및 포트폴리오 ---
market_col, portfolio_col = st.columns([0.6, 0.4])

with market_col:
    st.subheader(f"주식 시장 (1.5초마다 업데이트)")
    for company in COMPANIES:
        with st.container(border=True):
            price = st.session_state.stock_prices[company]
            prev_price = st.session_state.previous_prices.get(company, price) # .get으로 안전하게 접근
            price_change = price - prev_price
            price_delta = f"{price_change:+,d} 원" if price_change != 0 else ""

            c1, c2 = st.columns([0.6, 0.4])
            with c1:
                st.markdown(f"**{company}**")
                st.metric("현재가", f"{price:,d} 원", delta=price_delta)
            with c2:
                st.line_chart(st.session_state.stock_price_history[company], height=100)

            with st.form(key=f"form_{company}"):
                quantity = st.number_input("수량", min_value=1, step=1, key=f"q_{company}")
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    buy_button = st.form_submit_button("매수", use_container_width=True)
                with f_col2:
                    sell_button = st.form_submit_button("매도", use_container_width=True)

                if buy_button:
                    cost = quantity * price
                    if st.session_state.cash >= cost:
                        st.session_state.cash -= cost
                        st.session_state.portfolio[company] += quantity
                        st.session_state.log.insert(0, f"[매수] {company} {quantity}주, {cost:,.0f}원")
                        st.rerun()
                    else:
                        st.error("현금이 부족합니다.")
                
                if sell_button:
                    if st.session_state.portfolio[company] >= quantity:
                        revenue = quantity * price
                        st.session_state.cash += revenue
                        st.session_state.portfolio[company] -= quantity
                        st.session_state.log.insert(0, f"[매도] {company} {quantity}주, {revenue:,.0f}원")
                        st.rerun()
                    else:
                        st.error("보유 주식이 부족합니다.")

with portfolio_col:
    st.subheader("내 주식 현황")
    portfolio_data = []
    for company, shares in st.session_state.portfolio.items():
        if shares > 0:
            current_price = st.session_state.stock_prices[company]
            value = shares * current_price
            portfolio_data.append({
                "회사명": company, "보유 수량": shares,
                "현재가": f"{current_price:,.0f}", "평가액": f"{value:,.0f}"
            })

    if not portfolio_data:
        st.info("보유한 주식이 없습니다.")
    else:
        st.dataframe(pd.DataFrame(portfolio_data).set_index("회사명"), use_container_width=True)
    
    st.subheader("거래 기록")
    st.text_area("log", value="\n".join(st.session_state.log), height=200, disabled=True)

# --- 1.5초마다 자동 새로고침 ---
st.html("<meta http-equiv='refresh' content='1.5'>")
