import streamlit as st
import pandas as pd

# 1. 網頁基本設定
st.set_page_config(page_title="車輛資訊查詢系統", layout="centered")
st.title("🚗 車輛型號與地區篩選器")

# 2. 你的 Google Sheets CSV 連結
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUroRgmX-R1wQx5ndR5B8plTm7uajQg4OdpdxV8UK21exlpKhmix-wjLKGgG2HrLqWLhHQpQn-Gmfv/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=600)  # 每 10 分鐘自動更新一次資料
def load_data():
    # 讀取資料並自動去除欄位名稱與內容的空格
    data = pd.read_csv(sheet_url)
    data.columns = data.columns.str.strip()
    return data

try:
    df = load_data()

    # 3. 建立篩選介面
    st.info("請從下方選單選擇條件以獲取答案：")
    
    col1, col2 = st.columns(2)

    with col1:
        # 取得所有不重複的車型
        models = sorted(df['Model'].dropna().unique())
        selected_model = st.selectbox("1. 選擇車型 (Model)", models)

    with col2:
        # 根據選擇的車型，過濾出該車型有的地區
        available_regions = sorted(df[df['Model'] == selected_model]['Region'].dropna().unique())
        selected_region = st.selectbox("2. 選擇地區 (Region)", available_regions)

    # 4. 顯示篩選結果
    st.divider()
    
    # 進行資料比對
    final_result = df[(df['Model'] == selected_model) & (df['Region'] == selected_region)]

    if not final_result.empty:
        st.subheader("📍 查詢結果：")
        # 顯示 Result 欄位的內容
        answer = final_result.iloc[0]['Result']
        st.success(f"**答案：** {answer}")
    else:
        st.warning("查無此組合的相關資料。")

except Exception as e:
    st.error("讀取雲端資料庫時發生錯誤。")
    st.write("錯誤訊息：", e)
    st.write("請確認您的 Google Sheet 第一列標題是否為：Model, Region, Result")
