import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib
import hmac

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

# Configuração de usuários (em produção, use banco de dados)
USERS = {
    "Juan": {
        "password": "Ju@n1990",
        "name": "Juan Carlos",
        "role": "admin"
    }
}

def hash_password(password):
    """Cria hash da senha"""
    return hashlib.sha256(password.encode()).hexdigest()

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
                st.error(f"Erro ao carregar {ano}: {str(e)}")
                dfs[ano] = None
        
        return dfs
    
    except FileNotFoundError:
        st.error("❌ Arquivo Pasta1.xlsx não encontrado! Verifique se o arquivo está na mesma pasta.")
        return None
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return None

# ============================================
# FUNÇÕES DE ANÁLISE
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
    delta_color = "normal" if saldo_total > 0 else "inverse"
    st.metric("📊 Saldo Anual", f"R$ {saldo_total:,.2f}", 
              delta="Positivo" if saldo_total > 0 else "Negativo",
              delta_color="normal")
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
    
    # Gráfico de pizza - Distribuição de gastos por categoria
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
        
        if not df_barras.empty:
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
    
    # Formatar valores para exibição
    df_display = df_gastos.copy()
    for mes in meses:
        df_display[mes] = df_display[mes].apply(lambda x: f'R$ {x:,.2f}' if pd.notna(x) else '-')
    
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        hide_index=True
    )

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
        # Preparar dados para comparação
        dados_comparacao = preparar_dados_gastos(df_gastos)
        dados_comparacao = dados_comparacao[dados_comparacao['Mês'].isin(meses_selecionados)]
        
        if not dados_comparacao.empty:
            # Gráfico de barras agrupadas
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
        else:
            st.warning("Nenhum dado encontrado para os meses selecionados")

# ============================================
# ANÁLISES ESPECÍFICAS NO SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("---")
    st.subheader("📌 Insights Rápidos")
    
    # Maior gasto do mês
    gastos_mensais = gastos_por_mes(df_gastos)
    if not gastos_mensais.empty:
        maior_gasto_mes = gastos_mensais.loc[gastos_mensais['Valor'].idxmax()]
        st.info(f"🔥 **Mês de maior gasto:**\n{maior_gasto_mes['Mês']}\nR$ {maior_gasto_mes['Valor']:,.2f}")
    
    # Categoria que mais gasta
    top_categorias = top_gastos(df_gastos, 3)
    if not top_categorias.empty:
        st.warning(f"💰 **Top 3 categorias:**\n\n1. {top_categorias.index[0]}: R$ {top_categorias.values[0]:,.2f}\n\n2. {top_categorias.index[1]}: R$ {top_categorias.values[1]:,.2f}\n\n3. {top_categorias.index[2]}: R$ {top_categorias.values[2]:,.2f}")
    
    # Alertas
    if saldo_total < 0:
        st.error("⚠️ **ALERTA:** Saldo anual negativo! Revise seus gastos.")
    elif media_mensal > (total_ganhos / 12) * 0.8:
        st.warning("⚠️ **Cuidado:** Você está gastando mais de 80% da sua renda média mensal.")
    elif saldo_total > 0:
        st.success(f"✅ **Bom trabalho!** Saldo positivo de R$ {saldo_total:,.2f}")
    
    # Download dos dados
    st.markdown("---")
    st.subheader("📥 Exportar dados")
    
    dados_export = preparar_dados_gastos(df_gastos)
    if not dados_export.empty:
        csv = dados_export.to_csv(index=False)
        st.download_button(
            label="📊 Baixar CSV",
            data=csv,
            file_name=f"gastos_{ano_selecionado}_{st.session_state['username']}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>💰 Controle Financeiro Pessoal | Desenvolvido com ❤️ para Juan</p>
    <p style='font-size: 12px;'>Dados atualizados automaticamente</p>
</div>
""", unsafe_allow_html=True)
