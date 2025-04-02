import pandas as pd
from google.cloud import secretmanager
from google.oauth2.service_account import Credentials
import gspread
import streamlit as st
import json
import plotly.graph_objects as go
from babel.numbers import format_currency
import mysql.connector

barra_1 = '#047c6c'
barra_2 = '#FB0D0D'

def formatar_moeda(valor):
    if pd.isnull(valor):  # Lida com valores NaN
        return None
    return format_currency(valor, 'BRL', locale='pt_BR')

@st.cache_data(ttl=1200)
def Chamada_Reclame_Aqui():
    project_id = "luckjpa"

    # ID of the secret to create.
    secret_id = "Cred"

    # Create the Secret Manager client.
    secret_client = secretmanager.SecretManagerServiceClient()

    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})

    secret_payload = response.payload.data.decode("UTF-8")

    credentials_info = json.loads(secret_payload)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Use the credentials to authorize the gspread client
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key('1VMpRCgMv6_2aZxZ8opWD6KL-PMY0-9gy7RzMZh7Dj0Q')

    # Select the desired worksheet
    planilha = spreadsheet.worksheet('Reclame_Aqui')

    # Get all values from the sheet
    dados_planilha = planilha.get_all_values()
    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])

    df["NOTA DO CLIENTE"] = pd.to_numeric(df["NOTA DO CLIENTE"], errors='coerce')
    df["DATA DA RECLAMAÇÃO"] = pd.to_datetime(df["DATA DA RECLAMAÇÃO"], format="%d/%m/%Y", errors='coerce')
    df["DATA DA OCORRÊNCIA"] = pd.to_datetime(df["DATA DA OCORRÊNCIA"], format="%d/%m/%Y", errors='coerce')
    df['Mes_Ano'] = df['DATA DA RECLAMAÇÃO'].dt.to_period('M').astype(str)
    df['VOLTARIA A FAZER NEGÓCIO?'] = df['VOLTARIA A FAZER NEGÓCIO?'].fillna("")
    #df['AVALIAÇÃO DA SOLUÇÃO'] = df['AVALIAÇÃO DA SOLUÇÃO'].fillna("")
    df['RESOLVIDO?'] = df['RESOLVIDO?'].fillna("")
    
    df['VALIDACAO_NEGOCIO'] = df['VOLTARIA A FAZER NEGÓCIO?'].apply(lambda x: 1 if x == 'SIM' else 0)
    #df['VALIDACAO_RESOLVIDO'] = df['AVALIAÇÃO DA SOLUÇÃO'].apply(lambda x: 1 if x == 'RESOLVIDO' else 0)
    df['VALIDACAO_RESOLVIDO'] = df['RESOLVIDO?'].apply(lambda x: 1 if x == 'SIM' else 0)

    return df

@st.cache_data(ttl=1200)
def Chamada_Reembolso():
    project_id = "luckjpa"

    # ID of the secret to create.
    secret_id = "Cred"

    # Create the Secret Manager client.
    secret_client = secretmanager.SecretManagerServiceClient()

    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})

    secret_payload = response.payload.data.decode("UTF-8")

    credentials_info = json.loads(secret_payload)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Use the credentials to authorize the gspread client
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key('1VMpRCgMv6_2aZxZ8opWD6KL-PMY0-9gy7RzMZh7Dj0Q')

    # Select the desired worksheet
    planilha = spreadsheet.worksheet('Reembolsos')

    # Get all values from the sheet
    dados_planilha = planilha.get_all_values()

    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])

    df["Data_Reembolso"] = pd.to_datetime(df["Data_Reembolso"], dayfirst=True)
    df['Motivo'] = df['Motivo'].fillna('').replace('', 'SEM MOTIVO LANÇADO')

    if df['Valor'].dtype == 'float':
        df['Valor'] = df['Valor']
    else:
        df["Valor"] = df["Valor"].fillna("R$ 0,00").replace("", "R$ 0,00")
        df["Valor"] = (df["Valor"].astype(str).
                                str.strip().str.replace("R$ ", "", regex=False).
                                str.replace(".", "", regex=False).
                                str.replace(",", ".", regex=False).astype(float)
                                )
        
    df['Mes_Ano'] = df['Data_Reembolso'].dt.to_period('M').astype(str)

    return df

@st.cache_data(ttl=1200)
def Chamada_NPS():
    project_id = "luckjpa"

    # ID of the secret to create.
    secret_id = "Cred"

    # Create the Secret Manager client.
    secret_client = secretmanager.SecretManagerServiceClient()

    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})

    secret_payload = response.payload.data.decode("UTF-8")

    credentials_info = json.loads(secret_payload)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Use the credentials to authorize the gspread client
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key('1b0-SVMcwSURxIbYJH0MC0ItiLhuykg8NOYoHZu5vdw4')

    planilha = spreadsheet.worksheet('Respostas ao formulário 1')

    dados_planilha = planilha.get_all_values()

    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])

    #df['Data'] = pd.to_datetime(df['Carimbo de data/hora'], errors='coerce').dt.date
    df['Data'] = pd.to_datetime(df['Carimbo de data/hora'], dayfirst=True, errors='coerce').dt.date

    df['Data_Carimbo'] = pd.to_datetime(df['Carimbo de data/hora'], dayfirst=True, errors='coerce')
    df['Mes_Ano'] = df['Data_Carimbo'].dt.to_period('M').astype(str)
    df['Em uma escala de 1 a 5, quão satisfeito você está com sua experiência no passeio de hoje?'] = df['Em uma escala de 1 a 5, quão satisfeito você está com sua experiência no passeio de hoje?'].astype(str).str.strip().astype(int)
    df.rename(columns={
        'Em uma escala de 1 a 5, quão satisfeito você está com sua experiência no passeio de hoje?': 'NPS',
        'Qual roteiro você está realizando hoje?': 'Roteiro',
        'Nome do seu guia': 'Guia_Passeio',
    }, inplace=True)

    return df

@st.cache_data(ttl=1200)
def Chamada_Elogios():
    project_id = "luckjpa"

    # ID of the secret to create.
    secret_id = "Cred"

    # Create the Secret Manager client.
    secret_client = secretmanager.SecretManagerServiceClient()

    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})

    secret_payload = response.payload.data.decode("UTF-8")

    credentials_info = json.loads(secret_payload)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Use the credentials to authorize the gspread client
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key('1VMpRCgMv6_2aZxZ8opWD6KL-PMY0-9gy7RzMZh7Dj0Q')

    # Select the desired worksheet
    planilha = spreadsheet.worksheet('Elogios')

    # Get all values from the sheet
    dados_planilha = planilha.get_all_values()

    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])
    df["Data_Elogio"] = pd.to_datetime(df["Data_Elogio"], format="%d/%m/%Y", errors='coerce')
    df['Mes_Ano'] = df['Data_Elogio'].dt.to_period('M').astype(str)

    return df

@st.cache_data(ttl=1200)
def BD_Escala(data_ini=None, data_fim=None):
    # Parametros de Login AWS
    config = {
    'user': 'user_automation_jpa',
    'password': 'luck_jpa_2024',
    'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
    'database': 'test_phoenix_joao_pessoa'
    }
    conexao = mysql.connector.connect(**config)
    cursor = conexao.cursor()

    query = '''
        SELECT 
            `Tipo de Servico`,
            `Data | Horario Apresentacao`,
            `Data Execucao`,
            COALESCE(NULLIF(`Voo`, ''), '-') AS `Voo`,
            `Reserva`,
            `Total ADT`,
            `Total CHD`,
            `Escala`,
            `Guia`,
            `Servico`,
            CASE
                WHEN `Tipo de Servico` = 'IN' THEN `Est. Destino`
                ELSE `Est. Origem`
            END AS `Estabelecimento`
        FROM vw_payment_guide
    '''
    if data_ini and data_fim:
        query += " WHERE `Data | Horario Apresentacao` BETWEEN %s AND %s"
        cursor.execute(query, (data_ini, data_fim))
    else:
        cursor.execute(query)
        
    # Coloca o request em uma variavel
    resultado = cursor.fetchall()
    # Busca apenas o cabecalhos do Banco
    cabecalho = [desc[0] for desc in cursor.description]

    # Fecha a conexão
    cursor.close()
    conexao.close()

    # Coloca em um dataframe e muda o tipo de decimal para float
    df = pd.DataFrame(resultado, columns=cabecalho)
    df['Data | Horario Apresentacao'] = pd.to_datetime(df['Data | Horario Apresentacao'], format='%Y-%m-%d', errors='coerce')
    df['Data Escala'] = df['Data | Horario Apresentacao']
    df['Data Escala'] = pd.to_datetime(df['Data Escala'], errors='coerce').dt.normalize()
    return df

@st.cache_data(ttl=1200)
def Chamada_Reclamacoes():
    project_id = "luckjpa"

    # ID of the secret to create.
    secret_id = "Cred"

    # Create the Secret Manager client.
    secret_client = secretmanager.SecretManagerServiceClient()

    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})

    secret_payload = response.payload.data.decode("UTF-8")

    credentials_info = json.loads(secret_payload)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Use the credentials to authorize the gspread client
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key('1VMpRCgMv6_2aZxZ8opWD6KL-PMY0-9gy7RzMZh7Dj0Q')

    # Select the desired worksheet
    planilha = spreadsheet.worksheet('Ocorrências/Reclamações')

    # Get all values from the sheet
    dados_planilha = planilha.get_all_values()

    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])
    
    df["Data_Reclamacao"] = pd.to_datetime(df["Data_Reclamacao"],format="%d/%m/%Y")
    df['Mes_Ano'] = df['Data_Reclamacao'].dt.to_period('M').astype(str)

    return df

@st.cache_data(ttl=1200)
def Chamada_Uber():
    project_id = "luckjpa"

    # ID of the secret to create.
    secret_id = "Cred"

    # Create the Secret Manager client.
    secret_client = secretmanager.SecretManagerServiceClient()

    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})

    secret_payload = response.payload.data.decode("UTF-8")

    credentials_info = json.loads(secret_payload)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Use the credentials to authorize the gspread client
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key('1VMpRCgMv6_2aZxZ8opWD6KL-PMY0-9gy7RzMZh7Dj0Q')

    # Select the desired worksheet
    planilha = spreadsheet.worksheet('Uber')

    # Get all values from the sheet
    dados_planilha = planilha.get_all_values()

    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])

    if df['Valor'].dtype == 'float':
        df['Valor'] = df['Valor']
    else:
        df["Valor"] = df["Valor"].str.replace("R$ ", "", regex=False).str.replace(",", ".").astype(float)

    df["Data_Uber"] = pd.to_datetime(df["Data_Uber"], format="%d/%m/%Y")
    df['Mes_Ano'] = df['Data_Uber'].dt.to_period('M').astype(str)

    return df

@st.cache_data(ttl=1200)
def Chamada_KPI():
    project_id = "luckjpa"

    # ID of the secret to create.
    secret_id = "Cred"

    # Create the Secret Manager client.
    secret_client = secretmanager.SecretManagerServiceClient()

    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": secret_name})

    secret_payload = response.payload.data.decode("UTF-8")

    credentials_info = json.loads(secret_payload)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Use the credentials to authorize the gspread client
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key('1VMpRCgMv6_2aZxZ8opWD6KL-PMY0-9gy7RzMZh7Dj0Q')

    # Select the desired worksheet
    planilha = spreadsheet.worksheet('KPI_Qualidade')

    # Get all values from the sheet
    dados_planilha = planilha.get_all_values()

    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])

    df["Data_KPI"] = pd.to_datetime(df["Data_KPI"], format="%d/%m/%Y")
    df['Mes_Ano'] = df['Data_KPI'].dt.to_period('M').astype(str)

    if df['Valor_KPI'].dtype == 'float':
        df['Valor_KPI'] = df['Valor_KPI']
    else:
        df["Valor_KPI"] = df["Valor_KPI"].fillna("R$ 0,00").replace("", "R$ 0,00")
        df["Valor_KPI"] = (df["Valor_KPI"].astype(str).
                                str.strip().str.replace("R$ ", "", regex=False).
                                str.replace(".", "", regex=False).
                                str.replace(",", ".", regex=False).astype(float)
                            )

    return df

def Grafico_Pizza_Relacao_Problema(df_grafico_relacao_problema):
    # Criar o gráfico de pizza
    fig = go.Figure(data=[go.Pie(
        labels=df_grafico_relacao_problema["Relacao_Problema"],
        values=df_grafico_relacao_problema["Contador_Problema"].astype(float),
        textinfo='label+percent+value',
        marker=dict(colors=[barra_1, barra_2])
    )])
    fig.update_layout(
        title_text='Comparativo Problemas'
    )
    return fig

def Grafico_Pizza_Simples(label, values, titulo):
    # Criar o gráfico de pizza
    fig = go.Figure(data=[go.Pie(
        labels=label,
        values=values.astype(float),
        textinfo='label+percent+value',
        marker=dict(colors=[barra_1, barra_2])
    )])
    fig.update_layout(
        title_text=f'Comparativo - {titulo}'
    )

    return fig

def Grafico_Barra_Relacao_Problema_Mensal(df_Reembolso_filtrado_Relacao_Problema_Mensal):
    # Recriar o gráfico de barras empilhadas
    fig = go.Figure()

    maximo = df_Reembolso_filtrado_Relacao_Problema_Mensal['Valor'].max()
    df_Reembolso_filtrado_Relacao_Problema_Mensal = df_Reembolso_filtrado_Relacao_Problema_Mensal.rename(columns={'Cod_Reserva': 'Total_Reembolsos'})

    # Adicionar barras para cada categoria de 'Relacao_Problema'

    for problema in df_Reembolso_filtrado_Relacao_Problema_Mensal['Relacao_Problema'].unique():
        df_filtered = df_Reembolso_filtrado_Relacao_Problema_Mensal[df_Reembolso_filtrado_Relacao_Problema_Mensal['Relacao_Problema'] == problema]
        
        fig.add_trace(go.Bar(
            x=df_filtered['Mes_Ano'],
            y=df_filtered['Valor'],
            text=df_filtered['Valor'].apply(formatar_moeda),
            textfont=dict(size=10),
            textposition='outside',
            name=problema
        ))

    # Configurar layout do gráfico
    fig.update_layout(
        title="Total Reembolsos - Cliente x Empresa - Mensal",
        xaxis=dict(
                title='Mes',
                tickmode='array',
                tickvals=df_filtered['Mes_Ano'],
                showgrid=False
            ),
            yaxis=dict(
                title='Valores',
                showgrid=False,
                range=[0, maximo * 2]
            ),
            barmode='group',
            bargap=0.5,
            bargroupgap=0.2,
            legend=dict(
            title='Indicadores',
            orientation='h',
            ),
            uniformtext=dict(mode='show', minsize=10)
        )

    return fig

def Grafico_Pizza_Qtde_Reembolso_MesxMes(df):

    df_Reembolso_filtrado_Relacao_Problema_Filtrado_Empresa = df.copy()

    df_Reembolso_filtrado_Relacao_Problema_Filtrado_Empresa = df_Reembolso_filtrado_Relacao_Problema_Filtrado_Empresa.sort_values('Mes_Ano')

    meses_unicos = df_Reembolso_filtrado_Relacao_Problema_Filtrado_Empresa['Mes_Ano'].unique()

    pizzas = []
    barras = []
    for mes in meses_unicos:
        df_pizza = df_Reembolso_filtrado_Relacao_Problema_Filtrado_Empresa[df_Reembolso_filtrado_Relacao_Problema_Filtrado_Empresa['Mes_Ano'] == mes]
        df_pizza = df_pizza.rename(columns={'Cod_Reserva': 'Quantidade'})
        df_pizza['Mes_Nome'] = pd.to_datetime(df_Reembolso_filtrado_Relacao_Problema_Filtrado_Empresa['Mes_Ano']).dt.month_name('pt_BR.UTF-8')
        df_pizza['Ano'] = pd.to_datetime(df_Reembolso_filtrado_Relacao_Problema_Filtrado_Empresa['Mes_Ano']).dt.year
        fig = go.Figure(data=[go.Pie(
            labels=df_pizza["Setor_Relacionado"],
            values=df_pizza["Quantidade"],
            textinfo='label+percent+value',
        )])
        fig.update_layout(
            title_text=f"Quantidade de Reembolsos - {df_pizza['Mes_Nome'].unique()[0]}/{df_pizza['Ano'].unique()[0]}"
        )
        fig1 = go.Figure(data=[go.Bar(
            x=df_pizza['Setor_Relacionado'],
            y=df_pizza['Valor'],
            text=df_pizza['Valor'].apply(formatar_moeda),
            marker_color=barra_1,
            textfont=dict(size=10, color=barra_1),
            textposition='outside'
        )])
        fig1.update_layout(
            title_text=f'Valor Reembolsos - {df_pizza["Mes_Nome"].unique()[0]}/{df_pizza["Ano"].unique()[0]}',
            yaxis=dict(
                range=[0, df_pizza['Valor'].max() * 2],
                showgrid=False,
            )
        )
        
        # Adicionar à lista de gráficos
        pizzas.append(fig)
        barras.append(fig1)

    return pizzas, barras

def Grafico_Barra_Reembolso_Setor(df):

    df_Reembolso_Filtrado_Motivo_Setor = df.copy()

    df_Reembolso_Filtrado_Motivo_Setor = df_Reembolso_Filtrado_Motivo_Setor.sort_values('Setor_Relacionado')

    setor_unicos = df_Reembolso_Filtrado_Motivo_Setor['Setor_Relacionado'].unique()

    pizzas = []
    for setor in setor_unicos:
        df_pizza = df_Reembolso_Filtrado_Motivo_Setor[df_Reembolso_Filtrado_Motivo_Setor['Setor_Relacionado'] == setor]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_pizza['Motivo'],
            y=df_pizza['Valor'],
            name=df_pizza['Motivo'].unique()[0],
            marker_color=barra_1,
            text=df_pizza['Valor'].apply(formatar_moeda),
            textfont=dict(size=10, color=barra_1),
            textposition='outside',
        ))
        
        fig.update_layout(
            title_text=f'Motivos / Setor - {setor}',
            yaxis=dict(
            showgrid=False,
            range=[0, df_pizza['Valor'].max() * 3]
        ),
        )
        
        # Adicionar à lista de gráficos
        pizzas.append(fig)

    return pizzas

def Grafico_Pizza_Reembolso_Setor(df):

    df_Reembolso_Filtrado_Motivo_Setor = df.copy()

    df_Reembolso_Filtrado_Motivo_Setor = df_Reembolso_Filtrado_Motivo_Setor.sort_values('Setor_Relacionado')

    setor_unicos = df_Reembolso_Filtrado_Motivo_Setor['Setor_Relacionado'].unique()

    pizzas = []
    for setor in setor_unicos:
        df_pizza = df_Reembolso_Filtrado_Motivo_Setor[df_Reembolso_Filtrado_Motivo_Setor['Setor_Relacionado'] == setor]
        df_pizza = df_pizza.rename(columns={'Cod_Reserva': 'Quantidade'})

        fig = go.Figure(data=[go.Pie(
            labels=df_pizza["Motivo"],
            values=df_pizza["Quantidade"],
            textinfo='label+percent+value',
        )])
        fig.update_layout(
            title_text=f'Motivos / Setor - {setor}',
        )
        
        # Adicionar à lista de gráficos
        pizzas.append(fig)

    return pizzas

def Grafico_Linha_Reembolsos_Geral(df, parametro_eixo_y, meta, titulo):
    df_Reembolso_Total_Mes = df.copy()
    df_Reembolso_Total_Mes['Meta'] = meta
    
    if isinstance(meta, pd.Series):
        meta_max = meta.max()
    else:
        meta_max = meta

    maximo = parametro_eixo_y.max()
    range_max = max(meta_max, maximo)

    # Criar figura
    fig = go.Figure()

    # Adicionar linha de Cod_Reserva no eixo Y primário
    fig.add_trace(go.Scatter(
        x=df_Reembolso_Total_Mes['Mes_Ano'], 
        y=parametro_eixo_y,
        mode='lines+markers+text', 
        text=round(parametro_eixo_y, 2),
        name='Valor',
        line=dict(color=barra_1, shape='spline'),
        textfont=dict(size=10, color=barra_1),
        textposition='top center'
        ))

    # Adicionar linha de Valor no eixo Y secundário
    fig.add_trace(go.Scatter(
        x=df_Reembolso_Total_Mes['Mes_Ano'], 
        y=df_Reembolso_Total_Mes['Meta'],
        mode='lines+markers+text', 
        text=df_Reembolso_Total_Mes['Meta'],
        name='Meta',
        line=dict(color=barra_2, shape='spline'), 
        textfont=dict(size=10, color=barra_2),
        textposition='top center',
        ))

    # Configurar layout do gráfico
    fig.update_layout(
        title=titulo,
        xaxis=dict(title='Mês/Ano', type='category'),
        yaxis=dict(
            title='Valor', 
            side='left', 
            showgrid=False, 
            range=[0, range_max * 1.5],
        ),
        bargap=0
    )

    return fig

def Grafico_Barra_Simples_Geral(parametro_eixo_x, parametro_eixo_y, titulo):

    fig = go.Figure()

    maximo = parametro_eixo_y.max()
    
    fig.add_trace(go.Bar(
        x=parametro_eixo_x,
        y=parametro_eixo_y,
        text=parametro_eixo_y,
        textfont=dict(size=10, color=barra_1),
        textposition='outside',
        name=titulo
    ))

    # Configurar layout do gráfico
    fig.update_layout(
        title=titulo,
        xaxis=dict(
                title='Mes',
                tickmode='array',
                tickvals=parametro_eixo_x,
                showgrid=False
            ),
            yaxis=dict(
                title='Valores',
                showgrid=False,
                range=[0, maximo * 2]
            ),
            barmode='group',
            bargap=0.5,
            bargroupgap=0.2,
            legend=dict(
            title='Indicadores',
            orientation='h',
            ),
            uniformtext=dict(mode='show', minsize=16)
        )

    return fig

def Grafico_Pizza_Categoria_SubCategoria(df_ReclamacoesfiltradoSubcategoria):
    df = df_ReclamacoesfiltradoSubcategoria.copy()
    df = df.drop(columns=["Unnamed: 0"], errors="ignore")
    df = df.rename(columns={'Data_Reclamacao': 'Quantidade'})

    categorias = df["Categoria"].unique()
    pizzas = []
    valores = []
    cat = []
    # Criar gráficos de pizza para cada categoria usando Plotly
    for categoria in categorias:
        sub_df = df[df["Categoria"] == categoria]
        subcategoria_counts = sub_df.groupby("Subcategoria")["Quantidade"].sum().reset_index()
        total_reclamacoes = subcategoria_counts['Quantidade'].sum()

        fig = go.Figure(data=[go.Pie(
            labels=subcategoria_counts['Subcategoria'], 
            values=subcategoria_counts['Quantidade'], 
            textinfo='value+percent',
            hole=0.3
            )])
        fig.update_layout(
            title_text=f'Distribuição de Reclamações por Subcategoria - {categoria}'
            )
        
        pizzas.append(fig)
        valores.append(total_reclamacoes)
        cat.append(categoria)


    return pizzas, valores, cat

def Grafico_Linha_Dupla(df, linha_1, linha_2, legenda_1, legenda_2, titulo):
    df_lines = df.copy()
    
    # Criar figura
    fig = go.Figure()

    # Adicionar linha de Cod_Reserva no eixo Y primário
    fig.add_trace(go.Scatter(
        x=df_lines['Mes_Ano'], 
        y=linha_1,
        mode='lines+markers+text', 
        text=linha_1,
        name=legenda_1,
        line=dict(color=barra_1, shape='spline'),
        textfont=dict(size=10, color=barra_1),
        textposition='top center'
        ))

    # Adicionar linha de Valor no eixo Y secundário
    fig.add_trace(go.Scatter(
        x=df_lines['Mes_Ano'], 
        y=linha_2,
        mode='lines+markers+text', 
        text=linha_2,
        name=legenda_2,
        line=dict(color=barra_2, shape='spline'), 
        textfont=dict(size=10, color=barra_2),
        textposition='top center',
        ))

    # Configurar layout do gráfico
    fig.update_layout(
        title=titulo,
        xaxis=dict(title='Mês/Ano', type='category'),
        yaxis=dict(
            title='Valor', 
            side='left', 
            showgrid=False,
            range=[0, max(linha_1.max(), linha_2.max()) * 1.5]
        ),
    )

    return fig

def Grafico_Rosca_Meta(kpi_avaliacao, cor_mark, meta):
    valores = [kpi_avaliacao, meta - kpi_avaliacao]
    labels = ["Desempenho", "Meta"]

    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=labels,  
        values=valores,
        hole=0.7,
        textinfo="none", 
        marker=dict(colors=[cor_mark, "lightgray"]), 
        sort=False 
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            go.layout.Annotation(
                text=f"<b>{kpi_avaliacao:.1f}</b>", 
                x=0.5,  
                y=0.5,  
                font=dict(size=80, color=cor_mark),
                showarrow=False
            ),
        ],
        showlegend=False,  
        template="plotly_white",
        margin=dict(l=0, r=0, t=0, b=80),
        height=500,
        width=500
    )
    return fig

def Grafico_Rosca_Meta_Nome(kpi_avaliacao, cor_mark, meta, nome, cor_letra):

    valores = [kpi_avaliacao, meta - kpi_avaliacao]
    labels = ["Desempenho", "Meta"]

    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=labels,  
        values=valores,
        hole=0,
        textinfo="none", 
        marker=dict(colors=[cor_mark, cor_mark],
        line=dict(color='white', width=1)
        ), 
        sort=False 
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",  # Remove o fundo externo
        annotations=[
            go.layout.Annotation(
                text=f"<b>{nome}</b>",  # Exibe o KPI no centro
                x=0.5,  
                y=0.5,  
                font=dict(size=80, color=cor_letra),
                showarrow=False
            ),
        ],
        showlegend=False,  # Remove legenda para um visual mais limpo
        template="plotly_white",
        margin=dict(l=100, r=0, t=0, b=0),
        height=500,
        width=500
    )
    return fig

def Grafico_Linha_Simples(df, linha_1, legenda_1, titulo):
    df_lines = df.copy()
    df_lines['Data'] = df_lines['Data'].dt.strftime('%d/%m/%Y')
    linha_1 = round(linha_1, 2)
    
    # Criar figura
    fig = go.Figure()

    # Adicionar linha de Cod_Reserva no eixo Y primário
    fig.add_trace(go.Scatter(
        x=df_lines['Data'], 
        y=linha_1,
        mode='lines+markers+text', 
        text=linha_1,
        name=legenda_1,
        line=dict(color=barra_1, shape='spline'),
        textfont=dict(size=16, color=barra_1),
        textposition='top center'
        ))

    # Configurar layout do gráfico
    fig.update_layout(
        title=titulo,
        xaxis=dict(title='Mês/Ano', type='category'),
        yaxis=dict(
            title='Valor', 
            side='left', 
            showgrid=False,
            range=[0, linha_1.max() * 1.5]
        ),
    )

    return fig

def Grafico_Barra_NPS(parametro_eixo_x, parametro_eixo_y, titulo):

    fig = go.Figure()

    maximo = parametro_eixo_y.max()
    
    fig.add_trace(go.Bar(
        x=parametro_eixo_x,
        y=parametro_eixo_y,
        text=parametro_eixo_y,
        textfont=dict(size=10, color=barra_1),
        textposition='outside',
        name=titulo
    ))

    # Configurar layout do gráfico
    fig.update_layout(
        title=titulo,
        xaxis=dict(
                title='Nota',
                tickmode='array',
                tickvals=parametro_eixo_x,
                tickformat="%b %d, %Y",
                showgrid=False
            ),
            yaxis=dict(
                title='Quantidade',
                showgrid=False,
                range=[0, maximo * 2]
            ),
            barmode='group',
            bargap=0.5,
            bargroupgap=0.2,
            legend=dict(
            title='Indicadores',
            orientation='h',
            ),
            uniformtext=dict(mode='show', minsize=16)
        )

    return fig

def Grafico_Barra_NPS_Qtde_nota(parametro_eixo_x, parametro_eixo_y, titulo):
    fig = go.Figure()

    # Converter eixo X para datas
    parametro_eixo_x = pd.to_datetime(parametro_eixo_x)

    # Criar um DataFrame com todas as datas no intervalo mínimo e máximo
    data_min, data_max = parametro_eixo_x.min(), parametro_eixo_x.max()
    todas_as_datas = pd.date_range(start=data_min, end=data_max, freq='D')

    # Criar um DataFrame preenchendo as datas ausentes com 0
    df = pd.DataFrame({'Data': parametro_eixo_x, 'Valores': parametro_eixo_y})
    df_completo = pd.DataFrame({'Data': todas_as_datas})
    df_completo = df_completo.merge(df, on='Data', how='left').fillna(0)
    df_completo = df_completo[df_completo['Valores'] != 0]

    fig.add_trace(go.Bar(
        x=df_completo['Data'].dt.strftime('%d/%m/%Y'),
        y=df_completo['Valores'],
        text=df_completo['Valores'],
        textfont=dict(size=10, color="blue"),
        textposition='outside',
        name=titulo
    ))

    # Configurar layout do gráfico
    fig.update_layout(
        title=titulo,
        xaxis=dict(
            title='Data',
            tickmode='array',  # Garante uma escala contínua
            tickvals=df_completo['Data'].dt.strftime('%d/%m/%Y'),
            tickformat="%b %d, %Y",
            showgrid=False
        ),
        yaxis=dict(
            title='Quantidade',
            showgrid=False,
            range=[0, df_completo['Valores'].max() * 1.5]
        ),
        barmode='group',
        bargap=0.2,  # Remove o espaço entre as barras
        bargroupgap=0,  # Remove o espaço entre grupos de barras
        legend=dict(
            title='Indicadores',
            orientation='h',
        ),
        uniformtext=dict(mode='show', minsize=16)
    )

    return fig
