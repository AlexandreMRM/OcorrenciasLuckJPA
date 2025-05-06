import streamlit as st
import pandas as pd
from datetime import date
import pages.Logistica.bbtc as bbtc
import pandas as pd
import os
#Remover Log de erro de sistema operacional, exibido pelo GCP Google
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

def app_titularidade():
    st.title("Titularidade")

    if 'df_phoenix' not in st.session_state:
        st.session_state.df_phoenix = bbtc.BD_Phoenix()
    df_phoenix_geral = st.session_state.df_phoenix

    if 'df_titularidade' not in st.session_state:
        st.session_state.df_titularidade= bbtc.Kpi_Titularidade()
    df_titularidade = st.session_state.df_titularidade

    #lista os veiculos da frota e remove as SPINS e Mamulengos (Não tem Titularidade)
    lista_frota = df_titularidade['Veiculo'].unique().tolist()

    # Inputs de datas
    data_ini = st.date_input('Data inicial', value=date.today(), format='DD/MM/YYYY', key='data_ini_titularidade')
    data_fim = st.date_input('Data final', value=date.today(), format='DD/MM/YYYY', key='data_fim_titularidade')
    data_ini = pd.to_datetime(data_ini)
    data_fim = pd.to_datetime(data_fim)

    # Variável de controle
    atualizado = False

    # Botão de Atualizar
    if st.button('Atualizar', key='atualizar_titularidade'):
        atualizado = True

    if atualizado:

        df_phoenix = df_phoenix_geral[(df_phoenix_geral['Data da Escala'] >= data_ini) & (df_phoenix_geral['Data da Escala'] <= data_fim)]

        veiculos_remover = ['SN71', 'SN72', 'SN73', 'SN74', 'MM01', 'MM02', 'MM03']
        lista_frota = [v for v in lista_frota if v not in veiculos_remover]

        #filtra as escalas do phoenix para contar apenas os veiculos da frota
        df_phoenix = df_phoenix[df_phoenix['Veiculo'].isin(lista_frota)]

        # Remover duplicados para ficar apenas uma escala por veiculo
        df_sem_duplicados = df_phoenix.drop_duplicates().copy()

        # Preenche os dias faltantes entre alteracao de frota
        df_titularidade_novo = bbtc.preencher_datas_intervalo(df_titularidade)

        # Cria uma chave de comparação
        df_sem_duplicados['chave'] = (
            df_sem_duplicados['Data da Escala'].astype(str) + '|' +
            df_sem_duplicados['Veiculo'].astype(str) + '|' +
            df_sem_duplicados['Motorista'].astype(str)
        )

        df_titularidade_novo['chave'] = (
            df_titularidade_novo['Data_Frota'].astype(str) + '|' +
            df_titularidade_novo['Veiculo'].astype(str) + '|' +
            df_titularidade_novo['Motorista_Phoenix'].astype(str)
        )

        # Adiciona a coluna de status comparando as chaves entre os dataframes
        df_sem_duplicados['STATUS'] = df_sem_duplicados['chave'].isin(df_titularidade_novo['chave']).astype(int)

        # Remove a chave do dataframe
        df_sem_duplicados.drop(columns='chave', inplace=True)

        # Remove duplicados
        df_sem_duplicados.drop_duplicates(inplace=True, subset=['Data da Escala', 'Escala', 'Veiculo', 'Motorista'])

        # Junta os servicos de IN e OUT como apenas 1 servico
        servicos_transfer = [
            "HOTÉIS JOÃO PESSOA / AEROPORTO JOÃO PESSOA",
            "AEROPORTO JOÃO PESSOA / HOTEIS JOÃO PESSOA"
        ]
        df_transfer = df_sem_duplicados[df_sem_duplicados["Servico"].isin(servicos_transfer)].copy()
        df_outros = df_sem_duplicados[~df_sem_duplicados["Servico"].isin(servicos_transfer)].copy()

        df_transfer = (
            df_transfer.sort_values(['Escala']).drop_duplicates(subset=['Data da Escala', 'Veiculo'])
        )
        df_transfer['Servico'] = 'TRANSFER AEROPORTO'

        df_final = pd.concat([df_outros, df_transfer], ignore_index=True).sort_values(by=["Data da Escala", "Veiculo"])


        # Exibe o resultado
        st.dataframe(df_final[['Data da Escala', 'Escala', 'Veiculo', 'Motorista', 'Servico', 'STATUS']], hide_index=True, use_container_width=True)


        # Contar os Status 1 para motoristas titulares e somar
        df_status_1 = df_final[df_final['STATUS'] == 1]
        df_status_1_count = df_status_1['STATUS'].sum()

        st.write(f"###### Serviços com Motoristas Titulares: {df_status_1_count}") #df_status_1_count

        # Contar os Status 0 para motoristas não titulares e somar
        df_status_0 = df_final[df_final['STATUS'] == 0]
        df_status_0_count = df_status_0['STATUS'].count()

        st.write(f"###### Serviços sem Motoristas Titulares: {df_status_0_count}") #df_status_0_count

        total_servicos = df_status_1_count + df_status_0_count

        st.write(f"###### Total de Serviços: {total_servicos}") #df_status_0_count

        # Porcentagem de Metas Batidas
        porcentagem_metas_batidas = df_status_1_count / total_servicos * 100

        st.write(f"###### Porcentagem Titularidade Alcancada: {porcentagem_metas_batidas:.2f}%") #df_status_0_count
















