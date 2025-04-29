import pandas as pd
import streamlit as st
from . import bbtc_qualidade
from datetime import datetime
import calendar
import plotly.graph_objects as go

def BD_Reclame_Aqui():

    cor_mark = 'black'
    cor_letra_mark = '#047c6c'

    st.markdown(f"""
    <style>
        /* Esconde o ícone de link automático do Streamlit */
        [data-testid="stHeaderActionElements"] {{
            display: none !important;
        }}

        /* Ajustes no card */
        .custom-box {{
            background-color: #f0f0f5;
            border-radius: 10px;
            border: 2px solid #ccc;
            text-align: right;
            max-width: 300px;
            margin: 0px auto;
            margin-left: 0px;
            min-height: 0px;
            padding: 10px;
        }}

        /* Ajusta o número */
        .custom-box h2 {{
            color: #047c6c;
            font-size: 48px;
            padding: 10px;
            text-align: center;
            margin: 0;
        }}
        </style>
    """, unsafe_allow_html=True)

    if 'df_Reclame_Aqui' not in st.session_state:
        st.session_state.df_Reclame_Aqui = bbtc_qualidade.Chamada_Reclame_Aqui()
    df_Reclame_Aqui = st.session_state.df_Reclame_Aqui

    df_Reclame_Aqui['MEDIA_NOTA'] = df_Reclame_Aqui['NOTA DO CLIENTE'].mean()
    df_Reclame_Aqui['TOTAL'] = df_Reclame_Aqui['ID DA RECLAMAÇÃO'].count()
    #df_Reclame_Aqui['AVALIAÇÃO DA SOLUÇÃO'] = df_Reclame_Aqui['AVALIAÇÃO DA SOLUÇÃO'].replace("", pd.NA)
    df_Reclame_Aqui['RESOLVIDO?'] = df_Reclame_Aqui['RESOLVIDO?'].replace("", pd.NA)

    #df_Reclame_Aqui['QTDE AVALIADAS'] = df_Reclame_Aqui['AVALIAÇÃO DA SOLUÇÃO'].map(df_Reclame_Aqui['AVALIAÇÃO DA SOLUÇÃO'].dropna().value_counts())
    df_Reclame_Aqui['QTDE AVALIADAS'] = df_Reclame_Aqui['RESOLVIDO?'].map(df_Reclame_Aqui['RESOLVIDO?'].dropna().value_counts())
    
    #df_Reclame_Aqui['QTDE NÃO AVALIADAS'] = df_Reclame_Aqui['AVALIAÇÃO DA SOLUÇÃO'].map(df_Reclame_Aqui['AVALIAÇÃO DA SOLUÇÃO'].value_counts(dropna=False))
    df_Reclame_Aqui['QTDE NÃO AVALIADAS'] = df_Reclame_Aqui['RESOLVIDO?'].map(df_Reclame_Aqui['RESOLVIDO?'].value_counts(dropna=False))


    df_Reclame_Aqui.loc[df_Reclame_Aqui['QTDE AVALIADAS'].notna(),'QTDE NÃO AVALIADAS'] = 0

    #df_Reclame_Aqui_Filtrado = df_Reclame_Aqui.dropna(subset=['NOTA DO CLIENTE', 'VOLTARIA A FAZER NEGÓCIO?', 'AVALIAÇÃO DA SOLUÇÃO']).copy()
    df_Reclame_Aqui_Filtrado = df_Reclame_Aqui.dropna(subset=['NOTA DO CLIENTE', 'VOLTARIA A FAZER NEGÓCIO?', 'RESOLVIDO?']).copy()
    df_Reclame_Aqui_Filtrado['TOTAL'] = df_Reclame_Aqui_Filtrado ['ID DA RECLAMAÇÃO'].count() 
    df_Reclame_Aqui_Filtrado['MEDIA_NOTA'] = df_Reclame_Aqui_Filtrado['NOTA DO CLIENTE'].mean()
    df_Reclame_Aqui_Filtrado.loc[df_Reclame_Aqui_Filtrado['QTDE AVALIADAS'].notna(),'QTDE AVALIADAS']=1
    df_Reclame_Aqui_Filtrado['NOVOS_NEGOCIOS']= df_Reclame_Aqui_Filtrado['VOLTARIA A FAZER NEGÓCIO?'].apply(lambda x: 1 if x == 'SIM' else 0)

    kpi_ir = int(df_Reclame_Aqui_Filtrado['TOTAL'].mean()) / int(df_Reclame_Aqui_Filtrado['TOTAL'].mean()) * 100
    kpi_media_avaliacoes = float(df_Reclame_Aqui_Filtrado['MEDIA_NOTA'].mean())
    kpi_indice_solucoes = (int(df_Reclame_Aqui_Filtrado['VALIDACAO_RESOLVIDO'].sum()) / int(df_Reclame_Aqui_Filtrado['TOTAL'].mean())) * 100
    kpi_novos_negocios = (int(df_Reclame_Aqui_Filtrado['NOVOS_NEGOCIOS'].sum()) / int(df_Reclame_Aqui_Filtrado['TOTAL'].mean())) * 100

    qtde_avaliadas = df_Reclame_Aqui['TOTAL'].mean() - df_Reclame_Aqui['QTDE NÃO AVALIADAS'].max()
    kpi_peso_avaliacoes_total = round(qtde_avaliadas / df_Reclame_Aqui['TOTAL'].mean() * 100, 2)

    validacao_negocio = round(df_Reclame_Aqui['VALIDACAO_NEGOCIO'].sum() / qtde_avaliadas * 100, 2)

    negocio_resolvido = round(df_Reclame_Aqui['VALIDACAO_RESOLVIDO'].sum() / qtde_avaliadas * 100, 2)

    kpi_avaliacao = ((kpi_ir * 2) + (kpi_media_avaliacoes*10*3) + (kpi_indice_solucoes * 3) + (kpi_novos_negocios * 2)) / 100

    status_reclame_aqui = ''
    if kpi_avaliacao < 5:
        status_reclame_aqui = 'NÃO RECOMENDADA'
        cor_mark = '#8A2BE2'
    if kpi_avaliacao >= 5 and kpi_avaliacao <= 5.9:
        status_reclame_aqui = 'RUIM'
        cor_mark = '#FF0000'
    if kpi_avaliacao >= 6 and kpi_avaliacao <= 6.9:
        status_reclame_aqui = 'REGULAR'
        cor_mark = '#FFD700'
    if kpi_avaliacao >= 7 and kpi_avaliacao <= 7.9:
        status_reclame_aqui = 'BOM'
        cor_mark = '#000080'
    if kpi_avaliacao >= 8:
        status_reclame_aqui = 'ÓTIMO'
        cor_mark = '#32CD32'

    st.markdown(f"""
    <style>
        /* Esconde o ícone de link automático do Streamlit */
        [data-testid="stHeaderActionElements"] {{
            display: none !important;
        }}
        .custom-box1 {{
            background-color: {cor_mark};
            border-radius: 100%;
            border: 2px solid #ccc;
            text-align: center;
            width: 250px;
            height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 48px;
        }}
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([8, 2])
    with col1:
        st.title('Painel Calculadora Reclame Aqui')
        st.write('Base de Calculos, apenas reclamações avaliadas')
        st.divider()

    col1, col2, col3 = st.columns([0.3, 0.3, 0.3])
    with col1:
        st.markdown("<h3 style='text-align: center;font-size: 48px;'>Indice de Respostas - IR</h3>", unsafe_allow_html=True)
        st.plotly_chart(bbtc_qualidade.Grafico_Rosca_Meta(kpi_ir, cor_mark, 100), use_container_width=True)
        st.markdown("<h3 style='text-align: center;font-size: 48px;'>Média Avaliações - MA</h3>", unsafe_allow_html=True)
        st.plotly_chart(bbtc_qualidade.Grafico_Rosca_Meta(kpi_media_avaliacoes, cor_mark, 10), use_container_width=True)

    with col2:
        st.markdown("<h3 style='text-align: center;font-size: 48px;'>Indice de Soluções - IS</h3>", unsafe_allow_html=True)
        st.plotly_chart(bbtc_qualidade.Grafico_Rosca_Meta(kpi_indice_solucoes, cor_mark, 100), use_container_width=True)
        
        st.markdown("<h3 style='text-align: center;font-size: 48px;'>Indice de Novos Negócios - IN</h3>", unsafe_allow_html=True)
        st.plotly_chart(bbtc_qualidade.Grafico_Rosca_Meta(kpi_novos_negocios, cor_mark, 100), use_container_width=True)
        
    with col3:
        st.markdown("<h3 style='text-align: center;font-size: 48px;'>Reputação Reclame Aqui - IN</h3>", unsafe_allow_html=True)
        st.plotly_chart(bbtc_qualidade.Grafico_Rosca_Meta_Nome(0, cor_mark, 1, status_reclame_aqui, 'white'), use_container_width=True)

        st.markdown("<h3 style='text-align: center;font-size: 48px;'>Avaliação Reclame Aqui</h3>", unsafe_allow_html=True)
        st.plotly_chart(bbtc_qualidade.Grafico_Rosca_Meta(kpi_avaliacao, cor_mark, 10), use_container_width=True)

    st.divider()
        

    st.title('Painel Analise Geral / Periodo')
    st.write('Base de Calculos, todas as reclamações inseridas no portal')
    st.divider()
    col1, col2, col3 = st.columns([0.3, 0.3, 0.3])
    with col1:
        st.markdown("<h3 style='text-align: center;font-size: 48px;'>Total de Reclamações</h3>", unsafe_allow_html=True)
        total_reclam = int(df_Reclame_Aqui['TOTAL'].mean())
        st.plotly_chart(bbtc_qualidade.Grafico_Rosca_Meta_Nome(total_reclam, 'white', total_reclam, total_reclam, cor_letra_mark), use_container_width=True)


    with col2:
        st.markdown("<h3 style='text-align: center;font-size: 48px;'>Quantidade Avaliadas</h3>", unsafe_allow_html=True)
        st.plotly_chart(bbtc_qualidade.Grafico_Rosca_Meta_Nome(int(qtde_avaliadas), 'white', int(qtde_avaliadas), int(qtde_avaliadas), cor_letra_mark), use_container_width=True)


    with col3:
        st.markdown("<h3 style='text-align: center;font-size: 48px;'>Peso Avaliações / Total em %</h3>", unsafe_allow_html=True)
        st.plotly_chart(bbtc_qualidade.Grafico_Rosca_Meta_Nome(kpi_peso_avaliacoes_total, 'white', kpi_peso_avaliacoes_total, kpi_peso_avaliacoes_total, cor_letra_mark), use_container_width=True)

    col1_1, col2_1 = st.columns(2)
    with col1_1:
        st.markdown("<h3 style='text-align: center;font-size: 48px;'>Voltaria Fazer Negocio?</h3>", unsafe_allow_html=True)
        st.plotly_chart(bbtc_qualidade.Grafico_Rosca_Meta_Nome(validacao_negocio, 'white', validacao_negocio, validacao_negocio, cor_letra_mark), use_container_width=True)
    with col2_1:
        st.markdown("<h3 style='text-align: center;font-size: 48px;'>Solução Resolvida</h3>", unsafe_allow_html=True)
        st.plotly_chart(bbtc_qualidade.Grafico_Rosca_Meta_Nome(negocio_resolvido, 'white', negocio_resolvido, negocio_resolvido, cor_letra_mark), use_container_width=True)


    df_linha_print_mes_ano = df_Reclame_Aqui.groupby('Mes_Ano').agg({
        'ID DA RECLAMAÇÃO': 'count',
        'QTDE AVALIADAS': 'count'
    }).reset_index()

    st.plotly_chart(bbtc_qualidade.Grafico_Linha_Dupla(df_linha_print_mes_ano,df_linha_print_mes_ano['ID DA RECLAMAÇÃO'], df_linha_print_mes_ano['QTDE AVALIADAS'], 'Num. Reclamações', 'Avaliadas', 'Reclamações / Avaliações'))









    
    
