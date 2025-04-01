import pandas as pd
import streamlit as st
from . import bbtc_qualidade
from datetime import datetime
import calendar

def BD_Uber():

    if 'df_Uber' not in st.session_state:
        st.session_state.df_Uber = bbtc_qualidade.Chamada_Uber()
    df_Uber = st.session_state.df_Uber

    df_uber_agrupado = df_Uber.groupby(['Mes_Ano']).agg({
        'Valor': 'sum',
        'Data_Uber': 'count'
    }).reset_index()

    # Obter o primeiro dia do mês e ano atual
    datainicio_usuario = datetime(datetime.today().year, datetime.today().month, 1) #datetime 64 - pd.to_datetime datetime
    ultimo_dia = calendar.monthrange(datetime.today().year, datetime.today().month)[1]
    datafim_usuario = datetime(datetime.today().year, datetime.today().month, ultimo_dia)

    datainicio = st.date_input('Data de Inicio', value=datainicio_usuario, format='DD/MM/YYYY', key='botao008')
    datafim = st.date_input('Data de Final', value=datafim_usuario, format='DD/MM/YYYY', key='botao009')

    datainicio = pd.to_datetime(datainicio)
    datafim = pd.to_datetime(datafim)
    st.divider()

    df_UberFiltrado = df_Uber[
    (df_Uber['Data_Uber'] >= datainicio) &
    (df_Uber['Data_Uber'] <= datafim)
    ]

    df_UberFiltrado = df_UberFiltrado.copy()
    df_UberFiltrado['Quantidade'] = df_UberFiltrado['Data_Uber'].count()
    df_UberFiltrado['Valor_Total_Uber'] = df_UberFiltrado['Valor'].sum()

    df_UberFiltrado_Motivo_Valor = df_UberFiltrado.groupby(['Motivo']).agg({
        'Valor': 'sum',
        'Data_Uber': 'count'
    }).reset_index()

    df_UberFiltrado_Custo = df_UberFiltrado.groupby(['Custo']).agg({
        'Valor': 'sum',
        'Data_Uber': 'count'
    }).reset_index()

    df_UberFiltrado_Setor = df_UberFiltrado.groupby(['Setor_Relacionado']).agg({
        'Valor': 'sum',
        'Data_Uber': 'count'
    }).reset_index()

    st.plotly_chart(bbtc_qualidade.Grafico_Linha_Reembolsos_Geral(df_uber_agrupado, df_uber_agrupado['Valor'], 1000, 'Uber - Mensal'))
    st.divider()

    st.container()
    col1, col2 = st.columns([8, 4])
    with col1:
        st.plotly_chart(bbtc_qualidade.Grafico_Barra_Simples_Geral(df_UberFiltrado_Custo['Custo'], df_UberFiltrado_Custo['Data_Uber'], 'Custo / Quantidade'))
    with col2:
        st.plotly_chart(bbtc_qualidade.Grafico_Pizza_Simples(df_UberFiltrado_Custo['Custo'], df_UberFiltrado_Custo['Valor'], 'Custo Empresa / Colaborador'))
    st.divider()

    st.container()
    col1, col2 = st.columns([8, 4])
    with col1:
            st.plotly_chart(bbtc_qualidade.Grafico_Barra_Simples_Geral(df_UberFiltrado_Setor['Setor_Relacionado'], df_UberFiltrado_Setor['Data_Uber'], 'Setor / Quantidade'))
    with col2:
        st.plotly_chart(bbtc_qualidade.Grafico_Pizza_Simples(df_UberFiltrado_Setor['Setor_Relacionado'], df_UberFiltrado_Setor['Valor'], 'Setor Relacionado'))
    st.divider()

    st.container()
    col1, col2 = st.columns([8, 4])
    with col1:
        st.plotly_chart(bbtc_qualidade.Grafico_Barra_Simples_Geral(df_UberFiltrado_Motivo_Valor['Motivo'], df_UberFiltrado_Motivo_Valor['Data_Uber'], 'Motivo / Quantidade'))
    with col2:
        st.plotly_chart(bbtc_qualidade.Grafico_Pizza_Simples(df_UberFiltrado_Motivo_Valor['Motivo'], df_UberFiltrado_Motivo_Valor['Valor'], 'Uber - Motivo / R$'))
    st.divider()




