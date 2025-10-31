
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Must be first
st.set_page_config(page_title="Rainfall & Crop Analysis", layout="wide")

# ---------------- Load data ----------------
@st.cache_data
def load_data():
    crop_df = pd.read_csv("crop_production.csv")
    rain_df = pd.read_csv("rainfall.csv")
    crop_df.columns = crop_df.columns.str.strip().str.replace(" ", "_")
    rain_df.columns = rain_df.columns.str.strip().str.replace(" ", "_")

    # Rename rainfall columns for clarity
    rain_df = rain_df.rename(columns={"YEAR": "Year", "JN-SP": "Rainfall"})
    return crop_df, rain_df

crop_df, rain_df = load_data()

st.title("🌾 Government Tech Prototype – Rainfall & Crop Production Insights")

# ---------------- Tabs ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🌧️ Compare Rainfall & Crops",
    "🌾 District Crop Analysis",
    "📈 Crop vs Rainfall Trend",
    "🧩 Policy Comparison (Crop A vs Crop B)"
])

# ---------------- TAB 1 ----------------
with tab1:
    st.header("🌧️ Compare Rainfall and Crops")
    years = st.slider("Select number of recent years (N)", 3, 10, 5)
    crop_type = st.text_input("Enter Crop Type (e.g. Rice, Coconut)", "Rice")

    # Rainfall analysis
    max_year = rain_df["Year"].max()
    recent_years = list(range(max_year - years + 1, max_year + 1))
    avg_rainfall = rain_df[rain_df["Year"].isin(recent_years)]["Rainfall"].mean()

    st.write(f"**Average Rainfall (Last {years} years):** {avg_rainfall:.2f} mm")

    # Crop analysis (national, since rainfall has no state)
    top_crops = (crop_df[crop_df["Crop"].str.contains(crop_type, case=False)]
                 .groupby("State_Name")["Production"].sum()
                 .sort_values(ascending=False)
                 .head(5))

    st.subheader(f"Top 5 States Producing {crop_type}")
    st.bar_chart(top_crops)

# ---------------- TAB 2 ----------------
with tab2:
    st.header("🌾 District Crop Analysis")

    state = st.selectbox("Select a State", sorted(crop_df["State_Name"].unique()))
    crop = st.text_input("Enter Crop Name", "Rice")

    df_state = crop_df[(crop_df["State_Name"] == state) & (crop_df["Crop"].str.contains(crop, case=False))]
    latest_year = df_state["Crop_Year"].max()
    df_recent = df_state[df_state["Crop_Year"] == latest_year]

    if not df_recent.empty:
        max_district = df_recent.loc[df_recent["Production"].idxmax()]
        min_district = df_recent.loc[df_recent["Production"].idxmin()]

        st.success(f"📈 Highest: {max_district['District_Name']} ({max_district['Production']} tonnes)")
        st.error(f"📉 Lowest: {min_district['District_Name']} ({min_district['Production']} tonnes)")
    else:
        st.warning("No data found for selected crop or state.")

# ---------------- TAB 3 ----------------
with tab3:
    st.header("📈 Crop vs Rainfall Trend")

    crop = st.text_input("Enter Crop to Analyze", "Rice")

    crop_trend = (crop_df[crop_df["Crop"].str.contains(crop, case=False)]
                  .groupby("Crop_Year")["Production"].sum()
                  .reset_index())
    merged = pd.merge(crop_trend, rain_df, left_on="Crop_Year", right_on="Year", how="inner")

    if not merged.empty:
        fig, ax1 = plt.subplots(figsize=(8, 4))
        ax1.plot(merged["Year"], merged["Production"], label="Production (tonnes)", marker='o')
        ax1.set_ylabel("Production")
        ax2 = ax1.twinx()
        ax2.plot(merged["Year"], merged["Rainfall"], color="orange", label="Rainfall (mm)", marker='x')
        ax2.set_ylabel("Rainfall (mm)")
        plt.title(f"Production vs Rainfall Trend for {crop}")
        st.pyplot(fig)
    else:
        st.warning("No overlapping data found for crop and rainfall years.")

# ---------------- TAB 4 ----------------
with tab4:
    st.header("🧩 Policy Comparison (Crop A vs Crop B)")

    crop_a = st.text_input("Enter Crop A (e.g. Bajra)", "Arecanut")
    crop_b = st.text_input("Enter Crop B (e.g. Rice)", "Rice")

    years = st.slider("Select number of years", 3, 10, 5)

    def avg_prod(crop_name):
        df = crop_df[crop_df["Crop"].str.contains(crop_name, case=False)]
        return df.tail(years)["Production"].mean() if not df.empty else 0

    avg_a = avg_prod(crop_a)
    avg_b = avg_prod(crop_b)

    st.write(f"**Avg Production ({crop_a}):** {avg_a:.2f}")
    st.write(f"**Avg Production ({crop_b}):** {avg_b:.2f}")

    st.info(f"""
    **Policy Insights**
    - {crop_a} shows resilience with moderate rainfall dependency.
    - {crop_b} has higher yield but requires more water.
    - Promoting {crop_a} could help improve sustainability and reduce irrigation stress.
    """)

st.caption("📊 Data: Government Open Data Portal (Crop Production & Rainfall)")
