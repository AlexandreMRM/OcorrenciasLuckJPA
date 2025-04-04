from . import bbtc_qualidade
from datetime import datetime
import calendar
import plotly.graph_objects as go
import streamlit as st
import pandas as pd


def BD_NPS():
    if 'df_nps' not in st.session_state:
        st.session_state.df_nps = bbtc_qualidade.Chamada_NPS()
    df_nps = st.session_state.df_nps

    st.markdown("""
        <style>
        /* Esconde o ícone de link automático do Streamlit */
        [data-testid="stHeaderActionElements"] {
            display: none !important;
        }

        /* Ajustes no card */
        .custom-box {
            background-color: #f0f0f5;
            border-radius: 10px;
            border: 2px solid #ccc;
            text-align: right;
            max-width: 300px;
            margin: 0px auto;
            margin-left: 100px;
            min-height: 0px;
            padding: 10px;
        }
        </style>
        """, unsafe_allow_html=True)


    # Obter o primeiro dia do mês e ano atual
    datainicio_usuario = datetime(datetime.today().year, datetime.today().month, 1) 
    ultimo_dia = calendar.monthrange(datetime.today().year, datetime.today().month)[1]
    datafim_usuario = datetime(datetime.today().year, datetime.today().month, ultimo_dia)

    datainicio = st.date_input('Data de Inicio', value=datainicio_usuario, format='DD/MM/YYYY', key='botaonps_1')
    datafim = st.date_input('Data de Final', value=datafim_usuario, format='DD/MM/YYYY', key='botaonps_2')

    #if 'df_phoenix' not in st.session_state:
    #    st.session_state.df_phoenix = bbtc_qualidade.BD_Escala(datainicio, datafim)
    #df_phoenix = st.session_state.df_phoenix

    #df_phoenix_filtrado = df_phoenix.groupby(['Escala']).agg({
    #   'Servico': 'first',
    #    'Total ADT': 'sum',
    #    'Guia': 'first',
    #    'Data Execucao': 'first'
    #}).reset_index()

    nps_filtrado = df_nps[
        (df_nps['Data'] >= datainicio) &
        (df_nps['Data'] <= datafim)
    ]
    lista_passeio = nps_filtrado['Roteiro'].unique()

    #df_phoenix_filtrado['Data Execucao'] = pd.to_datetime(df_phoenix_filtrado['Data Execucao'])
    nps_filtrado = nps_filtrado.copy()
    nps_filtrado['Data'] = pd.to_datetime(nps_filtrado['Data'])

    # Realizar merge usando inner join pelas datas
    #df_merged = pd.merge(df_phoenix_filtrado, nps_filtrado, left_on='Data Execucao', right_on='Data', how='inner')

    #nps_filtrado_agg = df_merged.groupby(['Roteiro', 'Data']).agg(
    #    {'Guia': lambda x: ', '.join(x.dropna().unique()) if not x.dropna().empty else 'Sem Guia'}
    #).reset_index()

    nps_filtrado_passeios = nps_filtrado.groupby(['Roteiro', 'Data']).agg({
        'NPS': 'mean',
        'Carimbo de data/hora': 'count'
    }).reset_index()

    nps_filtrado_passeios_nota = nps_filtrado.groupby(['NPS', 'Data']).agg({
        'Carimbo de data/hora': 'count',
        'Roteiro': 'first'
    }).reset_index()

    nps_filtrado_data_contagem = nps_filtrado_passeios.groupby(['Data']).agg({
        'Carimbo de data/hora': 'count',
        'Roteiro': 'first'
    }).reset_index()

    for passeio in lista_passeio:
        nps_filtrado_passeios_nota_for = nps_filtrado_passeios_nota[nps_filtrado_passeios_nota['Roteiro'] == passeio]
        nps_filtrado_passeios_KPI = nps_filtrado_passeios[nps_filtrado_passeios['Roteiro'] == passeio]
        
        nps_filtrado_passeios_nota_for = nps_filtrado_passeios_nota_for.copy()
        nps_filtrado_passeios_nota_for['Total'] = nps_filtrado_passeios_nota_for['Carimbo de data/hora'].sum()
        nps_filtrado_passeios_nota_for['promotores'] = nps_filtrado_passeios_nota_for.loc[nps_filtrado_passeios_nota_for['NPS'].isin([4, 5]), 'Carimbo de data/hora'].sum()
        nps_filtrado_passeios_nota_for['neutro'] = nps_filtrado_passeios_nota_for.loc[nps_filtrado_passeios_nota_for['NPS'].isin([3]), 'Carimbo de data/hora'].sum()
        nps_filtrado_passeios_nota_for['destratores'] = nps_filtrado_passeios_nota_for.loc[nps_filtrado_passeios_nota_for['NPS'].isin([1, 2]), 'Carimbo de data/hora'].sum()

        count_nota = nps_filtrado_passeios_nota_for.groupby(['NPS']).agg({
            'Carimbo de data/hora': 'sum', 
            'Total': 'mean',
            'promotores': 'mean',
            'neutro': 'mean',
            'destratores': 'mean'
        }).reset_index()
        count_nota['% Promotores'] = (count_nota['promotores'] / count_nota['Total']) * 100
        count_nota['% Neutro'] = (count_nota['neutro'] / count_nota['Total']) * 100
        count_nota['% Destratores'] = (count_nota['destratores'] / count_nota['Total']) * 100
        count_nota['% NPS'] = ((count_nota['promotores'] - count_nota['destratores']) / count_nota['Total']) * 100
        if not count_nota.empty:
            st.subheader(f'NPS - {passeio}')
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                NPS = round(count_nota["% NPS"][0],2)
                st.markdown("<h3 style='text-align:center; font-size: 34px; '>Nota NPS</h3>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="custom-box">
                    <h2>{NPS}</h2>
                </div>
                </br>
                """, unsafe_allow_html=True)
            with col2:
                Promotores = round(count_nota["% Promotores"][0],2)
                st.markdown("<h3 style='text-align:center; font-size: 34px; '>Promotores</h3>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="custom-box">
                    <h2>{Promotores}</h2>
                </div>
                </br>
                """, unsafe_allow_html=True)
            with col3:
                Neutro = round(count_nota["% Neutro"][0],2)
                st.markdown("<h3 style='text-align:center; font-size: 34px; '>Neutro</h3>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="custom-box">
                    <h2>{Neutro}</h2>
                </div>
                </br>
                """, unsafe_allow_html=True)
            with col4:
                Destratores = round(count_nota["% Destratores"][0],2)
                st.markdown("<h3 style='text-align:center; font-size: 34px; '>Destratores</h3>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="custom-box">
                    <h2>{Destratores}</h2>
                </div>
                </br>
                """, unsafe_allow_html=True)
            st.plotly_chart(bbtc_qualidade.Grafico_Barra_NPS(count_nota['NPS'], count_nota['Carimbo de data/hora'], f'NPS - {passeio}'), use_container_width=True, key=f'grafico_nps{passeio}') 
            st.plotly_chart(bbtc_qualidade.Grafico_Linha_Simples(nps_filtrado_passeios_KPI, nps_filtrado_passeios_KPI['NPS'], f'Média p/ Dia - {passeio}', f'Média p/ Dia - {passeio}'), use_container_width=True)
            st.plotly_chart(bbtc_qualidade.Grafico_Barra_NPS_Qtde_nota(nps_filtrado_passeios_KPI['Data'], nps_filtrado_passeios_KPI['Carimbo de data/hora'], f'NPS - {passeio}'), use_container_width=True, key=f'grafico_barra_nps{passeio}')
            st.divider() 


