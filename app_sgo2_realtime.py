import streamlit as st
from streamlit_autorefresh import st_autorefresh
from google.cloud import bigquery
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="SGO2 YMS - Performance & Tempo Real",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
)

META_PERMANENCIA_MIN = 30  # Meta operacional fixa: 30 minutos

# 2. Theme State
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# 3. Custom CSS Styles
bg_color = "#09090b" if IS_DARK else "#ffffff"
card_bg = "#121215" if IS_DARK else "#f8f9fa"
border_color = "#27272a" if IS_DARK else "#e4e4e7"
text_color = "#fafafa" if IS_DARK else "#09090b"
text_muted = "#a1a1aa" if IS_DARK else "#71717a"
accent_color = "#ffe600" # Meli Yellow

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], .main {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
        font-family: 'DM Sans', sans-serif !important;
    }}
    
    header[data-testid="stHeader"], #MainMenu, footer, .stDeployButton {{
        display: none !important;
    }}
    
    .block-container {{
        padding: 1.5rem 2rem 2.5rem !important;
        max-width: 1440px !important;
    }}
    
    .kpi-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        height: 100%;
    }}
    .kpi-label {{
        font-size: 0.78rem;
        color: {text_muted};
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {text_color};
        margin-top: 0.2rem;
        line-height: 1.1;
    }}
    .kpi-subtext {{
        font-size: 0.78rem;
        margin-top: 0.4rem;
    }}
    
    .badge {{
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 600;
        display: inline-block;
    }}
    .badge-success {{ background: rgba(34, 197, 94, 0.18); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); }}
    .badge-danger {{ background: rgba(239, 68, 68, 0.18); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }}
    .badge-warning {{ background: rgba(234, 179, 8, 0.18); color: #eab308; border: 1px solid rgba(234, 179, 8, 0.3); }}
    .badge-xpt {{ background: rgba(168, 85, 247, 0.18); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.3); }}
    
    .chart-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.2rem;
        margin-top: 1rem;
    }}
    .chart-title {{
        font-size: 0.95rem;
        font-weight: 700;
        color: {text_color};
        margin-bottom: 0.8rem;
    }}
    .insight-card {{
        background: rgba(37, 99, 235, 0.08);
        border: 1px solid rgba(37, 99, 235, 0.3);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }}
</style>
""", unsafe_allow_html=True)

# 4. Auto Refresh (1 min = 60000ms)
st_autorefresh(interval=60000, key="yms_sgo2_realtime_refresh_v2")

# 5. Header & Controls
col_title, col_status, col_theme = st.columns([6, 3, 1])

with col_title:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 2.2rem;">🚛</span>
        <div>
            <h2 style="margin: 0; font-weight: 700; font-size: 1.65rem; color: {text_color};">
                Monitor YMS SGO2 <span style="font-size: 0.85rem; color: {accent_color}; background: rgba(255,230,0,0.15); padding: 3px 8px; border-radius: 6px; margin-left: 6px;">META 30 MIN</span>
            </h2>
            <p style="margin: 0; font-size: 0.82rem; color: {text_muted};">Pátio Service Center Rio Verde - GO (SGO2) • Atualização em Tempo Real (60s)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_status:
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div style="text-align: right; padding-top: 6px;">
        <span class="badge badge-success">🟢 SESSÃO STREAMING ATIVA</span>
        <div style="font-size: 0.78rem; color: {text_muted}; margin-top: 4px;">Atualizado às: <b>{now_str}</b></div>
    </div>
    """, unsafe_allow_html=True)

with col_theme:
    st.button("☀️ Light" if IS_DARK else "🌙 Dark", on_click=toggle_theme, use_container_width=True)

st.markdown("<hr style='margin: 1rem 0; border-color: " + border_color + ";'>", unsafe_allow_html=True)

# 6. Sidebar Controls
with st.sidebar:
    st.header("⚙️ Configurações & Filtros")
    facility_selected = st.selectbox("Facility (Centro Logístico)", ["SGO2", "BRXGO1", "SSP1", "SDO1"], index=0)
    meta_permanencia_input = st.number_input("Meta Tempo Permanência (Min):", min_value=5, max_value=120, value=30, step=5)
    
    st.subheader("Filtros de Veículos")
    exclude_heavy = st.checkbox("Excluir Veículos Pesados (Truck/Carreta)", value=True)
    only_offenders = st.checkbox("Exibir Apenas Veículos Fora da Meta (> 30 min)", value=False)
    only_xpt = st.checkbox("Exibir Apenas Operações XPT", value=False)
    
    search_plate = st.text_input("Filtrar Placa:", value="").upper().strip()

# 7. BigQuery Query Fetcher
@st.cache_data(ttl=55)
def load_yms_realtime_data(facility_id: str, exclude_heavy_v: bool):
    client = bigquery.Client(project="meli-bi-data")
    
    heavy_clause = ""
    if exclude_heavy_v:
        heavy_clause = 'AND v.VEHICLE_TYPE NOT IN ("Cavalo","Carreta_Alongada","Truck","Toco")'
        
    query = f"""
    SELECT
      jo.JOURNEY_ID,
      jo.SITE_ID,
      jo.NODE_ID,
      jo.JOURNEY_STATUS,
      DATETIME_ADD(jo.STARTED_AT,  INTERVAL 1 HOUR) AS checkin,
      DATETIME_ADD(jo.FINISHED_AT, INTERVAL 1 HOUR) AS checkout,
      
      -- Cálculo exato da permanência (Se não finalizou, compara com horário atual)
      COALESCE(
        DATETIME_DIFF(DATETIME_ADD(jo.FINISHED_AT, INTERVAL 1 HOUR), DATETIME_ADD(jo.STARTED_AT, INTERVAL 1 HOUR), MINUTE),
        DATETIME_DIFF(CURRENT_DATETIME(), DATETIME_ADD(jo.STARTED_AT, INTERVAL 1 HOUR), MINUTE)
      ) AS permanencia_minutos,
      
      p.LOGISTIC_CENTER AS facility,
      
      -- Rota
      COALESCE(p.ROUTE.EXECUTED_ID, p.ROUTE.PLAN_ID, p.SERVICE_CODE) AS route_id,
      p.ROUTE.ROUTE_TYPE AS route_type_planner,
      p.PROCESS_TYPE AS process_type,
      p.MILE AS mile,
      
      -- Veículo
      v.VEHICLE_PLATE AS plate,
      v.VEHICLE_TYPE AS vehicle_type,
      
      -- Destino
      COALESCE(r.SHP_LG_DESTINATION_FACILITY_ID, r.SHP_LG_ROUTE_NODE_ID_DESTINATION) AS destination_id,
      COALESCE(plc.HUB_NAME, ag.SHP_AGEN_BUSINESS_NAME, r.SHP_LG_DESTINATION_FACILITY_ID, 'Last Mile Direct') AS destination_name,
      
      -- Flag XPT
      CASE 
          WHEN r.SHP_EXCHANGE_POINT_ID IS NOT NULL 
            OR UPPER(COALESCE(r.SHP_LG_TYPE, '')) LIKE '%XPT%' 
            OR UPPER(COALESCE(r.SHP_LG_DESTINATION_FACILITY_ID, '')) LIKE '%XPT%'
            OR UPPER(COALESCE(p.ROUTE.ROUTE_TYPE, '')) LIKE '%XPT%'
            OR xpt.UR_VIRTUAL_XPT_ID IS NOT NULL
          THEN TRUE 
          ELSE FALSE 
      END AS is_xpt

    FROM `meli-bi-data.WHOWNER.BT_YMS_JOURNEY_PLANNER` AS jo
    CROSS JOIN UNNEST(jo.PURPOSES) AS p
    CROSS JOIN UNNEST(jo.VEHICLES) AS v

    LEFT JOIN `meli-bi-data.WHOWNER.LK_SHP_LG_ROUTES` r 
        ON SAFE_CAST(COALESCE(p.ROUTE.EXECUTED_ID, p.ROUTE.PLAN_ID) AS NUMERIC) = r.SHP_LG_ROUTE_ID

    LEFT JOIN `meli-bi-data.WHOWNER.LK_UR_CONFIG_XPT_VIRTUAL` xpt
        ON r.SHP_LG_DESTINATION_FACILITY_ID = xpt.UR_FACILITY_ID

    LEFT JOIN `meli-bi-data.WHOWNER.LK_PLACER_PLACES` plc
        ON COALESCE(r.SHP_LG_DESTINATION_FACILITY_ID, r.SHP_LG_ROUTE_NODE_ID_DESTINATION) = plc.PLACE_ID

    LEFT JOIN `meli-bi-data.WHOWNER.LK_MLB_PLACES_AGENCY_LIST` ag
        ON COALESCE(r.SHP_LG_DESTINATION_FACILITY_ID, r.SHP_LG_ROUTE_NODE_ID_DESTINATION) = ag.SHP_AGENCY_ID

    WHERE DATE(jo.STARTED_AT) = CURRENT_DATE()
      AND jo.NODE_ID = "{facility_id}"
      {heavy_clause}

    ORDER BY jo.STARTED_AT DESC
    """
    
    return client.query(query).to_dataframe()

try:
    with st.spinner("Atualizando indicadores YMS do SGO2..."):
        df_raw = load_yms_realtime_data(facility_selected, exclude_heavy)
        
    df = df_raw.copy()
    
    # 8. Metricas e Aderencia (YMS do Dia)
    if not df.empty:
        df["excedente_min"] = df["permanencia_minutos"].apply(lambda x: max(0, x - meta_permanencia_input))
        df["dentro_meta"] = df["permanencia_minutos"] <= meta_permanencia_input
        
        total_rotas_dia = len(df)
        total_dentro_meta = df["dentro_meta"].sum()
        total_fora_meta = total_rotas_dia - total_dentro_meta
        
        pct_aderencia_yms = (total_dentro_meta / total_rotas_dia * 100) if total_rotas_dia > 0 else 0
        tempo_medio_dia = round(df["permanencia_minutos"].mean(), 1)
        tempo_maximo_dia = df["permanencia_minutos"].max()
    else:
        total_rotas_dia = total_dentro_meta = total_fora_meta = 0
        pct_aderencia_yms = 0
        tempo_medio_dia = tempo_maximo_dia = 0

    # 9. Top KPI Cards Section
    k1, k2, k3, k4 = st.columns(4)
    
    # Status color for YMS Adherence
    if pct_aderencia_yms >= 90:
        badge_class = "badge-success"
        status_text = "🟢 EXCELENTE (>= 90%)"
        kpi_color = "#22c55e"
    elif pct_aderencia_yms >= 80:
        badge_class = "badge-warning"
        status_text = "🟡 ATENÇÃO (80% - 89%)"
        kpi_color = "#eab308"
    else:
        badge_class = "badge-danger"
        status_text = "🔴 CRÍTICO (< 80%)"
        kpi_color = "#ef4444"

    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">ADERÊNCIA YMS DO DIA (TODAS AS ROTAS)</div>
            <div class="kpi-value" style="color: {kpi_color};">{pct_aderencia_yms:.1f}%</div>
            <div class="kpi-subtext"><span class="badge {badge_class}">{status_text}</span></div>
        </div>
        """, unsafe_allow_html=True)
        
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">TOTAL VEÍCULOS / ROTAS HOJE</div>
            <div class="kpi-value">{total_rotas_dia}</div>
            <div class="kpi-subtext" style="color: {text_muted};">Pátio {facility_selected}</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">FORA DA META (> {meta_permanencia_input} MIN)</div>
            <div class="kpi-value" style="color: #ef4444;">{total_fora_meta}</div>
            <div class="kpi-subtext" style="color: #ef4444;">Veículos Ofensores de Tempo</div>
        </div>
        """, unsafe_allow_html=True)
        
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">PERMANÊNCIA MÉDIA VS MÁXIMA</div>
            <div class="kpi-value" style="color: #3b82f6;">{tempo_medio_dia} min</div>
            <div class="kpi-subtext" style="color: {text_muted};">Maior Estadia: <b style="color: #ef4444;">{tempo_maximo_dia} min</b></div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 10. Automated Insights Section (Recomendações Operacionais)
    if not df.empty and total_fora_meta > 0:
        df_offenders = df[df["dentro_meta"] == False]
        worst_vehicle_type = df_offenders["vehicle_type"].mode()[0] if not df_offenders.empty else "N/A"
        worst_vehicle_count = len(df_offenders[df_offenders["vehicle_type"] == worst_vehicle_type])
        
        # Peak Hour for Offenses
        df_offenders["checkin_hour"] = pd.to_datetime(df_offenders["checkin"]).dt.hour
        peak_hour = df_offenders["checkin_hour"].mode()[0] if not df_offenders.empty else None
        peak_str = f"{peak_hour:02d}:00 - {peak_hour+1:02d}:00" if peak_hour is not None else "N/A"

        st.markdown(f"""
        <div class="insight-card">
            <h4 style="margin:0 0 6px 0; color: #3b82f6; font-weight: 700; font-size: 1rem;">💡 Insights Operacionais Automatizados do Pátio</h4>
            <div style="display: flex; gap: 2rem; flex-wrap: wrap; font-size: 0.85rem; color: {text_color};">
                <div>🚨 <b>Principal Modelo Ofensor:</b> <span style="color:#ef4444; font-weight:bold;">{worst_vehicle_type}</span> ({worst_vehicle_count} estouros)</div>
                <div>⏱️ <b>Horário Crítico de Gargalo:</b> <span style="color:#eab308; font-weight:bold;">{peak_str}</span></div>
                <div>📍 <b>Meta Alvo:</b> Permanência máxima de <b>{meta_permanencia_input} minutos</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Apply Client-Side Filters
    if only_offenders:
        df = df[df["dentro_meta"] == False]
    if only_xpt:
        df = df[df["is_xpt"] == True]
    if search_plate:
        df = df[df["plate"].str.contains(search_plate, case=False, na=False)]

    # 11. Highlighted Section: Ranking de Carros Ofensores (Maior para Menor Tempo)
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='chart-title'>🔥 Ranking de Classificação de Estouro de Permanência (> {meta_permanencia_input} min)</div>", unsafe_allow_html=True)
    
    df_ranking = df[df["permanencia_minutos"] > meta_permanencia_input].sort_values(by="permanencia_minutos", ascending=False).copy()
    
    if not df_ranking.empty:
        df_ranking_display = df_ranking[[
            "permanencia_minutos", "excedente_min", "vehicle_type", "plate", 
            "route_id", "destination_name", "checkin", "checkout", "is_xpt"
        ]].copy()
        
        df_ranking_display.columns = [
            "Permanência Total (min)", "Tempo Excedido (+min)", "Classificação do Carro", "Placa", 
            "ID Rota", "Destino (Place / Agencia)", "Check-in", "Check-out", "É XPT?"
        ]
        
        st.dataframe(
            df_ranking_display,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success(f"🎉 Nenhum veículo excedeu a meta de {meta_permanencia_input} minutos com os filtros atuais!")
        
    st.markdown("</div>", unsafe_allow_html=True)

    # 12. Visual Charts (Aderência por Categoria e Evolução da Permanência)
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.markdown("<div class='chart-card'><div class='chart-title'>📊 Aderência YMS (<= 30 min) por Classificação do Veículo</div>", unsafe_allow_html=True)
        if not df_raw.empty:
            df_cat = df_raw.groupby("vehicle_type").agg(
                total=("JOURNEY_ID", "count"),
                aderentes=("permanencia_minutos", lambda x: (x <= meta_permanencia_input).sum())
            ).reset_index()
            df_cat["pct_aderencia"] = round((df_cat["aderentes"] / df_cat["total"]) * 100, 1)
            df_cat = df_cat.sort_values(by="pct_aderencia", ascending=True)
            
            fig_cat = px.bar(
                df_cat,
                x="pct_aderencia",
                y="vehicle_type",
                orientation="h",
                color="pct_aderencia",
                color_continuous_scale=["#ef4444", "#eab308", "#22c55e"],
                text="pct_aderencia"
            )
            fig_cat.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_muted, size=11),
                margin=dict(l=0, r=0, t=10, b=0),
                coloraxis_showscale=False,
                xaxis=dict(range=[0, 105], title="% Aderência à Meta (30 min)"),
                yaxis=dict(title="")
            )
            st.plotly_chart(fig_cat, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("<div class='chart-card'><div class='chart-title'>📈 Distribuição de Permanência dos Veículos (Minutos)</div>", unsafe_allow_html=True)
        if not df_raw.empty:
            fig_hist = px.histogram(
                df_raw,
                x="permanencia_minutos",
                nbins=20,
                color_discrete_sequence=["#3b82f6"]
            )
            fig_hist.add_vline(x=meta_permanencia_input, line_dash="dash", line_color="#ef4444", annotation_text=f"Meta: {meta_permanencia_input} min")
            fig_hist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=text_muted, size=11),
                margin=dict(l=0, r=0, t=10, b=0),
                xaxis=dict(title="Tempo de Permanência (min)"),
                yaxis=dict(title="Qtd Veículos")
            )
            st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # 13. Tabela Completa de Todas as Movimentações
    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
    st.markdown("<div class='chart-title'>📋 Tabela Geral de Movimentações (Todas as Rotas do Dia)</div>", unsafe_allow_html=True)
    
    if not df.empty:
        df_all = df[[
            "checkin", "checkout", "permanencia_minutos", "dentro_meta", 
            "vehicle_type", "plate", "route_id", "destination_name", "is_xpt", "JOURNEY_STATUS"
        ]].copy()
        
        df_all.columns = [
            "Check-in", "Check-out", "Permanência (min)", "Dentro Meta (<=30min)?", 
            "Classificação do Carro", "Placa", "ID Rota", "Destino (Place / Agencia)", "É XPT?", "Status Jornada"
        ]
        
        st.dataframe(df_all, use_container_width=True, hide_index=True)
        
        # Download Button
        csv_data = df_all.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar Todas as Rotas (CSV)",
            data=csv_data,
            file_name=f"YMS_SGO2_TodasRotas_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao consultar o BigQuery: {e}")
