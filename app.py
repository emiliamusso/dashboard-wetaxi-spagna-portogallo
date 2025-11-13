import pandas as pd
import streamlit as st
import plotly.express as px
import os


# =========================
# CARICAMENTO DEI DATI
# =========================
@st.cache_data
def load_data():
    filename = "wetaxi_clean_dataset_1311.csv"

    local_path = r"D:\WeTaxi\dataexplore_spain\dashboard\wetaxi_clean_dataset_1311.csv"

    cloud_path = filename 

    # ---- LÓGICA DE CARGA ----

    
    if os.path.exists(local_path):
        df = pd.read_csv(local_path, low_memory=False)
        return df

    
    if os.path.exists(cloud_path):
        df = pd.read_csv(cloud_path, low_memory=False)
        return df

   
    st.error(
        "❌ Il file del dataset non è stato trovato.\n"
        "Caricalo nelle *App Files* di Streamlit Cloud oppure "
        "controlla il percorso locale sul tuo computer."
    )
    return pd.DataFrame() 

# Carica dataset
st.set_page_config(page_title="Dashboard WeTaxi", layout="wide")
st.title("Dashboard Interattivo - WeTaxi Spagna - Portogallo")
df = load_data()

# =========================
# FILTRI INTERATTIVI
# =========================
st.sidebar.header("Filtri")

# Filtro Paese
paesi = sorted(df["raw_orig_country"].dropna().unique())
paese_sel = st.sidebar.selectbox("Seleziona Paese di Origine", options=["Tutti"] + list(paesi))

# Filtro Città
if paese_sel != "Tutti":
    città = sorted(df.loc[df["raw_orig_country"] == paese_sel, "raw_orig_city_clean"].dropna().unique())
else:
    città = sorted(df["raw_orig_city_clean"].dropna().unique())
città_sel = st.sidebar.selectbox("Seleziona Città di Origine", options=["Tutte"] + list(città))

# Filtro Mese e Ora
mesi = sorted(df["pickup_month_local"].dropna().unique())
mesi_sel = st.sidebar.multiselect("Mese di Prelievo", options=mesi, default=mesi)
ore = sorted(df["pickup_hour_local"].dropna().unique())
ore_sel = st.sidebar.multiselect("Ora di Prelievo", options=ore, default=ore)

# Applica filtri
df_filtered = df.copy()
if paese_sel != "Tutti":
    df_filtered = df_filtered[df_filtered["raw_orig_country"] == paese_sel]
if città_sel != "Tutte":
    df_filtered = df_filtered[df_filtered["raw_orig_city_clean"] == città_sel]
df_filtered = df_filtered[
    df_filtered["pickup_month_local"].isin(mesi_sel)
    & df_filtered["pickup_hour_local"].isin(ore_sel)
]

st.success(f"Filtrati {len(df_filtered):,} viaggi")

# =========================
# KPI PRINCIPALI
# =========================
st.subheader("Indicatori Chiave (KPI)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Distanza Totale (km)", f"{df_filtered['raw_driving_dist_km'].sum():,.0f}")
col2.metric("Totale Viaggi", f"{len(df_filtered):,}")
col3.metric("Totale Viaggi con origine Aeroporto", f"{df_filtered['is_from_airport'].sum():,}")
col4.metric("Totale Viaggi con destinazione Aeroporto", f"{df_filtered['is_to_airport'].sum():,}")

# =========================
# DISTRIBUZIONE PAESI E CITTÀ
# =========================
st.subheader("Distribuzioni per Paese e Città")

col1, col2 = st.columns(2)

with col1:
    df_orig_country = df_filtered["raw_orig_country"].value_counts().reset_index()
    df_orig_country.columns = ["Paese", "Conteggio"]
    fig1 = px.bar(df_orig_country, x="Paese", y="Conteggio", title="Paesi di Origine")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    df_dest_country = df_filtered["raw_dest_country"].value_counts().reset_index()
    df_dest_country.columns = ["Paese", "Conteggio"]
    fig2 = px.bar(df_dest_country, x="Paese", y="Conteggio", title="Paesi di Destinazione")
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    df_city_orig = df_filtered["raw_orig_city_clean"].value_counts().head(20).reset_index()
    df_city_orig.columns = ["Città", "Conteggio"]
    fig3 = px.bar(df_city_orig, x="Città", y="Conteggio", title="Top 20 Città Origine")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    df_city_dest = df_filtered["raw_dest_city_clean"].value_counts().head(20).reset_index()
    df_city_dest.columns = ["Città", "Conteggio"]
    fig4 = px.bar(df_city_dest, x="Città", y="Conteggio", title="Top 20 Città Destinazione")
    st.plotly_chart(fig4, use_container_width=True)

# =========================
# TRAFFICO AEROPORTUALE
# =========================
st.subheader("Viaggi da o verso aeroporti")

col5, col6 = st.columns(2)
with col5:
    df_air_orig = df_filtered["orig_airport_code"].value_counts().reset_index()
    df_air_orig.columns = ["Aeroporto", "Conteggio"]
    fig5 = px.bar(df_air_orig, x="Aeroporto", y="Conteggio", title="Aeroporti di Origine")
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    df_air_dest = df_filtered["dest_airport_code"].value_counts().reset_index()
    df_air_dest.columns = ["Aeroporto", "Conteggio"]
    fig6 = px.bar(df_air_dest, x="Aeroporto", y="Conteggio", title="Aeroporti di Destinazione")
    st.plotly_chart(fig6, use_container_width=True)

# =========================
# DISTRIBUZIONE TEMPORALE E PASSEGGERI
# =========================
st.subheader("Distribuzione Temporale e Passeggeri")

col7, col8 = st.columns(2)
with col7:
    fig7 = px.histogram(
        df_filtered,
        x="pickup_hour_local",
        nbins=24,
        title="Distribuzione per Ora del Giorno",
        color_discrete_sequence=["#1f77b4"]
    )
    fig7.update_layout(
        xaxis_title="Ora del Giorno",
        yaxis_title="Conteggio"
    )
    st.plotly_chart(fig7, use_container_width=True)

with col8:

    ordine_giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

    fig8 = px.histogram(
        df_filtered,
        x="pickup_day_local",
        category_orders={"pickup_day_local": ordine_giorni},
        title="Distribuzione per Giorno della Settimana",
        color_discrete_sequence=["#2ca02c"]
    )
    fig8.update_layout(
        xaxis_title="Giorno",
        yaxis_title="Conteggio"
    )
    st.plotly_chart(fig8, use_container_width=True)

fig9 = px.histogram(
    df_filtered,
    x="raw_passengers",
    title="Numero di Passeggeri per Viaggio",
    color_discrete_sequence=["#ff7f0e"]
)
fig9.update_layout(
    xaxis_title="Numero di Passeggeri per viaggio",
    yaxis_title="Conteggio"
)
st.plotly_chart(fig9, use_container_width=True)

# =========================
# MAPPE
# =========================
st.subheader("Mappe di Origine e Destinazione")

# Per evitare errore Streamlit, rinominiamo le colonne in lat/lon
df_map_orig = df_filtered.rename(columns={"raw_orig_latitude": "lat", "raw_orig_longitude": "lon"})
df_map_dest = df_filtered.rename(columns={"raw_dest_latitude": "lat", "raw_dest_longitude": "lon"})

col9, col10 = st.columns(2)
with col9:
    st.map(df_map_orig[["lat", "lon"]].dropna().sample(min(5000, len(df_map_orig))), zoom=4)
    st.caption("📍 Punti di Origine")

with col10:
    st.map(df_map_dest[["lat", "lon"]].dropna().sample(min(5000, len(df_map_dest))), zoom=4)
    st.caption("🏁 Punti di Destinazione")
