import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Quincy Limo Prices", layout="centered")
st.title("🚗 Quincy Limo Price Finder")

# 2. Your Google Sheets CSV Link
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUroRgmX-R1wQx5ndR5B8plTm7uajQg4OdpdxV8UK21exlpKhmix-wjLKGgG2HrLqWLhHQpQn-Gmfv/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60) # Refreshes data every 60 seconds
def load_data():
    # Load data and strip extra spaces from headers and content
    data = pd.read_csv(sheet_url)
    data.columns = data.columns.str.strip()
    return data

# --- Main Logic ---

try:
    df = load_data()

    # 3. Check for required headers
    required_columns = ['Model', 'Region', 'Result']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"Error: Missing columns in Excel: {missing_columns}")
        st.info("Please ensure your Google Sheet headers are exactly: **Model**, **Region**, and **Result**.")
    else:
        # 4. Create Filters
        st.write("Select your options below to see the price:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            models = sorted(df['Model'].dropna().unique())
            selected_model = st.selectbox("1. Select Car Model:", models)

        with col2:
            # Filter regions based on the selected model
            available_regions = sorted(df[df['Model'] == selected_model]['Region'].dropna().unique())
            selected_region = st.selectbox("2. Select Region:", available_regions)

        st.divider()
        
        # 5. Display Result
        final_result = df[(df['Model'] == selected_model) & (df['Region'] == selected_region)]

        if not final_result.empty:
            price_info = final_result.iloc[0]['Result']
            st.subheader("📍 Quote Detail:")
            st.success(f"**The rate is:** {price_info}")
        else:
            st.warning("No pricing found for this specific combination.")

except Exception as e:
    st.error("System could not connect to the database.")
    st.exception(e)
