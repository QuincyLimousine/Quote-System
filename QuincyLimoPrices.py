import streamlit as st
import pandas as pd
from dateutil import parser
from datetime import date

# 1. 初始化語言設定 (預設為中文)
if 'lang' not in st.session_state:
    st.session_state.lang = 'CH'

def toggle_language():
    st.session_state.lang = 'EN' if st.session_state.lang == 'CH' else 'CH'

# 2. 翻譯字典
texts = {
    'CH': {
        'title': 'Quincy Limousine 報價系統',
        'step1': '1. 使用時間與日期',
        'date_label': '使用日期:',
        'time_label': '使用時間:',
        'time_placeholder': '例如: 22:30',
        'night_warning': '🌙 已計入夜間服務費 $100 (22:00-07:00)',
        'step2': '2. 接送詳情',
        'type_label': '接送類型:',
        'region_label': '地區:',
        'model_label': '車型:',
        'district_label': '區域:',
        'select_op': '請選擇',
        'select_reg_first': '請先選擇地區',
        'step3': '3. 附加選項',
        'seat_label': '兒童安全座椅 ($120/張):',
        'mg_label': '機場接機服務 ($80)',
        'mg_pickup': '接機地點: 接機大堂 A',
        'summary_title': '📍 預約彙總與報價',
        'item': '項目',
        'details': '內容',
        'items_list': ["日期", "時間", "行程", "安全座椅", "接機服務", "基本車資", "總費用"],
        'total_metric': '預計總費用',
        'info_msg': '💡 請依序完成所有選單以獲取報價。',
        'no_price': '查無此組合價格。',
        'seat_unit': '張'
    },
    'EN': {
        'title': 'Quincy Limousine Quote System',
        'step1': '1. Time and Date',
        'date_label': 'Date:',
        'time_label': 'Pick-up Time:',
        'time_placeholder': 'e.g. 10:30 PM',
        'night_warning': '🌙 Night surcharge $100 included (22:00-07:00)',
        'step2': '2. Transfer Details',
        'type_label': 'Transfer Type:',
        'region_label': 'Region:',
        'model_label': 'Model:',
        'district_label': 'District:',
        'select_op': 'Please Select',
        'select_reg_first': 'Select region first',
        'step3': '3. Extra Options',
        'seat_label': 'Child Safety Seat ($120/each):',
        'mg_label': 'Meet & Greet Service ($80)',
        'mg_pickup': 'Pickup Point: Arrival Hall A',
        'summary_title': '📍 Summary & Quote',
        'item': 'Item',
        'details': 'Details',
        'items_list': ["Date", "Time", "Route", "Child Seat", "Meet & Greet", "Base Fare", "Total"],
        'total_metric': 'Total Estimated Price',
        'info_msg': '💡 Please complete all fields to get a quote.',
        'no_price': 'Price not found for this combination.',
        'seat_unit': 'Seat(s)'
    }
}

L = texts[st.session_state.lang]

# 3. 網頁基本設定
st.set_page_config(page_title="Quincy Limo Prices", layout="centered")

# 頂部：標題與語言切換按鈕並列
col_title, col_lang = st.columns([0.8, 0.2])
with col_title:
    logo_url = "https://raw.githubusercontent.com/QuincyLimousine/Quincy-Limousine-Prices/main/quincyLimo_Q.png"
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 15px;">
            <img src="{logo_url}" style="height: 40px;">
            <h1 style="margin: 0; font-size: 1.8rem;">{L['title']}</h1>
        </div>
        """, unsafe_allow_html=True
    )
with col_lang:
    st.button("🌐 EN/中文", on_click=toggle_language)

# 4. 資料載入
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
    st.error("Database error.")
else:
    # --- 1. 時間日期 ---
    st.subheader(L['step1'])
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        selected_date = st.date_input(L['date_label'], value=date.today(), min_value=date.today())
    with col_t2:
        pickup_input = st.text_input(L['time_label'], placeholder=L['time_placeholder'])
        night_fee = 0
        if pickup_input:
            try:
                parsed_time = parser.parse(pickup_input).time()
                if parsed_time >= pd.to_datetime("22:00").time() or parsed_time <= pd.to_datetime("07:00").time():
                    night_fee = 100
            except:
                st.caption("Format: 22:30 / 10:30 PM")

    st.divider()

    # --- 2. 接送詳情 ---
    st.subheader(L['step2'])
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        t_types = [L['select_op']] + sorted(df['Transfer Type'].dropna().unique().tolist())
        selected_type = st.selectbox(L['type_label'], t_types)
        
        mods = [L['select_op']] + sorted(df['Model'].dropna().unique().tolist())
        selected_model = st.selectbox(L['model_label'], mods)
        
    with col_s2:
        
        regs = [L['select_op']] + sorted(df['Region'].dropna().unique().tolist())
        selected_region = st.selectbox(L['region_label'], regs)
        
        if selected_region != L['select_op']:
            dists = [L['select_op']] + sorted(df[df['Region'] == selected_region]['District'].dropna().unique().tolist())
            selected_district = st.selectbox(L['district_label'], dists)
        else:
            selected_district = st.selectbox(L['district_label'], [L['select_reg_first']])

    # 車型圖片預覽
    model_images = {
        "Comfort 5-Seater": "https://raw.githubusercontent.com/QuincyLimousine/Quincy-Limousine-Prices/main/Vehicle%20Type/Compact%205-Seater.png",
        "Deluxe 5-Seater": "https://raw.githubusercontent.com/QuincyLimousine/Quincy-Limousine-Prices/main/Vehicle%20Type/Deluxe%205-Seater.png",
        "Deluxe 7-Seater": "https://raw.githubusercontent.com/QuincyLimousine/Quincy-Limousine-Prices/main/Vehicle%20Type/Deluxe%207-Seater.png",
        "Premium 7-Seater": "https://raw.githubusercontent.com/QuincyLimousine/Quincy-Limousine-Prices/main/Vehicle%20Type/Premium%207-Seater.png"
    }
    if selected_model in model_images:
        st.image(model_images[selected_model], use_container_width=True)

    st.divider()

    # --- 3. 附加選項 ---
    st.subheader(L['step3'])
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        seat_count = st.number_input(L['seat_label'], min_value=0, max_value=4, value=0)
        seat_fee = seat_count * 120

    meet_greet_fee = 0
    with col_opt2:
        if selected_type == "Airport Transfer(Arrival)":
            st.markdown(f"**{L['mg_label']}**")
            is_meet_greet = st.checkbox(L['mg_pickup'])
            if is_meet_greet:
                meet_greet_fee = 80
        else:
            st.write("")

    st.divider()

    # --- 報價計算 ---
    required = [selected_type, selected_model, selected_region, selected_district]
    if L['select_op'] not in required and L['select_reg_first'] not in required:
        res = df[(df['Transfer Type'] == selected_type) & (df['Model'] == selected_model) & 
                 (df['Region'] == selected_region) & (df['District'] == selected_district)]

        if not res.empty:
            base_raw = res.iloc[0]['Result']
            try:
                base_price = int(''.join(filter(str.isdigit, str(base_raw))))
            except:
                base_price = 0
            
            total_price = base_price + seat_fee + night_fee + meet_greet_fee
            
            # 行程描述邏輯
            if selected_type == "Airport Transfer(Arrival)":
                route = f"HKIA → {selected_district}"
            elif selected_type == "Airport Transfer(Departure)":
                route = f"{selected_district} → HKIA"
            else:
                route = f"{selected_type} ({selected_region}-{selected_district})"
            
            st.subheader(L['summary_title'])
            summary = {
                f"{L['item']}": L['items_list'],
                f"{L['details']}": [
                    selected_date.strftime("%Y-%m-%d"),
                    pickup_input if pickup_input else "---",
                    route,
                    f"{seat_count} {L['seat_unit']}",
                    "$80" if meet_greet_fee > 0 else "N/A",
                    f"${base_price}",
                    f"HKD ${total_price}"
                ]
            }
            st.table(pd.DataFrame(summary))
            st.metric(label=L['total_metric'], value=f"HKD ${total_price}")
            
            if night_fee > 0:
                st.warning(L['night_warning'])
        else:
            st.warning(L['no_price'])
    else:
        st.info(L['info_msg'])
