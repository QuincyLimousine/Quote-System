import streamlit as st
import pandas as pd
from dateutil import parser
from datetime import date

# 1. 網頁基本設定
st.set_page_config(page_title="Quincy Limo Prices", layout="centered")

# --- 【GitHub Logo 設定】 ---
logo_url = "https://raw.githubusercontent.com/QuincyLimousine/Quincy-Limousine-Prices/main/quincyLimo_Q.png"

st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
        <img src="{logo_url}" style="height: 40px;">
        <h1 style="margin: 0; font-size: 2rem;">Quincy Limousine 報價系統</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# 2. 資料來源
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
    # --- 1. 預約時間與日期 ---
    st.subheader("1. 使用時間與日期")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        selected_date = st.date_input("使用日期 (Date):", value=date.today(), min_value=date.today())
    with col_t2:
        pickup_input = st.text_input("使用時間 (Pick-up Time):", placeholder="例如: 22:30")
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
    st.subheader("2. 接送詳情")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        transfer_types = ["請選擇"] + sorted(df['Transfer Type'].dropna().unique().tolist())
        selected_type = st.selectbox("接送類型 (Transfer Type):", transfer_types)
        regions = ["請選擇"] + sorted(df['Region'].dropna().unique().tolist())
        selected_region = st.selectbox("地區 (Region):", regions)
    with col_s2:
        models = ["請選擇"] + sorted(df['Model'].dropna().unique().tolist())
        selected_model = st.selectbox("車型 (Model):", models)
        if selected_region != "請選擇":
            districts = ["請選擇"] + sorted(df[df['Region'] == selected_region]['District'].dropna().unique().tolist())
            selected_district = st.selectbox("區域 (District):", districts)
        else:
            selected_district = st.selectbox("區域 (District):", ["請先選擇地區"])

    st.divider()

    # --- 第三步：附加選項 ---
    st.subheader("3. 附加選項")
    col_opt1, col_opt2 = st.columns(2)
    
    with col_opt1:
        # 兒童安全座椅選項
        seat_count = st.number_input("兒童安全座椅 ($120/張):", min_value=0, max_value=4, value=0)
        seat_fee = seat_count * 120

    meet_greet_fee = 0
    with col_opt2:
        # 僅在 Airport Transfer(Arrival) 時顯示
        if selected_type == "Airport Transfer(Arrival)":
            # 將字樣放在勾選項上方
            st.markdown("Meet And Greet Services ($80)", unsafe_allow_html=True)
            is_meet_greet = st.checkbox("Pickup Point: Arrival Hall A")
            if is_meet_greet:
                meet_greet_fee = 80
        else:
            st.write("") # 保持列對齊

    st.divider()

    # --- 最終報價顯示 ---
required_fields = [selected_type, selected_model, selected_region, selected_district]

if "請選擇" not in required_fields and "請先選擇地區" not in required_fields:
    final_result = df[
        (df['Transfer Type'] == selected_type) & 
        (df['Model'] == selected_model) & 
        (df['Region'] == selected_region) & 
        (df['District'] == selected_district)
    ]

    if not final_result.empty:
        base_price_raw = final_result.iloc[0]['Result']
        try:
            base_price = int(''.join(filter(str.isdigit, str(base_price_raw))))
        except:
            base_price = 0
        
        total_price = base_price + seat_fee + night_fee + meet_greet_fee
        
        # --- 判斷行程顯示文字 ---
        if selected_type == "Airport Transfer(Arrival)":
            route_display = f"HKIA → {selected_district}"
        elif selected_type == "Airport Transfer(Departure)":
            route_display = f"{selected_district} → HKIA"
        else:
            # 處理 Point to Point 或其他類型的顯示
            route_display = f"{selected_type} ({selected_region}-{selected_district})"
        
        st.subheader("📍 預約彙總與報價")
        summary_data = {
            "項目 (Item)": ["日期", "時間", "行程", "安全座椅", "接機服務", "基本車資", "總費用"],
            "內容 (Details)": [
                selected_date.strftime("%Y-%m-%d"),
                pickup_input if pickup_input else "未輸入",
                route_display, # 使用上面定義的判斷變數
                f"{seat_count} 張",
                "Meet & Greet ($80)" if meet_greet_fee > 0 else "無",
                f"${base_price}",
                f"HKD ${total_price}"
            ]
        }
        
        st.table(pd.DataFrame(summary_data))
        st.metric(label="預計總費用 (Total Estimated Price)", value=f"HKD ${total_price}")
        
        if night_fee > 0:
            st.warning("🌙 已計入夜間服務費 $100 (22:00-07:00)")
    else:
        st.warning("查無此組合價格。")
else:
        st.info("💡 請依序完成所有選單以獲取報價。")
