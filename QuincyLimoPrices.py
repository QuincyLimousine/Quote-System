import streamlit as st
import pandas as pd
from dateutil import parser
from datetime import date, datetime

# --- 1. 初始化語言與步驟設定 ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'CH'
if 'step' not in st.session_state:
    st.session_state.step = 1

def toggle_language():
    st.session_state.lang = 'EN' if st.session_state.lang == 'CH' else 'CH'

# --- 2. 翻譯字典 ---
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
        'items_list': ["客戶姓名", "聯絡電話", "Gmail", "日期", "時間", "行程", "安全座椅", "接機服務", "基本車資", "總費用"],
        'total_metric': '預計總費用',
        'no_price': '查無此組合價格，請聯繫客服。',
        'seat_unit': '張'
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
        'seat_label': 'Child Seat ($120/each):',
        'mg_label': 'Meet & Greet Service ($80)',
        'mg_pickup': 'Meet & Greet (Arrival Hall A)',
        'summary_title': '📍 Summary & Quote',
        'item': 'Item',
        'details': 'Details',
        'items_list': ["Name", "Phone", "Gmail", "Date", "Time", "Route", "Child Seat", "Meet & Greet", "Base Fare", "Total"],
        'total_metric': 'Total Estimated Price',
        'no_price': 'Price not found for this combination.',
        'seat_unit': 'Seat(s)'
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
    
    # 這裡移除 value=...，改用 key 綁定
    st.text_input(L['name_label'], key='u_name', placeholder="Chan Tai Man")
    
    raw_codes = [("🇭🇰 Hong Kong +852", "+852"), ("🇨🇳 China +86", "+86"), ("🇲🇴 Macau +853", "+853"), ("🇹🇼 Taiwan +886", "+886")]
    country_codes = sorted(raw_codes, key=lambda x: x[0][3:])
    
    col_c, col_p = st.columns([0.45, 0.55])
    with col_c:
        hk_idx = next((i for i, c in enumerate(country_codes) if "+852" in c[1]), 0)
        st.selectbox("Code", options=[c[0] for c in country_codes], index=hk_idx, key='sel_code_disp')
    with col_p:
        st.text_input(L['phone_label'], key='u_phone_raw', placeholder="9123 4567")
    
    st.text_input(L['email_label'], key='u_email', placeholder="example@gmail.com")
    
    # 點擊「下一步」按鈕
    if st.button(L['next']):
        # 直接從 session_state 讀取當前畫面上的值
        name = st.session_state.u_name.strip()
        phone_raw = st.session_state.u_phone_raw.strip()
        email = st.session_state.u_email.strip()
        
        # 獲取選中的區碼
        sel_code = next(c[1] for c in country_codes if c[0] == st.session_state.sel_code_disp)
        
        email_valid = "@gmail.com" in email.lower() if email else False

        if name and phone_raw and email_valid:
            st.session_state.u_phone_full = f"{sel_code} {phone_raw}"
            st.session_state.step = 2
            st.rerun()
        else:
            if email and not email_valid: 
                st.error(L['email_error'])
            else: 
                st.warning(L['fill_all'])

# 步驟 2: 行程詳情
elif st.session_state.step == 2:
    st.subheader(L['step2'])
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.date_input(L['date_label'], key='s_date', min_value=date.today())
    with col_t2:
        st.text_input(L['time_label'], key='p_time', placeholder=L['time_placeholder'])
    
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
        
        # 處理動態地區選單
        current_reg = st.session_state.s_region
        if current_reg != L['select_op']:
            dists = [L['select_op']] + sorted(df[df['Region'] == current_reg]['District'].dropna().unique().tolist())
            st.selectbox(L['district_label'], dists, key='s_district')
        else:
            st.selectbox(L['district_label'], [L['select_reg_first']], disabled=True, key='s_district_disabled')

    st.divider()

    col_o1, col_o2 = st.columns(2)
    with col_o1:
        st.number_input(L['seat_label'], min_value=0, max_value=4, key='seat_count_val')
    with col_o2:
        if "Arrival" in st.session_state.s_type:
            st.markdown("<br>", unsafe_allow_html=True)
            st.checkbox(L['mg_pickup'], key='mg_selected_val')
        else:
            # 非接機行程強制設為 False
            st.session_state.mg_selected_val = False

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button(L['prev']): st.session_state.step = 1; st.rerun()
    with col_nav2:
        if st.button(L['next']):
            # 檢查必填項
            time_input = st.session_state.p_time.strip()
            type_sel = st.session_state.s_type
            model_sel = st.session_state.s_model
            region_sel = st.session_state.s_region
            district_sel = st.session_state.get('s_district', L['select_op'])
            
            if time_input and type_sel != L['select_op'] and model_sel != L['select_op'] and \
               region_sel != L['select_op'] and district_sel != L['select_op']:
                st.session_state.step = 3
                st.rerun()
            else:
                st.warning(L['fill_all'])

# 步驟 3: 報價彙總
elif st.session_state.step == 3:
    st.subheader(L['step3']) 
    
    # 從 session_state 提取資料進行過濾
    res = df[(df['Transfer Type'].astype(str).str.strip() == st.session_state.s_type) & 
             (df['Model'].astype(str).str.strip() == st.session_state.s_model) & 
             (df['Region'].astype(str).str.strip() == st.session_state.s_region) & 
             (df['District'].astype(str).str.strip() == st.session_state.s_district)]

    if not res.empty:
        base_price = int(''.join(filter(str.isdigit, str(res.iloc[0]['Result']))))
        
        try:
            parsed_time = parser.parse(st.session_state.p_time).time()
            night_fee = 100 if (parsed_time >= pd.to_datetime("22:00").time() or 
                                parsed_time <= pd.to_datetime("07:00").time()) else 0
        except:
            night_fee = 0 
            
        mg_fee = 80 if st.session_state.get('mg_selected_val', False) else 0
        seat_fee = st.session_state.get('seat_count_val', 0) * 120
        total = base_price + night_fee + mg_fee + seat_fee
        
        route = f"HKIA → {st.session_state.s_district}" if "Arrival" in st.session_state.s_type else (f"{st.session_state.s_district} → HKIA" if "Departure" in st.session_state.s_type else f"{st.session_state.s_type} ({st.session_state.s_district})")
        
        summary_df = pd.DataFrame({L['item']: L['items_list'], L['details']: [
            st.session_state.u_name, st.session_state.u_phone_full, st.session_state.u_email, 
            st.session_state.s_date.strftime("%Y-%m-%d"), st.session_state.p_time, route, 
            f"{st.session_state.seat_count_val} {L['seat_unit']}", 
            f"${mg_fee}" if mg_fee > 0 else "N/A", f"${base_price}", f"HKD ${total}"
        ]})
        st.table(summary_df)
        st.metric(label=L['total_metric'], value=f"HKD ${total}")
        if night_fee > 0: st.warning(L['night_warning'])
    else: 
        st.error(L['no_price'])
    
    if st.button(L['prev']): st.session_state.step = 2; st.rerun()
