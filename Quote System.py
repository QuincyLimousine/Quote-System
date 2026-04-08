# 步驟 2: 行程詳情
elif st.session_state.step == 2:
    st.subheader(L['step2'])
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.date_input(L['date_label'], key='s_date_widget', min_value=date.today())
    with col_t2:
        st.text_input(L['time_label'], key='p_time', value=st.session_state.p_time_val)
    
    st.divider()
    
    # 第一行：接送類型與車型選擇
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        t_types = [L['select_op']] + sorted(df['Transfer Type'].dropna().unique().tolist())
        st.selectbox(L['type_label'], t_types, key='s_type')
        
    with col_s2:
        mods = [L['select_op']] + sorted(df['Model'].dropna().unique().tolist())
        selected_model = st.selectbox(L['model_label'], mods, key='s_model')

    # 第二行：地區與區域選擇
    col_s3, col_s4 = st.columns(2)
    with col_s3:
        regs = [L['select_op']] + sorted(df['Region'].dropna().unique().tolist())
        st.selectbox(L['region_label'], regs, key='s_region')
        
    with col_s4:
        if st.session_state.s_region != L['select_op']:
            dists = [L['select_op']] + sorted(df[df['Region'] == st.session_state.s_region]['District'].dropna().unique().tolist())
            st.selectbox(L['district_label'], dists, key='s_district')
        else:
            st.selectbox(L['district_label'], [L['select_reg_first']], disabled=True, key='s_district_tmp')

    # --- 新增：車型圖片顯示 (放在車型及地域下方的中間位置) ---
    model_images = {
        "Comfort 5-Seater": "https://raw.githubusercontent.com/QuincyLimousine/Quincy-Limousine-Prices/main/Vehicle%20Type/Compact%205-Seater.png",
        "Deluxe 5-Seater": "https://raw.githubusercontent.com/QuincyLimousine/Quincy-Limousine-Prices/main/Vehicle%20Type/Deluxe%205-Seater.png",
        "Deluxe 7-Seater": "https://raw.githubusercontent.com/QuincyLimousine/Quincy-Limousine-Prices/main/Vehicle%20Type/Deluxe%207-Seater.png",
        "Premium 7-Seater": "https://raw.githubusercontent.com/QuincyLimousine/Quincy-Limousine-Prices/main/Vehicle%20Type/Premium%207-Seater.png"
    }
    
    if selected_model in model_images:
        # 使用 columns 稍微縮小圖片寬度，使其不會顯得過大
        _, img_col, _ = st.columns([0.2, 0.6, 0.2])
        with img_col:
            st.image(model_images[selected_model], use_container_width=True)

    st.divider()

    col_o1, col_o2 = st.columns(2)
    with col_o1:
        st.number_input(L['seat_label'], min_value=0, max_value=4, key='seat_count')
    with col_o2:
        # 這裡修正了判斷邏輯，使用 key 本身的值
        if "Arrival" in st.session_state.s_type:
            st.markdown("<br>", unsafe_allow_html=True)
            st.checkbox(L['mg_pickup'], key='mg_selected', value=st.session_state.mg_selected_val)
        else:
            st.session_state.mg_selected_val = False

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button(L['prev']): st.session_state.step = 1; st.rerun()
    with col_nav2:
        if st.button(L['next']):
            time_val = st.session_state.p_time.strip()
            if time_val and st.session_state.s_type != L['select_op'] and st.session_state.s_region != L['select_op'] and st.session_state.s_model != L['select_op']:
                st.session_state.p_time_val = time_val
                st.session_state.s_type_val = st.session_state.s_type
                st.session_state.s_model_val = st.session_state.s_model
                st.session_state.s_region_val = st.session_state.s_region
                st.session_state.s_district_val = st.session_state.get('s_district', '')
                st.session_state.seat_count_val = st.session_state.seat_count
                st.session_state.mg_selected_val = st.session_state.get('mg_selected', False)
                st.session_state.s_date_val = st.session_state.s_date_widget
                st.session_state.step = 3
                st.rerun()
            else:
                st.warning(L['fill_all'])
