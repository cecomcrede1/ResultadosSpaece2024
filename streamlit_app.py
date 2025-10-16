"""
Aplicação Streamlit para Consulta e Análise de Dados SPAECE

Esta aplicação permite consultar dados do SPAECE (Sistema Permanente de Avaliação da Educação Básica do Ceará)
e realizar análises visuais dos dados de proficiência, participação, desempenho e habilidades dos estudantes.

Funcionalidades principais:
- Consulta de dados por código de agregado
- Análise de taxa de participação
- Visualização de proficiência média
- Distribuição por padrão de desempenho
- Análise de habilidades específicas
- Dados contextuais por etnia, NSE e sexo
- Exportação de dados em CSV e JSON

Autor: Sistema SPAECE
Data: 2024
"""

import streamlit as st
import requests
import pandas as pd
import json
import base64
import plotly.graph_objects as go
import plotly.express as px
from config_api import API_URL, INDICADORES, HEADERS, criar_payload

# Sistema de Autenticação - Carregar do secrets.toml
try:
    # Combinar todas as credenciais em um único dicionário
    PASSWORDS = {}
    ENTITY_NAMES = {}
    
    # Carregar senha mestra
    MASTER_PASSWORD = st.secrets.get("master", {}).get("password", "SPAECE2024")
    
    # Carregar usuários regionais
    if "xregionais" in st.secrets:
        PASSWORDS.update(st.secrets["xregionais"])
        for codigo in st.secrets["xregionais"].keys():
            ENTITY_NAMES[codigo] = f"Regional {codigo}"
    
    # Carregar usuários municipais
    if "xmunicipios" in st.secrets:
        PASSWORDS.update(st.secrets["xmunicipios"])
        # Mapear códigos municipais para nomes
        municipios_map = {
            "2301000": "AQUIRAZ",
            "2303709": "CAUCAIA", 
            "2304285": "EUSEBIO",
            "2304954": "GUAIUBA",
            "2306256": "ITAITINGA",
            "2307650": "MARACANAU",
            "2307700": "MARANGUAPE",
            "2309706": "PACATUBA"
        }
        for codigo in st.secrets["xmunicipios"].keys():
            ENTITY_NAMES[codigo] = municipios_map.get(codigo, f"Município {codigo}")
    
    # Carregar usuários de escolas
    if "xescolas" in st.secrets:
        PASSWORDS.update(st.secrets["xescolas"])
        # Mapear códigos de escolas para nomes (usando comentários do secrets.toml)
        escolas_map = {
            # AQUIRAZ
            "23061197": "ALOISIO BERNARDO DE CASTRO EMEF",
            "23061723": "ANTONIO DE BRITO LIMA EMEF",
            "23060956": "BATOQUE EMEF",
            "23564385": "CENTRO DE EDUCACAO E CIDADANIA MANUEL ASSUNCAO PIRES",
            "23061251": "CENTRO DE EDUCACAO E CIDADANIA MARIA DE CASTRO BERNARDO",
            "23061634": "CLARENCIO CRISOSTOMO DE FREITAS EMEF",
            "23061014": "CORREGO DA MINHOCA EMEF",
            "23061758": "DIONISIA GUERRA EMEF",
            "23061022": "ERNESTO GURGEL VALENTE EMEF",
            "23061618": "ESCOLA MUNICIPAL DE ENSINO FUNDAMENTAL TIA ALZIRA",
            "23262672": "FERDINANDO TANSI CENTRO EDUCACIONAL MUNICIPAL",
            "23061049": "FRANCISCA MONTEIRO DA SILVA EMEF",
            "23061057": "FRANCISCO DA SILVA SAMPAIO EMEF",
            "23061650": "FRANCISCO GOMES FARIAS EMEF CEL",
            "23061073": "GUILHERME JANJA EMEF",
            "23061081": "HENRIQUE GONCALVES DA JUSTA FILHO EMEF",
            "23061774": "ISIDORO DE SOUSA ASSUNCAO EMEF",
            "23061090": "JARBAS PASSARINHO MIN EMEF",
            "23061790": "JOAO JAIME GADELHA EMEF",
            "23061804": "JOAO PIRES CARDOSO EMEF",
            "23061111": "JOAQUIM DE SOUSA TAVARES EMEF",
            "23204150": "JOSE ALMIR DA SILVA EMEF",
            "23061413": "JOSE CAMARA DE ALMEIDA EMEF",
            "23061146": "JOSE FERREIRA DA COSTA EMEF",
            "23204141": "JOSE ISAAC SARAIVA DA CUNHA EMEF",
            "23061820": "JOSE RAIMUNDO DA COSTA EMEF",
            "23060999": "JOSE RODRIGUES MONTEIRO EMEF",
            "23061162": "JUSCELINO KUBITSCHEK EMEF",
            "23061847": "JUVENAL PEREIRA FACANHA EMEF",
            "23061189": "LAGOA DE CIMA EMEF",
            "23061855": "LAGOA DO MATO DE SERPA EMEF",
            "23248750": "LAIS SIDRIM TARGINO EMEF",
            "23176423": "LEOLINA BATISTA RAMOS EMEF",
            "23204125": "LUIZ EDUARDO STUDART GOMES EMEF",
            "23061278": "MARIA FACANHA DE SA EMEF",
            "23061294": "MARIA MARGARIDA RAMOS COELHO EMEF",
            "23061685": "MARIA SOARES DE FREITAS EMEF",
            "23061430": "PLACIDO CASTELO EMEF",
            "23060905": "RAIMUNDA DE FREITAS FACANHA CEI",
            "23061626": "RAIMUNDA FERREIRA DA SILVA EMEF",
            "23061480": "RAIMUNDO RAMOS DA COSTA EMEF",
            "23061448": "RITA PAULA DE BRITO EMEF",
            "23061596": "VILA PAGA EMEF",
            "23061910": "VINDINA ASSUNCAO DE AQUINO EMEF",
            # PACATUBA - Exemplo de algumas escolas
            "23264292": "JOAO PAULO SAMPAIO DE MENEZES EEIEF",
            "23083417": "ANA ALBUQUERQUE CAMPOS EEIEF",
            "23083433": "ANGELA COSTA CAMPOS EEF",
            "23083735": "CLOVIS DE CASTRO PEREIRA EEF",
            "23083492": "CRISPIANA DE ALBUQUERQUE EEF",
            "23083450": "DR CARLOS ALBERTO DE ALMEIDA PONTE EEF",
            "23083751": "FIRMINO DE ABREU LIMA EEIEF",
            "23182342": "GELIA DA SILVA CORREIA EEIEF",
            "23083778": "JARDIM BOM RETIRO EREIEF",
            "23326662": "JOANA VASCONCELOS DE OLIVEIRA EMTI",
            "23264020": "JOSE BATISTA DE OLIVEIRA EEIEF",
            "23083697": "MAJOR MANOEL ASSIS NEPOMUCENO EEIEF",
            "23267259": "MANOEL ROSENDO FREIRE EEF",
            "23083611": "MANUEL PONTES DE MEDEIROS EEIEF",
            "23083700": "MARIA DE SA RORIZ EEIEF",
            "23083808": "MARIA GUIOMAR BASTOS CAVALCANTE PROFESSORA EEIEF",
            "23083638": "MARIA MIRTES HOLANDA DO VALE PROF EEF",
            "23083719": "MARIA MOCINHA ROCHA SA EEIEF",
            "23083824": "NELLY DE LIMA E MELO EEIEF",
            "23083760": "OS HEROIS DO TIMBO EEIEF",
            "23083832": "PEDRO DE SA RORIZ EEIEF",
            "23083506": "RAIMUNDA DA CRUZ ALEXANDRE EREIEF",
            "23083689": "VICENTE FERRER DE LIMA EEIEF",
            "23190906": "WALNEY DO CARMO LOPES EEIEF"
        }
        for codigo in st.secrets["xescolas"].keys():
            ENTITY_NAMES[codigo] = escolas_map.get(codigo, f"Escola {codigo}")
    
    if not PASSWORDS:
        st.error("❌ Nenhuma credencial encontrada no secrets.toml!")
        st.stop()
        
except Exception as e:
    st.error(f"❌ Erro ao carregar secrets.toml: {str(e)}")
    st.stop()

# Configuração da página
st.set_page_config(
    page_title="Resultados SPAECE 2024 - CREDE 1", 
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# CSS Global para Relatório Formal
st.markdown("""
    <style>
    /* Reset e configurações globais */
    .stContainer {
        padding: 0 !important;
    }
    
    /* Tema de relatório formal */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
        max-width: 1200px;
        background: #fafafa;
        font-family: 'Arial', sans-serif;
    }
    
    /* Cards de métricas estilo relatório formal */
    div[data-testid="stMetric"] {
        background: #ffffff;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: #2ca02c;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: #2ca02c;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #2ca02c;
        margin-bottom: 8px;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 12px;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Espaçamento entre colunas */
    [data-testid="column"] {
        padding: 0 8px;
    }
    
    /* Botões estilo relatório formal */
    .stButton > button {
        background: #2ca02c;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        background: #2ca02c;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Selectbox estilo relatório formal */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #d1d5db;
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #2ca02c;
        box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.1);
    }
    
    /* Expanders estilo relatório formal */
    .streamlit-expander {
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        background: white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .streamlit-expanderHeader {
        background: #f9fafb;
        border-radius: 6px 6px 0 0;
        font-weight: 600;
        color: #1f2937;
        border-bottom: 1px solid #e5e7eb;
    }
    
    /* DataFrames estilo relatório formal */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    
    /* Dividers estilo relatório formal */
    .stDivider {
        background: #d1d5db;
        height: 1px;
        border: none;
        margin: 1.5rem 0;
    }
    
    /* Headers de seção estilo relatório formal */
    .report-header {
        background: #2ca02c;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 6px;
        margin: 1.5rem 0 1rem 0;
        font-weight: 700;
        font-size: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Cards de informação estilo relatório formal */
    .report-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .report-card-header {
        background: #f9fafb;
        border-bottom: 2px solid #2ca02c;
        padding: 0.75rem 1rem;
        margin: -1.5rem -1.5rem 1rem -1.5rem;
        border-radius: 6px 6px 0 0;
        font-weight: 700;
        color: #1f2937;
    }
    
    /* Cores da paleta do gráfico de habilidades */
    .color-primary { color: #2ca02c; }
    .color-secondary { color: #ff7f0e; }
    .color-success { color: #2ca02c; }
    .color-danger { color: #d62728; }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2ca02c;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #2ca02c;
    }
    
    /* Estilos para impressão */
    @media print {
        /* Configurações gerais da página */
        * {
            -webkit-print-color-adjust: exact !important;
            color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        
        /* Container principal - sem compressão */
        .main .block-container {
            padding: 0.5in !important;
            max-width: none !important;
            width: 100% !important;
            margin: 0 !important;
        }
        
        /* Ocultar sidebar */
        .stSidebar {
            display: none !important;
        }
        
        /* Ocultar elementos interativos */
        .stButton > button,
        .stDownloadButton,
        .stSelectbox,
        .stTextInput,
        .stButton,
        .stDownloadButton {
            display: none !important;
        }
        
        /* Expanders */
        .stExpander {
            border: 1px solid #ccc !important;
        }
        
        /* Quebras de página estratégicas */
        .page-break {
            page-break-before: always;
            break-before: page;
        }
        
        .page-break-before {
            page-break-before: always;
            break-before: page;
        }
        
        .page-break-after {
            page-break-after: always;
            break-after: page;
        }
        
        /* Evitar quebras de página desnecessárias */
        .stMarkdown {
            page-break-inside: avoid;
            break-inside: avoid;
        }
        
        /* Evitar quebras em elementos pequenos */
        .stDivider {
            page-break-after: avoid;
            break-after: avoid;
        }
        
        .avoid-break {
            break-inside: avoid;
            page-break-inside: avoid;
        }
        
        /* Headers sempre no topo da página */
        .report-header {
            break-inside: avoid;
            page-break-inside: avoid;
            break-after: avoid;
            page-break-after: avoid;
            margin: 0.5rem 0 !important;
            padding: 0.75rem 1rem !important;
        }
        
        /* Cards evitam quebra no meio */
        .report-card {
            break-inside: avoid;
            page-break-inside: avoid;
            margin-bottom: 1rem;
            padding: 1rem !important;
        }
        
        /* Métricas evitam quebra */
        div[data-testid="stMetric"] {
            break-inside: avoid;
            page-break-inside: avoid;
            margin: 0.25rem !important;
            padding: 0.75rem !important;
        }
        
        /* DataFrames podem quebrar se necessário */
        .stDataFrame {
            break-inside: auto;
            page-break-inside: auto;
            width: 100% !important;
            overflow: visible !important;
        }
        
        /* Gráficos evitam quebra */
        .stPlotlyChart {
            break-inside: avoid;
            page-break-inside: avoid;
            width: 100% !important;
        }
        
        /* Dividers evitam quebra */
        .stDivider {
            break-inside: avoid;
            page-break-inside: avoid;
            margin: 0.5rem 0 !important;
        }
        
        /* Seções que devem ficar na mesma página */
        .same-page-section {
            break-inside: avoid;
            page-break-inside: avoid;
            margin-bottom: 0.5rem !important;
        }
        
        /* Colunas responsivas */
        [data-testid="column"] {
            width: 100% !important;
            padding: 0.25rem !important;
        }
        
        /* Ajustar cores para impressão */
        .report-header {
            background: #2ca02c !important;
            color: white !important;
        }
        
        div[data-testid="stMetric"] {
            border: 2px solid #2ca02c !important;
        }
        
        div[data-testid="stMetricValue"] {
            color: #2ca02c !important;
        }
        
        /* Margens da página - reduzidas para melhor aproveitamento */
        @page {
            margin: 0.5in;
            size: A4 landscape;
        }
        
        /* Garantir que o conteúdo não seja comprimido */
        body {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Ajustar tabelas para impressão */
        table {
            width: 100% !important;
            border-collapse: collapse !important;
        }
        
        /* Ajustar imagens e gráficos */
        img, svg {
            max-width: 100% !important;
            height: auto !important;
        }
        
        /* Corrigir compressão de colunas */
        .element-container {
            width: 100% !important;
            max-width: none !important;
        }
        
        /* Ajustar espaçamento geral */
        .stMarkdown {
            margin: 0.25rem 0 !important;
        }
        
        /* Corrigir largura de elementos */
        .stDataFrame > div {
            width: 100% !important;
            overflow: visible !important;
        }
        
        /* Ajustar botões ocultos */
        .stButton {
            display: none !important;
        }
        
        /* Corrigir layout de métricas */
        .metric-container {
            width: 100% !important;
            display: block !important;
        }
        
        /* Ajustar headers personalizados */
        .report-header {
            width: 100% !important;
            box-sizing: border-box !important;
        }
        
        /* Ajustar cards personalizados */
        .report-card {
            width: 100% !important;
            box-sizing: border-box !important;
        }
    }
    
    /* Estilo do botão Consultar com hover laranja */
    .stButton > button {
        background-color: #2ca02c !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #ff7f0e !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(255, 127, 14, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 6px rgba(255, 127, 14, 0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Header estilo relatório formal com logos
st.markdown("""
    <div style="
        background: #2ca02c;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        border: 3px solid #2ca02c;
        position: relative;
    ">
        <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        ">
            <div style="flex: 0 0 auto; width: 180px;">
                <img src="data:image/png;base64,{}" style="max-width: 100%; height: auto; max-height: 120px;" />
            </div>
            <div style="flex: 1; text-align: center;">
                <h1 style="
                    color: white;
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin: 0;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                ">Resultados SPAECE 2024</h1>
                <p style="
                    color: rgba(255,255,255,0.9);
                    font-size: 1.1rem;
                    margin: 0.5rem 0 0 0;
                    font-weight: 500;
                ">Sistema Permanente de Avaliação da Educação Básica do Ceará</p>
            </div>
            <div style="flex: 0 0 auto; width: 180px;">
                <img src="data:image/png;base64,{}" style="max-width: 100%; height: auto; max-height: 120px;" />
            </div>
        </div>
        <div style="
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 2px solid rgba(255,255,255,0.3);
        ">
            <p style="
                color: rgba(255,255,255,0.8);
                font-size: 0.9rem;
                margin: 0;
                font-style: italic;
            ">Análise de Dados Educacionais - Relatório Executivo</p>
        </div>
    </div>
""".format(
    # Logo CECOM (lado esquerdo)
    base64.b64encode(open('logo_CECOM_branco2.png', 'rb').read()).decode(),
    # Logo CREDE (lado direito)
    base64.b64encode(open('logo_CREDE_branco2.png', 'rb').read()).decode()
), unsafe_allow_html=True)

# ==================== CONSTANTES ====================

# Códigos de tipos de entidade no sistema SPAECE
CODIGOS_ENTIDADE = {
    'ESTADO': '01',      # Estado do Ceará
    'CREDE': '02',       # Coordenadoria Regional de Desenvolvimento da Educação
    'MUNICIPIO': '11',   # Município
    'ESCOLA': '03'       # Escola individual
}

# ==================== FUNÇÕES DE API ====================

def consultar_api(agregado):
    """Consulta a API SPAECE com tratamento de erros aprimorado"""
    try:
        # Validar entrada
        if not agregado or not str(agregado).strip():
            st.error("❌ Código da Entidade não pode estar vazio")
            return None
            
        payload = criar_payload(
            indicadores=INDICADORES,
            agregado=str(agregado).strip(),
            filtros=[],
            nivel_abaixo="0"
        )
        
        response = requests.post(
            API_URL, 
            json=payload, 
            headers=HEADERS, 
            timeout=30
        )
        response.raise_for_status()
        
        # Verificar se a resposta contém dados válidos
        data = response.json()
        if not data:
            st.warning(f"⚠️ Nenhum dado retornado para o agregado {agregado}")
            return None
            
        return data
        
    except requests.exceptions.Timeout:
        st.error(f"⏱️ Timeout ao consultar agregado {agregado}. Tente novamente.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"🌐 Erro de conexão. Verifique sua internet.")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Erro HTTP {e.response.status_code}: {e.response.reason}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro na requisição: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("❌ Erro ao decodificar resposta da API")
        return None
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
        return None

# ==================== FUNÇÕES DE PROCESSAMENTO ====================

def processar_dados(data):
    """Processa dados da API e retorna DataFrame"""
    if not data:
        st.warning("⚠️ Nenhum dado fornecido para processamento")
        return None
        
    try:
        if isinstance(data, dict):
            if 'result' in data and data['result']:
                df = pd.DataFrame(data['result'])
            elif 'data' in data and data['data']:
                df = pd.DataFrame(data['data'])
            elif 'results' in data and data['results']:
                df = pd.DataFrame(data['results'])
            else:
                # Tentar normalizar dados aninhados
                df = pd.json_normalize(data)
        elif isinstance(data, list) and data:
            df = pd.DataFrame(data)
        else:
            st.warning("⚠️ Formato de dados não suportado")
            return None
            
        if df.empty:
            st.warning("⚠️ DataFrame vazio após processamento")
            return None
            
        return df
        
    except pd.errors.EmptyDataError:
        st.warning("⚠️ Dados vazios recebidos da API")
        return None
    except pd.errors.ParserError as e:
        st.error(f"❌ Erro ao processar dados: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Erro inesperado ao processar dados: {str(e)}")
        return None

def converter_para_numerico(df, colunas):
    """Converte colunas para formato numérico com tratamento robusto"""
    if df is None or df.empty:
        return df
        
    for col in colunas:
        if col in df.columns:
            try:
                # Substituir valores inválidos por NaN
                df[col] = df[col].replace(['-', 'N/A', 'n/a', '', 'NULL', 'null', 'None'], pd.NA)
                
                # Limpar strings se for coluna de texto
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.strip()
                    # Substituir strings vazias por NaN
                    df[col] = df[col].replace('', pd.NA)
                
                # Converter para numérico
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
            except Exception as e:
                st.warning(f"⚠️ Erro ao converter coluna '{col}': {str(e)}")
                continue
                
    return df

def extrair_agregados_hierarquia(df):
    """Extrai códigos de agregados da coluna DC_HIERARQUIA"""
    if 'DC_HIERARQUIA' not in df.columns:
        return []
    
    agregados = set()
    for valor in df['DC_HIERARQUIA'].dropna():
        if isinstance(valor, str):
            codigos = valor.split('/')
            agregados.update([cod.strip() for cod in codigos if cod.strip()])
    
    return sorted(list(agregados))

def obter_nome_entidade(df):
    """Obtém o nome da entidade da coluna NM_ENTIDADE"""
    if 'NM_ENTIDADE' in df.columns and not df['NM_ENTIDADE'].empty:
        nome = df['NM_ENTIDADE'].iloc[0]
        if pd.notna(nome):
            return str(nome)
    return None

def obter_tipo_entidade(df):
    """Obtém o tipo da entidade da coluna DC_TIPO_ENTIDADE"""
    if 'DC_TIPO_ENTIDADE' in df.columns and not df['DC_TIPO_ENTIDADE'].empty:
        tipo = df['DC_TIPO_ENTIDADE'].iloc[0]
        if pd.notna(tipo):
            return str(tipo).upper()
    return None

# ==================== FUNÇÕES DE VISUALIZAÇÃO ====================

def criar_card_entidade(titulo):
    """Cria um card HTML para exibir título de entidade"""
    return f"""
        <div style="
            border: 3px solid #358242;
            border-radius: 15px;
            padding: 20px 20px 5px 20px;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            height: 120px;
            display: flex;
            flex-direction: column;
        ">
            <h3 style="
                text-align: center;
                color: #358242;
                font-size: 1.4em;
                font-weight: bold;
                margin: 0 0 10px 0;
                padding-bottom: 10px;
                border-bottom: 3px solid #358242;
            ">{titulo}</h3>
        </div>
    """

def obter_proficiencia_media(df, codigo_tipo):
    """Obtém a proficiência média para um tipo de entidade"""
    if df is None or df.empty:
        return None
    try:
        return df[df['Tipo de Entidade'].str.contains(codigo_tipo, case=False, na=False)]['Proficiência Média'].mean()
    except:
        return None

def aplicar_substituicoes(df):
    """Aplica substituições padronizadas nas colunas do DataFrame"""
    if df is None or df.empty:
        return df
        
    # Substituições para disciplina
    if 'VL_FILTRO_DISCIPLINA' in df.columns:
        df['VL_FILTRO_DISCIPLINA'] = df['VL_FILTRO_DISCIPLINA'].replace({
            'LP': 'Língua Portuguesa',
            'MT': 'Matemática'
        })
    
    # Substituições para rede
    if 'VL_FILTRO_REDE' in df.columns:
        df['VL_FILTRO_REDE'] = df['VL_FILTRO_REDE'].replace({
            'ESTADUAL': 'Estadual',
            'MUNICIPAL': 'Municipal',
            'PUBLICA': 'Pública',
            'PÚBLICA': 'Pública'
        })
    
    # Substituições para etapa
    if 'VL_FILTRO_ETAPA' in df.columns:
        df['VL_FILTRO_ETAPA'] = df['VL_FILTRO_ETAPA'].replace({
            'ENSINO FUNDAMENTAL DE 9 ANOS - 2º ANO': '2º Ano - Fundamental',
            'ENSINO FUNDAMENTAL DE 9 ANOS - 5º ANO': '5º Ano - Fundamental',
            'ENSINO FUNDAMENTAL DE 9 ANOS - 9º ANO': '9º Ano - Fundamental'
        })
    
    # Substituições para tipo de entidade
    if 'DC_TIPO_ENTIDADE' in df.columns:
        df['DC_TIPO_ENTIDADE'] = df['DC_TIPO_ENTIDADE'].replace({
            'ESTADO': 'Ceará',
            'REGIONAL': 'CREDE',
            'MUNICIPIO': 'Município',
            'ESCOLA': 'Escola'
        })
    
    return df

def criar_gauge_participacao(df, titulo, codigo_tipo, key_suffix):
    """
    Cria um gauge de participação para um tipo específico de entidade dentro de um card
    
    Args:
        df: DataFrame com dados de participação
        titulo: Título do gauge
        codigo_tipo: Código para filtrar o tipo de entidade
        key_suffix: Sufixo para chave única do plotly
    """
    if df.empty:
        st.info("Sem dados de participação disponíveis")
        return
    
    # Filtrar dados do tipo específico
    dados_filtrados = df[df['Tipo de Entidade'].str.contains(codigo_tipo, case=False, na=False)]
    
    if dados_filtrados.empty:
        st.info(f"Sem dados de {titulo} para exibir")
        return
    
    # Encontrar a linha com o maior valor de participação
    idx_max_participacao = dados_filtrados['Participação'].idxmax()
    linha_max_participacao = dados_filtrados.loc[idx_max_participacao]
    
    # Pegar valores da linha com maior participação
    participacao_maxima = linha_max_participacao['Participação']
    total_previstos = linha_max_participacao['Alunos Previstos']
    total_efetivos = linha_max_participacao['Alunos Efetivos']
    
    # Card com altura fixa
    st.markdown(f"""
        <div style="
            border: 3px solid #358242;
            border-radius: 15px;
            padding: 20px 20px 5px 20px;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
            height: 120px;
            display: flex;
            flex-direction: column;
        ">
            <h3 style="
                text-align: center;
                color: #358242;
                font-size: 1.4em;
                font-weight: bold;
                margin: 0 0 10px 0;
                padding-bottom: 10px;
                border-bottom: 3px solid #358242;
            ">{titulo}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Criar gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=participacao_maxima,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Participação", 'font': {'size': 16, 'color': '#358242'}},
        number={'suffix': "%", 'font': {'size': 28}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#358242"},
            'steps': [
                {'range': [0, 80], 'color': "#ffcccc"},
                {'range': [80, 90], 'color': "#ffff99"},
                {'range': [90, 100], 'color': "#ccffcc"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': participacao_maxima,
            }
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=50, b=5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=16)
    )
    st.plotly_chart(fig, use_container_width=True, key=f"gauge_{key_suffix}")
    
    # Métricas de alunos
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="👥 Previstos", 
            value=f"{int(total_previstos):,}".replace(',', '.')
        )
    with col2:
        st.metric(
            label="✅ Efetivos", 
            value=f"{int(total_efetivos):,}".replace(',', '.')
        )

# ==================== INICIALIZAÇÃO DO SESSION STATE ====================

if 'df_concatenado' not in st.session_state:
    st.session_state.df_concatenado = None
if 'agregado_consultado' not in st.session_state:
    st.session_state.agregado_consultado = None

# ==================== SISTEMA DE AUTENTICAÇÃO ====================

# Inicializar session state para autenticação
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_code' not in st.session_state:
    st.session_state.user_code = None

# Interface de Login
if not st.session_state.authenticated:
    st.markdown("### 🔐 Sistema de Autenticação SPAECE")
    
    # CSS customizado para botões laranja #ff7100 (aplicado globalmente)
    st.markdown("""
    <style>
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #ff7100, #ff8c00) !important;
        color: white !important;
        border: 3px solid #ff7100 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        font-size: 1.1rem !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
        box-shadow: 0 3px 6px rgba(255, 113, 0, 0.4) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #e65a00, #ff7100) !important;
        border-color: #e65a00 !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 6px 12px rgba(255, 113, 0, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            codigo = st.text_input("🏢 Código da Entidade", placeholder="Ex: 23, 230010, 230020...", help="Digite o código da entidade que deseja consultar, ou use a senha mestra para acessar todos os dados")
        
        with col2:
            senha = st.text_input("🔑 Senha", type="password", placeholder="Digite a senha da entidade")
        
        submitted = st.form_submit_button("🚀 Fazer Login e Consultar", type="secondary")
        
        if submitted:
            if not codigo or not senha:
                st.error("❌ Por favor, preencha todos os campos")
            elif not codigo.isdigit():
                st.error("❌ O código da entidade deve conter apenas números")
            elif len(codigo) < 2:
                st.error("❌ O código da entidade deve ter pelo menos 2 dígitos")
            elif codigo not in PASSWORDS and senha != MASTER_PASSWORD:
                st.error("❌ Código da entidade não encontrado")
            elif PASSWORDS.get(codigo) != senha and senha != MASTER_PASSWORD:
                st.error("❌ Senha incorreta")
            else:
                # Login bem-sucedido
                st.session_state.authenticated = True
                st.session_state.user_code = codigo
                
                # Verificar se é senha mestra
                if senha == MASTER_PASSWORD:
                    st.success(f"✅ Login realizado com sucesso usando **SENHA MESTRA** para: **{ENTITY_NAMES.get(codigo, f'Entidade {codigo}')}**")
                else:
                    st.success(f"✅ Login realizado com sucesso para: **{ENTITY_NAMES.get(codigo, f'Entidade {codigo}')}**")
                st.rerun()
    
   
else:
    # Usuário autenticado - mostrar interface principal
    codigo = st.session_state.user_code
    nome_entidade = ENTITY_NAMES.get(codigo, f"Entidade {codigo}")
    
    # Botão de logout
    col1, col2 = st.columns([4, 1])
    with col1:
        st.success(f"✅ Logado como: **{nome_entidade}** (Código: {codigo})")
    with col2:
        
        if st.button("🚪 Sair", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user_code = None
            st.session_state.agregado_consultado = None
            st.session_state.df_concatenado = None
            st.rerun()
    
    # Consulta automática usando o código do login
    agregado = codigo
    
    # Fazer consulta automaticamente
    if st.session_state.agregado_consultado != agregado:
        with st.spinner(f"🔄 Consultando dados da entidade {agregado}..."):
            # Lista para armazenar todos os dataframes
            lista_dfs = []
            
            # Consulta inicial
            data = consultar_api(agregado)
            if data:
                df = processar_dados(data)
                if df is not None:
                    # Adicionar coluna identificadora do agregado
                    df['AGREGADO_ORIGEM'] = agregado
                    lista_dfs.append(df)
                    
                    # Extrair agregados da hierarquia (sem exibir)
                    agregados_hierarquia = []
                    if len(agregado) > 2:
                        agregados_hierarquia = extrair_agregados_hierarquia(df)
                        agregados_hierarquia = [ag for ag in agregados_hierarquia if ag != agregado]
                    
                    # Consultar agregados da hierarquia silenciosamente
                    if agregados_hierarquia:
                        for ag_hierarquia in agregados_hierarquia:
                            data_hierarquia = consultar_api(ag_hierarquia)
                            if data_hierarquia:
                                df_hierarquia = processar_dados(data_hierarquia)
                                if df_hierarquia is not None:
                                    df_hierarquia['AGREGADO_ORIGEM'] = ag_hierarquia
                                    lista_dfs.append(df_hierarquia)
                    
                    # Criar dataframe concatenado (sem exibir)
                    if len(lista_dfs) == 1:
                        df_unico = lista_dfs[0].copy()
                        df_unico = aplicar_substituicoes(df_unico)
                        st.session_state.df_concatenado = df_unico
                        st.session_state.agregado_consultado = agregado
                    elif len(lista_dfs) > 1:
                        df_concatenado = pd.concat(lista_dfs, ignore_index=True)
                        df_concatenado = aplicar_substituicoes(df_concatenado)
                        st.session_state.df_concatenado = df_concatenado
                        st.session_state.agregado_consultado = agregado
                    
                    # Calcular total de registros
                    total_registros = sum(len(df) for df in lista_dfs)
                    st.success(f"✅ Dados carregados: {total_registros} registros (incluindo hierarquia)")
                else:
                    st.error("❌ Erro ao processar dados")
            else:
                st.warning("⚠️ Nenhum dado retornado pela API")
    
    # Verificar se há dados para exibir
    if st.session_state.df_concatenado is not None:
        # ==================== SEÇÃO DE ANÁLISE ====================
        df_concat = st.session_state.df_concatenado.copy()
        
        
        # Header estilo relatório formal para análise dos dados
        st.markdown("""
        <div class="report-header" style="font-size: 2rem; text-align: left;">
            📊 ANÁLISE DOS DADOS
        </div>


        """, unsafe_allow_html=True)
        
        # ==================== INFORMAÇÕES DA ENTIDADE ====================
        st.markdown("---")
        
        
        # Exibir informações da entidade consultada
        entidade_info = []
    
    # Verificar e adicionar nome da entidade principal
    if 'NM_ENTIDADE' in df_concat.columns and not df_concat.empty:
        entidade_nome = df_concat['NM_ENTIDADE'].iloc[0]
        if pd.notna(entidade_nome) and str(entidade_nome).strip():
            entidade_info.append(f"Entidade: {entidade_nome}")
    
    # Verificar e adicionar informações do município
    if 'NM_MUNICIPIO' in df_concat.columns and not df_concat.empty:
        municipio = df_concat['NM_MUNICIPIO'].iloc[0]
        if pd.notna(municipio) and str(municipio).strip():
            entidade_info.append(f"Município: {municipio}")
    
    # Verificar e adicionar informações da CREDE
    if 'NM_REGIONAL' in df_concat.columns and not df_concat.empty:
        crede = df_concat['NM_REGIONAL'].iloc[0]
        if pd.notna(crede) and str(crede).strip():
            entidade_info.append(f"CREDE: {crede}")
    
    # Verificar e adicionar informações do estado
    if 'NM_ESTADO' in df_concat.columns and not df_concat.empty:
        estado = df_concat['NM_ESTADO'].iloc[0]
        if pd.notna(estado) and str(estado).strip():
            entidade_info.append(f"Estado: {estado}")
    
    # Exibir as informações se existirem, senão mostrar Código da Entidade
    if entidade_info:
        # Card estilo relatório formal para informações da entidade
        st.markdown(f"""
        <div class="report-card">
            <div class="report-card-header">
                🏛️ INFORMAÇÕES DA ENTIDADE
            </div>
            <div style="
                font-size: 1rem;
                line-height: 1.8;
                color: #374151;
                font-weight: 500;
            ">
                {"<br>".join(entidade_info)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="report-card">
            <div class="report-card-header" style="border-bottom-color: #6b7280;">
                🏛️ ENTIDADE CONSULTADA
            </div>
            <div style="
                font-size: 1rem;
                line-height: 1.8;
                color: #4b5563;
                font-weight: 500;
            ">
                <strong>Código:</strong> {st.session_state.agregado_consultado}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # # ==================== ESTATÍSTICAS GERAIS ====================
    # with st.expander("📈 Estatísticas Gerais", expanded=False):
    #     col1, col2, col3, col4 = st.columns(4)
    #     with col1:
    #         st.metric("Total de Registros", f"{len(df_concat):,}".replace(',', '.'))
    #     with col2:
    #         if 'VL_FILTRO_DISCIPLINA' in df_concat.columns:
    #             st.metric("Componentes", df_concat['VL_FILTRO_DISCIPLINA'].nunique())
    #     with col3:
    #         if 'VL_FILTRO_ETAPA' in df_concat.columns:
    #             st.metric("Etapas", df_concat['VL_FILTRO_ETAPA'].nunique())
    #     with col4:
    #         if 'NM_ENTIDADE' in df_concat.columns:
    #             st.metric("Entidades", df_concat['NM_ENTIDADE'].nunique())
    
    # Filtrar por entidade se for consulta de nível estadual
    agregado_original = st.session_state.agregado_consultado
    if agregado_original and len(agregado_original) == 2:
        if 'CD_ENTIDADE' in df_concat.columns:
            df_concat = df_concat[df_concat['CD_ENTIDADE'] == agregado_original].copy()
            nome_estado = df_concat['NM_ENTIDADE'].iloc[0] if 'NM_ENTIDADE' in df_concat.columns and len(df_concat) > 0 else agregado_original
            st.info(f"🎯 Exibindo apenas dados da entidade: **{nome_estado}**")
    
    # Sidebar estilo relatório formal
    with st.sidebar:
        # Imagem do painel CECOM no topo do sidebar
        st.image("painel_cecom.png", use_container_width=True)
        
        # Card estilo relatório formal para informações da entidade no sidebar
        st.markdown("""
        <div style="
            background: #2ca02c;
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 2px solid #2ca02c;
        ">
            <h3 style="
                margin: 0;
                font-size: 1rem;
                font-weight: 700;
                text-align: center;
            ">🏛️ INFORMAÇÕES DA ENTIDADE</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Verificar e exibir informações da entidade
        sidebar_info = []
        
        # Verificar e adicionar nome da entidade principal
        if 'NM_ENTIDADE' in df_concat.columns and not df_concat.empty:
            entidade_nome = df_concat['NM_ENTIDADE'].iloc[0]
            if pd.notna(entidade_nome) and str(entidade_nome).strip():
                sidebar_info.append(f"Entidade: {entidade_nome}")
        
        # Verificar e adicionar informações do município
        if 'NM_MUNICIPIO' in df_concat.columns and not df_concat.empty:
            municipio = df_concat['NM_MUNICIPIO'].iloc[0]
            if pd.notna(municipio) and str(municipio).strip():
                sidebar_info.append(f"Município: {municipio}")
        
        # Verificar e adicionar informações da CREDE
        if 'NM_REGIONAL' in df_concat.columns and not df_concat.empty:
            crede = df_concat['NM_REGIONAL'].iloc[0]
            if pd.notna(crede) and str(crede).strip():
                sidebar_info.append(f"CREDE: {crede}")
        
        # Verificar e adicionar informações do estado
        if 'NM_ESTADO' in df_concat.columns and not df_concat.empty:
            estado = df_concat['NM_ESTADO'].iloc[0]
            if pd.notna(estado) and str(estado).strip():
                sidebar_info.append(f"Estado: {estado}")
        
        # Exibir as informações no sidebar com estilo relatório formal
        if sidebar_info:
            for info in sidebar_info:
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 0.6rem;
                    margin: 0.3rem 0;
                    border-radius: 4px;
                    border-left: 3px solid #2ca02c;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                    font-size: 0.8rem;
                    border: 1px solid #e5e7eb;
                ">{info}</div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                background: white;
                padding: 0.6rem;
                margin: 0.3rem 0;
                border-radius: 4px;
                border-left: 3px solid #6b7280;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                font-size: 0.8rem;
                border: 1px solid #e5e7eb;
            ">**Código:** {st.session_state.agregado_consultado}</div>
            """, unsafe_allow_html=True)
        
        # Header estilo relatório formal para filtros
        st.markdown("""
        <div style="
            background: #2ca02c;
            padding: 0.8rem;
            border-radius: 4px;
            margin: 1rem 0;
            text-align: center;
            border: 2px solid #2ca02c;
        ">
            <h3 style="
                margin: 0;
                color: white;
                font-size: 0.9rem;
                font-weight: 700;
            ">🔍 FILTROS</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Filtro de Etapa
        if 'VL_FILTRO_ETAPA' in df_concat.columns:
            etapas_unicas = df_concat['VL_FILTRO_ETAPA'].unique()
            etapas_unicas = [e for e in etapas_unicas if pd.notna(e)]  # Remove NaN
            
            # Remover etapas específicas do seletor
            etapas_remover = [
                'ENSINO MEDIO - 2ª SERIE',
                'ENSINO MEDIO - 3ª SERIE', 
                'EJA DO ENSINO MÉDIO - 3ª SÉRIE'
            ]
            etapas_unicas = [e for e in etapas_unicas if e not in etapas_remover]
            
            if len(etapas_unicas) > 0:
                etapa_selecionada = st.selectbox("Selecione a Etapa", etapas_unicas, key="etapa_selecionada")
                if etapa_selecionada:
                    df_concat = df_concat[df_concat['VL_FILTRO_ETAPA'] == etapa_selecionada]
        
        # Filtro de Disciplina
        if 'VL_FILTRO_DISCIPLINA' in df_concat.columns:
            disciplinas_unicas = df_concat['VL_FILTRO_DISCIPLINA'].unique()
            disciplinas_unicas = [d for d in disciplinas_unicas if pd.notna(d)]  # Remove NaN
            
            if len(disciplinas_unicas) > 0:
                # Definir "Língua Portuguesa" como padrão se disponível
                default_disciplina = None
                if "Língua Portuguesa" in disciplinas_unicas:
                    default_disciplina = "Língua Portuguesa"
                elif "Língua Portuguesa - Escrita e Leitura" in disciplinas_unicas:
                    default_disciplina = "Língua Portuguesa - Escrita e Leitura"
                
                # Encontrar o índice da disciplina padrão
                default_index = 0
                if default_disciplina:
                    try:
                        default_index = list(disciplinas_unicas).index(default_disciplina)
                    except ValueError:
                        default_index = 0
                
                disciplina_selecionada = st.selectbox("Selecione a Disciplina", disciplinas_unicas, index=default_index, key="disciplina_selecionada")
                if disciplina_selecionada:
                    df_concat = df_concat[df_concat['VL_FILTRO_DISCIPLINA'] == disciplina_selecionada]
        
        # Filtro de Rede
        if 'VL_FILTRO_REDE' in df_concat.columns:
            redes_unicas = df_concat['VL_FILTRO_REDE'].unique()
            redes_unicas = [r for r in redes_unicas if pd.notna(r)]  # Remove NaN
            
            if len(redes_unicas) > 0:
                rede_selecionada = st.selectbox("Selecione a Rede", redes_unicas, key="rede_selecionada")
                if rede_selecionada:
                    df_concat = df_concat[df_concat['VL_FILTRO_REDE'] == rede_selecionada]
    
    # ==================== TAXA DE PARTICIPAÇÃO ====================
    colunas_participacao = ['TP_ENTIDADE','NM_ENTIDADE','QT_ALUNO_PREVISTO','QT_ALUNO_EFETIVO', 
                           'TX_PARTICIPACAO', 'VL_FILTRO_DISCIPLINA','VL_FILTRO_ETAPA']
    
    if not df_concat.empty and all(col in df_concat.columns for col in colunas_participacao):
        df_participacao = df_concat[colunas_participacao].dropna().copy()
        df_participacao = df_participacao[df_participacao['VL_FILTRO_DISCIPLINA'] != 'Língua Portuguesa - Escrita e Leitura']
        df_participacao.columns = ['Tipo de Entidade', 'Entidade', 'Alunos Previstos', 'Alunos Efetivos', 
                                   'Participação', 'Componente Curricular', 'Etapa']
        
        # Só aplicar quebra de página se houver dados válidos após processamento
        if not df_participacao.empty:
            st.markdown("""
            <div class="report-header same-page-section" style="background: #2ca02c;">
                📊 TAXA DE PARTICIPAÇÃO
            </div>
            """, unsafe_allow_html=True)
            
            # Converter para numérico
            df_participacao = converter_para_numerico(
                df_participacao, 
                ['Alunos Previstos', 'Alunos Efetivos', 'Participação']
            )
            
            # Gauges de participação
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                criar_gauge_participacao(df_participacao, "Ceará", CODIGOS_ENTIDADE['ESTADO'], "ceara")
            
            with col2:
                criar_gauge_participacao(df_participacao, "CREDE", CODIGOS_ENTIDADE['CREDE'], "crede")
            
            with col3:
                criar_gauge_participacao(df_participacao, "Município", CODIGOS_ENTIDADE['MUNICIPIO'], "municipio")
            
            with col4:
                criar_gauge_participacao(df_participacao, "Escola", CODIGOS_ENTIDADE['ESCOLA'], "escola")
            
            # Download
            csv_part = df_participacao.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Baixar Dados de Participação",
                data=csv_part,
                file_name="participacao.csv",
                mime="text/csv",
                key="download_participacao"
            )
        else:
            st.info("Sem dados válidos de participação após processamento")
    else:
        st.info("Colunas necessárias não encontradas para exibir participação")
    
    # Espaçamento menor para manter na mesma página
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================== PROFICIÊNCIA MÉDIA ====================
    st.markdown("""
    <div class="report-header same-page-section" style="background: #2ca02c;">
        📈 PROFICIÊNCIA MÉDIA
    </div>
    """, unsafe_allow_html=True)
    colunas_proficiencia = ['TP_ENTIDADE','NM_ENTIDADE','AVG_PROFICIENCIA_E1','VL_FILTRO_DISCIPLINA','VL_FILTRO_ETAPA']
    
    if not df_concat.empty and all(col in df_concat.columns for col in colunas_proficiencia):
        df_proficiencia = df_concat[colunas_proficiencia].dropna().copy()
        df_proficiencia = df_proficiencia[df_proficiencia['VL_FILTRO_DISCIPLINA'] != 'Língua Portuguesa - Escrita e Leitura']
        df_proficiencia.columns = ['Tipo de Entidade', 'Entidade', 'Proficiência Média', 'Componente Curricular', 'Etapa']
        
        # Converter para numérico
        df_proficiencia['Proficiência Média'] = pd.to_numeric(df_proficiencia['Proficiência Média'], errors='coerce')
        
        # DataFrame para exibição (sem a coluna Tipo de Entidade)
        df_proficiencia_display = df_proficiencia[['Entidade', 'Proficiência Média', 'Componente Curricular', 'Etapa']].copy()
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Cards de proficiência
        entidades = [
            ("Ceará", CODIGOS_ENTIDADE['ESTADO']),
            ("CREDE", CODIGOS_ENTIDADE['CREDE']),
            ("Município", CODIGOS_ENTIDADE['MUNICIPIO']),
            ("Escola", CODIGOS_ENTIDADE['ESCOLA'])
        ]
        
        for i, (nome, codigo) in enumerate(entidades):
            with [col1, col2, col3, col4][i]:
                st.markdown(criar_card_entidade(nome), unsafe_allow_html=True)
                proficiencia = obter_proficiencia_media(df_proficiencia, codigo)
                st.metric("📊 Proficiência", f"{proficiencia:.0f}" if not pd.isna(proficiencia) else "N/A")
        
        #Download
        csv_prof = df_proficiencia_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Baixar Dados de Proficiência",
            data=csv_prof,
            file_name="proficiencia.csv",
            mime="text/csv",
            key="download_proficiencia"
        )
    else:
        st.info("Colunas necessárias não encontradas para exibir proficiência")
    
    # ==================== DISTRIBUIÇÃO POR DESEMPENHO ====================
    colunas_desempenho = ['TP_ENTIDADE','DC_TIPO_ENTIDADE','NM_ENTIDADE','NU_N01_TRI_E1','NU_N02_TRI_E1','NU_N03_TRI_E1',
                         'NU_N04_TRI_E1','NU_N05_TRI_E1','TX_N01_TRI_E1', 'TX_N02_TRI_E1', 
                         'TX_N03_TRI_E1', 'TX_N04_TRI_E1', 'TX_N05_TRI_E1', 'VL_FILTRO_DISCIPLINA', 
                         'VL_FILTRO_ETAPA']
    
    if not df_concat.empty and all(col in df_concat.columns for col in colunas_desempenho):
        # Quebra de página antes da seção de desempenho (só se houver dados)
        st.markdown("""
        <div style="page-break-before: always; break-before: page;">
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="report-header" style="background: #ff7f0e;">
            📊 DISTRIBUIÇÃO POR PADRÃO DE DESEMPENHO
        </div>
        """, unsafe_allow_html=True)
        # Usar dropna apenas nas colunas essenciais, não nas de desempenho
        df_desempenho = df_concat[colunas_desempenho].dropna(
            subset=['TP_ENTIDADE', 'DC_TIPO_ENTIDADE', 'NM_ENTIDADE', 'VL_FILTRO_DISCIPLINA', 'VL_FILTRO_ETAPA']
        ).copy()
        
        df_desempenho.columns = ['Tipo de Entidade', 'Tipo de Entidade Descrição', 'Entidade', 'Nível 1', 'Nível 2', 'Nível 3', 
                                'Nível 4', 'Nível 5', 'Taxa Nível 1', 'Taxa Nível 2', 
                                'Taxa Nível 3', 'Taxa Nível 4', 'Taxa Nível 5', 
                                'Componente Curricular', 'Etapa']
        
        # Definir ordem dos tipos de entidade e criar coluna de ordenação
        ordem_tipos = {'01': 1, '02': 2, '11': 3, '03': 4}
        df_desempenho['Ordem_Tipo'] = df_desempenho['Tipo de Entidade'].map(ordem_tipos)
        df_desempenho['Tipo de Entidade'] = pd.Categorical(
            df_desempenho['Tipo de Entidade'], 
            categories=['01', '02', '11', '03'], 
            ordered=True
        )
        
        # Ordenar o DataFrame principal pela ordem correta
        df_desempenho = df_desempenho.sort_values(['Ordem_Tipo', 'Entidade'])
        
        # Converter colunas de níveis para numérico
        df_desempenho = converter_para_numerico(
            df_desempenho, 
            ['Nível 1', 'Nível 2', 'Nível 3', 'Nível 4', 'Nível 5', 
             'Taxa Nível 1', 'Taxa Nível 2', 'Taxa Nível 3', 'Taxa Nível 4', 'Taxa Nível 5']
        )
        
        
        # Criar gráfico de barras para apresentar os níveis de desempenho
        st.subheader("Gráfico de Distribuição por Padrão de Desempenho")
        
        # Preparar dados para o gráfico
        df_grafico = df_desempenho.copy()
        
        # Ordenar por ordem numérica do tipo e depois por Entidade
        df_grafico = df_grafico.sort_values(['Ordem_Tipo', 'Entidade'])
        
        # Agrupar por entidade e calcular a média apenas para colunas que existem
        colunas_agregacao = {}
        for col in ['Taxa Nível 1', 'Taxa Nível 2', 'Taxa Nível 3', 'Taxa Nível 4', 'Taxa Nível 5']:
            if col in df_grafico.columns:
                colunas_agregacao[col] = 'mean'
        
        # Adicionar também as colunas de quantidade (Nível 1-5) para o hover
        for col in ['Nível 1', 'Nível 2', 'Nível 3', 'Nível 4', 'Nível 5']:
            if col in df_grafico.columns:
                colunas_agregacao[col] = 'sum'  # Somar as quantidades
        
        df_agregado = df_grafico.groupby(['Tipo de Entidade', 'Tipo de Entidade Descrição', 'Ordem_Tipo'], observed=True).agg(colunas_agregacao).reset_index()
        
        if len(df_agregado) > 0:
            # Ordenar o DataFrame agregado para manter a ordem no gráfico
            df_agregado = df_agregado.sort_values(['Ordem_Tipo', 'Tipo de Entidade Descrição'])
            
            # Detectar colunas de níveis disponíveis
            colunas_niveis_disponiveis = [col for col in df_agregado.columns if col.startswith('Taxa Nível')]
            
            # Transformar os dados para formato adequado para plotagem
            df_plot = pd.melt(
                df_agregado, 
                id_vars=['Tipo de Entidade', 'Tipo de Entidade Descrição', 'Ordem_Tipo'],
                value_vars=colunas_niveis_disponiveis,
                var_name='Padrão de Desempenho',
                value_name='Percentual'
            )
            
            # Ordenar o DataFrame plot para manter a ordem das entidades
            df_plot = df_plot.sort_values(['Ordem_Tipo', 'Tipo de Entidade Descrição'])
            
            # As colunas TX_* já são percentuais (0-100), não precisamos multiplicar por 100
            
            # Criar o gráfico de barras empilhadas usando go.Figure
            fig = go.Figure()
            
            # Detectar quantos níveis existem baseado na etapa
            # Usar df_desempenho que tem a coluna Etapa, não df_grafico que pode não ter
            etapa_atual = df_desempenho['Etapa'].iloc[0] if 'Etapa' in df_desempenho.columns and len(df_desempenho) > 0 else None
            
            if etapa_atual and '2º Ano' in etapa_atual:
                # 2º ano tem 5 níveis
                niveis = ['Taxa Nível 1', 'Taxa Nível 2', 'Taxa Nível 3', 'Taxa Nível 4', 'Taxa Nível 5']
                cores = ['#e30513', '#fdc300', '#ffed00', '#cce4ce', '#1ca041']
                # Nomes para a legenda do 2º ano
                nomes_legenda = ['Não Alfabetizado', 'Alfabetização Incompleta', 'Intermediário', 'Suficiente', 'Avançado']
            else:
                # 5º e 9º ano têm 4 níveis
                niveis = ['Taxa Nível 1', 'Taxa Nível 2', 'Taxa Nível 3', 'Taxa Nível 4']
                cores = ['#e30513', '#fdc300', '#cce4ce','#1ca041']
                # Nomes para a legenda do 5º e 9º ano
                nomes_legenda = ['Muito Crítico', 'Crítico', 'Intermediário', 'Avançado']
            
            # Filtrar apenas os níveis que existem nos dados
            niveis_existentes = [nivel for nivel in niveis if nivel in df_agregado.columns]
            cores = cores[:len(niveis_existentes)]
            nomes_legenda_filtrados = nomes_legenda[:len(niveis_existentes)]
            
            # Adicionar uma barra para cada nível
            for i, nivel in enumerate(niveis_existentes):
                dados_nivel = df_plot[df_plot['Padrão de Desempenho'] == nivel]
                # Criar nome simplificado para o hover
                nome_nivel = nivel.replace('Taxa ', '')
                
                # Buscar os valores numéricos correspondentes (Nível 1, Nível 2, etc.)
                coluna_numerica = nome_nivel  # Nível 1, Nível 2, etc.
                
                # Criar dados para hover com quantidade de alunos
                hover_data = []
                for idx, row in dados_nivel.iterrows():
                    entidade_desc = row['Tipo de Entidade Descrição']
                    percentual = row['Percentual']
                    # Buscar quantidade de alunos correspondente (coluna Nível 1, Nível 2, etc.)
                    # O percentual já vem da coluna Taxa Nível X, agora buscamos a quantidade da coluna Nível X
                    quantidade_alunos = df_agregado[df_agregado['Tipo de Entidade Descrição'] == entidade_desc][coluna_numerica].iloc[0] if coluna_numerica in df_agregado.columns else 0
                    hover_data.append(f'<b>{entidade_desc}</b><br>Nível: {nomes_legenda_filtrados[i]}<br>Percentual: {percentual:.1f}%<br>Quantidade de Alunos: {quantidade_alunos:.0f}')
                
                fig.add_trace(go.Bar(
                    name=nomes_legenda_filtrados[i],
                    x=dados_nivel['Percentual'],
                    y=dados_nivel['Tipo de Entidade Descrição'],
                    orientation='h',
                    marker_color=cores[i],
                    customdata=hover_data,
                    hovertemplate='%{customdata}<extra></extra>',
                    text=dados_nivel['Percentual'].round(2).astype(str) + '%',
                    textposition='inside',
                    textfont=dict(size=20, color='black')
                ))
            
            # Criar ordem específica das entidades baseada no tipo (01, 02, 11, 03)
            df_ordenado = df_plot.sort_values(['Ordem_Tipo', 'Tipo de Entidade Descrição'])
            ordem_entidades = df_ordenado['Tipo de Entidade Descrição'].unique().tolist()
            
            # Criar ordem fixa baseada nos tipos de entidade (01, 02, 11, 03)
            # Mapear códigos para descrições na ordem correta
            mapeamento_ordem = {
                '01': 'ESTADO',
                '02': 'REGIONAL', 
                '11': 'MUNICIPIO',
                '03': 'ESCOLA'
            }
            
            # Criar ordem baseada na ordem dos tipos
            ordem_manual = []
            for codigo in ['01', '02', '11', '03']:
                if codigo in mapeamento_ordem:
                    descricao = mapeamento_ordem[codigo]
                    if descricao in df_ordenado['Tipo de Entidade Descrição'].unique():
                        ordem_manual.append(descricao)
            
            # Configurar o layout para barras empilhadas
            fig.update_layout(
                barmode='stack',
                title=dict(
                    text='Distribuição por Padrão de Desempenho',
                    font=dict(size=20, family='Arial Black')
                ),
                xaxis_title=dict(
                    text='Percentual (%)',
                    font=dict(size=16)
                ),
                yaxis_title=dict(
                    text='Entidade',
                    font=dict(size=16)
                ),
                legend=dict(
                    title=dict(
                        text='Padrão de Desempenho',
                        font=dict(size=16)
                    ),
                    font=dict(size=14)
                ),
                font=dict(size=16),
                height=500,
                yaxis=dict(
                    categoryorder='array', 
                    categoryarray=ordem_manual,
                    tickfont=dict(size=15)
                ),
                xaxis=dict(
                    tickfont=dict(size=15)
                ),
                hoverlabel=dict(
                    font_size=16,
                    font_family="Arial"
                )
            )
            
            # Exibir o gráfico
            st.plotly_chart(fig, use_container_width=True)
            
            csv_desemp = df_desempenho.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Baixar Dados de Desempenho",
                data=csv_desemp,
                file_name="desempenho.csv",
                mime="text/csv",
                key="download_desempenho"
            )
    else:
        st.info("Colunas necessárias não encontradas para exibir distribuição de desempenho")
    
    # ==================== TAXA DE ACERTO POR HABILIDADE ====================
    colunas_habilidade = ['TP_ENTIDADE','DC_TIPO_ENTIDADE','NM_ENTIDADE','VL_FILTRO_DISCIPLINA','VL_FILTRO_ETAPA',
                         'TX_ACERTO','DC_HABILIDADE','CD_HABILIDADE_MODELO_02']
    
    if not df_concat.empty and all(col in df_concat.columns for col in colunas_habilidade):
        # Quebra de página antes da seção de habilidades (só se houver dados)
        st.markdown("""
        <div style="page-break-before: always; break-before: page;">
        </div>
        """, unsafe_allow_html=True)
        
        # Só exibir o header se houver dados
        st.markdown("""
        <div class="report-header" style="background: #d62728;">
            📚 TAXA DE ACERTO POR HABILIDADE
        </div>
        """, unsafe_allow_html=True)
        df_habilidade = df_concat[colunas_habilidade].copy()
        
        df_habilidade.columns = ['Tipo de Entidade Código', 'Tipo de Entidade', 'Entidade', 'Componente Curricular', 'Etapa', 
                                'Taxa de Acerto', 'Habilidade', 'Código Habilidade']
        
        # Converter Taxa de Acerto para numérico
        df_habilidade['Taxa de Acerto'] = pd.to_numeric(df_habilidade['Taxa de Acerto'], errors='coerce')
        
        # Criar gráfico de barras para taxa de acerto por habilidade
        if not df_habilidade.empty:
            st.subheader("Gráfico de Taxa de Acerto por Habilidade")
            
            # Remover valores NaN e ordenar por taxa de acerto
            df_habilidade_grafico = df_habilidade.dropna(subset=['Taxa de Acerto']).copy()
            
            if not df_habilidade_grafico.empty:
                # Criar gráfico de barras agrupadas
                fig_habilidade = go.Figure()
                
                # Mapear tipos de entidade para nomes amigáveis
                mapa_tipos = {
                    '01': 'Ceará',
                    '02': 'CREDE',
                    '11': 'Município',
                    '03': 'Escola',
                    'Estado': 'Ceará',
                    'Regional': 'CREDE',
                    'Município': 'Município',
                    'Escola': 'Escola'
                }
                
                # Criar coluna com tipo de entidade amigável
                df_habilidade_grafico['Tipo Simplificado'] = df_habilidade_grafico['Tipo de Entidade Código'].map(mapa_tipos)
                if df_habilidade_grafico['Tipo Simplificado'].isna().any():
                    df_habilidade_grafico['Tipo Simplificado'] = df_habilidade_grafico['Tipo Simplificado'].fillna(
                        df_habilidade_grafico['Tipo de Entidade'].map(mapa_tipos)
                    )
                
                # Agrupar por tipo de entidade e código de habilidade, calculando a média
                df_agrupado = df_habilidade_grafico.groupby(['Tipo Simplificado', 'Código Habilidade', 'Habilidade']).agg({
                    'Taxa de Acerto': 'mean'
                }).reset_index()
                
                # Obter tipos de entidade únicos na ordem correta
                ordem_tipos = ['Ceará', 'CREDE', 'Município', 'Escola']
                tipos_disponiveis = [t for t in ordem_tipos if t in df_agrupado['Tipo Simplificado'].unique()]
                
                # Cores fixas para cada tipo de entidade
                cores_tipos = {
                    'Ceará': '#e94f0e',
                    'CREDE': '#f59c00',
                    'Município': '#26a737',
                    'Escola': '#2db39e'
                }
                
                # Adicionar uma barra para cada tipo de entidade
                for tipo in tipos_disponiveis:
                    df_tipo = df_agrupado[df_agrupado['Tipo Simplificado'] == tipo]
                    
                    if not df_tipo.empty:
                        # Ordenar por código da habilidade para manter consistência
                        df_tipo = df_tipo.sort_values('Código Habilidade')
                        
                        fig_habilidade.add_trace(go.Bar(
                            name=tipo,
                            x=df_tipo['Código Habilidade'],
                            y=df_tipo['Taxa de Acerto'],
                            text=df_tipo['Taxa de Acerto'].round(1).astype(str) + '%',
                            textposition='auto',
                            textfont=dict(size=12, family='Arial', color='black'),
                            marker_color=cores_tipos.get(tipo, '#999999'),
                            hovertemplate='<b style="font-size:18px">%{fullData.name}</b><br><span style="font-size:16px">Código: %{x}<br>Taxa de Acerto: %{y:.1f}%<br>Habilidade: %{customdata}</span><extra></extra>',
                            customdata=df_tipo['Habilidade']
                        ))
                
                # Configurar o layout do gráfico
                fig_habilidade.update_layout(
                    title=dict(
                        text='Taxa de Acerto por Habilidade - Comparação entre Tipos de Entidade',
                        font=dict(size=20, family='Arial Black')
                    ),
                    xaxis_title=dict(
                        text='Código da Habilidade',
                        font=dict(size=16)
                    ),
                    yaxis_title=dict(
                        text='Taxa de Acerto (%)',
                        font=dict(size=16)
                    ),
                    legend=dict(
                        title=dict(
                            text='Tipo de Entidade',
                            font=dict(size=16)
                        ),
                        font=dict(size=14)
                    ),
                    font=dict(size=16),
                    height=500,
                    yaxis=dict(
                        range=[0, 100],
                        tickfont=dict(size=15)
                    ),
                    xaxis=dict(
                        tickfont=dict(size=15)
                    ),
                    barmode='group',
                    hoverlabel=dict(
                        font_size=18,
                        font_family="Arial"
                    )
                )
                
                # Exibir o gráfico
                st.plotly_chart(fig_habilidade, use_container_width=True)
            else:
                st.info("Sem dados válidos de taxa de acerto para criar o gráfico")
        else:
            st.info("Sem dados suficientes para criar o gráfico de habilidades")
        
        csv_hab = df_habilidade.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Baixar Dados de Habilidade",
            data=csv_hab,
            file_name="habilidade.csv",
            mime="text/csv",
            key="download_habilidade"
        )
    else:
        st.info("Colunas necessárias não encontradas para exibir taxa de acerto por habilidade")
    
    # Quebra de página antes da seção de etnia (removida para evitar páginas vazias)
    # st.markdown("""
    # <div style="page-break-before: always; break-before: page;">
    # </div>
    # """, unsafe_allow_html=True)
    
    # ==================== DADOS CONTEXTUAIS - ETNIA ====================
    colunas_etnia = ['TP_ENTIDADE','DC_TIPO_ENTIDADE','NM_ENTIDADE', 'VL_FILTRO_DISCIPLINA', 'VL_FILTRO_ETAPA', 'VL_PRETA',
                    'VL_BRANCA', 'VL_PARDA', 'VL_AMARELA', 'VL_INDIGENA','TX_PRETA','TX_BRANCA',
                    'TX_PARDA','TX_AMARELA','TX_INDIGENA','NU_PRETA','NU_BRANCA','NU_PARDA',
                    'NU_AMARELA','NU_INDIGENA']
    colunas_etnia_disponiveis = [col for col in colunas_etnia if col in df_concat.columns]
    
    if len(colunas_etnia_disponiveis) >= 4:
        # Quebra de página antes da seção de etnia (só se houver dados)
        st.markdown("""
        <div style="page-break-before: always; break-before: page;">
        </div>
        """, unsafe_allow_html=True)
        
        # Só exibir o header se houver dados
        st.markdown("""
        <div class="report-header" style="background: #2ca02c;">
            👥 PROFICIÊNCIA POR ETNIA
        </div>
        """, unsafe_allow_html=True)
        df_etnia = df_concat[colunas_etnia_disponiveis].copy()
        
        colunas_valores_etnia = ['VL_PRETA', 'VL_BRANCA', 'VL_PARDA', 'VL_AMARELA', 'VL_INDIGENA',
                                     'TX_PRETA','TX_BRANCA','TX_PARDA','TX_AMARELA','TX_INDIGENA',
                                     'NU_PRETA','NU_BRANCA','NU_PARDA','NU_AMARELA','NU_INDIGENA']
        df_etnia = converter_para_numerico(df_etnia, colunas_valores_etnia)
        
        colunas_etnia_valores = [col for col in colunas_valores_etnia if col in df_etnia.columns]
        if colunas_etnia_valores:
            df_etnia = df_etnia.dropna(subset=colunas_etnia_valores, how='all')
        
        if not df_etnia.empty:
            renomear = {
                'TP_ENTIDADE': 'Tipo de Entidade Código',
                'DC_TIPO_ENTIDADE': 'Tipo de Entidade',
                'NM_ENTIDADE': 'Entidade',
                'VL_FILTRO_DISCIPLINA': 'Componente Curricular',
                'VL_FILTRO_ETAPA': 'Etapa',
                'VL_PRETA': 'Proficiência Preta',
                'VL_BRANCA': 'Proficiência Branca',
                'VL_PARDA': 'Proficiência Parda',
                'VL_AMARELA': 'Proficiência Amarela',
                'VL_INDIGENA': 'Proficiência Indígena',
                'TX_PRETA': 'Taxa Preta',
                'TX_BRANCA': 'Taxa Branca',
                'TX_PARDA': 'Taxa Parda',
                'TX_AMARELA': 'Taxa Amarela',
                'TX_INDIGENA': 'Taxa Indígena',
                'NU_PRETA': 'Número Preta',
                'NU_BRANCA': 'Número Branca',
                'NU_PARDA': 'Número Parda',
                'NU_AMARELA': 'Número Amarela',
                'NU_INDIGENA': 'Número Indígena'
            }
            df_etnia = df_etnia.rename(columns={k: v for k, v in renomear.items() if k in df_etnia.columns})
            
            st.info(f"📊 {len(df_etnia)} registros com dados de proficiência por etnia")
            
            csv_etnia = df_etnia.to_csv(index=False).encode('utf-8')
            
            # Criar gráfico de barras para taxa e proficiência por Etnia
            st.subheader("Gráfico de Taxa e Proficiência por Etnia - Por Tipo de Entidade")
            
            # Verificar quais colunas estão disponíveis
            colunas_taxa_etnia = [col for col in ['Taxa Preta', 'Taxa Branca', 
                                                'Taxa Parda', 'Taxa Amarela', 
                                                'Taxa Indígena'] if col in df_etnia.columns]
            
            colunas_prof_etnia = [col for col in ['Proficiência Preta', 'Proficiência Branca', 
                                                'Proficiência Parda', 'Proficiência Amarela', 
                                                'Proficiência Indígena'] if col in df_etnia.columns]
            
            if colunas_taxa_etnia and colunas_prof_etnia and ('Tipo de Entidade Código' in df_etnia.columns or 'Tipo de Entidade' in df_etnia.columns):
                # Preparar dados para o gráfico
                df_plot = df_etnia.copy()
                
                # Mapear tipos de entidade para nomes amigáveis
                mapa_tipos = {
                    '01': 'Ceará',
                    '02': 'CREDE',
                    '11': 'Município',
                    '03': 'Escola',
                    'Estado': 'Ceará',
                    'Regional': 'CREDE',
                    'Município': 'Município',
                    'Escola': 'Escola'
                }
                
                # Criar coluna com tipo de entidade amigável
                if 'Tipo de Entidade Código' in df_plot.columns:
                    df_plot['Tipo Simplificado'] = df_plot['Tipo de Entidade Código'].map(mapa_tipos)
                    if df_plot['Tipo Simplificado'].isna().any() and 'Tipo de Entidade' in df_plot.columns:
                        df_plot['Tipo Simplificado'] = df_plot['Tipo Simplificado'].fillna(
                            df_plot['Tipo de Entidade'].map(mapa_tipos)
                        )
                elif 'Tipo de Entidade' in df_plot.columns:
                    df_plot['Tipo Simplificado'] = df_plot['Tipo de Entidade'].map(mapa_tipos)
                
                # Incluir colunas de número
                colunas_numero_etnia = [col for col in ['Número Preta', 'Número Branca', 
                                                    'Número Parda', 'Número Amarela', 
                                                    'Número Indígena'] if col in df_etnia.columns]
                
                # Agrupar por tipo de entidade e calcular a média
                todas_colunas = colunas_taxa_etnia + colunas_prof_etnia + colunas_numero_etnia
                df_plot = df_plot.groupby('Tipo Simplificado')[todas_colunas].mean().reset_index()
                
                # Criar lista de dados para o gráfico
                dados_grafico = []
                
                # Categorias de etnia
                categorias = {
                    'Preta': {'taxa': 'Taxa Preta', 'prof': 'Proficiência Preta', 'numero': 'Número Preta', 'cor_base': '#2ca02c'},
                    'Branca': {'taxa': 'Taxa Branca', 'prof': 'Proficiência Branca', 'numero': 'Número Branca', 'cor_base': '#ff7f0e'},
                    'Parda': {'taxa': 'Taxa Parda', 'prof': 'Proficiência Parda', 'numero': 'Número Parda', 'cor_base': '#2ca02c'},
                    'Amarela': {'taxa': 'Taxa Amarela', 'prof': 'Proficiência Amarela', 'numero': 'Número Amarela', 'cor_base': '#d62728'},
                    'Indígena': {'taxa': 'Taxa Indígena', 'prof': 'Proficiência Indígena', 'numero': 'Número Indígena', 'cor_base': '#9467bd'}
                }
                
                # Função para calcular cor baseada na proficiência (laranja -> verde)
                def calcular_cor_intensidade(cor_base_hex, proficiencia, prof_min, prof_max):
                    """Calcula a cor variando de laranja (baixa proficiência) a verde (alta proficiência)"""
                    # Cores: Laranja para proficiência baixa, Verde para proficiência alta
                    # Laranja: #FF6B35 (255, 107, 53)
                    # Amarelo intermediário: #FFB830 (255, 184, 48)
                    # Verde claro: #87C147 (135, 193, 71)
                    # Verde escuro: #2E7D32 (46, 125, 50)
                    
                    # Normalizar proficiência entre 0 e 1
                    if prof_max > prof_min:
                        normalizado = (proficiencia - prof_min) / (prof_max - prof_min)
                    else:
                        normalizado = 0.5
                    
                    # Interpolar cores de acordo com a proficiência
                    if normalizado < 0.33:  # Laranja a Amarelo
                        # Escalar de 0-0.33 para 0-1
                        t = normalizado / 0.33
                        r = int(255)  # Mantém vermelho alto
                        g = int(107 + (184 - 107) * t)  # De 107 a 184
                        b = int(53 + (48 - 53) * t)  # De 53 a 48
                    elif normalizado < 0.67:  # Amarelo a Verde claro
                        # Escalar de 0.33-0.67 para 0-1
                        t = (normalizado - 0.33) / 0.34
                        r = int(255 - (255 - 135) * t)  # De 255 a 135
                        g = int(184 + (193 - 184) * t)  # De 184 a 193
                        b = int(48 + (71 - 48) * t)  # De 48 a 71
                    else:  # Verde claro a Verde escuro
                        # Escalar de 0.67-1.0 para 0-1
                        t = (normalizado - 0.67) / 0.33
                        r = int(135 - (135 - 46) * t)  # De 135 a 46
                        g = int(193 - (193 - 125) * t)  # De 193 a 125
                        b = int(71 - (71 - 50) * t)  # De 71 a 50
                    
                    return f'rgb({r},{g},{b})'
                
                # Calcular proficiência mínima e máxima para normalização
                todas_proficiencias = []
                for cat_info in categorias.values():
                    if cat_info['prof'] in df_plot.columns:
                        todas_proficiencias.extend(df_plot[cat_info['prof']].dropna().tolist())
                
                prof_min = min(todas_proficiencias) if todas_proficiencias else 0
                prof_max = max(todas_proficiencias) if todas_proficiencias else 100
                
                # Preparar dados para cada tipo de entidade e categoria
                for tipo_entidade in df_plot['Tipo Simplificado']:
                    for cat_nome, cat_info in categorias.items():
                        if cat_info['taxa'] in df_plot.columns and cat_info['prof'] in df_plot.columns and cat_info['numero'] in df_plot.columns:
                            dados_tipo = df_plot[df_plot['Tipo Simplificado'] == tipo_entidade]
                            if not dados_tipo.empty:
                                taxa = dados_tipo[cat_info['taxa']].values[0]
                                proficiencia = dados_tipo[cat_info['prof']].values[0]
                                numero = dados_tipo[cat_info['numero']].values[0]
                                
                                if pd.notna(taxa) and pd.notna(proficiencia) and pd.notna(numero):
                                    cor = calcular_cor_intensidade(cat_info['cor_base'], proficiencia, prof_min, prof_max)
                                    
                                    dados_grafico.append({
                                        'Tipo de Entidade': tipo_entidade,
                                        'Etnia': cat_nome,
                                        'Taxa': taxa,
                                        'Proficiência': proficiencia,
                                        'Numero': numero,
                                        'Cor': cor,
                                        'Label': f"{cat_nome}<br>{taxa:.1f}%"
                                    })
                
                # Criar DataFrame dos dados
                df_grafico = pd.DataFrame(dados_grafico)
                
                if not df_grafico.empty:
                    # Criar gráfico
                    fig_etnia = go.Figure()
                    
                    # Definir ordem dos tipos de entidade
                    ordem_tipos = ['Ceará', 'CREDE', 'Município', 'Escola']
                    
                    # Adicionar barras para cada etnia
                    categorias_etnias = df_grafico['Etnia'].unique()
                    
                    for etnia in categorias_etnias:
                        df_etnia_cat = df_grafico[df_grafico['Etnia'] == etnia].copy()
                        
                        # Ordenar pelo tipo de entidade usando a ordem definida
                        df_etnia_cat['Ordem'] = df_etnia_cat['Tipo de Entidade'].map({t: i for i, t in enumerate(ordem_tipos)})
                        df_etnia_cat = df_etnia_cat.sort_values('Ordem')
                        
                        fig_etnia.add_trace(go.Bar(
                            name=etnia,
                            x=df_etnia_cat['Tipo de Entidade'],
                            y=df_etnia_cat['Taxa'],
                            marker=dict(
                                color=df_etnia_cat['Cor'].tolist(),
                                line=dict(color='rgba(0,0,0,0.3)', width=1)
                            ),
                            text=[f"{e}<br>{t:.1f}%<br>Prof: {p:.0f}<br>N: {n:.0f}" for e, t, p, n in zip(df_etnia_cat['Etnia'], df_etnia_cat['Taxa'], df_etnia_cat['Proficiência'], df_etnia_cat['Numero'])],
                            textposition='outside',
                            textfont=dict(size=12, family='Arial', color='black'),
                            textangle=-90,
                            hovertemplate='<b style="font-size:18px">Tipo: %{x}</b><br><span style="font-size:16px">Etnia: ' + etnia + '<br>Percentual de Alunos: %{y:.1f}%<br>Proficiência: %{customdata[0]:.1f}<br>Número de Alunos: %{customdata[1]:,}</span><extra></extra>',
                            customdata=list(zip(df_etnia_cat['Proficiência'], df_etnia_cat['Numero'])),
                            showlegend=False
                        ))
                    
                    # Tipos disponíveis na ordem correta
                    tipos_disponiveis = [t for t in ordem_tipos if t in df_grafico['Tipo de Entidade'].unique()]
                    
                    # Configurar o layout do gráfico
                    fig_etnia.update_layout(
                        title=dict(
                            text=f'👥 Taxa (altura) e Proficiência (cor) por Etnia<br><sub style="font-size:14px;">🟠 Laranja = Proficiência Baixa | 🟡 Amarelo = Proficiência Média | 🟢 Verde = Proficiência Alta | Escala: {prof_min:.0f} - {prof_max:.0f}</sub>',
                            font=dict(size=20, family='Arial Black')
                        ),
                        xaxis_title=dict(
                            text='Tipo de Entidade',
                            font=dict(size=18)
                        ),
                        yaxis_title=dict(
                            text='Taxa (%)',
                            font=dict(size=18)
                        ),
                        font=dict(size=16),
                        height=600,
                        barmode='group',
                        bargap=0.2,
                        bargroupgap=0.15,
                        yaxis=dict(
                            range=[0, 110],
                            tickfont=dict(size=16)
                        ),
                        showlegend=False,
                        xaxis=dict(
                            categoryorder='array',
                            categoryarray=tipos_disponiveis,
                            tickfont=dict(size=16)
                        ),
                        hoverlabel=dict(
                            font_size=20,
                            font_family="Arial"
                        )
                    )
                    
                    # Exibir o gráfico
                    st.plotly_chart(fig_etnia, use_container_width=True)
                else:
                    st.info("Não foi possível gerar o gráfico com os dados disponíveis")
            else:
                st.info("Dados de taxa e proficiência por etnia insuficientes para gerar o gráfico ou coluna de tipo de entidade não disponível")
            
            st.download_button(
                "📥 Baixar Dados de Etnia",
                data=csv_etnia,
                file_name="proficiencia_etnia.csv",
                mime="text/csv",
                key="download_etnia"
            )
        else:
            st.info("Sem dados válidos de proficiência por etnia após limpeza")
    else:
        st.info("Colunas de etnia não encontradas no conjunto de dados")
    
    # Quebra de página antes da seção de NSE (removida para evitar páginas vazias)
    # st.markdown("""
    # <div style="page-break-before: always; break-before: page;">
    # </div>
    # """, unsafe_allow_html=True)
    
    # ==================== DADOS CONTEXTUAIS - NSE ====================
    colunas_nse = ['TP_ENTIDADE', 'DC_TIPO_ENTIDADE', 'NM_ENTIDADE', 'VL_FILTRO_DISCIPLINA', 'VL_FILTRO_ETAPA', 'VL_NSE1', 
                   'VL_NSE2', 'VL_NSE3', 'VL_NSE4', 'TX_NSE1','TX_NSE2','TX_NSE3','TX_NSE4',
                   'NU_NSE1','NU_NSE2','NU_NSE3','NU_NSE4']
    colunas_nse_disponiveis = [col for col in colunas_nse if col in df_concat.columns]
    
    if len(colunas_nse_disponiveis) >= 4:
        # Quebra de página antes da seção de NSE (só se houver dados)
        st.markdown("""
        <div style="page-break-before: always; break-before: page;">
        </div>
        """, unsafe_allow_html=True)
        
        # Só exibir o header se houver dados
        st.markdown("""
        <div class="report-header" style="background: #ff7f0e;">
            💰 PROFICIÊNCIA POR NÍVEL SOCIOECONÔMICO (NSE)
        </div>
        """, unsafe_allow_html=True)
        df_nse = df_concat[colunas_nse_disponiveis].copy()
        
        colunas_valores_nse = ['VL_NSE1', 'VL_NSE2', 'VL_NSE3', 'VL_NSE4', 
                              'NU_NSE1', 'NU_NSE2', 'NU_NSE3', 'NU_NSE4',
                              'TX_NSE1','TX_NSE2','TX_NSE3','TX_NSE4']
        df_nse = converter_para_numerico(df_nse, colunas_valores_nse)
        
        colunas_nse_valores = [col for col in colunas_valores_nse if col in df_nse.columns]
        if colunas_nse_valores:
            df_nse = df_nse.dropna(subset=colunas_nse_valores, how='all')
        
        if not df_nse.empty:
            renomear = {
                'TP_ENTIDADE': 'Tipo de Entidade Código',
                'DC_TIPO_ENTIDADE': 'Tipo de Entidade',
                'NM_ENTIDADE': 'Entidade',
                'VL_FILTRO_DISCIPLINA': 'Componente Curricular',
                'VL_FILTRO_ETAPA': 'Etapa',
                'VL_NSE1': 'Proficiência NSE 1 (Mais Baixo)',
                'VL_NSE2': 'Proficiência NSE 2',
                'VL_NSE3': 'Proficiência NSE 3',
                'VL_NSE4': 'Proficiência NSE 4 (Mais Alto)',
                'NU_NSE1': 'Número NSE 1',
                'NU_NSE2': 'Número NSE 2',
                'NU_NSE3': 'Número NSE 3',
                'NU_NSE4': 'Número NSE 4',
                'TX_NSE1': 'Taxa NSE 1',
                'TX_NSE2': 'Taxa NSE 2',
                'TX_NSE3': 'Taxa NSE 3',
                'TX_NSE4': 'Taxa NSE 4'
            }
            df_nse = df_nse.rename(columns={k: v for k, v in renomear.items() if k in df_nse.columns})
            
            st.info(f"📊 {len(df_nse)} registros com dados de proficiência por NSE")
            # st.dataframe(df_nse, use_container_width=True, height=400)
            
            # Criar gráfico para NSE
            st.subheader("Gráfico de Taxa e Proficiência por NSE - Por Tipo de Entidade")
            
            # Verificar quais colunas estão disponíveis
            colunas_taxa_nse = [col for col in ['Taxa NSE 1', 'Taxa NSE 2', 
                                                'Taxa NSE 3', 'Taxa NSE 4'] if col in df_nse.columns]
            
            colunas_prof_nse = [col for col in ['Proficiência NSE 1 (Mais Baixo)', 'Proficiência NSE 2', 
                                                'Proficiência NSE 3', 'Proficiência NSE 4 (Mais Alto)'] if col in df_nse.columns]
            
            if colunas_taxa_nse and colunas_prof_nse and ('Tipo de Entidade Código' in df_nse.columns or 'Tipo de Entidade' in df_nse.columns):
                # Preparar dados para o gráfico
                df_plot_nse = df_nse.copy()
                
                # Mapear tipos de entidade para nomes amigáveis
                mapa_tipos = {
                    '01': 'Ceará',
                    '02': 'CREDE',
                    '11': 'Município',
                    '03': 'Escola',
                    'Estado': 'Ceará',
                    'Regional': 'CREDE',
                    'Município': 'Município',
                    'Escola': 'Escola'
                }
                
                # Criar coluna com tipo de entidade amigável
                if 'Tipo de Entidade Código' in df_plot_nse.columns:
                    df_plot_nse['Tipo Simplificado'] = df_plot_nse['Tipo de Entidade Código'].map(mapa_tipos)
                    if df_plot_nse['Tipo Simplificado'].isna().any() and 'Tipo de Entidade' in df_plot_nse.columns:
                        df_plot_nse['Tipo Simplificado'] = df_plot_nse['Tipo Simplificado'].fillna(
                            df_plot_nse['Tipo de Entidade'].map(mapa_tipos)
                        )
                elif 'Tipo de Entidade' in df_plot_nse.columns:
                    df_plot_nse['Tipo Simplificado'] = df_plot_nse['Tipo de Entidade'].map(mapa_tipos)
                
                # Agrupar por tipo de entidade e calcular a média
                colunas_numero_nse = [col for col in ['Número NSE 1', 'Número NSE 2', 
                                                    'Número NSE 3', 'Número NSE 4'] if col in df_plot_nse.columns]
                todas_colunas_nse = colunas_taxa_nse + colunas_prof_nse + colunas_numero_nse
                df_plot_nse = df_plot_nse.groupby('Tipo Simplificado')[todas_colunas_nse].mean().reset_index()
                
                # Criar lista de dados para o gráfico
                dados_grafico_nse = []
                
                # Categorias de NSE
                categorias_nse = {
                     'NSE 1 (Mais Baixo)': {'taxa': 'Taxa NSE 1', 'prof': 'Proficiência NSE 1 (Mais Baixo)', 'numero': 'Número NSE 1', 'cor_base': '#d62728'},
                     'NSE 2': {'taxa': 'Taxa NSE 2', 'prof': 'Proficiência NSE 2', 'numero': 'Número NSE 2', 'cor_base': '#ff7f0e'},
                     'NSE 3': {'taxa': 'Taxa NSE 3', 'prof': 'Proficiência NSE 3', 'numero': 'Número NSE 3', 'cor_base': '#2ca02c'},
                     'NSE 4 (Mais Alto)': {'taxa': 'Taxa NSE 4', 'prof': 'Proficiência NSE 4 (Mais Alto)', 'numero': 'Número NSE 4', 'cor_base': '#2ca02c'}
                }
                
                # Função para calcular cor baseada na proficiência
                def calcular_cor_intensidade_nse(cor_base_hex, proficiencia, prof_min, prof_max):
                    if prof_max > prof_min:
                        normalizado = (proficiencia - prof_min) / (prof_max - prof_min)
                    else:
                        normalizado = 0.5
                    
                    if normalizado < 0.33:
                        t = normalizado / 0.33
                        r = int(255)
                        g = int(107 + (184 - 107) * t)
                        b = int(53 + (48 - 53) * t)
                    elif normalizado < 0.67:
                        t = (normalizado - 0.33) / 0.34
                        r = int(255 - (255 - 135) * t)
                        g = int(184 + (193 - 184) * t)
                        b = int(48 + (71 - 48) * t)
                    else:
                        t = (normalizado - 0.67) / 0.33
                        r = int(135 - (135 - 46) * t)
                        g = int(193 - (193 - 125) * t)
                        b = int(71 - (71 - 50) * t)
                    
                    return f'rgb({r},{g},{b})'
                
                # Calcular proficiência mínima e máxima
                todas_proficiencias_nse = []
                for cat_info in categorias_nse.values():
                    if cat_info['prof'] in df_plot_nse.columns:
                        todas_proficiencias_nse.extend(df_plot_nse[cat_info['prof']].dropna().tolist())
                
                prof_min_nse = min(todas_proficiencias_nse) if todas_proficiencias_nse else 0
                prof_max_nse = max(todas_proficiencias_nse) if todas_proficiencias_nse else 100
                
                # Preparar dados para cada tipo de entidade e categoria
                for tipo_entidade in df_plot_nse['Tipo Simplificado']:
                    for cat_nome, cat_info in categorias_nse.items():
                        if cat_info['taxa'] in df_plot_nse.columns and cat_info['prof'] in df_plot_nse.columns and cat_info['numero'] in df_plot_nse.columns:
                            dados_tipo = df_plot_nse[df_plot_nse['Tipo Simplificado'] == tipo_entidade]
                            if not dados_tipo.empty:
                                taxa = dados_tipo[cat_info['taxa']].values[0]
                                proficiencia = dados_tipo[cat_info['prof']].values[0]
                                numero = dados_tipo[cat_info['numero']].values[0]
                                
                                if pd.notna(taxa) and pd.notna(proficiencia) and pd.notna(numero):
                                    cor = calcular_cor_intensidade_nse(cat_info['cor_base'], proficiencia, prof_min_nse, prof_max_nse)
                                    
                                    dados_grafico_nse.append({
                                        'Tipo de Entidade': tipo_entidade,
                                        'NSE': cat_nome,
                                        'Taxa': taxa,
                                        'Proficiência': proficiencia,
                                        'Numero': numero,
                                        'Cor': cor,
                                        'Label': f"{cat_nome}<br>{taxa:.1f}%"
                                    })
                
                # Criar DataFrame dos dados
                df_grafico_nse = pd.DataFrame(dados_grafico_nse)
                
                if not df_grafico_nse.empty:
                    # Criar gráfico
                    fig_nse = go.Figure()
                    
                    # Definir ordem dos tipos de entidade
                    ordem_tipos = ['Ceará', 'CREDE', 'Município', 'Escola']
                    
                    # Adicionar barras para cada NSE
                    categorias_nse_grafico = df_grafico_nse['NSE'].unique()
                    
                    for nse in categorias_nse_grafico:
                        df_nse_cat = df_grafico_nse[df_grafico_nse['NSE'] == nse].copy()
                        
                        # Ordenar pelo tipo de entidade
                        df_nse_cat['Ordem'] = df_nse_cat['Tipo de Entidade'].map({t: i for i, t in enumerate(ordem_tipos)})
                        df_nse_cat = df_nse_cat.sort_values('Ordem')
                        
                        fig_nse.add_trace(go.Bar(
                            name=nse,
                            x=df_nse_cat['Tipo de Entidade'],
                            y=df_nse_cat['Taxa'],
                            marker=dict(
                                color=df_nse_cat['Cor'].tolist(),
                                line=dict(color='rgba(0,0,0,0.3)', width=1)
                            ),
                             text=[f"{n}<br>{t:.1f}%<br>Prof: {p:.0f}<br>N: {num:.0f}" for n, t, p, num in zip(df_nse_cat['NSE'], df_nse_cat['Taxa'], df_nse_cat['Proficiência'], df_nse_cat['Numero'])],
                             textposition='outside',
                             textfont=dict(size=12, family='Arial', color='black'),
                             textangle=-90,
                            hovertemplate='<b style="font-size:18px">Tipo: %{x}</b><br><span style="font-size:16px">NSE: ' + nse + '<br>Taxa: %{y:.1f}%<br>Proficiência: %{customdata:.1f}</span><extra></extra>',
                            customdata=df_nse_cat['Proficiência'],
                            showlegend=False
                        ))
                    
                    # Tipos disponíveis na ordem correta
                    tipos_disponiveis_nse = [t for t in ordem_tipos if t in df_grafico_nse['Tipo de Entidade'].unique()]
                    
                    # Configurar o layout do gráfico
                    fig_nse.update_layout(
                        title=dict(
                            text=f'📊 Taxa (altura) e Proficiência (cor) por NSE<br><sub style="font-size:14px;">🟠 Laranja = Proficiência Baixa | 🟡 Amarelo = Proficiência Média | 🟢 Verde = Proficiência Alta | Escala: {prof_min_nse:.0f} - {prof_max_nse:.0f}</sub>',
                            font=dict(size=20, family='Arial Black')
                        ),
                        xaxis_title=dict(
                            text='Tipo de Entidade',
                            font=dict(size=18)
                        ),
                        yaxis_title=dict(
                            text='Taxa (%)',
                            font=dict(size=18)
                        ),
                        font=dict(size=16),
                        height=600,
                        barmode='group',
                        bargap=0.2,
                        bargroupgap=0.15,
                        yaxis=dict(
                            range=[0, 110],
                            tickfont=dict(size=16)
                        ),
                        showlegend=False,
                        xaxis=dict(
                            categoryorder='array',
                            categoryarray=tipos_disponiveis_nse,
                            tickfont=dict(size=16)
                        ),
                        hoverlabel=dict(
                            font_size=20,
                            font_family="Arial"
                        )
                    )
                    
                    # Exibir o gráfico
                    st.plotly_chart(fig_nse, use_container_width=True)
                else:
                    st.info("Não foi possível gerar o gráfico com os dados disponíveis")
            else:
                st.info("Dados de taxa e proficiência por NSE insuficientes para gerar o gráfico ou coluna de tipo de entidade não disponível")
            
            csv_nse = df_nse.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Baixar Dados de NSE",
                data=csv_nse,
                file_name="proficiencia_nse.csv",
                mime="text/csv",
                key="download_nse"
            )
    
    # ==================== DADOS CONTEXTUAIS - SEXO ====================
    colunas_sexo = ['TP_ENTIDADE', 'DC_TIPO_ENTIDADE', 'NM_ENTIDADE', 'VL_FILTRO_DISCIPLINA', 'VL_FILTRO_ETAPA', 'VL_FEMININO', 
                   'VL_MASCULINO', 'TX_FEMININO','TX_MASCULINO','NU_FEMININO','NU_MASCULINO']
    colunas_sexo_disponiveis = [col for col in colunas_sexo if col in df_concat.columns]
    
    if len(colunas_sexo_disponiveis) >= 4:
        # Quebra de página antes da seção de sexo (só se houver dados)
        st.markdown("""
        <div style="page-break-before: always; break-before: page;">
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="report-header" style="background: #2ca02c;">
            👫 PROFICIÊNCIA POR SEXO
        </div>
        """, unsafe_allow_html=True)
        df_sexo = df_concat[colunas_sexo_disponiveis].copy()
        
        colunas_valores_sexo = ['VL_FEMININO', 'VL_MASCULINO', 'NU_FEMININO', 
                               'NU_MASCULINO', 'TX_FEMININO', 'TX_MASCULINO']
        df_sexo = converter_para_numerico(df_sexo, colunas_valores_sexo)
        
        colunas_sexo_valores = [col for col in colunas_valores_sexo if col in df_sexo.columns]
        if colunas_sexo_valores:
            df_sexo = df_sexo.dropna(subset=colunas_sexo_valores, how='all')
        
        if not df_sexo.empty:
            renomear = {
                'TP_ENTIDADE': 'Tipo de Entidade Código',
                'DC_TIPO_ENTIDADE': 'Tipo de Entidade',
                'NM_ENTIDADE': 'Entidade',
                'VL_FILTRO_DISCIPLINA': 'Componente Curricular',
                'VL_FILTRO_ETAPA': 'Etapa',
                'VL_FEMININO': 'Proficiência Feminino',
                'VL_MASCULINO': 'Proficiência Masculino',
                'NU_FEMININO': 'Número Feminino',
                'NU_MASCULINO': 'Número Masculino',
                'TX_FEMININO': 'Taxa Feminino',
                'TX_MASCULINO': 'Taxa Masculino'
            }
            df_sexo = df_sexo.rename(columns={k: v for k, v in renomear.items() if k in df_sexo.columns})
            
            st.info(f"📊 {len(df_sexo)} registros com dados de proficiência por sexo")
            # st.dataframe(df_sexo, use_container_width=True, height=400)
            
            # Criar gráfico para Sexo
            st.subheader("Gráfico de Taxa e Proficiência por Sexo - Por Tipo de Entidade")
            
            # Verificar quais colunas estão disponíveis
            colunas_taxa_sexo = [col for col in ['Taxa Feminino', 'Taxa Masculino'] if col in df_sexo.columns]
            
            colunas_prof_sexo = [col for col in ['Proficiência Feminino', 'Proficiência Masculino'] if col in df_sexo.columns]
            
            if colunas_taxa_sexo and colunas_prof_sexo and ('Tipo de Entidade Código' in df_sexo.columns or 'Tipo de Entidade' in df_sexo.columns):
                # Preparar dados para o gráfico
                df_plot_sexo = df_sexo.copy()
                
                # Mapear tipos de entidade para nomes amigáveis
                mapa_tipos = {
                    '01': 'Ceará',
                    '02': 'CREDE',
                    '11': 'Município',
                    '03': 'Escola',
                    'Estado': 'Ceará',
                    'Regional': 'CREDE',
                    'Município': 'Município',
                    'Escola': 'Escola'
                }
                
                # Criar coluna com tipo de entidade amigável
                if 'Tipo de Entidade Código' in df_plot_sexo.columns:
                    df_plot_sexo['Tipo Simplificado'] = df_plot_sexo['Tipo de Entidade Código'].map(mapa_tipos)
                    if df_plot_sexo['Tipo Simplificado'].isna().any() and 'Tipo de Entidade' in df_plot_sexo.columns:
                        df_plot_sexo['Tipo Simplificado'] = df_plot_sexo['Tipo Simplificado'].fillna(
                            df_plot_sexo['Tipo de Entidade'].map(mapa_tipos)
                        )
                elif 'Tipo de Entidade' in df_plot_sexo.columns:
                    df_plot_sexo['Tipo Simplificado'] = df_plot_sexo['Tipo de Entidade'].map(mapa_tipos)
                
                # Agrupar por tipo de entidade e calcular a média
                colunas_numero_sexo = [col for col in ['Número Feminino', 'Número Masculino'] if col in df_plot_sexo.columns]
                todas_colunas_sexo = colunas_taxa_sexo + colunas_prof_sexo + colunas_numero_sexo
                df_plot_sexo = df_plot_sexo.groupby('Tipo Simplificado')[todas_colunas_sexo].mean().reset_index()
                
                # Criar lista de dados para o gráfico
                dados_grafico_sexo = []
                
                # Categorias de Sexo
                categorias_sexo = {
                    'Feminino': {'taxa': 'Taxa Feminino', 'prof': 'Proficiência Feminino', 'numero': 'Número Feminino', 'cor_base': '#ff7f0e'},
                    'Masculino': {'taxa': 'Taxa Masculino', 'prof': 'Proficiência Masculino', 'numero': 'Número Masculino', 'cor_base': '#2ca02c'}
                }
                
                # Função para calcular cor baseada na proficiência
                def calcular_cor_intensidade_sexo(cor_base_hex, proficiencia, prof_min, prof_max):
                    if prof_max > prof_min:
                        normalizado = (proficiencia - prof_min) / (prof_max - prof_min)
                    else:
                        normalizado = 0.5
                    
                    if normalizado < 0.33:
                        t = normalizado / 0.33
                        r = int(255)
                        g = int(107 + (184 - 107) * t)
                        b = int(53 + (48 - 53) * t)
                    elif normalizado < 0.67:
                        t = (normalizado - 0.33) / 0.34
                        r = int(255 - (255 - 135) * t)
                        g = int(184 + (193 - 184) * t)
                        b = int(48 + (71 - 48) * t)
                    else:
                        t = (normalizado - 0.67) / 0.33
                        r = int(135 - (135 - 46) * t)
                        g = int(193 - (193 - 125) * t)
                        b = int(71 - (71 - 50) * t)
                    
                    return f'rgb({r},{g},{b})'
                
                # Calcular proficiência mínima e máxima
                todas_proficiencias_sexo = []
                for cat_info in categorias_sexo.values():
                    if cat_info['prof'] in df_plot_sexo.columns:
                        todas_proficiencias_sexo.extend(df_plot_sexo[cat_info['prof']].dropna().tolist())
                
                prof_min_sexo = min(todas_proficiencias_sexo) if todas_proficiencias_sexo else 0
                prof_max_sexo = max(todas_proficiencias_sexo) if todas_proficiencias_sexo else 100
                
                # Preparar dados para cada tipo de entidade e categoria
                for tipo_entidade in df_plot_sexo['Tipo Simplificado']:
                    for cat_nome, cat_info in categorias_sexo.items():
                        if cat_info['taxa'] in df_plot_sexo.columns and cat_info['prof'] in df_plot_sexo.columns and cat_info['numero'] in df_plot_sexo.columns:
                            dados_tipo = df_plot_sexo[df_plot_sexo['Tipo Simplificado'] == tipo_entidade]
                            if not dados_tipo.empty:
                                taxa = dados_tipo[cat_info['taxa']].values[0]
                                proficiencia = dados_tipo[cat_info['prof']].values[0]
                                numero = dados_tipo[cat_info['numero']].values[0]
                                
                                if pd.notna(taxa) and pd.notna(proficiencia) and pd.notna(numero):
                                    cor = calcular_cor_intensidade_sexo(cat_info['cor_base'], proficiencia, prof_min_sexo, prof_max_sexo)
                                    
                                    dados_grafico_sexo.append({
                                        'Tipo de Entidade': tipo_entidade,
                                        'Sexo': cat_nome,
                                        'Taxa': taxa,
                                        'Proficiência': proficiencia,
                                        'Numero': numero,
                                        'Cor': cor,
                                        'Label': f"{cat_nome}<br>{taxa:.1f}%"
                                    })
                
                # Criar DataFrame dos dados
                df_grafico_sexo = pd.DataFrame(dados_grafico_sexo)
                
                if not df_grafico_sexo.empty:
                    # Criar gráfico
                    fig_sexo = go.Figure()
                    
                    # Definir ordem dos tipos de entidade
                    ordem_tipos = ['Ceará', 'CREDE', 'Município', 'Escola']
                    
                    # Adicionar barras para cada Sexo
                    categorias_sexo_grafico = df_grafico_sexo['Sexo'].unique()
                    
                    for sexo in categorias_sexo_grafico:
                        df_sexo_cat = df_grafico_sexo[df_grafico_sexo['Sexo'] == sexo].copy()
                        
                        # Ordenar pelo tipo de entidade
                        df_sexo_cat['Ordem'] = df_sexo_cat['Tipo de Entidade'].map({t: i for i, t in enumerate(ordem_tipos)})
                        df_sexo_cat = df_sexo_cat.sort_values('Ordem')
                        
                        fig_sexo.add_trace(go.Bar(
                            name=sexo,
                            x=df_sexo_cat['Tipo de Entidade'],
                            y=df_sexo_cat['Taxa'],
                            marker=dict(
                                color=df_sexo_cat['Cor'].tolist(),
                                line=dict(color='rgba(0,0,0,0.3)', width=1)
                            ),
                            text=[f"{s}<br>{t:.1f}%<br>Prof: {p:.0f}<br>N: {num:.0f}" for s, t, p, num in zip(df_sexo_cat['Sexo'], df_sexo_cat['Taxa'], df_sexo_cat['Proficiência'], df_sexo_cat['Numero'])],
                            textposition='outside',
                            textfont=dict(size=12, family='Arial', color='black'),
                            textangle=-90,
                            hovertemplate='<b style="font-size:18px">Tipo: %{x}</b><br><span style="font-size:16px">Sexo: ' + sexo + '<br>Taxa: %{y:.1f}%<br>Proficiência: %{customdata:.1f}</span><extra></extra>',
                            customdata=df_sexo_cat['Proficiência'],
                            showlegend=False
                        ))
                    
                    # Tipos disponíveis na ordem correta
                    tipos_disponiveis_sexo = [t for t in ordem_tipos if t in df_grafico_sexo['Tipo de Entidade'].unique()]
                    
                    # Configurar o layout do gráfico
                    fig_sexo.update_layout(
                        title=dict(
                            text=f'👫 Taxa (altura) e Proficiência (cor) por Sexo<br><sub style="font-size:14px;">🟠 Laranja = Proficiência Baixa | 🟡 Amarelo = Proficiência Média | 🟢 Verde = Proficiência Alta | Escala: {prof_min_sexo:.0f} - {prof_max_sexo:.0f}</sub>',
                            font=dict(size=20, family='Arial Black')
                        ),
                        xaxis_title=dict(
                            text='Tipo de Entidade',
                            font=dict(size=18)
                        ),
                        yaxis_title=dict(
                            text='Taxa (%)',
                            font=dict(size=18)
                        ),
                        font=dict(size=16),
                        height=600,
                        barmode='group',
                        bargap=0.2,
                        bargroupgap=0.15,
                        yaxis=dict(
                            range=[0, 110],
                            tickfont=dict(size=16)
                        ),
                        showlegend=False,
                        xaxis=dict(
                            categoryorder='array',
                            categoryarray=tipos_disponiveis_sexo,
                            tickfont=dict(size=16)
                        ),
                        hoverlabel=dict(
                            font_size=20,
                            font_family="Arial"
                        )
                    )
                    
                    # Exibir o gráfico
                    st.plotly_chart(fig_sexo, use_container_width=True)
                else:
                    st.info("Não foi possível gerar o gráfico com os dados disponíveis")
            else:
                st.info("Dados de taxa e proficiência por sexo insuficientes para gerar o gráfico ou coluna de tipo de entidade não disponível")
            
            csv_sexo = df_sexo.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Baixar Dados de Sexo",
                data=csv_sexo,
                file_name="proficiencia_sexo.csv",
                mime="text/csv",
                key="download_sexo"
            )
        else:
            st.info("Sem dados válidos de proficiência por sexo após limpeza")
    else:
        st.info("Colunas de sexo não encontradas no conjunto de dados")
    
    # ==================== RESUMO EXECUTIVO ====================
    st.markdown("""
    <div class="report-header" style="background: #2ca02c;">
        📋 RESUMO EXECUTIVO
    </div>
    """, unsafe_allow_html=True)
    
    # Resumo executivo do relatório
    st.markdown("""
    <div class="report-card">
        <div class="report-card-header">
            📊 INFORMAÇÕES GERAIS DO RELATÓRIO
        </div>
        <div style="
            font-size: 0.95rem;
            line-height: 1.6;
            color: #374151;
        ">
            <p><strong>Data de Geração:</strong> {}</p>
            <p><strong>Agregado Consultado:</strong> {}</p>
            <p><strong>Total de Registros:</strong> {:,}</p>
            <p><strong>Período de Dados:</strong> Sistema Permanente de Avaliação da Educação Básica do Ceará (SPAECE)</p>
            <p><strong>Escopo:</strong> Análise educacional com foco em proficiência, participação e desempenho dos estudantes</p>
        </div>
    </div>
    """.format(
        pd.Timestamp.now().strftime("%d/%m/%Y às %H:%M"),
        st.session_state.agregado_consultado if st.session_state.agregado_consultado else "N/A",
        len(st.session_state.df_concatenado) if st.session_state.df_concatenado is not None else 0
    ), unsafe_allow_html=True)
    
    # Instruções de impressão
    st.markdown("""
    <div class="report-card">
        <div class="report-card-header" style="border-bottom-color: #ff7f0e;">
            🖨️ INSTRUÇÕES PARA IMPRESSÃO
        </div>
        <div style="
            font-size: 0.9rem;
            line-height: 1.6;
            color: #374151;
        ">
            <p><strong>Para salvar como PDF:</strong></p>
            <ul>
                <li>Use Ctrl+P (Windows/Linux) ou Cmd+P (Mac)</li>
                <li>Selecione "Salvar como PDF" como destino</li>
                <li><strong>Configurações recomendadas:</strong></li>
                <li style="margin-left: 1rem;">• Orientação: Paisagem (Landscape)</li>
                <li style="margin-left: 1rem;">• Margens: Mínimas (0.5in)</li>
                <li style="margin-left: 1rem;">• Escala: 100%</li>
                <li style="margin-left: 1rem;">• Gráficos de fundo: Ativado</li>
                <li style="margin-left: 1rem;">• Opções: Marcar "Mais configurações" e ativar "Gráficos de fundo"</li>
            </ul>

       </div>
    </div>
    """, unsafe_allow_html=True)
    
    

    st.markdown("<div style='text-align: center;'>Relatório SPAECE - CREDE 1 - Maracanaú</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>Equipe Cecom 1</div>", unsafe_allow_html=True)
