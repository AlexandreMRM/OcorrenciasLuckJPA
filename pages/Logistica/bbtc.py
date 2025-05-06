import pandas as pd
import mysql.connector
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from google.cloud import secretmanager
import json



@st.cache_resource(ttl=60000, show_spinner=False)
def BD_Phoenix():
    config = {
    'user': 'user_automation_jpa',
    'password': 'new_luck_2025',
    'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
    'database': 'test_phoenix_joao_pessoa'
    }
    # Conexão as Views
    conexao = mysql.connector.connect(**config)
    cursor = conexao.cursor()

    # Script MySql para requests
    cursor.execute(
        'SELECT * FROM vw_payment_guide'
    )
    # Coloca o request em uma variavel
    resultado = cursor.fetchall()
    # Busca apenas o cabecalhos do Banco
    cabecalho = [desc[0] for desc in cursor.description]

    # Fecha a conexão
    cursor.close()
    conexao.close()

    # Coloca em um dataframe e muda o tipo de decimal para float
    df = pd.DataFrame(resultado, columns=cabecalho)
    #df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

    #De 01/06/2024 (data da escala) até hoje - Data da execucao, Servico, Veiculo, Soma ADT E CHD
    cols = ['Data da Escala', 
        'Escala',
        'Guia', 
        'Data Execucao', 
        'Servico', 
        'Data | Horario Apresentacao', 
        'Status do Servico',
        'Motorista',
        'Total ADT',
        'Total CHD',
        'Veiculo',

    #Agrupar desde 01/06/2024 ate hoje a 'Data da execucao', 'Servico', 'Veiculo', 'Soma ADT', 'Soma CHD'

    ]
    df = df[cols]
    df['Data Execucao'] = pd.to_datetime(df['Data Execucao'])
    df['Data da Escala'] = pd.to_datetime(df['Data da Escala'])

    return df

def Capacidade_Carro():
    
    # ID do projeto no Google Cloud
    project_id = "luckjpa"

    # ID do segredo armazenado no Secret Manager
    secret_id = "Cred"

    # Criação do cliente do Secret Manager
    secret_client = secretmanager.SecretManagerServiceClient()

    # Nome do segredo com a versão mais recente
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    # Acessa o conteúdo do segredo (credenciais do serviço)
    response = secret_client.access_secret_version(request={"name": secret_name})

    # Decodifica o conteúdo secreto para string
    secret_payload = response.payload.data.decode("UTF-8")

    # Converte a string JSON para dicionário Python
    credentials_info = json.loads(secret_payload)

    # Escopo necessário para acessar e editar planilhas do Google Sheets
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Cria as credenciais a partir do dicionário e define o escopo
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)

    # Autoriza o cliente do gspread com as credenciais
    client = gspread.authorize(credentials)

    # Abre a planilha do Google Sheets usando a chave da planilha (disponível na URL)
    spreadsheet = client.open_by_key('1QC9K1wO8pCg0bEiuUKXf4Sg56ozL5kw-a-5Nbdvwxd4')
    
    # Seleciona a aba (worksheet) chamada
    planilha = spreadsheet.worksheet('CAP')

    # Obtém todos os valores da aba como uma lista de listas
    dados_planilha = planilha.get_all_values()

    # Converte os dados em um DataFrame do pandas (pulando o cabeçalho na primeira linha)
    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])

    # Retorna o DataFrame com os dados da planilha
    return df

def Kpi_Titularidade():
    
    # ID do projeto no Google Cloud
    project_id = "luckjpa"

    # ID do segredo armazenado no Secret Manager
    secret_id = "Cred"

    # Criação do cliente do Secret Manager
    secret_client = secretmanager.SecretManagerServiceClient()

    # Nome do segredo com a versão mais recente
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    # Acessa o conteúdo do segredo (credenciais do serviço)
    response = secret_client.access_secret_version(request={"name": secret_name})

    # Decodifica o conteúdo secreto para string
    secret_payload = response.payload.data.decode("UTF-8")

    # Converte a string JSON para dicionário Python
    credentials_info = json.loads(secret_payload)

    # Escopo necessário para acessar e editar planilhas do Google Sheets
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Cria as credenciais a partir do dicionário e define o escopo
    credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)

    # Autoriza o cliente do gspread com as credenciais
    client = gspread.authorize(credentials)

    # Abre a planilha do Google Sheets usando a chave da planilha (disponível na URL)
    spreadsheet = client.open_by_key('1QC9K1wO8pCg0bEiuUKXf4Sg56ozL5kw-a-5Nbdvwxd4')
    
    # Seleciona a aba (worksheet) chamada
    planilha = spreadsheet.worksheet('Frota')

    # Obtém todos os valores da aba como uma lista de listas
    dados_planilha = planilha.get_all_values()

    # Converte os dados em um DataFrame do pandas (pulando o cabeçalho na primeira linha)
    df = pd.DataFrame(dados_planilha[1:], columns=dados_planilha[0])

    # Retorna o DataFrame com os dados da planilha
    return df

def preencher_datas_intervalo(df, col_data='Data_Frota'):
    # Converter a coluna de data para datetime
    df[col_data] = pd.to_datetime(df[col_data], dayfirst=True)

    # Obter o intervalo completo de datas
    min_date = df[col_data].min()
    today = pd.Timestamp.today().normalize()
    full_date_range = pd.date_range(start=min_date, end=today, freq='D')

    # Colunas que identificam exclusivamente cada motorista-veículo
    group_cols = ["Veiculo", "Motorista_Sheet", "Motorista_Phoenix", "Base_Comparativo"]
    unique_combinations = df[group_cols].drop_duplicates()

    # Gerar todas as combinações com as datas
    full_df = pd.DataFrame([
        {
            col_data: date,
            "Veiculo": row["Veiculo"],
            "Motorista_Sheet": row["Motorista_Sheet"],
            "Motorista_Phoenix": row["Motorista_Phoenix"],
            "Base_Comparativo": row["Base_Comparativo"]
        }
        for date in full_date_range
        for _, row in unique_combinations.iterrows()
    ])

    return full_df


 


