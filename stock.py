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

# --- 세션 상태 초기화 ---
def initialize_game():
    if 'initialized' not in st.session_state:
        st.session_state.cash = 100_000
        st.session_state.portfolio = {company: 0 for company in COMPANIES}
        
        # 초기 주가 설정
        prices = {}
        for company in COMPANIES:
            prices[company] = random.randint(1000, 50000)
        st.session_state.stock_prices = prices
        st.session_state.previous_prices = prices.copy()

        st.session_state.log = ["게임이 시작되었습니다."]
        st.session_state.asset_history = [100_000]
        st.session_state.initialized = True

# --- 주가 업데이트 함수 ---
def update_prices():
    st.session_state.previous_prices = st.session_state.stock_prices.copy()
    new_prices = {}
    for company, price in st.session_state.stock_prices.items():
        # 변동폭을 현재 가격에 비례하여 설정 (가격이 높을수록 변동폭도 커짐)
        max_change = int(price * 0.1) # 최대 10% 변동
        change = random.randint(-max_change, max_change)
        new_price = price + change
        # 가격이 최소/최대 범위를 벗어나지 않도록 조정
        new_price = max(MIN_PRICE, min(MAX_PRICE, new_price))
        new_prices[company] = new_price
    st.session_state.stock_prices = new_prices

# 게임 초기화 함수 호출
initialize_game()
update_prices()

# --- UI 구성 ---
st.title("📈 실시간 주식 거래 게임")
st.markdown("---")

# --- 자산 현황판 ---
portfolio_value = sum(
    st.session_state.portfolio[c] * st.session_state.stock_prices[c] for c in COMPANIES
)
total_assets = st.session_state.cash + portfolio_value
st.session_state.asset_history.append(total_assets)

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
    st.subheader("주식 시장 (5초마다 업데이트)")
    for company in COMPANIES:
        price = st.session_state.stock_prices[company]
        prev_price = st.session_state.previous_prices[company]
        
        price_change = price - prev_price
        price_delta = f"{price_change:+,d} 원" if price_change != 0 else ""

        c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
        c1.markdown(f"**{company}**")
        c2.metric("현재가", f"{price:,d} 원", delta=price_delta)

        with c3.form(key=f"form_{company}"):
            quantity = st.number_input("수량", min_value=1, step=1, key=f"q_{company}")
            buy_button = st.form_submit_button("매수")
            sell_button = st.form_submit_button("매도")

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
                "회사명": company,
                "보유 수량": shares,
                "현재가": f"{current_price:,.0f}",
                "평가액": f"{value:,.0f}"
            })

    if not portfolio_data:
        st.info("보유한 주식이 없습니다.")
    else:
        st.dataframe(pd.DataFrame(portfolio_data).set_index("회사명"), use_container_width=True)
    
    st.subheader("거래 기록")
    st.text_area("log", value="\n".join(st.session_state.log), height=200, disabled=True)


# --- 5초마다 자동 새로고침 ---
st.html("<meta http-equiv='refresh' content='5'>")
