import streamlit as st
import pandas as pd
from dateutil import parser
from datetime import date, datetime

# --- 1. 初始化與變數設定 ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'CH'
if 'step' not in st.session_state:
    st.session_state.step = 1

persistent_vars = ['u_name_val', 'u_phone_full', 'u_phone_raw_val', 'u_email_val', 
                   'p_time_val', 's_type_val', 's_model_val', 's_region_val', 
                   's_district_val', 'seat_count_val', 'mg_selected_val', 's_date_val']
for var in persistent_vars:
    if var not in st.session_state:
        st.session_state[var] = "" if "val" in var else False

def toggle_language():
    st.session_state.lang = 'EN' if st.session_state.lang == 'CH' else 'CH'

# --- 2. 翻譯字典 (微調項目清單以支援動態顯示) ---
texts = {
    'CH': {
        'title': 'Quincy Limousine 報價系統',
        'step1': '步驟 1: 客戶聯絡資料',
        'step2': '步驟 2: 行程詳情與選項',
        'step3': '步驟 3: 最終預約報價',
        'next': '下一步',
        'prev': '返回上一步',
        'fill_all': '⚠️ 請填寫所有必填項以繼續。',
        'name_label': '姓名 (Full Name):',
        'phone_label': '電話號碼 (Phone Number):',
        'email_label': 'Gmail 地址:',
        'email_error': '⚠️ 請輸入有效的電地址 (需包含 @gmail.com)',
        'date_label': '使用日期:',
        'time_label': '使用時間:',
        'time_placeholder': '例如: 22:30',
        'night_warning': '🌙 已計入夜間服務費 $100 (22:00-07:00)',
        'type_label': '接送類型:',
        'region_label': '地區:',
        'model_label': '車型:',
        'district_label': '區域:',
        'select_op': '請選擇',
        'select_reg_first': '請先選擇地區',
        'seat_label': '兒童安全座椅 ($120/張):',
        'mg_label': '機場接機服務 ($80)',
        'mg_pickup': '需要接機服務 (接機大堂 A)',
        'summary_title': '📍 預約彙總與報價',
        'item': '項目',
        'details': '內容',
        'total_metric': '預計總費用',
        'no_price': '查無此組合價格，請聯繫客服。',
        'seat_unit': '張',
        'map_labels': {
            "Name": "客戶姓名", "Phone": "聯絡電話", "Gmail": "Gmail", 
            "Date": "日期", "Time": "時間", "Route": "行程路徑", 
            "Seat": "安全座椅", "MG": "接機服務", "Base": "基本車資", "Total": "總費用"
        }
    },
    'EN': {
        'title': 'Quincy Limousine Quote System',
        'step1': 'Step 1: Contact Information',
        'step2': 'Step 2: Journey & Options',
        'step3': 'Step 3: Final Quote',
        'next': 'Next',
        'prev': 'Back',
        'fill_all': '⚠️ Please fill in all required fields.',
        'name_label': 'Full Name:',
        'phone_label': 'Phone Number:',
        'email_label': 'Gmail Address:',
        'email_error': '⚠️ Invalid Gmail (must contain @gmail.com)',
        'date_label': 'Date:',
        'time_label': 'Pick-up Time:',
        'time_placeholder': 'e.g. 22:30',
        'night_warning': '🌙 Night surcharge $100 included',
        'type_label': 'Transfer Type:',
        'region_label': 'Region:',
        'model_label': 'Vehicle Type:',
        'district_label': 'District:',
        'select_op': 'Please Select',
        'select_reg_first': 'Select region first',
        'seat_label': 'Baby Car Seat ($120/each):',
        'mg_label': 'Meet & Greet Service ($80)',
        'mg_pickup': 'Meet & Greet (Arrival Hall A)',
        'summary_title': '📍 Summary & Quote',
        'item': 'Item',
        'details': 'Details',
        'total_metric': 'Total Estimated Price',
        'no_price': 'Price not found for this combination.',
        'seat_unit': 'Seat(s)',
        'map_labels': {
            "Name": "Name", "Phone": "Phone", "Gmail": "Gmail", 
            "Date": "Date", "Time": "Time", "Route": "Route", 
            "Seat": "Child Seat", "MG": "Meet & Greet", "Base": "Base Fare", "Total": "Total"
        }
    }
}

L = texts[st.session_state.lang]

# --- 3. 網頁設定 ---
st.set_page_config(page_title="Quincy Limo Prices", layout="centered")

col_title, col_lang = st.columns([0.8, 0.2])
with col_title:
    logo_url = "https://raw.githubusercontent.com/QuincyLimousine/Quincy-Limousine-Prices/main/quincyLimo_Q.png"
    st.markdown(f'<div style="display: flex; align-items: center; gap: 15px;"><img src="{logo_url}" style="height: 40px;"><h1 style="margin: 0; font-size: 1.8rem;">{L["title"]}</h1></div>', unsafe_allow_html=True)
with col_lang:
    st.button("🌐 EN/中文", on_click=toggle_language)

st.progress(st.session_state.step / 3)

# --- 4. 資料載入 ---
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUroRgmX-R1wQx5ndR5B8plTm7uajQg4OdpdxV8UK21exlpKhmix-wjLKGgG2HrLqWLhHQpQn-Gmfv/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(sheet_url)
        data.columns = data.columns.str.strip()
        return data
    except: return pd.DataFrame()

df = load_data()

# --- 5. 分步流程 ---

# 步驟 1: 聯絡資料
if st.session_state.step == 1:
    st.subheader(L['step1'])
    st.text_input(L['name_label'], key='u_name', value=st.session_state.u_name_val)
    
    raw_codes = [("Hong Kong +852", "+852"), ("China +86", "+86"), ("Macau +853", "+853"), ("Taiwan +886", "+886")]
    country_codes = sorted(raw_codes, key=lambda x: x[0][3:])
    
    col_c, col_p = st.columns([0.45, 0.55])
    with col_c:
        hk_idx = next((i for i, c in enumerate(country_codes) if "+852" in c[1]), 0)
        st.selectbox("Code", options=[c[0] for c in country_codes], index=hk_idx, key='sel_code_disp')
    with col_p:
        st.text_input(L['phone_label'], key='u_phone_raw', value=st.session_state.u_phone_raw_val)
    
    st.text_input(L['email_label'], key='u_email', value=st.session_state.u_email_val)
    
    if st.button(L['next']):
        name = st.session_state.u_name.strip()
        phone = st.session_state.u_phone_raw.strip()
        email = st.session_state.u_email.strip()
        sel_code = next(c[1] for c in country_codes if c[0] == st.session_state.sel_code_disp)
        
        if name and phone and "@gmail.com" in email.lower():
            st.session_state.u_name_val = name
            st.session_state.u_phone_raw_val = phone
            st.session_state.u_phone_full = f"{sel_code} {phone}"
            st.session_state.u_email_val = email
            st.session_state.step = 2
            st.rerun()
        else:
            st.warning(L['fill_all'])

# 步驟 2: 行程詳情
elif st.session_state.step == 2:
    st.subheader(L['step2'])
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.date_input(L['date_label'], key='s_date_widget', min_value=date.today())
    with col_t2:
        st.text_input(L['time_label'], key='p_time', value=st.session_state.p_time_val)
    
    st.divider()
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        t_types = [L['select_op']] + sorted(df['Transfer Type'].dropna().unique().tolist())
        st.selectbox(L['type_label'], t_types, key='s_type')
        regs = [L['select_op']] + sorted(df['Region'].dropna().unique().tolist())
        st.selectbox(L['region_label'], regs, key='s_region')
        
    with col_s2:
        mods = [L['select_op']] + sorted(df['Model'].dropna().unique().tolist())
        st.selectbox(L['model_label'], mods, key='s_model')
        
        if st.session_state.s_region != L['select_op']:
            dists = [L['select_op']] + sorted(df[df['Region'] == st.session_state.s_region]['District'].dropna().unique().tolist())
            st.selectbox(L['district_label'], dists, key='s_district')
        else:
            st.selectbox(L['district_label'], [L['select_reg_first']], disabled=True, key='s_district_tmp')

    st.divider()

    col_o1, col_o2 = st.columns(2)
    with col_o1:
        st.number_input(L['seat_label'], min_value=0, max_value=4, key='seat_count')
    with col_o2:
        # 修改點 1: 僅在選擇了 Airport Transfer(Arrival) 時顯示接機服務選項
        if "Arrival" in st.session_state.s_type:
            st.markdown("<br>", unsafe_allow_html=True)
            st.checkbox(L['mg_pickup'], key='mg_selected', value=st.session_state.mg_selected_val)
        else:
            # 如果不是接機，確保後台變數為 False
            st.session_state.mg_selected_val = False

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button(L['prev']): st.session_state.step = 1; st.rerun()
    with col_nav2:
        if st.button(L['next']):
            time_val = st.session_state.p_time.strip()
            if time_val and st.session_state.s_type != L['select_op'] and st.session_state.s_region != L['select_op']:
                st.session_state.p_time_val = time_val
                st.session_state.s_type_val = st.session_state.s_type
                st.session_state.s_model_val = st.session_state.s_model
                st.session_state.s_region_val = st.session_state.s_region
                st.session_state.s_district_val = st.session_state.get('s_district', '')
                st.session_state.seat_count_val = st.session_state.seat_count
                # 如果畫面上沒有 mg_selected (非接機行程)，預設為 False
                st.session_state.mg_selected_val = st.session_state.get('mg_selected', False)
                st.session_state.s_date_val = st.session_state.s_date_widget
                st.session_state.step = 3
                st.rerun()
            else:
                st.warning(L['fill_all'])

# 步驟 3: 報價彙總
elif st.session_state.step == 3:
    st.subheader(L['step3']) 
    
    res = df[(df['Transfer Type'] == st.session_state.s_type_val) & 
             (df['Model'] == st.session_state.s_model_val) & 
             (df['Region'] == st.session_state.s_region_val) & 
             (df['District'] == st.session_state.s_district_val)]

    if not res.empty:
        base_raw = res.iloc[0]['Result']
        try:
            base_price = int(''.join(filter(str.isdigit, str(base_raw))))
        except: base_price = 0
            
        try:
            parsed_time = parser.parse(st.session_state.p_time_val).time()
            night_fee = 100 if (parsed_time >= pd.to_datetime("22:00").time() or 
                                parsed_time <= pd.to_datetime("07:00").time()) else 0
        except: night_fee = 0 
            
        mg_fee = 80 if st.session_state.mg_selected_val else 0
        seat_fee = st.session_state.seat_count_val * 120
        total_price = base_price + night_fee + mg_fee + seat_fee
        
        s_type = st.session_state.s_type_val
        s_district = st.session_state.s_district_val
        route = f"HKIA → {s_district}" if "Arrival" in s_type else (f"{s_district} → HKIA" if "Departure" in s_type else f"{s_type} ({s_district})")
        
        # 修改點 2: 動態建構表格內容
        m = L['map_labels']
        items = [
            (m["Name"], st.session_state.u_name_val),
            (m["Phone"], st.session_state.u_phone_full),
            (m["Gmail"], st.session_state.u_email_val),
            (m["Date"], st.session_state.s_date_val.strftime("%Y-%m-%d")),
            (m["Time"], st.session_state.p_time_val),
            (m["Route"], route)
        ]
        
        # 如果有安全座椅才顯示
        if st.session_state.seat_count_val > 0:
            items.append((m["Seat"], f"{st.session_state.seat_count_val} {L['seat_unit']}"))
            
        # 僅當「使用者勾選了接機服務」才顯示在彙總中
        if st.session_state.mg_selected_val:
            items.append((m["MG"], f"${mg_fee}"))
            
        items.extend([
            (m["Base"], f"${base_price}"),
            (m["Total"], f"HKD ${total_price}")
        ])
        
        summary_df = pd.DataFrame(items, columns=[L['item'], L['details']])
        st.table(summary_df)
        st.metric(label=L['total_metric'], value=f"HKD ${total_price}")
        
        if night_fee > 0:
            st.warning(L['night_warning'])
            
    else: 
        st.error(L['no_price'])
    
    if st.button(L['prev']): 
        st.session_state.step = 2
        st.rerun()
