import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import requests

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE LA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Mortalidad Colombia 2019",
    page_icon="🇨🇴",
    layout="wide"
)

st.title("🇨🇴 Análisis de Mortalidad en Colombia — 2019")
st.markdown("Aplicación interactiva para explorar los datos de mortalidad no fetal del DANE para el año 2019.")
st.markdown("---")

# ─────────────────────────────────────────────
# CARGA Y LIMPIEZA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    # Datos de mortalidad
    df = pd.read_excel("datos/NoFetal2019.xlsx")

    # Códigos de muerte (encabezado en fila 8)
    codigos = pd.read_excel("datos/CodigosDeMuerte.xlsx", header=8)
    codigos.columns = [
        "Capitulo", "Nombre_Capitulo",
        "Codigo3", "Descripcion3",
        "Codigo4", "Descripcion4"
    ]
    codigos = codigos.dropna(subset=["Codigo4"])
    codigos["Codigo4"] = codigos["Codigo4"].astype(str).str.strip()

    # Divipola
    divipola = pd.read_excel("datos/Divipola.xlsx")

    # Limpiar y unir
    df["COD_MUERTE"] = df["COD_MUERTE"].astype(str).str.strip()
    df["COD_DANE"] = df["COD_DANE"].astype(str).str.strip()
    divipola["COD_DANE"] = divipola["COD_DANE"].astype(str).str.strip()

    df = df.merge(divipola[["COD_DANE", "DEPARTAMENTO", "MUNICIPIO"]], on="COD_DANE", how="left")
    df = df.merge(codigos[["Codigo4", "Descripcion4"]], left_on="COD_MUERTE", right_on="Codigo4", how="left")

    # Mapeo de sexo
    df["SEXO_NOMBRE"] = df["SEXO"].map({1: "Masculino", 2: "Femenino", 3: "Indeterminado"})

    # Mapeo de grupos de edad
    grupos_edad = {
        **{i: "Mortalidad neonatal" for i in range(0, 5)},
        **{i: "Mortalidad infantil" for i in range(5, 7)},
        **{i: "Primera infancia" for i in range(7, 9)},
        **{i: "Niñez" for i in range(9, 11)},
        11: "Adolescencia",
        **{i: "Juventud" for i in range(12, 14)},
        **{i: "Adultez temprana" for i in range(14, 17)},
        **{i: "Adultez intermedia" for i in range(17, 20)},
        **{i: "Vejez" for i in range(20, 25)},
        **{i: "Longevidad / Centenarios" for i in range(25, 29)},
        29: "Edad desconocida"
    }
    df["CATEGORIA_EDAD"] = df["GRUPO_EDAD1"].map(grupos_edad)

    return df, codigos, divipola

df, codigos, divipola = cargar_datos()

# ─────────────────────────────────────────────
# SIDEBAR — RESUMEN GENERAL
# ─────────────────────────────────────────────
st.sidebar.header("📊 Resumen General")
st.sidebar.metric("Total de muertes", f"{len(df):,}")
st.sidebar.metric("Departamentos", df["DEPARTAMENTO"].nunique())
st.sidebar.metric("Municipios", df["MUNICIPIO"].nunique())
st.sidebar.metric("Causas de muerte", df["COD_MUERTE"].nunique())
st.sidebar.markdown("---")
st.sidebar.markdown("**Fuente:** DANE — Estadísticas Vitales 2019")

# ─────────────────────────────────────────────
# 1. MAPA: MUERTES POR DEPARTAMENTO
# ─────────────────────────────────────────────
st.header("🗺️ Distribución de Muertes por Departamento")

muertes_depto = (
    df.groupby("DEPARTAMENTO")
    .size()
    .reset_index(name="Total_Muertes")
    .sort_values("Total_Muertes", ascending=False)
)

# GeoJSON de departamentos de Colombia (fuente pública)
GEOJSON_URL = "https://raw.githubusercontent.com/mpalber/colombia-geojson/main/colombia.geo.json"

@st.cache_data
def cargar_geojson():
    try:
        resp = requests.get(GEOJSON_URL, timeout=10)
        return resp.json()
    except Exception:
        return None

geojson = cargar_geojson()

if geojson:
    # Normalizar nombres para match con el geojson
    muertes_depto["DEPARTAMENTO_NORM"] = muertes_depto["DEPARTAMENTO"].str.upper().str.strip()

    fig_mapa = px.choropleth(
        muertes_depto,
        geojson=geojson,
        locations="DEPARTAMENTO_NORM",
        featureidkey="properties.NOMBRE_DPT",
        color="Total_Muertes",
        color_continuous_scale="Reds",
        title="Total de muertes por departamento — Colombia 2019",
        labels={"Total_Muertes": "Total Muertes", "DEPARTAMENTO_NORM": "Departamento"}
    )
    fig_mapa.update_geos(fitbounds="locations", visible=False)
    fig_mapa.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=550)
    st.plotly_chart(fig_mapa, use_container_width=True)
else:
    # Fallback: gráfico de barras si no hay conexión al geojson
    fig_mapa_alt = px.bar(
        muertes_depto.head(20),
        x="Total_Muertes",
        y="DEPARTAMENTO",
        orientation="h",
        title="Top 20 departamentos por total de muertes (2019)",
        labels={"Total_Muertes": "Total Muertes", "DEPARTAMENTO": "Departamento"},
        color="Total_Muertes",
        color_continuous_scale="Reds"
    )
    fig_mapa_alt.update_layout(yaxis=dict(autorange="reversed"), height=500)
    st.plotly_chart(fig_mapa_alt, use_container_width=True)

with st.expander("📋 Ver tabla completa por departamento"):
    st.dataframe(muertes_depto.reset_index(drop=True), use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# 2. GRÁFICO DE LÍNEAS: MUERTES POR MES
# ─────────────────────────────────────────────
st.header("📈 Total de Muertes por Mes")

meses_nombres = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

muertes_mes = (
    df.groupby("MES")
    .size()
    .reset_index(name="Total_Muertes")
)
muertes_mes["MES_NOMBRE"] = muertes_mes["MES"].map(meses_nombres)

fig_lineas = px.line(
    muertes_mes,
    x="MES_NOMBRE",
    y="Total_Muertes",
    markers=True,
    title="Total de muertes por mes — Colombia 2019",
    labels={"Total_Muertes": "Total Muertes", "MES_NOMBRE": "Mes"},
    text="Total_Muertes"
)
fig_lineas.update_traces(textposition="top center", line_color="#c0392b", marker_color="#c0392b")
fig_lineas.update_layout(
    xaxis=dict(categoryorder="array", categoryarray=list(meses_nombres.values())),
    height=420
)
st.plotly_chart(fig_lineas, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# 3. GRÁFICO DE BARRAS: 5 CIUDADES MÁS VIOLENTAS
# ─────────────────────────────────────────────
st.header("🔫 5 Ciudades Más Violentas (Homicidios — Código X95)")

homicidios = df[df["COD_MUERTE"].str.startswith("X95", na=False)]
ciudades_violentas = (
    homicidios.groupby("MUNICIPIO")
    .size()
    .reset_index(name="Homicidios")
    .sort_values("Homicidios", ascending=False)
    .head(5)
)

fig_barras = px.bar(
    ciudades_violentas,
    x="MUNICIPIO",
    y="Homicidios",
    title="Top 5 ciudades con más homicidios por arma de fuego (X95) — 2019",
    labels={"Homicidios": "Número de Homicidios", "MUNICIPIO": "Ciudad"},
    color="Homicidios",
    color_continuous_scale="Reds",
    text="Homicidios"
)
fig_barras.update_traces(textposition="outside")
fig_barras.update_layout(showlegend=False, height=420)
st.plotly_chart(fig_barras, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# 4. GRÁFICO CIRCULAR: 10 CIUDADES CON MENOR MORTALIDAD
# ─────────────────────────────────────────────
st.header("🥧 10 Ciudades con Menor Índice de Mortalidad")

menor_mortalidad = (
    df.groupby("MUNICIPIO")
    .size()
    .reset_index(name="Total_Muertes")
    .sort_values("Total_Muertes")
    .head(10)
)

fig_pie = px.pie(
    menor_mortalidad,
    names="MUNICIPIO",
    values="Total_Muertes",
    title="10 municipios con menor número de muertes registradas — 2019",
    hole=0.3
)
fig_pie.update_traces(textposition="inside", textinfo="percent+label")
fig_pie.update_layout(height=480)
st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# 5. TABLA: TOP 10 CAUSAS DE MUERTE
# ─────────────────────────────────────────────
st.header("📋 Top 10 Causas de Muerte en Colombia")

top_causas = (
    df.groupby(["COD_MUERTE", "Descripcion4"])
    .size()
    .reset_index(name="Total_Casos")
    .sort_values("Total_Casos", ascending=False)
    .head(10)
    .reset_index(drop=True)
)
top_causas.index += 1
top_causas.columns = ["Código CIE-10", "Descripción", "Total Casos"]

st.dataframe(top_causas, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# 6. BARRAS APILADAS: MUERTES POR SEXO Y DEPARTAMENTO
# ─────────────────────────────────────────────
st.header("⚥ Muertes por Sexo en cada Departamento")

sexo_depto = (
    df[df["SEXO_NOMBRE"].isin(["Masculino", "Femenino"])]
    .groupby(["DEPARTAMENTO", "SEXO_NOMBRE"])
    .size()
    .reset_index(name="Total")
)

fig_apilado = px.bar(
    sexo_depto,
    x="DEPARTAMENTO",
    y="Total",
    color="SEXO_NOMBRE",
    barmode="stack",
    title="Total de muertes por sexo en cada departamento — Colombia 2019",
    labels={"Total": "Total Muertes", "DEPARTAMENTO": "Departamento", "SEXO_NOMBRE": "Sexo"},
    color_discrete_map={"Masculino": "#2980b9", "Femenino": "#e74c3c"}
)
fig_apilado.update_layout(
    xaxis_tickangle=-45,
    height=500,
    legend_title="Sexo"
)
st.plotly_chart(fig_apilado, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# 7. HISTOGRAMA: DISTRIBUCIÓN POR GRUPO DE EDAD
# ─────────────────────────────────────────────
st.header("👶👴 Distribución de Muertes por Grupo de Edad")

orden_categorias = [
    "Mortalidad neonatal",
    "Mortalidad infantil",
    "Primera infancia",
    "Niñez",
    "Adolescencia",
    "Juventud",
    "Adultez temprana",
    "Adultez intermedia",
    "Vejez",
    "Longevidad / Centenarios",
    "Edad desconocida"
]

dist_edad = (
    df.groupby("CATEGORIA_EDAD")
    .size()
    .reset_index(name="Total_Muertes")
)
dist_edad["CATEGORIA_EDAD"] = pd.Categorical(
    dist_edad["CATEGORIA_EDAD"],
    categories=orden_categorias,
    ordered=True
)
dist_edad = dist_edad.sort_values("CATEGORIA_EDAD")

fig_edad = px.bar(
    dist_edad,
    x="CATEGORIA_EDAD",
    y="Total_Muertes",
    title="Distribución de muertes por grupo etario — Colombia 2019",
    labels={"Total_Muertes": "Total Muertes", "CATEGORIA_EDAD": "Grupo de Edad"},
    color="Total_Muertes",
    color_continuous_scale="Blues",
    text="Total_Muertes"
)
fig_edad.update_traces(textposition="outside")
fig_edad.update_layout(xaxis_tickangle=-30, height=470, showlegend=False)
st.plotly_chart(fig_edad, use_container_width=True)

st.markdown("---")
st.caption("Datos: DANE — Estadísticas Vitales EEVV 2019 | Desarrollado con Python, Streamlit y Plotly")
