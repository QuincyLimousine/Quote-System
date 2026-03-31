import streamlit as st
import pandas as pd
from datetime import time

# 1. 網頁基本設定
st.set_page_config(page_title="Quincy Limo Prices", layout="centered")
st.title("🚗 Quincy Limo 預約與價格查詢")

# 2. 你的 Google Sheets CSV 連結
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUroRgmX-R1wQx5ndR5B8plTm7uajQg4OdpdxV8UK21exlpKhmix-wjLKGgG2HrLqWLhHQpQn-Gmfv/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    data = pd.read_csv(sheet_url)
    data.columns = data.columns.str.strip()
    return data

try:
    df = load_data()
    
    # --- 第一部分：基本篩選 (車型與地區) ---
    st.subheader("第一步：選擇路線與車型")
    col1, col2 = st.columns(2)
    
    with col1:
        models = sorted(df['Model'].dropna().unique())
        selected_model = st.selectbox("選擇車型 (Select Model):", models)

    with col2:
        available_regions = sorted(df[df['Model'] == selected_model]['Region'].dropna().unique())
        selected_region = st.selectbox("選擇地區 (Select Region):", available_regions)

    st.divider()

    # --- 第二部分：附加選項 (座椅與時間) ---
    st.subheader("第二步：附加選項與時間")
    col3, col4 = st.columns(2)

    with col3:
        # 1. 兒童安全座椅選單
        seat_count = st.number_input("兒童安全座椅數量 (Child Seats):", min_value=0, max_value=4, step=1, value=0)
        seat_total = seat_count * 120
        if seat_count > 0:
            st.caption(f"💡 安全座椅小計: {seat_total} 元")

    with col4:
        # 2. Pick-up time 選單
        pickup_time = st.time_input("預約上車時間 (Pick-up Time):", time(12, 0))

    st.divider()

    # --- 第三部分：結果顯示 ---
    final_result = df[(df['Model'] == selected_model) & (df['Region'] == selected_region)]

    if not final_result.empty:
        base_price = final_result.iloc[0]['Result']
        
        st.subheader("📍 預約摘要 (Summary):")
        
        # 建立一個簡單的表格顯示明細
        summary_data = {
            "項目 (Item)": ["車型與路線", "上車時間", "安全座椅數量", "額外費用 (Seats)"],
            "內容 (Details)": [f"{selected_model} - {selected_region}", pickup_time.strftime("%H:%M"), f"{seat_count} 張", f"{seat_total} 元"]
        }
        st.table(pd.DataFrame(summary_data))
        
        # 最終報價顯示
        st.success(f"**基本車資報價：** {base_price}")
        if seat_count > 0:
            st.info(f"請注意：最終費用將包含基本車資及安全座椅費用 ({seat_total} 元)。")
    else:
        st.warning("查無此組合資料。")

except Exception as e:
    st.error("系統無法連結到資料庫。")
    st.exception(e)
