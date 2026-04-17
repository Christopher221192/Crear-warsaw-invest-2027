import math
import os
import sys

import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
import streamlit as st
import yaml

sys.path.append(os.getcwd())

from analysis.listing_analyzer import ListingAnalysis, analyze_listing
from analysis.market_analysis import MarketAnalysis
from analysis.mortgage_calc import MortgageCalculator
from dashboard.styles import get_css

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Poland House Hunter",
    page_icon="🇵🇱",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(get_css(), unsafe_allow_html=True)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

DB_PATH = "data/poland_real_estate.duckdb"


# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    analyzer = MarketAnalysis(DB_PATH, config)
    df = analyzer.get_ranked_listings()
    if df.empty:
        return pd.DataFrame()
    if "calculated_price_per_sqm" in df.columns:
        df["price_per_sqm"] = df["price_per_sqm"].fillna(df["calculated_price_per_sqm"])
    df["opportunity_score"] = df["opportunity_score"].clip(0, 10)
    return df


# ── CHARTS ────────────────────────────────────────────────────────────────────
def build_score_gauge(score: float) -> go.Figure:
    color = "#FFD700" if score >= 7 else "#FFA500" if score >= 5 else "#FF6B6B"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"valueformat": ".1f", "font": {"color": color, "size": 38, "family": "JetBrains Mono"}, "suffix": "/10"},
        gauge={
            "axis": {"range": [0, 10], "tickcolor": "rgba(255,255,255,0.2)", "tickfont": {"color": "rgba(255,255,255,0.25)", "size": 9}},
            "bar": {"color": color, "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(255,255,255,0.08)",
            "steps": [
                {"range": [0, 5],  "color": "rgba(255,107,107,0.12)"},
                {"range": [5, 7],  "color": "rgba(255,165,0,0.12)"},
                {"range": [7, 10], "color": "rgba(255,215,0,0.12)"},
            ],
            "threshold": {"line": {"color": color, "width": 2}, "thickness": 0.8, "value": score},
        },
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Opportunity Score", "font": {"color": "rgba(255,255,255,0.35)", "size": 11}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#ffffff", "family": "Inter"},
        margin=dict(l=20, r=20, t=30, b=10), height=230,
    )
    return fig


def build_appreciation_sparkline(appreciation_score: float) -> go.Figure:
    annual_growth = (appreciation_score / 10) * 0.12
    monthly_growth = (1 + annual_growth) ** (1 / 12) - 1
    base = 100.0
    points = [base * ((1 + monthly_growth) ** i) for i in range(13)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=points, mode="lines",
        line=dict(color="#FFD700", width=2),
        fill="tozeroy", fillcolor="rgba(255,215,0,0.08)",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0), height=70,
        showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False), hovermode=False,
    )
    return fig


def build_price_chart(listing_sqm, district_avg, city_avg, district, city) -> go.Figure:
    def _safe(v):
        return v if (v and not (isinstance(v, float) and math.isnan(v))) else 0

    labels = ["Este inmueble", f"Media {district}", f"Media {city.title()}"]
    values = [_safe(listing_sqm), _safe(district_avg), _safe(city_avg)]
    colors = ["#FFD700", "rgba(255,255,255,0.35)", "rgba(255,255,255,0.18)"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=values, marker_color=colors, marker_line_width=0,
        text=[f"{int(v):,} PLN" if v > 0 else "N/A" for v in values],
        textposition="outside",
        textfont=dict(color="rgba(255,255,255,0.7)", size=11, family="JetBrains Mono"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#ffffff", "family": "JetBrains Mono"},
        margin=dict(l=10, r=10, t=36, b=10), height=260,
        title=dict(text="PLN/m² vs Mercado", font=dict(color="rgba(255,255,255,0.4)", size=11, family="Inter")),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", showticklabels=False, zeroline=False),
        xaxis=dict(tickfont=dict(size=11)),
        bargap=0.42,
    )
    return fig


def build_pydeck_map(lat: float, lon: float, district: str, price: float) -> pdk.Deck:
    """Builds a professional deck.gl map."""
    data = [{"lat": lat, "lon": lon, "label": f"{district} · {int(price):,} PLN"}]

    scatter = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position=["lon", "lat"],
        get_fill_color=[255, 215, 0, 220],
        get_line_color=[255, 215, 0, 255],
        get_radius=180,
        radius_min_pixels=8,
        radius_max_pixels=40,
        pickable=True,
        stroked=True,
        line_width_min_pixels=2,
    )

    pulse = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position=["lon", "lat"],
        get_fill_color=[255, 215, 0, 30],
        get_radius=800,
        radius_min_pixels=20,
        radius_max_pixels=120,
        pickable=False,
    )

    view = pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=14,
        pitch=30,
        bearing=0,
    )

    return pdk.Deck(
        layers=[pulse, scatter],
        initial_view_state=view,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        tooltip={
            "html": "<b style='color:#FFD700;font-family:monospace'>{label}</b>",
            "style": {
                "backgroundColor": "rgba(8,8,20,0.95)",
                "color": "white",
                "padding": "8px 12px",
                "borderRadius": "8px",
                "border": "1px solid rgba(255,215,0,0.3)",
                "fontSize": "12px",
            },
        },
    )


def extract_key_features(row) -> list:
    features = []
    phase = (row.get("phase") or "").lower()
    if "plano" in phase:
        features.append("📐 En planos — máxima plusvalía")
    elif "construccion" in phase or "construcción" in phase:
        features.append("🏗️ En construcción")
    area = row.get("area_sqm") or 0
    if area:
        features.append(f"📏 {area:.1f} m² de superficie")
    rooms = row.get("rooms") or 0
    if rooms:
        features.append(f"🛏️ {int(rooms)} habitaciones")
    floor = row.get("floor")
    total = row.get("total_floors")
    if floor and total:
        features.append(f"🏢 Piso {int(floor)} de {int(total)}")
    elif floor:
        features.append(f"🏢 Piso {int(floor)}")
    delivery = row.get("delivery_date") or ""
    if delivery:
        features.append(f"📅 Entrega: {delivery}")
    price_type = (row.get("price_type") or "gross").lower()
    if "netto" in price_type:
        features.append("💶 Precio neto (+ 8% IVA)")
    else:
        features.append("💶 Precio con IVA incluido (8%)")
    dev = row.get("developer") or ""
    if dev and dev != "[INDIVIDUAL - REDACTED]":
        features.append(f"🏭 {dev}")
    return features


# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "view" not in st.session_state:
    st.session_state.view = "list"
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None
if "ai_analysis" not in st.session_state:
    st.session_state.ai_analysis = {}


# ═══════════════════════════════════════════════════════════════════════════════
# VISTA 1 — TABLA PRO
# ═══════════════════════════════════════════════════════════════════════════════
def render_list_view(data: pd.DataFrame):
    st.markdown(
        "<h1 style='font-family:Inter;font-weight:800;font-size:1.9rem;"
        "letter-spacing:-0.04em;margin-bottom:2px;'>🇵🇱 Poland House Hunter</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='premium-id'>Inversiones Q1/Q2 2027 · Mercado Primario · "
        f"{len(data)} oportunidades</p>",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("## 🔍 Radar de Inversión")
        if st.button("🔄 Actualizar datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.markdown("---")

        if data.empty:
            st.warning("No hay datos.")
            return

        all_cities = sorted(data["city"].dropna().unique().tolist())
        city_filter = st.multiselect("Ciudad", options=all_cities, default=all_cities)

        rooms_vals = data["rooms"].dropna()
        min_rooms = int(rooms_vals.min()) if not rooms_vals.empty else 1
        max_rooms = int(rooms_vals.max()) if not rooms_vals.empty else 5
        if min_rooms == max_rooms:
            max_rooms = min_rooms + 1
        rooms_range = st.slider("Habitaciones", min_rooms, max_rooms, (min_rooms, max_rooms))

        prices = data.loc[data["price_pln_gross"] > 0, "price_pln_gross"]
        min_price = int(prices.min()) if not prices.empty else 0
        max_price = int(prices.max()) if not prices.empty else 1
        if min_price == max_price:
            max_price = min_price + 1
        price_range = st.slider("Precio (PLN)", min_price, max_price, (min_price, max_price), step=10_000, format="%d PLN")

        score_min = st.slider("Score mínimo", 0.0, 10.0, 0.0, step=0.1, format="%.1f")

    if data.empty:
        st.warning("Ejecuta el scraper primero: `python main_local.py`")
        return

    mask = (
        data["city"].isin(city_filter)
        & data["rooms"].between(rooms_range[0], rooms_range[1])
        & ((data["price_pln_gross"] == 0) | data["price_pln_gross"].between(price_range[0], price_range[1]))
        & (data["opportunity_score"] >= score_min)
    )
    filtered = data[mask].copy()

    c1, c2, c3, c4 = st.columns(4)
    with_price = filtered[filtered["price_pln_gross"] > 0]
    c1.metric("Oportunidades", len(filtered))
    c2.metric("Yield promedio", f"{filtered['annual_yield_percent'].mean():.1f}%" if not filtered.empty else "—")
    c3.metric("Precio medio/m²", f"{int(with_price['price_per_sqm'].mean()):,} PLN" if not with_price.empty else "—")
    c4.metric("Score máximo", f"{filtered['opportunity_score'].max():.1f}" if not filtered.empty else "—")

    st.markdown("---")
    st.markdown("<p class='section-label'>Haz clic en ☑ para ver el análisis detallado</p>", unsafe_allow_html=True)

    DISPLAY_COLS = ["url", "price_pln_gross", "price_per_sqm", "rooms", "area_sqm", "floor", "district", "city", "delivery_date", "opportunity_score"]
    table_df = filtered[DISPLAY_COLS + ["id"]].copy().reset_index(drop=True)
    display_df = table_df[DISPLAY_COLS].copy()
    display_df.insert(0, "Select", False)

    edited = st.data_editor(
        display_df,
        use_container_width=True,
        height=580,
        hide_index=True,
        disabled=DISPLAY_COLS,
        column_config={
            "Select": st.column_config.CheckboxColumn(label="", width="small"),
            "url": st.column_config.LinkColumn(label="Link", display_text="Ver anuncio", help="Abrir en Otodom"),
            "price_pln_gross": st.column_config.NumberColumn(label="Precio", format="%d PLN"),
            "price_per_sqm": st.column_config.NumberColumn(label="PLN/m²", format="%d"),
            "rooms": st.column_config.NumberColumn(label="Hab.", format="%d"),
            "area_sqm": st.column_config.NumberColumn(label="Área m²", format="%.0f"),
            "floor": st.column_config.NumberColumn(label="Piso", format="%d"),
            "district": st.column_config.TextColumn(label="Distrito"),
            "city": st.column_config.TextColumn(label="Ciudad"),
            "delivery_date": st.column_config.TextColumn(label="Entrega"),
            "opportunity_score": st.column_config.ProgressColumn(label="Score", min_value=0.0, max_value=10.0, format="%.1f"),
        },
        key="listings_table",
    )

    checked = edited[edited["Select"]]
    if not checked.empty:
        row_idx = checked.index[0]
        st.session_state.selected_id = table_df.iloc[row_idx]["id"]
        st.session_state.view = "details"
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# VISTA 2 — DETALLE PREMIUM
# ═══════════════════════════════════════════════════════════════════════════════
def _render_ai_analysis_tab(row: dict):
    """Renders the AI Analysis tab content."""
    listing_id = row.get("id") or ""
    url = row.get("url") or ""
    cache_key = f"ai_{listing_id}"

    # Check if analysis already done
    cached = st.session_state.ai_analysis.get(cache_key)

    if cached is None:
        st.markdown(
            """
            <div class='ai-intro'>
                <p class='ai-intro-title'>Análisis con Inteligencia Artificial</p>
                <p class='ai-intro-desc'>
                    Claude analizará el anuncio original: leerá la descripción en polaco,
                    examinará las fotos y el plano de planta para evaluar la distribución,
                    orientación solar y calidad de luz natural.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_btn, col_note = st.columns([1, 2])
        with col_btn:
            run_analysis = st.button(
                "🤖 Analizar con Claude",
                use_container_width=True,
                type="primary",
                key=f"run_ai_{listing_id}",
            )
        with col_note:
            st.markdown(
                "<p style='color:rgba(255,255,255,0.35);font-size:0.78rem;padding-top:10px;'>"
                "Tarda ~15-30 segundos · Incluye análisis visual de imágenes</p>",
                unsafe_allow_html=True,
            )

        if run_analysis:
            with st.spinner("Descargando anuncio y analizando con Claude..."):
                analysis = analyze_listing(
                    url=url,
                    city=row.get("city", ""),
                    district=row.get("district", ""),
                    floor=int(row.get("floor") or 0),
                    total_floors=int(row.get("total_floors") or 0),
                    area=float(row.get("area_sqm") or 0),
                    rooms=int(row.get("rooms") or 0),
                    price=float(row.get("price_pln_gross") or 0),
                )
            st.session_state.ai_analysis[cache_key] = analysis
            st.rerun()
    else:
        analysis: ListingAnalysis = cached
        _render_analysis_results(analysis)


def _render_analysis_results(analysis: ListingAnalysis):
    """Renders the structured AI analysis results."""
    if analysis.error:
        st.error(f"Error en el análisis: {analysis.error}")
        return

    # Verdict colors
    verdict_config = {
        "excelente": ("#00FF88", "⭐ EXCELENTE"),
        "bueno":     ("#7FD9A8", "✓ BUENO"),
        "aceptable": ("#FFD700", "~ ACEPTABLE"),
        "dudoso":    ("#FFA500", "⚠ DUDOSO"),
        "evitar":    ("#FF6B6B", "✗ EVITAR"),
    }
    v_color, v_label = verdict_config.get(analysis.investment_verdict, ("#FFD700", analysis.investment_verdict.upper()))

    # Orientation icons
    orient_icon = {
        "sur": "☀️", "norte": "❄️", "este": "🌅", "oeste": "🌇",
        "sureste": "☀️", "suroeste": "☀️", "noreste": "🌅", "noroeste": "🌫️",
    }.get(analysis.orientation, "🧭")

    light_icon = {
        "excelente": "☀️☀️", "muy buena": "☀️", "buena": "🌤️",
        "moderada": "⛅", "baja": "🌥️", "muy baja": "☁️",
    }.get(analysis.light_quality, "⛅")

    # ── Hero row ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class='ai-metric-card'>
            <p class='ai-metric-label'>Veredicto de inversión</p>
            <p class='ai-metric-value' style='color:{v_color};'>{v_label}</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='ai-metric-card'>
            <p class='ai-metric-label'>Orientación</p>
            <p class='ai-metric-value'>{orient_icon} {analysis.orientation.title()}</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='ai-metric-card'>
            <p class='ai-metric-label'>Luz natural</p>
            <p class='ai-metric-value'>{light_icon} {analysis.light_quality.title()}</p>
        </div>""", unsafe_allow_html=True)
    with c4:
        score = analysis.distribution_score
        score_color = "#00FF88" if score >= 7 else "#FFD700" if score >= 5 else "#FF6B6B"
        st.markdown(f"""
        <div class='ai-metric-card'>
            <p class='ai-metric-label'>Score distribución</p>
            <p class='ai-metric-value' style='color:{score_color};'>{score:.1f} / 10</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Summary ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class='ai-summary-card'>
        <p class='section-label'>Resumen ejecutivo</p>
        <p class='ai-summary-text'>{analysis.summary}</p>
    </div>""", unsafe_allow_html=True)

    # ── Detail columns ────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        # Pros
        pros_html = "".join(f"<div class='ai-pro-item'>✓ {p}</div>" for p in analysis.pros)
        # Cons
        cons_html = "".join(f"<div class='ai-con-item'>✗ {c}</div>" for c in analysis.cons)
        st.markdown(f"""
        <div class='bento-card'>
            <p class='section-label'>Puntos fuertes</p>
            {pros_html}
            <div style='height:16px'></div>
            <p class='section-label'>Puntos débiles</p>
            {cons_html}
        </div>""", unsafe_allow_html=True)

    with col_right:
        st.markdown(f"""
        <div class='bento-card'>
            <p class='section-label'>Análisis de luz natural</p>
            <p class='ai-detail-text'>{analysis.light_analysis}</p>
            <div style='height:12px'></div>
            <p class='section-label'>Orientación — razonamiento</p>
            <p class='ai-detail-text'>{analysis.orientation_reasoning}</p>
            <div style='height:12px'></div>
            <p class='section-label'>Distribución del espacio</p>
            <p class='ai-detail-text'>{analysis.distribution_comment}</p>
        </div>""", unsafe_allow_html=True)

    # Footer note
    imgs = analysis.images_analyzed
    st.markdown(
        f"<p style='color:rgba(255,255,255,0.2);font-size:0.72rem;text-align:center;margin-top:8px;'>"
        f"Análisis basado en {imgs} imagen{'es' if imgs != 1 else ''} + descripción del anuncio · Powered by Claude Sonnet 4.6</p>",
        unsafe_allow_html=True,
    )

    # ── Image Gallery ─────────────────────────────────────────────────────────
    if hasattr(analysis, 'image_urls') and analysis.image_urls:
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown("<p class='section-label'>Mapas de Distribución y Fotos (Planos priorizados)</p>", unsafe_allow_html=True)
        cols = st.columns(min(len(analysis.image_urls), 4))
        for i, img_url in enumerate(analysis.image_urls[:4]):
            with cols[i]:
                st.image(img_url, use_container_width=True, caption=f"Imagen {i+1}")


def render_details_view(data: pd.DataFrame):
    match = data[data["id"] == st.session_state.selected_id]
    if match.empty:
        st.error("Listing no encontrado.")
        if st.button("← Volver"):
            st.session_state.view = "list"
            st.rerun()
        return

    row = match.iloc[0].to_dict()

    if st.button("← Volver a la tabla"):
        st.session_state.view = "list"
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────────────────────
    hero_left, hero_right = st.columns([3, 2], gap="large")

    district    = row.get("district") or "—"
    city        = (row.get("city") or "").title()
    portal      = (row.get("portal") or "otodom").upper()
    listing_id  = row.get("id") or ""
    phase       = row.get("phase") or ""
    price       = row.get("price_pln_gross") or 0
    ppm         = row.get("price_per_sqm") or 0

    with hero_left:
        st.markdown(
            f"<div class='detail-hero'>"
            f"<p class='detail-subtitle'>{portal} · {listing_id} · {phase.title()}</p>"
            f"<h1 class='detail-title'>{district}, {city}</h1>",
            unsafe_allow_html=True,
        )
        if price > 0:
            st.markdown(
                f"<p class='price-display'>{int(price):,} PLN</p>"
                f"<p class='price-sqm'>{int(ppm):,} PLN/m²</p>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<p class='price-display' style='color:rgba(255,255,255,0.25);'>Precio oculto</p>"
                "<p class='price-sqm'>Consultar promotor</p>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        appreciation = row.get("appreciation_score") or 5
        st.markdown("<p class='section-label' style='margin-top:16px;'>Tendencia de apreciación (12 meses proyectados)</p>", unsafe_allow_html=True)
        st.plotly_chart(
            build_appreciation_sparkline(appreciation),
            use_container_width=True,
            config={"displayModeBar": False},
            key=f"spark_{listing_id}",
        )

    with hero_right:
        score = row.get("opportunity_score") or 0
        st.plotly_chart(
            build_score_gauge(score),
            use_container_width=True,
            config={"displayModeBar": False},
            key=f"gauge_{listing_id}",
        )
        vs_avg = row.get("price_vs_avg_%") or 0
        vs_color = "#00FF88" if vs_avg <= 0 else "#FF6B6B"
        vs_label = "bajo la media ✓" if vs_avg <= 0 else "sobre la media"
        st.markdown(
            f"<p style='text-align:center;font-family:JetBrains Mono;font-size:0.85rem;"
            f"color:{vs_color};margin-top:-8px;'>{abs(vs_avg):.1f}% {vs_label}</p>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab_overview, tab_ai, tab_market = st.tabs(["📊 Overview", "🤖 AI Analysis", "📈 Mercado"])

    # ════════════════ TAB 1 — OVERVIEW ═══════════════════════════════════════
    with tab_overview:
        col_specs, col_feat, col_map = st.columns([1, 1, 1], gap="medium")

        with col_specs:
            area         = row.get("area_sqm") or 0
            rooms        = row.get("rooms") or 0
            floor        = row.get("floor")
            total_floors = row.get("total_floors")
            developer    = row.get("developer") or "—"
            delivery     = row.get("delivery_date") or "—"
            price_type   = row.get("price_type") or "gross"

            st.markdown(f"""
            <div class='bento-card' style='height:100%;'>
                <p class='section-label'>Especificaciones</p>
                <div class='spec-grid'>
                    <div class='spec-item'>
                        <span class='spec-label'>Precio bruto</span>
                        <span class='spec-value gold'>{int(price):,} PLN</span>
                    </div>
                    <div class='spec-item'>
                        <span class='spec-label'>Precio/m²</span>
                        <span class='spec-value'>{int(ppm):,} PLN/m²</span>
                    </div>
                    <div class='spec-item'>
                        <span class='spec-label'>Superficie</span>
                        <span class='spec-value'>{area:.1f} m²</span>
                    </div>
                    <div class='spec-item'>
                        <span class='spec-label'>Habitaciones</span>
                        <span class='spec-value'>{int(rooms) if rooms else '—'}</span>
                    </div>
                    <div class='spec-item'>
                        <span class='spec-label'>Piso</span>
                        <span class='spec-value'>{int(floor) if floor else '—'} / {int(total_floors) if total_floors else '?'}</span>
                    </div>
                    <div class='spec-item'>
                        <span class='spec-label'>Entrega</span>
                        <span class='spec-value'>{delivery}</span>
                    </div>
                    <div class='spec-item'>
                        <span class='spec-label'>Promotor</span>
                        <span class='spec-value' style='font-size:0.78rem;'>{developer[:28]}</span>
                    </div>
                    <div class='spec-item'>
                        <span class='spec-label'>IVA</span>
                        <span class='spec-value'>{'Neto +8%' if 'netto' in price_type else 'Incluido 8%'}</span>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        with col_feat:
            features = extract_key_features(row)
            items_html = "".join(f"<div class='feature-item'>{f}</div>" for f in features)
            city_raw = (row.get("city") or "").lower()
            loc_info = {
                "warszawa": ("🚇", "Metro + SKM", "🚶", "Score ~85"),
                "wroclaw":  ("🚋", "Tramvía + Bus", "🚶", "Score ~78"),
                "krakow":   ("🚌", "Bus + Tranvía", "🚶", "Score ~80"),
                "gdansk":   ("🚆", "SKM + Bus", "🚶", "Score ~72"),
                "lodz":     ("🚌", "Tramvía + Bus", "🚶", "Score ~68"),
            }.get(city_raw, ("🚌", "Transporte público", "🚶", "Score ~70"))

            st.markdown(f"""
            <div class='bento-card' style='height:100%;'>
                <p class='section-label'>Características</p>
                {items_html}
                <div style='margin-top:16px;border-top:1px solid rgba(255,255,255,0.06);padding-top:14px;'>
                    <p class='section-label'>Location Highlights</p>
                    <div class='feature-item'>{loc_info[0]} {loc_info[1]}</div>
                    <div class='feature-item'>{loc_info[2]} Walk {loc_info[3]}</div>
                    <div class='feature-item'>🏙️ {city} — Mercado primario</div>
                </div>
            </div>""", unsafe_allow_html=True)

        with col_map:
            lat = row.get("lat")
            lon = row.get("lon")
            has_coords = lat and lon and not (math.isnan(float(lat)) or math.isnan(float(lon)))

            if has_coords:
                deck = build_pydeck_map(float(lat), float(lon), district, price)
                st.pydeck_chart(deck, height=360, use_container_width=True)
            else:
                st.markdown(
                    "<div class='map-placeholder'>Coordenadas no disponibles</div>",
                    unsafe_allow_html=True,
                )

        # ── Link button ──────────────────────────────────────────────────────
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.link_button(
            "🔗 ABRIR ANUNCIO ORIGINAL EN OTODOM",
            url=row.get("url") or "#",
            use_container_width=True,
            type="primary",
        )

    # ════════════════ TAB 2 — AI ANALYSIS ════════════════════════════════════
    with tab_ai:
        _render_ai_analysis_tab(row)

    # ════════════════ TAB 3 — MERCADO ════════════════════════════════════════
    with tab_market:
        col_chart, col_mort = st.columns([1, 1], gap="large")

        with col_chart:
            city_data  = data[data["city"] == row.get("city")]
            dist_data  = city_data[city_data["district"] == district]
            city_avg_sqm = city_data.loc[city_data["price_per_sqm"] > 0, "price_per_sqm"].mean()
            dist_avg_sqm = dist_data.loc[dist_data["price_per_sqm"] > 0, "price_per_sqm"].mean() if not dist_data.empty else city_avg_sqm

            st.plotly_chart(
                build_price_chart(ppm, dist_avg_sqm, city_avg_sqm, district, city),
                use_container_width=True,
                config={"displayModeBar": False},
                key=f"pricechart_{listing_id}",
            )

        with col_mort:
            st.markdown("<div class='bento-card'>", unsafe_allow_html=True)
            st.markdown("<p class='section-label'>Simulador Hipotecario</p>", unsafe_allow_html=True)

            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                down_pct = st.slider("Entrada %", 10, 50, 20, key=f"down_{listing_id}")
            with mc2:
                term_yrs = st.slider("Plazo", 5, 30, 20, key=f"term_{listing_id}")
            with mc3:
                rate_pct = st.number_input("Tasa %", 1.0, 15.0, 5.75, step=0.25, key=f"rate_{listing_id}")

            if price > 0:
                monthly     = MortgageCalculator.calculate_monthly_payment(price, term_yrs, down_pct / 100, rate_pct / 100)
                down_pln    = price * (down_pct / 100)
                loan_pln    = price - down_pln
                monthly_rent = row.get("estimated_monthly_rent") or 0
                cashflow    = monthly_rent - monthly
                annual_yield = row.get("annual_yield_percent") or 0
                cf_class    = "green" if cashflow >= 0 else "red"
                cf_sign     = "+" if cashflow >= 0 else ""

                st.markdown(f"""
                <div class='mortgage-summary'>
                    <div class='mort-row'>
                        <span class='mort-label'>Cuota mensual</span>
                        <span class='mort-value gold'>{int(monthly):,} PLN/mes</span>
                    </div>
                    <div class='mort-row'>
                        <span class='mort-label'>Entrada ({down_pct}%)</span>
                        <span class='mort-value'>{int(down_pln):,} PLN</span>
                    </div>
                    <div class='mort-row'>
                        <span class='mort-label'>Préstamo</span>
                        <span class='mort-value'>{int(loan_pln):,} PLN</span>
                    </div>
                    <div class='mort-row'>
                        <span class='mort-label'>Alquiler estimado</span>
                        <span class='mort-value'>{int(monthly_rent):,} PLN/mes</span>
                    </div>
                    <div class='mort-row'>
                        <span class='mort-label'>Cashflow neto</span>
                        <span class='mort-value {cf_class}'>{cf_sign}{int(cashflow):,} PLN/mes</span>
                    </div>
                    <div class='mort-row'>
                        <span class='mort-label'>Yield bruto anual</span>
                        <span class='mort-value'>{annual_yield:.1f}%</span>
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("Precio no disponible — contactar al promotor para simulación.")
            st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
data = load_data()

if st.session_state.view == "list":
    render_list_view(data)
elif st.session_state.view == "details":
    render_details_view(data)
