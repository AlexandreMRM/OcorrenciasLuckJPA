import pandas as pd
import streamlit as st
from . import bbtc_qualidade
from datetime import datetime
import calendar

def BD_Elogios():

    if 'df_Elogios' not in st.session_state:
        st.session_state.df_Elogios = bbtc_qualidade.Chamada_Elogios()
    df_Elogios = st.session_state.df_Elogios

    # Obter o primeiro dia do mês e ano atual
    datainicio_usuario = datetime(datetime.today().year, datetime.today().month, 1) #datetime 64 - pd.to_datetime datetime
    ultimo_dia = calendar.monthrange(datetime.today().year, datetime.today().month)[1]
    datafim_usuario = datetime(datetime.today().year, datetime.today().month, ultimo_dia)

    st.container()
    col1, col2, col3, col4, col5 = st.columns([2, 2.5, 2.5, 3, 3])

    with col1:
        st.markdown("<h3 style='text-align:center; font-size: 26px; '>Selecione o Periodo</h3>", unsafe_allow_html=True)
        datainicio = st.date_input('Data de Inicio', value=datainicio_usuario, format='DD/MM/YYYY', key='botao003')
        datafim = st.date_input('Data de Final', value=datafim_usuario, format='DD/MM/YYYY', key='botao004')

    datainicio = pd.to_datetime(datainicio)
    datafim = pd.to_datetime(datafim)

    df_Elogiosfiltrado = df_Elogios[
        (df_Elogios['Data_Elogio'] >= datainicio) &
        (df_Elogios['Data_Elogio'] <= datafim)
    ]

    if df_Elogiosfiltrado.empty:
        st.warning('SEM ELOGIOS NO PERIODO')

    else:
        df_Elogiosfiltrado = df_Elogiosfiltrado.copy()
        df_Elogiosfiltrado['Total_Elogio'] = df_Elogiosfiltrado['Data_Elogio'].count()
        #df_Elogiosfiltrado['Total_Elogio'] = df_Elogiosfiltrado['Data_Elogio'].count()

        with col2:
            st.markdown("<h3 style='text-align:center; font-size: 26px; '>Elogios no Periodo</h3>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="custom-box">
                    <h2>{df_Elogiosfiltrado['Total_Elogio'].unique()[0]}</h2>
                </div>
                """, unsafe_allow_html=True)

        df_ElogiosfiltradoCanal = df_Elogiosfiltrado.groupby(["Canal_Elogio"]).agg({
        'Data_Elogio': 'count',
        'Mes_Ano': 'first'
        }).reset_index()
        df_ElogiosfiltradoCanal['Total_Elogio'] = df_ElogiosfiltradoCanal['Data_Elogio'].count()

        df_ElogiosFiltradoMotivo = df_Elogiosfiltrado.groupby(["Motivo"]).agg({
        'Data_Elogio': 'count',
        'Mes_Ano': 'first'
        }).reset_index()
        df_ElogiosFiltradoMotivo['Total_Elogio'] = df_ElogiosFiltradoMotivo['Data_Elogio'].count()

        df_ElogiosfiltradoSetor = df_Elogiosfiltrado.groupby(["Setor_Relacionado"]).agg({
        'Data_Elogio': 'count',
        'Mes_Ano': 'first'
        }).reset_index()
        df_ElogiosfiltradoSetor['Total_Elogio'] = df_ElogiosfiltradoSetor['Data_Elogio'].count()

        df_ElogiosfiltradoColaborador = df_Elogiosfiltrado.groupby(['Colaborador', 'Canal_Elogio']).agg({
        'Data_Elogio': 'count',
        'Setor_Relacionado': 'first'
        }).reset_index()

        df_ElogiosfiltradoColaborador['Peso'] = df_ElogiosfiltradoColaborador['Canal_Elogio'].map({'TripAdvisor': 1.2, 'Google': 1.1}).fillna(1)
        df_ElogiosfiltradoColaborador['Quantidade_Peso'] = df_ElogiosfiltradoColaborador['Data_Elogio'] * df_ElogiosfiltradoColaborador['Peso']

        df_ElogiosRankingGuia = df_ElogiosfiltradoColaborador[
            (df_ElogiosfiltradoColaborador['Setor_Relacionado'] == "Guias") 
        ]
        df_ElogiosRankingMotorista = df_ElogiosfiltradoColaborador[
            (df_ElogiosfiltradoColaborador['Setor_Relacionado'] == "Motorista") 
        ]
        df_ElogiosRankingVendas = df_ElogiosfiltradoColaborador[
            (df_ElogiosfiltradoColaborador['Setor_Relacionado'] == "Vendas") 
        ]

        df_ElogiosRankingGuia = df_ElogiosRankingGuia.sort_values(['Quantidade_Peso'], ascending=False)
        df_ElogiosRanking_Guia = df_ElogiosfiltradoColaborador.head(5)
        df_ElogiosRanking_Guia = df_ElogiosRanking_Guia.rename({'Data_Elogio': 'Quantidade'}, axis=1)
        df_ElogiosRankingMotorista = df_ElogiosRankingMotorista.sort_values(['Quantidade_Peso'], ascending=False)
        df_ElogiosRankingMotorista = df_ElogiosRankingMotorista.head(5)
        df_ElogiosRankingMotorista = df_ElogiosRankingMotorista.rename({'Data_Elogio': 'Quantidade'}, axis=1)
        df_ElogiosRankingVendas = df_ElogiosRankingVendas.sort_values(['Quantidade_Peso'], ascending=False)
        df_ElogiosRankingVendas = df_ElogiosRankingVendas.head(5)
        df_ElogiosRankingVendas = df_ElogiosRankingVendas.rename({'Data_Elogio': 'Quantidade'}, axis=1)

        with col3:
            st.markdown("<h3 style='text-align:center; font-size: 26px; '>TOP 5 Elogios - Vendas</h3>", unsafe_allow_html=True)
            st.dataframe(df_ElogiosRankingVendas[['Colaborador', 'Quantidade']], hide_index=True, use_container_width=True)

        with col4:
            st.markdown("<h3 style='text-align:center; font-size: 26px; '>TOP 5 Elogios - Guia</h3>", unsafe_allow_html=True)
            st.dataframe(df_ElogiosRanking_Guia[['Colaborador', 'Quantidade']], hide_index=True, use_container_width=True)


        with col5:
            st.markdown("<h3 style='text-align:center; font-size: 26px; '>TOP 5 Elogios - Motorista</h3>", unsafe_allow_html=True)
            st.dataframe(df_ElogiosRankingMotorista[['Colaborador', 'Quantidade']], hide_index=True, use_container_width=True)

        st.divider()
        st.subheader('Quantidade de Elogios - Periodo')
        st.plotly_chart(bbtc_qualidade.Grafico_Linha_Reembolsos_Geral(df_Elogiosfiltrado, df_Elogiosfiltrado['Total_Elogio'], 10.0, 'Quantidade de Elogios por Mes'))
        st.divider()

        
        st.container()
        st.subheader('Elogios por Canal')
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            st.plotly_chart(bbtc_qualidade.Grafico_Linha_Reembolsos_Geral(df_ElogiosfiltradoCanal, df_ElogiosfiltradoCanal['Total_Elogio'], 5.0, 'Evolução de Elogios por Canal'))
            st.divider()
        with col1_2:
            st.plotly_chart(bbtc_qualidade.Grafico_Pizza_Simples(df_ElogiosfiltradoCanal['Canal_Elogio'], df_ElogiosfiltradoCanal['Data_Elogio'], 'Elogios por Canal'))
            st.divider()
        

        st.container()
        st.subheader('Elogios por Setor')
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            st.plotly_chart(bbtc_qualidade.Grafico_Linha_Reembolsos_Geral(df_ElogiosfiltradoSetor, df_ElogiosfiltradoSetor['Total_Elogio'], 2.0, 'Evolução de Elogios por Setor'))
            st.divider()
        with col1_2:
            st.plotly_chart(bbtc_qualidade.Grafico_Pizza_Simples(df_ElogiosfiltradoSetor['Setor_Relacionado'], df_ElogiosfiltradoSetor['Data_Elogio'], 'Elogios por Setor'))
            st.divider()

        st.container()
        st.subheader('Elogios por Motivo')
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            st.plotly_chart(bbtc_qualidade.Grafico_Linha_Reembolsos_Geral(df_ElogiosFiltradoMotivo, df_ElogiosFiltradoMotivo['Total_Elogio'], 2.0, 'Evolução de Elogios por Motivo'))
            st.divider()
        with col1_2:
            st.plotly_chart(bbtc_qualidade.Grafico_Pizza_Simples(df_ElogiosFiltradoMotivo['Motivo'], df_ElogiosFiltradoMotivo['Data_Elogio'], 'Motivos de Elogios'))
            st.divider()
            

            