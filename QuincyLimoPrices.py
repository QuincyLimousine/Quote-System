import streamlit as st
import pandas as pd

# 1. 設定網頁標題
st.set_page_config(page_title="車輛資訊篩選器")
st.title("🚗 車輛型號與地區篩選系統")

# 2. 讀取資料庫 (這裡放入你的 Google Sheet CSV 連結)
# 格式範例: https://docs.google.com/spreadsheets/d/ID/export?format=csv
sheet_url = "你的_GOOGLE_SHEET_CSV_連結"

@st.cache_data
def load_data():
    return pd.read_csv(sheet_url)

try:
    df = load_data()

    # 3. 建立側邊欄或上方的篩選器
    col1, col2 = st.columns(2)

    with col1:
        models = df['Model'].unique()
        selected_model = st.selectbox("請選擇車型：", models)

    with col2:
        # 根據選擇的車型，過濾可用的地區
        regions = df[df['Model'] == selected_model]['Region'].unique()
        selected_region = st.selectbox("請選擇地區：", regions)

    # 4. 顯示結果
    st.divider()
    result = df[(df['Model'] == selected_model) & (df['Region'] == selected_region)]

    if not result.empty:
        st.subheader("查詢結果：")
        # 顯示 Result 欄位的內容
        st.success(result.iloc[0]['Result'])
    else:
        st.info("目前尚無相關資料。")

except Exception as e:
    st.error("資料讀取失敗，請檢查連結設定。")