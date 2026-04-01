import streamlit as st
import pandas as pd
from dateutil import parser
from datetime import date

# 1. 網頁基本設定
st.set_page_config(page_title="Quincy Limo Prices", layout="centered")
st.title("🚗 Quincy Limo 預約報價系統")

# 2. 資料來源 (Google Sheets CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUroRgmX-R1wQx5ndR5B8plTm7uajQg4OdpdxV8UK21exlpKhmix-wjLKGgG2HrLqWLhHQpQn-Gmfv/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(sheet_url)
        data.columns = data.columns.str.strip()
        return data
    except:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("無法載入資料庫，請檢查 Google Sheet 設定。")
else:
    # --- 第一步：預約時間與日期 ---
    st.subheader("📅 第一步：預約時間與日期")
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        # 日曆表輸入日期
        selected_date = st.date_input("預約上車日期 (Date):", date.today())
    
    with col_t2:
        # 手動輸入時間
        pickup_input = st.text_input("預約上車時間 (Pick-up Time):", placeholder="例如: 22:30")
        
        # 夜間收費判斷
        night_fee = 0
        if pickup_input:
            try:
                parsed_time = parser.parse(pickup_input).time()
                if parsed_time >= pd.to_datetime("22:00").time() or parsed_time <= pd.to_datetime("07:00").time():
                    night_fee = 100
            except:
                st.caption("⚠️ 格式參考: 22:30 或 10:30 PM")

    st.divider()

    # --- 第二步：接送詳情 ---
    st.subheader("🚘 第二步：接送詳情")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        transfer_types = ["請選擇"] + sorted(df['Transfer Type'].dropna().unique().tolist())
        selected_type = st.selectbox("接送類型 (Transfer Type):", transfer_types)
        
        regions = ["請選擇"] + sorted(df['Region'].dropna().unique().tolist())
        selected_region = st.selectbox("地區 (Region):", regions)

    with col_s2:
        models = ["請選擇"] + sorted(df['Model'].dropna().unique().tolist())
        selected_model = st.selectbox("車型 (Model):", models)

        # 連動選單：根據 Region 顯示 District
        if selected_region != "請選擇":
            filtered_districts = df[df['Region'] == selected_region]['District'].dropna().unique().tolist()
            districts = ["請選擇"] + sorted(filtered_districts)
        else:
            districts = ["請先選擇地區"]
        
        selected_district = st.selectbox("區域 (District):", districts)

    st.divider()

    # --- 第三步：附加選項 ---
    st.subheader("👶 第三步：附加選項")
    seat_count = st.number_input("兒童安全座椅 ($120/張):", min_value=0, max_value=4, value=0)
    seat_fee = seat_count * 120

    st.divider()

    # --- 最終結果計算 ---
    required_fields = [selected_type, selected_model, selected_region, selected_district]
    
    if "請選擇" not in required_fields and "請先選擇地區" not in required_fields:
        
        final_result = df[
            (df['Transfer Type'] == selected_type) & 
            (df['Model'] == selected_model) & 
            (df['Region'] == selected_region) & 
            (df['District'] == selected_district)
        ]

        if not final_result.empty:
            # 提取基本價格
            base_price_raw = final_result.iloc[0]['Result']
            try:
                base_price = int(''.join(filter(str.isdigit, str(base_price_raw))))
            except:
                base_price = 0
            
            total_price = base_price + seat_fee + night_fee
            
            # 顯示摘要表格
            st.subheader("📍 預約彙總與報價")
            
            summary_df = pd.DataFrame({
                "項目 (Item)": ["預約日期", "上車時間", "行程內容", "安全座椅", "基本車資", "附加費用 (夜間/座椅)"],
                "內容 (Details)": [
                    selected_date.strftime("%Y-%m-%d"),
                    pickup_input if pickup_input else "未輸入",
                    f"{selected_type} ({selected_region} - {selected_district})",
                    f"{seat_count} 張",
                    f"${base_price}",
                    f"${seat_fee + night_fee}"
                ]
            })
            st.table(summary_df)
            
            # 總金額
            st.metric(label="預計總費用 (Total Estimated Price)", value=f"HKD ${total_price}")
            
            if night_fee > 0:
                st.warning("🌙 已包含夜間服務費 $100 (22:00-07:00)")
        else:
            st.warning("查無此組合價格，請重新核對選擇。")
    else:
        st.info("💡 請完成以上步驟以顯示完整報價明細。")
