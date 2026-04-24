import streamlit as st
import pandas as pd

# Tentar importar plotly com tratamento de erro
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

import hashlib
import sys
import os

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Controle Financeiro Juan",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# SISTEMA DE AUTENTICAÇÃO
# ============================================

# Configuração de usuários
USERS = {
    "Juan": {
        "password": "Ju@n1990",
        "name": "Juan Carlos",
        "role": "admin"
    }
}

def check_password(username, password):
    """Verifica credenciais"""
    if username in USERS:
        return USERS[username]["password"] == password
    return False

def login():
    """Interface de login"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        color: white;
    }
    .login-container h1 {
        text-align: center;
        margin-bottom: 30px;
        font-size: 2em;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("<h1>💰 Controle Financeiro</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center'>Bem-vindo! Faça login</h3>", unsafe_allow_html=True)
        st.markdown("---", unsafe_allow_html=True)
        
        username = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
        password = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
        
        if st.button("🔓 Entrar", use_container_width=True):
            if check_password(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["user_name"] = USERS[username]["name"]
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos!")
        
        st.markdown("---")
        st.markdown("<p style='text-align: center; font-size: 12px'>Desenvolvido para controle financeiro pessoal</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def logout():
    """Logout do sistema"""
    if st.sidebar.button("🚪 Sair do Sistema"):
        for key in ["authenticated", "username", "user_name"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Verificar autenticação
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Se não estiver autenticado, mostrar login
if not st.session_state["authenticated"]:
    login()
    st.stop()

# ============================================
# SIDEBAR - USUÁRIO LOGADO
# ============================================
with st.sidebar:
    st.markdown(f"""
    <div style='text-align: center; padding: 10px;'>
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 50%; width: 80px; height: 80px; 
                    margin: 0 auto; display: flex; align-items: center; 
                    justify-content: center; font-size: 40px;'>
            👤
        </div>
        <h3 style='margin-top: 10px;'>{st.session_state.get('user_name', 'Usuário')}</h3>
        <p style='color: green;'>✅ Logado</p>
        <hr>
    </div>
    """, unsafe_allow_html=True)
    
    logout()

# ============================================
# FUNÇÃO PARA CARREGAR DADOS (SEM CACHE)
# ============================================
def carregar_dados_do_arquivo(arquivo):
    """Carrega os dados do Excel (sem cache)"""
    try:
        dfs = {}
        
        for ano in ['2026', '2027']:
            try:
                if isinstance(arquivo, str):
                    df_raw = pd.read_excel(arquivo, sheet_name=ano, header=None)
                else:
                    df_raw = pd.read_excel(arquivo, sheet_name=ano, header=None)
                
                linha_gastos = df_raw[df_raw[0] == 'Gastos'].index[0] + 1
                linha_ganhos = df_raw[df_raw[0] == 'Ganhos'].index[0]
                linha_contas_pagas = df_raw[df_raw[0] == 'Contas Pagas'].index[0]
                linha_total_gastos = df_raw[df_raw[0] == 'Total'].index[0]
                linha_total_ganhos = df_raw[df_raw[0] == 'Total'].index[1]
                
                meses = df_raw.iloc[linha_gastos - 1, 1:13].values.tolist()
                
                gastos = df_raw.iloc[linha_gastos:linha_ganhos, :12].copy()
                gastos.columns = ['Categoria'] + meses
                gastos = gastos.dropna(subset=['Categoria'])
                
                ganhos = df_raw.iloc[linha_ganhos + 1:linha_contas_pagas, :12].copy()
                ganhos.columns = ['Categoria'] + meses
                ganhos = ganhos.dropna(subset=['Categoria'])
                
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
                st.error(f"Erro ao carregar {ano}: {str(e)}")
                dfs[ano] = None
        
        return dfs
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

# ============================================
# FUNÇÕES DE ANÁLISE (COM CACHE APENAS PARA PROCESSAMENTO)
# ============================================
@st.cache_data
def preparar_dados_gastos_cached(df):
    """Converte dados de gastos para formato longo (com cache)"""
    dados_long = []
    meses = df.columns[1:]
    
    for _, row in df.iterrows():
        categoria = row['Categoria']
        for mes in meses:
            valor = row[mes]
            if pd.notna(valor) and valor != 0:
                dados_long.append({
                    'Categoria': categoria,
                    'Mês': mes,
                    'Valor': float(valor)
                })
    return pd.DataFrame(dados_long)

@st.cache_data
def top_gastos_cached(df_gastos, top_n=10):
    """Retorna os maiores gastos do ano (com cache)"""
    dados = preparar_dados_gastos_cached(df_gastos)
    totais = dados.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
    return totais.head(top_n)

def preparar_dados_gastos(df):
    """Converte dados de gastos para formato longo"""
    return preparar_dados_gastos_cached(df)

def top_gastos(df_gastos, top_n=10):
    """Retorna os maiores gastos do ano"""
    return top_gastos_cached(df_gastos, top_n)

def gastos_por_mes(df_gastos):
    """Retorna gastos agregados por mês"""
    dados = preparar_dados_gastos_cached(df_gastos)
    return dados.groupby('Mês')['Valor'].sum().reset_index()

# ============================================
# UPLOAD DO ARQUIVO
# ============================================

# Verificar se o arquivo já existe
arquivo_existe = os.path.exists('Pasta1.xlsx')

if not arquivo_existe:
    st.warning("📁 Arquivo Pasta1.xlsx não encontrado! Faça o upload:")
    uploaded_file = st.file_uploader("Escolha o arquivo Excel", type=['xlsx'])
    
    if uploaded_file is not None:
        # Salvar o arquivo carregado
        with open('Pasta1.xlsx', 'wb') as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ Arquivo carregado com sucesso!")
        st.rerun()
    else:
        st.stop()
else:
    # Arquivo existe, carregar dados
    dados = carregar_dados_do_arquivo('Pasta1.xlsx')
    
    if dados is None:
        st.error("Erro ao carregar dados. Verifique o arquivo Pasta1.xlsx")
        st.stop()

# ============================================
# MAIN APP
# ============================================

# Boas-vindas
st.balloons()
st.markdown(f"""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 20px; border-radius: 10px; margin-bottom: 20px; color: white;'>
    <h2 style='margin: 0;'>Olá, {st.session_state.get('user_name', 'Usuário')}! 👋</h2>
    <p style='margin: 5px 0 0 0;'>Bem-vindo ao seu controle financeiro</p>
</div>
""", unsafe_allow_html=True)

# Filtros no sidebar
with st.sidebar:
    st.markdown("---")
    st.subheader("🎛️ Filtros")
    
    ano_selecionado = st.selectbox(
        "Selecione o ano",
        options=['2026', '2027'],
        index=0
    )
    
    tipo_visao = st.radio(
        "Tipo de visão",
        options=['Visão Geral', 'Detalhado', 'Comparativo Mensal'],
        index=0
    )

dados_ano = dados[ano_selecionado]

if dados_ano is None:
    st.error(f"Dados não disponíveis para {ano_selecionado}")
    st.stop()

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
media_mensal = total_gastos / 12 if total_gastos > 0 else 0

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

# Verificar se plotly está disponível
if not PLOTLY_AVAILABLE:
    st.warning("⚠️ Plotly não está instalado. Execute: pip install plotly")
    st.subheader("📊 Dados de Gastos")
    st.dataframe(df_gastos, use_container_width=True)
    st.subheader("💰 Dados de Ganhos")
    st.dataframe(df_ganhos, use_container_width=True)
    st.stop()

# ============================================
# VISÃO GERAL
# ============================================
if tipo_visao == 'Visão Geral':
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📊 Evolução Mensal")
        
        df_temporal = pd.DataFrame({
            'Mês': meses,
            'Gastos': [float(x) if pd.notna(x) else 0 for x in dados_ano['total_gastos_ano']],
            'Ganhos': [float(x) if pd.notna(x) else 0 for x in dados_ano['total_ganhos_ano']],
            'Saldo': [float(x) if pd.notna(x) else 0 for x in dados_ano['saldo'].values()]
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
        top = top_gastos(df_gastos)
        
        fig = px.bar(
            x=top.values, y=top.index, orientation='h',
            title="Maiores despesas do ano",
            labels={'x': 'Valor (R$)', 'y': 'Categoria'},
            color=top.values, color_continuous_scale='Reds'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.subheader("🥧 Distribuição de Gastos por Categoria")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dados_gastos_long = preparar_dados_gastos(df_gastos)
        if not dados_gastos_long.empty:
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
        if not dados_gastos_long.empty:
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
    
    categorias = df_gastos['Categoria'].unique().tolist()
    categorias_selecionadas = st.multiselect(
        "Filtrar por categorias",
        options=categorias,
        default=categorias[:3] if len(categorias) > 3 else categorias
    )
    
    if categorias_selecionadas:
        df_filtrado = df_gastos[df_gastos['Categoria'].isin(categorias_selecionadas)]
        
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
        
        st.subheader("📊 Comparativo Mensal por Categoria")
        
        df_barras = df_filtrado.melt(id_vars=['Categoria'], var_name='Mês', value_name='Valor')
        df_barras = df_barras.dropna(subset=['Valor'])
        
        if not df_barras.empty:
            fig = px.bar(
                df_barras, x='Mês', y='Valor', color='Categoria',
                title="Gastos por categoria ao longo dos meses",
                barmode='stack',
                text_auto='.0f'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📑 Tabela Completa de Gastos")
    st.dataframe(df_gastos, use_container_width=True)

# ============================================
# COMPARATIVO MENSAL
# ============================================
else:
    st.subheader("📈 Comparativo Mensal Detalhado")
    
    meses_selecionados = st.multiselect(
        "Selecione os meses para comparar",
        options=meses,
        default=meses[:2] if len(meses) >= 2 else meses
    )
    
    if meses_selecionados:
        dados_comparacao = preparar_dados_gastos(df_gastos)
        dados_comparacao = dados_comparacao[dados_comparacao['Mês'].isin(meses_selecionados)]
        
        if not dados_comparacao.empty:
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

# ============================================
# SIDEBAR INSIGHTS
# ============================================
with st.sidebar:
    st.markdown("---")
    st.subheader("📌 Insights Rápidos")
    
    gastos_mensais = gastos_por_mes(df_gastos)
    if not gastos_mensais.empty:
        maior_gasto_mes = gastos_mensais.loc[gastos_mensais['Valor'].idxmax()]
        st.info(f"🔥 **Mês de maior gasto:**\n{maior_gasto_mes['Mês']}\nR$ {maior_gasto_mes['Valor']:,.2f}")
    
    top_categorias = top_gastos(df_gastos, 3)
    if not top_categorias.empty:
        st.warning(f"💰 **Top 3 categorias:**\n\n1. {top_categorias.index[0]}: R$ {top_categorias.values[0]:,.2f}\n\n2. {top_categorias.index[1]}: R$ {top_categorias.values[1]:,.2f}\n\n3. {top_categorias.index[2]}: R$ {top_categorias.values[2]:,.2f}")
    
    if saldo_total < 0:
        st.error("⚠️ **ALERTA:** Saldo anual negativo! Revise seus gastos.")
    elif saldo_total > 0:
        st.success(f"✅ **Bom trabalho!** Saldo positivo de R$ {saldo_total:,.2f}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>💰 Controle Financeiro Pessoal | Desenvolvido com ❤️ para Juan</p>
</div>
""", unsafe_allow_html=True)
