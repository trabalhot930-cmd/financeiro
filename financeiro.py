import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Controle Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CARREGAR DADOS
# ============================================
@st.cache_data
def carregar_dados():
    arquivo = 'Pasta1.xlsx'
    dfs = {}
    
    for ano in ['2026', '2027']:
        try:
            df_raw = pd.read_excel(arquivo, sheet_name=ano, header=None)
            
            # Encontrar linhas importantes
            linha_gastos = df_raw[df_raw[0] == 'Gastos'].index[0] + 1
            linha_ganhos = df_raw[df_raw[0] == 'Ganhos'].index[0]
            linha_contas_pagas = df_raw[df_raw[0] == 'Contas Pagas'].index[0]
            linha_total_gastos = df_raw[df_raw[0] == 'Total'].index[0]
            linha_total_ganhos = df_raw[df_raw[0] == 'Total'].index[1]
            
            # Meses
            meses = df_raw.iloc[linha_gastos - 1, 1:13].values.tolist()
            
            # Extrair gastos
            gastos = df_raw.iloc[linha_gastos:linha_ganhos, :12].copy()
            gastos.columns = ['Categoria'] + meses
            gastos = gastos.dropna(subset=['Categoria'])
            
            # Extrair ganhos
            ganhos = df_raw.iloc[linha_ganhos + 1:linha_contas_pagas, :12].copy()
            ganhos.columns = ['Categoria'] + meses
            ganhos = ganhos.dropna(subset=['Categoria'])
            
            # Saldo mensal
            saldo = df_raw.iloc[linha_contas_pagas:linha_contas_pagas + 1, 1:13].values[0]
            
            dfs[ano] = {
                'gastos': gastos,
                'ganhos': ganhos,
                'saldo': dict(zip(meses, saldo)),
                'total_gastos_ano': df_raw.iloc[linha_total_gastos, 1:13].values,
                'total_ganhos_ano': df_raw.iloc[linha_total_ganhos, 1:13].values,
                'meses': meses
            }
            
        except Exception as e:
            st.error(f"Erro ao carregar {ano}: {e}")
            dfs[ano] = None
    
    return dfs

# ============================================
# FUNÇÕES DE ANÁLISE
# ============================================
def preparar_dados_gastos(df):
    """Converte dados de gastos para formato longo"""
    dados_long = []
    for _, row in df.iterrows():
        categoria = row['Categoria']
        for mes in df.columns[1:]:
            valor = row[mes]
            if pd.notna(valor) and valor != 0:
                dados_long.append({
                    'Categoria': categoria,
                    'Mês': mes,
                    'Valor': float(valor)
                })
    return pd.DataFrame(dados_long)

def top_gastos(df_gastos, ano, top_n=10):
    """Retorna os maiores gastos do ano"""
    dados = preparar_dados_gastos(df_gastos)
    totais = dados.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
    return totais.head(top_n)

def gastos_por_mes(df_gastos):
    """Retorna gastos agregados por mês"""
    dados = preparar_dados_gastos(df_gastos)
    return dados.groupby('Mês')['Valor'].sum().reset_index()

# ============================================
# SIDEBAR - FILTROS
# ============================================
st.sidebar.title("🎛️ Filtros")

ano_selecionado = st.sidebar.selectbox(
    "Selecione o ano",
    options=['2026', '2027'],
    index=0
)

tipo_visao = st.sidebar.radio(
    "Tipo de visão",
    options=['Visão Geral', 'Detalhado', 'Comparativo Mensal'],
    index=0
)

# Carregar dados
dados = carregar_dados()

if dados[ano_selecionado] is None:
    st.error(f"Dados não disponíveis para {ano_selecionado}")
    st.stop()

dados_ano = dados[ano_selecionado]
df_gastos = dados_ano['gastos']
df_ganhos = dados_ano['ganhos']
meses = dados_ano['meses']

# ============================================
# HEADER PRINCIPAL
# ============================================
st.title("💰 Controle Financeiro Inteligente")
st.markdown(f"### 📅 Análise para {ano_selecionado}")

# Cards de resumo
col1, col2, col3, col4 = st.columns(4)

total_gastos = sum([v for v in dados_ano['total_gastos_ano'] if pd.notna(v)])
total_ganhos = sum([v for v in dados_ano['total_ganhos_ano'] if pd.notna(v)])
saldo_total = total_ganhos - total_gastos
media_mensal = total_gastos / 12

with col1:
    st.metric("💰 Total de Ganhos", f"R$ {total_ganhos:,.2f}")
with col2:
    st.metric("💸 Total de Gastos", f"R$ {total_gastos:,.2f}")
with col3:
    st.metric("📊 Saldo Anual", f"R$ {saldo_total:,.2f}", 
              delta="Positivo" if saldo_total > 0 else "Negativo")
with col4:
    st.metric("📅 Média Mensal", f"R$ {media_mensal:,.2f}")

st.divider()

# ============================================
# VISÃO GERAL
# ============================================
if tipo_visao == 'Visão Geral':
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📊 Evolução Mensal")
        
        # Criar dataframe para linha temporal
        df_temporal = pd.DataFrame({
            'Mês': meses,
            'Gastos': dados_ano['total_gastos_ano'],
            'Ganhos': dados_ano['total_ganhos_ano'],
            'Saldo': dados_ano['saldo'].values()
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_temporal['Mês'], y=df_temporal['Gastos'],
                                 name='Gastos', line=dict(color='red', width=3),
                                 fill='tozeroy', fillcolor='rgba(255,0,0,0.1)'))
        fig.add_trace(go.Scatter(x=df_temporal['Mês'], y=df_temporal['Ganhos'],
                                 name='Ganhos', line=dict(color='green', width=3)))
        fig.add_trace(go.Bar(x=df_temporal['Mês'], y=df_temporal['Saldo'],
                             name='Saldo', marker_color='lightblue', opacity=0.7))
        
        fig.update_layout(
            title="Gastos vs Ganhos vs Saldo",
            xaxis_title="Mês",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Top 10 Gastos Anuais")
        top = top_gastos(df_gastos, ano_selecionado)
        
        fig = px.bar(
            x=top.values, y=top.index, orientation='h',
            title="Maiores despesas do ano",
            labels={'x': 'Valor (R$)', 'y': 'Categoria'},
            color=top.values, color_continuous_scale='Reds'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Gráfico de pizza - Distribuição de gastos por categoria
    st.subheader("🥧 Distribuição de Gastos por Categoria")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dados_gastos_long = preparar_dados_gastos(df_gastos)
        gastos_categoria = dados_gastos_long.groupby('Categoria')['Valor'].sum().reset_index()
        gastos_categoria = gastos_categoria.sort_values('Valor', ascending=False).head(8)
        
        fig = px.pie(
            gastos_categoria, values='Valor', names='Categoria',
            title="Top 8 categorias - % do total",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de treemap
        fig = px.treemap(
            gastos_categoria, path=['Categoria'], values='Valor',
            title="Treemap - Hierarquia de gastos",
            color='Valor', color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# VISÃO DETALHADA
# ============================================
elif tipo_visao == 'Detalhado':
    st.subheader("📋 Análise Detalhada de Gastos")
    
    # Filtro por categoria
    categorias = df_gastos['Categoria'].unique().tolist()
    categorias_selecionadas = st.multiselect(
        "Filtrar por categorias",
        options=categorias,
        default=categorias[:3] if len(categorias) > 3 else categorias
    )
    
    if categorias_selecionadas:
        df_filtrado = df_gastos[df_gastos['Categoria'].isin(categorias_selecionadas)]
        
        # Gráfico de calor
        st.subheader("🔥 Mapa de Calor - Gastos Mensais por Categoria")
        
        matriz_calor = df_filtrado.set_index('Categoria')[meses]
        matriz_calor = matriz_calor.fillna(0)
        
        fig = px.imshow(
            matriz_calor,
            labels=dict(x="Mês", y="Categoria", color="Valor (R$)"),
            title="Intensidade de gastos ao longo do ano",
            color_continuous_scale='RdYlGn_r',
            aspect="auto",
            text_auto='.0f'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de barras empilhadas
        st.subheader("📊 Comparativo Mensal por Categoria")
        
        df_barras = df_filtrado.melt(id_vars=['Categoria'], var_name='Mês', value_name='Valor')
        df_barras = df_barras.dropna(subset=['Valor'])
        
        fig = px.bar(
            df_barras, x='Mês', y='Valor', color='Categoria',
            title="Gastos por categoria ao longo dos meses",
            barmode='stack',
            text_auto='.0f'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.subheader("📑 Tabela Completa de Gastos")
    st.dataframe(
        df_gastos.style.highlight_max(axis=1, color='lightcoral')
                               .format('R$ {:,.2f}', subset=meses),
        use_container_width=True,
        height=400
    )

# ============================================
# COMPARATIVO MENSAL
# ============================================
else:
    st.subheader("📈 Comparativo Mensal Detalhado")
    
    meses_selecionados = st.multiselect(
        "Selecione os meses para comparar",
        options=meses,
        default=meses[:2]
    )
    
    if meses_selecionados:
        # Preparar dados para comparação
        dados_comparacao = preparar_dados_gastos(df_gastos)
        dados_comparacao = dados_comparacao[dados_comparacao['Mês'].isin(meses_selecionados)]
        
        # Gráfico de radar
        fig = go.Figure()
        
        for mes in meses_selecionados:
            dados_mes = dados_comparacao[dados_comparacao['Mês'] == mes]
            totais_cat = dados_mes.groupby('Categoria')['Valor'].sum().reset_index()
            
            fig.add_trace(go.Bar(
                x=totais_cat['Categoria'],
                y=totais_cat['Valor'],
                name=mes
            ))
        
        fig.update_layout(
            title="Comparativo de gastos por categoria",
            xaxis_title="Categoria",
            yaxis_title="Valor (R$)",
            barmode='group',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de linha comparativo
        st.subheader("📉 Evolução comparativa")
        
        dados_linha = dados_comparacao.groupby(['Mês', 'Categoria'])['Valor'].sum().reset_index()
        
        fig = px.line(
            dados_linha, x='Mês', y='Valor', color='Categoria',
            title="Evolução dos gastos por categoria",
            markers=True
        )
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# ANÁLISES ESPECÍFICAS NO SIDEBAR
# ============================================
st.sidebar.divider()
st.sidebar.subheader("📌 Insights Rápidos")

# Maior gasto do mês
gastos_mensais = gastos_por_mes(df_gastos)
if not gastos_mensais.empty:
    maior_gasto_mes = gastos_mensais.loc[gastos_mensais['Valor'].idxmax()]
    st.sidebar.info(f"🔥 **Mês de maior gasto:**\n{maior_gasto_mes['Mês']} - R$ {maior_gasto_mes['Valor']:,.2f}")

# Categoria que mais gasta
top_categorias = top_gastos(df_gastos, ano_selecionado, 3)
if not top_categorias.empty:
    st.sidebar.warning(f"💰 **Top 3 categorias:**\n1. {top_categorias.index[0]}: R$ {top_categorias.values[0]:,.2f}\n2. {top_categorias.index[1]}: R$ {top_categorias.values[1]:,.2f}\n3. {top_categorias.index[2]}: R$ {top_categorias.values[2]:,.2f}")

# Alertas
if saldo_total < 0:
    st.sidebar.error("⚠️ **ALERTA:** Saldo anual negativo! Revise seus gastos.")
elif media_mensal > total_ganhos / 12 * 0.8:
    st.sidebar.warning("⚠️ **Cuidado:** Você está gastando mais de 80% da sua renda média mensal.")

# Download dos dados
st.sidebar.divider()
if st.sidebar.button("📥 Exportar dados (CSV)"):
    dados_export = preparar_dados_gastos(df_gastos)
    csv = dados_export.to_csv(index=False)
    st.sidebar.download_button(
        label="Baixar CSV",
        data=csv,
        file_name=f"gastos_{ano_selecionado}.csv",
        mime="text/csv"
    )

st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido para controle financeiro pessoal")
