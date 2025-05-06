import streamlit as st
import pandas as pd
from datetime import date
import pages.Logistica.bbtc as bbtc
import os
#Remover Log de erro de sistema operacional, exibido pelo GCP Google
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


def app_ocupacao():
    st.title("Ocupação Veicular")

    # Carregar os dados logo (independente do botão)
    if 'df_phoenix' not in st.session_state:
        st.session_state.df_phoenix = bbtc.BD_Phoenix()
    df_phoenix = st.session_state.df_phoenix

    excluir_servicos = ['ALUGUEL FORA DE JPA', 
                        'A DISPOSIÇÃO DA GARAGEM', 
                        'AEROPORTO JOÃO PESSOA / HOTEIS JOÃO PESSOA', 
                        'HOTÉIS JOÃO PESSOA / AEROPORTO JOÃO PESSOA', 
                        'A DISPOSIÇÃO DA GARAGEM - FORA DE JPA', 
                        'APOIO DA VOLTA - PIPA', 
                        'APOIO DA VOLTA', 
                        'HOTÉIS JOÃO PESSOA / RESTAURANTE JOÃO PESSOA / HOTÉIS JOÃO PESSOA', 
                        'PEGAR QUADRILHA', 
                        'ALUGUEL DENTRO DE JPA', 
                        'APOIO DA VOLTA - LITORAL NORTE COM ENTARDECER NA PRAIA DO JACARÉ',
                        'HOTÉIS JOÃO PESSOA / RESTAURANTE JOÃO PESSOA / HOTÉIS JOÃO PESSOA',
                        'HOTÉIS JOÃO PESSOA / MARINA / HOTÉIS JOÃO PESSOA',
                        'HOTÉIS CABEDELO/ AEROPORTO JOÃO PESSOA',
                        'APOIO DA VOLTA - PORTO DE GALINHAS']

    df_phoenix = df_phoenix[~df_phoenix['Servico'].isin(excluir_servicos)]

    if 'df_capacidade_carro' not in st.session_state:
        st.session_state.df_capacidade_carro = bbtc.Capacidade_Carro()
    df_capacidade_carro = st.session_state.df_capacidade_carro

    # Inputs de datas
    data_ini = st.date_input('Data inicial', value=date.today(), format= 'DD/MM/YYYY', key='data_ini_ocupacao')
    data_fim = st.date_input('Data final', value=date.today(), format= 'DD/MM/YYYY', key='data_fim_ocupacao')
    data_ini = pd.to_datetime(data_ini)
    data_fim = pd.to_datetime(data_fim)

    # Agrupar e preparar
    df_capacidade = df_phoenix.groupby(['Data Execucao', 'Escala', 'Veiculo']).agg({
        'Servico': 'first',
        'Total ADT': 'sum',
        'Total CHD': 'sum',
    }).reset_index()
    df_capacidade['Total_Geral'] = df_capacidade['Total ADT'] + df_capacidade['Total CHD']

    # Merge
    df_phoenix = pd.merge(
        df_phoenix,
        df_capacidade[['Data Execucao', 'Escala', 'Veiculo', 'Total_Geral']],
        how='left',
        on=['Data Execucao', 'Escala', 'Veiculo']
    )

    df_capacidade_carro_merge = pd.merge(
        df_capacidade,
        df_capacidade_carro[['Veiculo', 'Capacidade']],
        how='left',
        on='Veiculo'
    )

    # Garantir tipos corretos
    df_capacidade_carro_merge['Total_Geral'] = pd.to_numeric(df_capacidade_carro_merge['Total_Geral'], errors='coerce').fillna(0)
    df_capacidade_carro_merge['Capacidade'] = pd.to_numeric(df_capacidade_carro_merge['Capacidade'], errors='coerce').fillna("Veiculo não cadastrado")#######################
    df_capacidade_carro_merge.drop(df_capacidade_carro_merge[df_capacidade_carro_merge['Capacidade'] == "Veiculo não cadastrado"].index, inplace=True)

    df_capacidade_carro_merge['Ocupacao'] = (df_capacidade_carro_merge['Total_Geral'] / df_capacidade_carro_merge['Capacidade']) * 100
    df_capacidade_carro_merge['Ocupacao'] = pd.to_numeric(df_capacidade_carro_merge['Ocupacao'], errors='coerce')
    df_capacidade_carro_merge['Ocupacao'] = df_capacidade_carro_merge['Ocupacao'].round(2)
    df_capacidade_carro_merge['Data Execucao'] = pd.to_datetime(df_capacidade_carro_merge['Data Execucao'])

    # Filtrar pelas datas SELECIONADAS
    df_filtrado = df_capacidade_carro_merge[
        (df_capacidade_carro_merge['Data Execucao'] >= data_ini) &
        (df_capacidade_carro_merge['Data Execucao'] <= data_fim)
    ]

    seleceo_analise = st.radio(
        'Selecione o tipo de análise',
        ('Por Serviço', 'Por Veículo'),
        horizontal=True,
        key='seleceo_analise_ocupacao'
    )

    if seleceo_analise == 'Por Serviço':
        # Após data: já cria a lista de serviços disponíveis
        servicos_disponiveis = df_filtrado['Servico'].dropna().unique().tolist()
        servicos_disponiveis.sort()
        opcoes_servicos = ['TODOS'] + servicos_disponiveis

        # MULTISELECT após data
        servicos_selecionados = st.multiselect(
            'Selecione os serviços',
            options=opcoes_servicos,
            default=['TODOS'],
            key='servicos_selecionados_ocupacao'
        )

        # Variável de controle
        atualizado = False

        # Botão de Atualizar
        if st.button('Atualizar', key='atualizar_ocupacao'):
            atualizado = True

        if atualizado:
            # Aplicar filtro de serviços
            if 'TODOS' not in servicos_selecionados:
                df_filtrado = df_filtrado[df_filtrado['Servico'].isin(servicos_selecionados)]
                

            if not df_filtrado.empty:
                for servico in servicos_selecionados:
                    df_servico = df_filtrado[df_filtrado['Servico'] == servico]

                    if not df_servico.empty:
                        st.subheader(f"🔹 Serviço: {servico}")
                        st.dataframe(df_servico[['Data Execucao', 'Escala', 'Veiculo', 'Servico', 'Total_Geral', 'Capacidade', 'Ocupacao']],
                                    hide_index=True, use_container_width=True)

                        media_ocupacao = df_servico['Ocupacao'].mean()
                        total_passageiros = df_servico['Total ADT'].sum() + df_servico['Total CHD'].sum()

                        st.markdown(f"✅ **Média de Ocupação:** {media_ocupacao:.2f}%")
                        st.markdown(f"👥 **Total de Passageiros Transportados:** {int(total_passageiros)}")
                        st.markdown("---")  # Linha divisória

            if 'TODOS' in servicos_selecionados:
                ocupacao_geral = df_filtrado[df_filtrado['Servico'].isin(opcoes_servicos)]['Ocupacao'].mean()
                st.write(f"###### Média de Ocupação Geral com TODOS serviços tipo REGULAR: **{ocupacao_geral:.2f}%**")
                st.divider()
                for servico in opcoes_servicos:    
                    df_servico = df_filtrado[df_filtrado['Servico'] == servico]
                    
                    if not df_servico.empty:
                        st.subheader(f"🔹 Serviço: {servico}")
                        st.dataframe(df_servico[['Data Execucao', 'Escala', 'Veiculo', 'Servico', 'Total_Geral', 'Capacidade', 'Ocupacao']],
                                    hide_index=True, use_container_width=True)

                        media_ocupacao = df_servico['Ocupacao'].mean()
                        total_passageiros = df_servico['Total ADT'].sum() + df_servico['Total CHD'].sum()

                        st.markdown(f"✅ **Média de Ocupação: {servico}** - {media_ocupacao:.2f}%")
                        st.markdown(f"👥 **Total de Passageiros Transportados:** {int(total_passageiros)}")
                        st.markdown("---")  # Linha divisória
            else:
                st.warning("Nenhum dado disponível após o filtro.")

        else:
            st.info("Clique no botão **Atualizar** para carregar e visualizar os dados.")


    if seleceo_analise == 'Por Veículo':
        # Após data: já cria a lista de serviços disponíveis
        veiculos_disponiveis = df_filtrado['Veiculo'].dropna().unique().tolist()
        veiculos_disponiveis.sort()
        opcoes_veiculos = ['TODOS'] + veiculos_disponiveis

        # MULTISELECT após data
        veiculos_selecionados = st.multiselect(
            'Selecione os Veículos',
            options=opcoes_veiculos,
            default=['TODOS']
        )

        # Variável de controle
        atualizado = False

        # Botão de Atualizar
        if st.button('Atualizar', key='atualizar_ocupacao'):
            atualizado = True

        if atualizado:
            # Aplicar filtro de serviços
            if 'TODOS' not in veiculos_selecionados:
                df_filtrado = df_filtrado[df_filtrado['Veiculo'].isin(veiculos_selecionados)]
                

            if not df_filtrado.empty:
                for servico in veiculos_selecionados:
                    df_servico = df_filtrado[df_filtrado['Veiculo'] == servico]

                    if not df_servico.empty:
                        st.subheader(f"🔹 Veículo: {servico}")
                        st.dataframe(df_servico[['Data Execucao', 'Escala', 'Veiculo', 'Servico', 'Total_Geral', 'Capacidade', 'Ocupacao']],
                                    hide_index=True, use_container_width=True)

                        media_ocupacao = df_servico['Ocupacao'].mean()
                        total_passageiros = df_servico['Total_Geral'].sum()

                        st.markdown(f"✅ **Média de Ocupação:** {media_ocupacao:.2f}%")
                        st.markdown(f"👥 **Total de Passageiros Transportados:** {int(total_passageiros)}")
                        st.markdown("---")  # Linha divisória

            if 'TODOS' in veiculos_selecionados:
                ocupacao_geral = df_filtrado[df_filtrado['Veiculo'].isin(opcoes_veiculos)]['Ocupacao'].mean()
                st.write(f"###### Média de Ocupação Geral com TODOS serviços tipo REGULAR: **{ocupacao_geral:.2f}%**")
                st.divider()
                for veiculo in opcoes_veiculos:    
                    df_servico = df_filtrado[df_filtrado['Veiculo'] == veiculo]
                    
                    if not df_servico.empty:
                        st.subheader(f"🔹 Serviço: {veiculo}")
                        st.dataframe(df_servico[['Data Execucao', 'Escala', 'Veiculo', 'Servico', 'Total_Geral', 'Capacidade', 'Ocupacao']],
                                    hide_index=True, use_container_width=True)

                        media_ocupacao = df_servico['Ocupacao'].mean()
                        total_passageiros = df_servico['Total_Geral'].sum()

                        st.markdown(f"✅ **Média de Ocupação: {veiculo}** - {media_ocupacao:.2f}%")
                        st.markdown(f"👥 **Total de Passageiros Transportados:** {int(total_passageiros)}")
                        st.markdown("---")  # Linha divisória
            else:
                st.warning("Nenhum dado disponível após o filtro.")

        else:
            st.info("Clique no botão **Atualizar** para carregar e visualizar os dados.")

