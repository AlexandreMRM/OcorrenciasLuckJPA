import pandas as pd
from google.cloud import secretmanager
import json
from google.oauth2.service_account import Credentials
import gspread
import plotly.graph_objects as go
import streamlit as st

barra_1 = '#047c6c'
barra_2 = '#ff7f0e'

def Chamada_Historico():
  
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

    spreadsheet = client.open_by_key('1bLlpjuyadQLxl1R0HbisjERcAB_nTeXcifgRlmmrpLY')

    # Select the desired worksheet 
    planilha = spreadsheet.worksheet('BD_Historico')

    # Get all values from the sheet
    dados_planilha = planilha.get_all_values()

    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])
    df["Data_Ocorrencia"] = pd.to_datetime(df["Data_Ocorrencia"], format="%d/%m/%Y", errors='coerce')
    df["Mes_Ano"] = df["Data_Ocorrencia"].dt.to_period("M").astype(str)
    df['Ano'] = df['Data_Ocorrencia'].dt.year
    df['Mes'] = df['Data_Ocorrencia'].dt.month  

    return df  

def Chamada_Colaborador_Admissao():
  
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

    spreadsheet = client.open_by_key('1gK_H7cMdn6PkFGICmjSFw7ZW5GEEyse-IADjCAv8bo8')

    # Select the desired worksheet 
    planilha = spreadsheet.worksheet('Colaboradores')

    # Get all values from the sheet
    dados_planilha = planilha.get_all_values()

    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])

    df = df.loc[:, df.columns != '']
    df = df.loc[:, ~df.columns.duplicated()]

    df['Data_Admissão'] = pd.to_datetime(df['Data_Admissão'], format='%d/%m/%Y', errors='coerce')
    df['Data_Demissão'] = pd.to_datetime(df['Data_Demissão'], format='%d/%m/%Y', errors='coerce')

    return df 

def Grafico_Pizza(label, valor, titulo):

    fig = go.Figure(data=[go.Pie(
    labels=label, 
    values=valor,
    )])
    fig.update_layout(
    title=titulo
    )

    return fig

def Grafico_Linha_Simples(eixo_x, label_x, eixo_y, label_y, titulo):
    eixo_x = eixo_x.sort_values()

    fig = go.Figure(data=[go.Scatter(
    x=eixo_x, 
    y=eixo_y,
    mode='lines+markers+text',
    name=label_y,
    line=dict(color=barra_1, width=2, shape='spline'),
    text=eixo_y,
    textfont=dict(size=12, color=barra_1),
    textposition='top center',
    )])
    
    fig.update_layout(
    title=titulo,
     xaxis=dict(
        title=label_x,
        tickmode='array',
        tickvals=eixo_x,
        showgrid=False
    ),
    )

    return fig

def Grafico_Barras_Simples(eixo_x, label_x, eixo_y, label_y, titulo):
    #eixo_x = eixo_x.astype(float)

    fig = go.Figure(data=[go.Bar(
    x=eixo_x, 
    y=eixo_y,
    name=label_y,
    marker_color=barra_1,
    text=eixo_y,
    textfont=dict(size=12, color=barra_1),
    textposition='outside',
    )])
    
    fig.update_layout(
    title=titulo,
     xaxis=dict(
        title=label_x,
        tickmode='array',
        tickvals=eixo_x,
        showgrid=False
    ),
    yaxis=dict(
        title=label_y,
        showgrid=False,
        range=[0, eixo_y.max() * 1.5]
    ),
    )

    return fig
    st.set_page_config(layout="wide")

    return fig
    st.set_page_config(layout="wide")

@st.cache_data(ttl=1200)
def Chamada_Historico_leitura():
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

    spreadsheet = client.open_by_key('1bLlpjuyadQLxl1R0HbisjERcAB_nTeXcifgRlmmrpLY')

    # Select the desired worksheet
    planilha = spreadsheet.worksheet('BD_Teste')

    # Get all values from the sheet
    dados_planilha = planilha.get_all_values()
    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])
    
    return df 

def Carregar_Colaboradores_Setores_Funcao():
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

    spreadsheet = client.open_by_key('1gK_H7cMdn6PkFGICmjSFw7ZW5GEEyse-IADjCAv8bo8')

    # Select the desired worksheet
    planilha = spreadsheet.worksheet('Colaboradores')

    # Get all values from the sheet
    dados_planilha = planilha.get_all_values()
    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])

    return df

def verificar_login(usuario, senha_inserida, login, senha):
    if usuario in login:
        index = login.index(usuario)
        if senha_inserida == senha[index]:
            return True
    return False

def Salvar_Dados(df_inserir):
    try:
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

        spreadsheet = client.open_by_key('1bLlpjuyadQLxl1R0HbisjERcAB_nTeXcifgRlmmrpLY')

        # Select the desired worksheet
        planilha = spreadsheet.worksheet('BD_Teste')

        # Get all values from the sheet
        dados_planilha = planilha.get_all_values()
        df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])

        limpar_Colunas = "A:M"

        planilha.batch_clear([limpar_Colunas])

        df_novo = pd.concat([df, df_inserir], ignore_index=True)

        data = [df_novo.columns.values.tolist()] + df_novo.values.tolist()

        # Atualizar a planilha com os dados
        planilha.update(range_name='A1', values=data)

        return True
    except Exception as e:
        return f'Erro ao Salvar Dados {e}'
    
def Usuario_Senha():
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

    spreadsheet = client.open_by_key('1bLlpjuyadQLxl1R0HbisjERcAB_nTeXcifgRlmmrpLY')

    # Select the desired worksheet
    planilha = spreadsheet.worksheet('BD_Senhas')

    # Get all values from the sheet
    dados_planilha = planilha.get_all_values()
    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])

    return df
    
