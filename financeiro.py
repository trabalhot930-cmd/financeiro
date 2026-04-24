import streamlit as st
import pandas as pd
import json
from datetime import datetime

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

USERS = {
    "Juan": {"password": "Ju@n1990", "name": "Juan Carlos"},
    "Juan Carlos": {"password": "Ju@n1990", "name": "Juan Carlos"}
}

def check_password(username, password):
    if username in USERS:
        return USERS[username]["password"] == password
    return False

def login():
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center'>💰 Controle Financeiro</h1>")
        username = st.text_input("👤 Usuário")
        password = st.text_input("🔒 Senha", type="password")
        if st.button("🔓 Entrar", use_container_width=True):
            if check_password(username, password):
                st.session_state["authenticated"] = True
                st.session_state["user_name"] = USERS[username]["name"]
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos!")
        st.markdown('</div>', unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
    st.stop()

# ============================================
# DADOS EMBUTIDOS (FALLBACK)
# ============================================

# Dados de exemplo para 2026
DADOS_2026 = {
    'gastos': pd.DataFrame({
        'Categoria': ['Pensão', 'Aluguel', 'Energia', 'Cartão Itaú', 'Seguro', 
                      'Cartão Samsung', 'Cartão mercado pago', 'Gasolina', 'Outros',
                      'Estudos', 'Cartão Nubank', 'Cartão Lethicia'],
        'Janeiro': [1621, 450, 350, 580, 500, 460, 0, 400, 550, 360, 250, 500],
        'Fevereiro': [1621, 450, 535, 410, 0, 522, 490, 300, 450, 0, 258, 564],
        'Março': [1621, 450, 502, 410, 0, 680, 550, 300, 350, 0, 490, 550],
        'Abril': [1621, 450, 480, 410, 0, 80, 250, 200, 250, 260, 0, 0],
        'Maio': [1621, 450, 550, 0, 0, 880, 550, 300, 250, 260, 550, 210],
        'Junho': [1621, 450, 550, 0, 0, 280, 250, 300, 250, 260, 550, 210],
        'Julho': [1621, 450, 550, 0, 0, 280, 250, 300, 250, 260, 550, 210],
        'Agosto': [1621, 450, 550, 0, 0, 280, 250, 300, 250, 260, 550, 210],
        'Setembro': [1621, 450, 550, 0, 0, 280, 250, 300, 250, 260, 550, 210],
        'Outubro': [1621, 450, 550, 0, 0, 280, 250, 300, 250, 260, 550, 210],
        'Novembro': [1621, 450, 550, 0, 0, 280, 250, 300, 250, 260, 550, 210],
        'Dezembro': [1621, 450, 380, 0, 0, 280, 250, 300, 0, 260, 550, 210]
    }),
    'ganhos': pd.DataFrame({
        'Categoria': ['Salário', 'PL', 'Férias/13'],
        'Janeiro': [7330, 0, 0],
        'Fevereiro': [7330, 0, 0],
        'Março': [7330, 0, 0],
        'Abril': [7330, 0, 0],
        'Maio': [7330, 9100, 0],
        'Junho': [7330, 0, 0],
        'Julho': [7330, 0, 0],
        'Agosto': [7330, 0, 0],
        'Setembro': [7330, 0, 0],
        'Outubro': [7330, 0, 0],
        'Novembro': [7330, 0, 0],
        'Dezembro': [3380, 0, 13000]
    })
}

DADOS_2027 = {
    'gastos': pd.DataFrame({
        'Categoria': ['Pensão', 'Aluguel', 'Energia', 'Cartão Porto', 'Cartão Samsung',
                      'Cartão mercado pago', 'Gasolina', 'Outros', 'Estudos'],
        'Janeiro': [1700, 450, 600, 300, 150, 289, 500, 400, 600],
        'Fevereiro': [1700, 450, 600, 300, 150, 289, 500, 400, 600],
        'Março': [1700, 450, 600, 300, 150, 289, 500, 400, 600],
        'Abril': [1700, 450, 600, 300, 150, 289, 500, 400, 600],
        'Maio': [1700, 450, 600, 300, 150, 289, 500, 400, 600],
        'Junho': [1700, 450, 600, 300, 150, 289, 500, 400, 600],
        'Julho': [1700, 450, 600, 300, 150, 289, 500, 400, 600],
        'Agosto': [1700, 450, 600, 300, 150, 289, 500, 400, 600],
        'Setembro': [1700, 450, 600, 300, 150, 289, 500, 400, 600],
        'Outubro': [1700, 450, 600, 300, 150, 289, 500, 400, 600],
        'Novembro': [1700, 450, 600, 300, 150, 289, 500, 400, 600],
        'Dezembro': [1700, 450, 600, 300, 150, 289, 500, 400, 600]
    }),
    'ganhos': pd.DataFrame({
        'Categoria': ['Salário', 'PL', 'Férias/13'],
        'Janeiro': [6600, 8000, 0],
        'Fevereiro': [6600, 0, 0],
        'Março': [6600, 0, 0],
        'Abril': [6600, 10000, 0],
        'Maio': [8000, 0, 0],
        'Junho': [8000, 0, 0],
        'Julho': [8000, 0, 0],
        'Agosto': [8000, 0, 0],
        'Setembro': [8000, 0, 0],
        'Outubro': [8000, 0, 0],
        'Novembro': [8000, 0, 0],
        'Dezembro': [3300, 11000, 5000]
    })
}

# ============================================
# FUNÇÕES PARA CARREGAR DADOS DO EXCEL (TENTATIVA)
# ============================================
def carregar_do_excel():
    """Tenta carregar dados do Excel, se disponível"""
    try:
        import openpyxl
        arquivo = 'Pasta1.xlsx'
        if not os.path.exists(arquivo):
            return None
        
        dados = {}
        for ano in ['2026', '2027']:
            df_raw = pd.read_excel(arquivo, sheet_name=ano, header=None, engine='openpyxl')
            linha_gastos = df_raw[df_raw[0] == 'Gastos'].index[0] + 1
            linha_ganhos = df_raw[df_raw[0] == 'Ganhos'].index[0]
            meses = df_raw.iloc[linha_gastos - 1, 1:13].values.tolist()
            
            gastos = df_raw.iloc[linha_gastos:linha_ganhos, :12].copy()
            gastos.columns = ['Categoria'] + meses
            gastos = gastos.dropna(subset=['Categoria'])
            
            ganhos = df_raw.iloc[linha_ganhos + 1:linha_ganhos + 10, :12].copy()
            ganhos.columns = ['Categoria'] + meses
            ganhos = ganhos.dropna(subset=['Categoria'])
            
            dados[ano] = {'gastos': gastos, 'ganhos': ganhos, 'meses': meses}
        
        return dados
    except:
        return None

# ============================================
# FUNÇÕES DE ANÁLISE
# ============================================
def calcular_totais(df):
    """Calcula totais por mês"""
    meses = df.columns[1:]
    totais = []
    for mes in meses:
        total = df[mes].sum()
        totais.append(total if pd.notna(total) else 0)
    return totais

def preparar_dados_long(df):
    """Prepara dados para gráficos"""
    dados_long = []
    meses = df.columns[1:]
    for _, row in df.iterrows():
        categoria = row['Categoria']
        for mes in meses:
            valor = row[mes]
            if pd.notna(valor) and valor != 0:
                dados_long.append({'Categoria': categoria, 'Mês': mes, 'Valor': float(valor)})
    return pd.DataFrame(dados_long)

def top_gastos(df, n=10):
    """Retorna top N gastos"""
    dados_long = preparar_dados_long(df)
    if dados_long.empty:
        return pd.Series()
    return dados_long.groupby('Categoria')['Valor'].sum().sort_values(ascending=False).head(n)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown(f"""
    <div style='text-align: center; padding: 20px;'>
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 50%; width: 80px; height: 80px; 
                    margin: 0 auto; display: flex; align-items: center; 
                    justify-content: center; font-size: 40px;'>
            👤
        </div>
        <h3>{st.session_state.get('user_name', 'Usuário')}</h3>
        <p style='color: green;'>✅ Logado</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()
    
    st.markdown("---")
    
    ano_selecionado = st.selectbox("📅 Selecione o ano", ['2026', '2027'])
    tipo_visao = st.radio("📊 Tipo de visão", ['Visão Geral', 'Detalhado'])

# ============================================
# SELECIONAR DADOS
# ============================================
# Tentar carregar do Excel, se não conseguir usar dados embutidos
dados_excel = carregar_do_excel()

if dados_excel and ano_selecionado in dados_excel:
    dados_ano = dados_excel[ano_selecionado]
    df_gastos = dados_ano['gastos']
    df_ganhos = dados_ano['ganhos']
    meses = dados_ano['meses']
    st.info("📁 Dados carregados do arquivo Excel")
else:
    if ano_selecionado == '2026':
        df_gastos = DADOS_2026['gastos']
        df_ganhos = DADOS_2026['ganhos']
    else:
        df_gastos = DADOS_2027['gastos']
        df_ganhos = DADOS_2027['ganhos']
    meses = df_gastos.columns[1:].tolist()
    st.info("📊 Usando dados de demonstração (arquivo Excel não encontrado)")

# Calcular totais
totais_gastos = calcular_totais(df_gastos)
totais_ganhos = calcular_totais(df_ganhos)
saldo_mensal = [g - h for g, h in zip(totais_ganhos, totais_gastos)]

total_ano_gastos = sum(totais_gastos)
total_ano_ganhos = sum(totais_ganhos)
saldo_anual = total_ano_ganhos - total_ano_gastos

# ============================================
# MAIN APP
# ============================================
st.balloons()
st.markdown(f"""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 20px; border-radius: 10px; margin-bottom: 20px; color: white;'>
    <h2>Olá, {st.session_state.get('user_name', 'Usuário')}! 👋</h2>
    <p>Bem-vindo ao seu controle financeiro</p>
</div>
""", unsafe_allow_html=True)

st.title("💰 Controle Financeiro Inteligente")
st.markdown(f"### 📅 Análise para {ano_selecionado}")

# Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("💰 Total de Ganhos", f"R$ {total_ano_ganhos:,.2f}")
with col2:
    st.metric("💸 Total de Gastos", f"R$ {total_ano_gastos:,.2f}")
with col3:
    st.metric("📊 Saldo Anual", f"R$ {saldo_anual:,.2f}", 
              delta="Positivo" if saldo_anual > 0 else "Negativo")
with col4:
    st.metric("📅 Média Mensal", f"R$ {total_ano_gastos/12:,.2f}")

st.divider()

# ============================================
# VISÃO GERAL (COM GRÁFICOS NATIVOS)
# ============================================
if tipo_visao == 'Visão Geral':
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Evolução Mensal")
        
        df_plot = pd.DataFrame({
            'Mês': meses,
            'Gastos': totais_gastos,
            'Ganhos': totais_ganhos
        })
        
        st.line_chart(df_plot.set_index('Mês'), use_container_width=True)
        
        st.subheader("💰 Saldo Mensal")
        df_saldo = pd.DataFrame({'Mês': meses, 'Saldo': saldo_mensal})
        st.bar_chart(df_saldo.set_index('Mês'), use_container_width=True)
    
    with col2:
        st.subheader("🎯 Top 10 Gastos")
        top = top_gastos(df_gastos)
        if not top.empty:
            st.dataframe(pd.DataFrame({
                'Categoria': top.index,
                'Total (R$)': [f"R$ {v:,.2f}" for v in top.values]
            }), use_container_width=True)
        else:
            st.info("Nenhum gasto registrado")
    
    st.divider()
    
    st.subheader("🥧 Distribuição por Categoria")
    
    dados_long = preparar_dados_long(df_gastos)
    if not dados_long.empty:
        gastos_cat = dados_long.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
        
        # Criar um gráfico de barras horizontal simples
        st.bar_chart(pd.DataFrame(gastos_cat.head(10)), use_container_width=True)
        
        # Mostrar porcentagens
        st.subheader("📊 Percentual por Categoria")
        total = gastos_cat.sum()
        for cat, valor in gastos_cat.head(8).items():
            percent = (valor / total) * 100
            st.progress(percent / 100, text=f"{cat}: R$ {valor:,.2f} ({percent:.1f}%)")

# ============================================
# VISÃO DETALHADA
# ============================================
else:
    st.subheader("📋 Análise Detalhada")
    
    # Filtro
    categorias = df_gastos['Categoria'].tolist()
    cats_selecionadas = st.multiselect("Filtrar categorias", categorias, default=categorias[:3] if len(categorias) > 3 else categorias)
    
    if cats_selecionadas:
        df_filtrado = df_gastos[df_gastos['Categoria'].isin(cats_selecionadas)]
        
        st.subheader("📊 Comparativo Mensal")
        # Transpor para melhor visualização
        df_plot = df_filtrado.set_index('Categoria').T
        st.area_chart(df_plot, use_container_width=True)
    
    st.subheader("📑 Tabela Completa de Gastos")
    
    # Formatar para exibição
    df_display = df_gastos.copy()
    for mes in meses:
        df_display[mes] = df_display[mes].apply(lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "-")
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    st.subheader("💰 Tabela de Ganhos")
    df_ganhos_display = df_ganhos.copy()
    for mes in meses:
        df_ganhos_display[mes] = df_ganhos_display[mes].apply(lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "-")
    st.dataframe(df_ganhos_display, use_container_width=True, hide_index=True)

# ============================================
# INSIGHTS
# ============================================
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Insights")

# Maior gasto
dados_long = preparar_dados_long(df_gastos)
if not dados_long.empty:
    maior = dados_long.loc[dados_long['Valor'].idxmax()]
    st.sidebar.info(f"🔥 Maior gasto único:\n{maior['Categoria']} em {maior['Mês']}\nR$ {maior['Valor']:,.2f}")

# Categoria que mais gasta
top_cat = top_gastos(df_gastos, 1)
if not top_cat.empty:
    st.sidebar.warning(f"💰 Categoria que mais gasta:\n{top_cat.index[0]}\nR$ {top_cat.values[0]:,.2f}")

if saldo_anual < 0:
    st.sidebar.error("⚠️ ALERTA: Saldo anual negativo!")
elif saldo_anual > 0:
    st.sidebar.success(f"✅ Saldo positivo de R$ {saldo_anual:,.2f}")

st.sidebar.markdown("---")
st.sidebar.caption("💰 Controle Financeiro Pessoal")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'><p>Desenvolvido com ❤️ para Juan</p></div>", unsafe_allow_html=True)
