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
    st.warning("⚠️ Plotly não está instalado. Instale com: pip install plotly")

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
# CARREGAR DADOS
# ============================================
@st.cache_data
def carregar_dados():
    """Carrega os dados do Excel"""
    try:
        # Tentar diferentes caminhos para o arquivo
        possiveis_caminhos = ['Pasta1.xlsx', 'data/Pasta1.xlsx', '../Pasta1.xlsx']
        arquivo = None
        
        for caminho in possiveis_caminhos:
            if os.path.exists(caminho):
                arquivo = caminho
                break
        
        if arquivo is None:
            st.error("❌ Arquivo Pasta1.xlsx não encontrado!")
            st.info("📁 Por favor, faça upload do arquivo Pasta1.xlsx usando o botão abaixo:")
            
            uploaded_file = st.file_uploader("Escolha o arquivo Excel", type=['xlsx'])
            if uploaded_file is not None:
                arquivo = uploaded_file
            else:
                return None
        
        dfs = {}
        
        for ano in ['2026', '2027']:
            try:
                if isinstance(arquivo, str):
                    df_raw = pd.read_excel(arquivo, sheet_name=ano, header=None)
                else:
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
                st.error(f"Erro ao carregar {ano}: {str(e)}")
                dfs[ano] = None
        
        return dfs
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return None

# ============================================
# FUNÇÕES DE ANÁLISE (SEM PLOTLY)
# ============================================
def preparar_dados_gastos(df):
    """Converte dados de gastos para formato longo"""
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

def top_gastos(df_gastos, top_n=10):
    """Retorna os maiores gastos do ano"""
    dados = preparar_dados_gastos(df_gastos)
    totais = dados.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
    return totais.head(top_n)

def gastos_por_mes(df_gastos):
    """Retorna gastos agregados por mês"""
    dados = preparar_dados_gastos(df_gastos)
    return dados.groupby('Mês')['Valor'].sum().reset_index()

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

# Carregar dados
dados = carregar_dados()

if dados is None or dados[ano_selecionado] is None:
    st.error("Erro ao carregar dados. Verifique o arquivo Pasta1.xlsx")
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
    st.warning("""
    ⚠️ **Plotly não está instalado!** 
    
    Para instalar, execute:
    ```bash
    pip install plotly
