import streamlit as st
import pandas as pd

# 1. 網頁基本設定
st.set_page_config(page_title="Quincy Limo Prices", layout="centered")
st.title("🚗 Quincy Limo 價格查詢系統")

# 2. 你的 Google Sheets CSV 連結
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUroRgmX-R1wQx5ndR5B8plTm7uajQg4OdpdxV8UK21exlpKhmix-wjLKGgG2HrLqWLhHQpQn-Gmfv/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    # 嘗試讀取資料
    data = pd.read_csv(sheet_url)
    # 強制清理欄位名稱的空格
    data.columns = data.columns.str.strip()
    return data

# --- 執行邏輯 ---

try:
    # 呼叫函式並賦值給 df
    df = load_data()

    # 除錯資訊：顯示目前抓取到的標題
    # st.write("偵測到的欄位標題：", df.columns.tolist())

    # 3. 檢查關鍵欄位是否存在
    required_columns = ['Model', 'Region', 'Result']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"Excel 找不到以下欄位：{missing_columns}")
        st.write("請檢查 Excel 第一列是否精確包含：Model, Region, Result")
    else:
        # 4. 建立篩選器
        col1, col2 = st.columns(2)
        with col1:
            models = sorted(df['Model'].dropna().unique())
            selected_model = st.selectbox("請選擇車型：", models)
        with col2:
            regions = sorted(df[df['Model'] == selected_model]['Region'].dropna().unique())
            selected_region = st.selectbox("請選擇地區：", regions)

        st.divider()
        
        # 5. 顯示結果
        final_result = df[(df['Model'] == selected_model) & (df['Region'] == selected_region)]
        if not final_result.empty:
            st.success(f"**價格/資訊：** {final_result.iloc[0]['Result']}")
        else:
            st.warning("查無此組合資料。")

except Exception as e:
    st.error("系統無法連結到資料庫。")
    st.exception(e) # 這會顯示詳細的錯誤追蹤
