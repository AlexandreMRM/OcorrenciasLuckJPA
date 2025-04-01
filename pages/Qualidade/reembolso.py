import pandas as pd
import streamlit as st
from . import bbtc_qualidade
from datetime import datetime
import calendar
import plotly.graph_objects as go

def BD_Reembolsos():

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
                text-align: center;
                max-width: 300px;
                margin: 0px auto;
                }

        /* Ajusta o número */
        .custom-box h2 {
            color: #047c6c;
            font-size: 48px;
            padding: 10px;
            text-align: center;
            margin: 0;
        }
        </style>
        """, unsafe_allow_html=True)


    if 'df_Reembolsos' not in st.session_state:
        st.session_state.df_Reembolsos = bbtc_qualidade.Chamada_Reembolso()
    df_Reembolso = st.session_state.df_Reembolsos

    if 'df_KPI' not in st.session_state:
        st.session_state.df_KPI = bbtc_qualidade.Chamada_KPI()
    df_kpi = st.session_state.df_KPI

    merged_df = pd.merge(df_Reembolso, df_kpi, on='Mes_Ano', how='left')
    df_Reembolso = merged_df.copy()

    st.container()
    col1, col2, col3, col4, col5 = st.columns([0.25, 0.25, 0.25, 0.25, 0.25])


    # Obter o primeiro dia do mês e ano atual
    datainicio_usuario = datetime(datetime.today().year, datetime.today().month, 1) #datetime 64 - pd.to_datetime datetime
    ultimo_dia = calendar.monthrange(datetime.today().year, datetime.today().month)[1]
    datafim_usuario = datetime(datetime.today().year, datetime.today().month, ultimo_dia)

    with col1:
        datainicio = st.date_input('Data de Inicio', value=datainicio_usuario, format='DD/MM/YYYY', key='botao001')
        datafim = st.date_input('Data de Final', value=datafim_usuario, format='DD/MM/YYYY', key='botao002')

    datainicio = pd.to_datetime(datainicio)
    datafim = pd.to_datetime(datafim)

    df_Reembolso_filtrado = df_Reembolso[
        (df_Reembolso['Data_Reembolso'] >= datainicio) &
        (df_Reembolso['Data_Reembolso'] <= datafim)
    ]
    df_Reembolso_filtrado = df_Reembolso_filtrado.copy()

    df_Reembolso_filtrado['Total_Reembolsos'] = df_Reembolso_filtrado['Cod_Reserva'].count()
    df_Reembolso_filtrado['Valor_Total_Reembolsos'] = df_Reembolso_filtrado['Valor'].sum()
    df_Reembolso_filtrado['TM_Reembolsos'] = df_Reembolso_filtrado['Valor_Total_Reembolsos'] / df_Reembolso_filtrado['Total_Reembolsos']

    df_Reembolso_Filtrado_Motivo = df_Reembolso_filtrado.groupby(['Motivo']).agg({
        'Valor': 'sum',
        'Cod_Reserva': 'count'
    }).reset_index()

    df_Reembolso_Total_Mes = df_Reembolso.groupby(['Mes_Ano']).agg({
        'Cod_Reserva': 'count',
        'Valor': 'sum',
        'Valor_KPI': 'mean'
    }).reset_index()
    df_Reembolso_Total_Mes = df_Reembolso_Total_Mes.rename(columns={'Cod_Reserva': 'Quantidade'})

    top_motivos = df_Reembolso_Filtrado_Motivo.groupby("Motivo")["Cod_Reserva"].sum().nlargest(5).reset_index()
    top_motivos = top_motivos.rename(columns={'Cod_Reserva': 'Qtde'})

    top_vendedor = df_Reembolso_filtrado.groupby("Vendedor")["Valor"].sum().nlargest(5).reset_index()
    top_vendedor_print = top_vendedor.copy()
    top_vendedor_print['Valor'] = top_vendedor['Valor'].apply(lambda x: bbtc_qualidade.formatar_moeda(x))


    df_Reembolso_Filtrado_Motivo_Setor = df_Reembolso_filtrado.groupby(['Motivo', 'Setor_Relacionado']).agg({
        'Valor': 'sum',
        'Cod_Reserva': 'count'
    }).reset_index()

    df_Reembolso_filtrado_Relacao_Problema = df_Reembolso_filtrado.groupby(['Relacao_Problema', 'Setor_Relacionado', 'Mes_Ano']).agg({
        'Valor': 'sum',
        'Cod_Reserva': 'count'
    }).reset_index()

    df_Reembolso_filtrado_Relacao_Problema["Cliente"] = df_Reembolso_filtrado_Relacao_Problema.apply(
        lambda x: x["Cod_Reserva"] if x["Relacao_Problema"] == "Cliente" else 0, axis=1
    )

    df_Reembolso_filtrado_Relacao_Problema["Empresa"] = df_Reembolso_filtrado_Relacao_Problema.apply(
        lambda x: x["Cod_Reserva"] if x["Relacao_Problema"] == "Empresa" else 0, axis=1
    )

    df_Reembolso_filtrado_Relacao_Problema['Cont_Cliente'] = df_Reembolso_filtrado_Relacao_Problema["Cliente"].sum()
    df_Reembolso_filtrado_Relacao_Problema['Cont_Empresa'] = df_Reembolso_filtrado_Relacao_Problema["Empresa"].sum()


    df_Reembolso_filtrado_Relacao_Problema_Filtrado_Empresa = df_Reembolso_filtrado_Relacao_Problema[df_Reembolso_filtrado_Relacao_Problema['Relacao_Problema'] == 'Empresa']

    df_Reembolso_filtrado_Relacao_Problema_Mensal = df_Reembolso_filtrado_Relacao_Problema.groupby(['Relacao_Problema', 'Mes_Ano']).agg({'Valor': 'sum'}).reset_index()

    total_ocorrencias = df_Reembolso_filtrado_Relacao_Problema['Cod_Reserva'].sum()

    with col2:
        st.markdown("<h3 style='text-align:center; font-size: 26px; '>Reembolsos por Periodo</h3>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="custom-box">
                <h2>{total_ocorrencias}</h2>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        st.markdown("<h3 style='text-align:center; font-size: 26px; '>Média R$ por Reembolso</h3>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="custom-box">
                <h2>R${round(df_Reembolso_filtrado['TM_Reembolsos'].unique()[0], 2)}</h2>
            </div>
            """, unsafe_allow_html=True)
            
    df_grafico_relacao_problema = df_Reembolso_filtrado_Relacao_Problema.drop_duplicates('Relacao_Problema', ignore_index=True)
    df_grafico_relacao_problema = df_grafico_relacao_problema.copy()

    df_grafico_relacao_problema.loc[df_grafico_relacao_problema['Relacao_Problema'] == 'Cliente', 'Contador_Problema'] = df_grafico_relacao_problema['Cont_Cliente']
    df_grafico_relacao_problema.loc[df_grafico_relacao_problema['Relacao_Problema'] == 'Empresa', 'Contador_Problema'] = df_grafico_relacao_problema['Cont_Empresa']

    with col4:
        st.markdown("<h3 style='text-align:center; font-size: 26px; '>TOP 5 Motivos</h3>", unsafe_allow_html=True)
        st.data_editor(top_motivos, hide_index=True, use_container_width=True)

    with col5:
        st.markdown("<h3 style='text-align:center; font-size: 26px; '>TOP 5 Vendedores</h3>", unsafe_allow_html=True)
        st.data_editor(top_vendedor_print, hide_index=True, use_container_width=True)

    st.divider()
    st.container()
    st.header('Quantidade Reembolsos')
    st.plotly_chart(bbtc_qualidade.Grafico_Linha_Reembolsos_Geral(df_Reembolso_Total_Mes, df_Reembolso_Total_Mes['Quantidade'], 60, 'Reembolsos / Quantidade'))
    st.write('')
    st.plotly_chart(bbtc_qualidade.Grafico_Linha_Reembolsos_Geral(df_Reembolso_Total_Mes, df_Reembolso_Total_Mes['Valor'], df_Reembolso_Total_Mes['Valor_KPI'], 'Reembolsos / Valor'))
    st.divider()


    st.container()
    st.header('Relação Problema - Empresa / Cliente')
    col1, col2 = st.columns([8, 4])
    with col1:
        st.plotly_chart(bbtc_qualidade.Grafico_Barra_Relacao_Problema_Mensal(df_Reembolso_filtrado_Relacao_Problema_Mensal))
        st.write('')


    with col2:
        st.plotly_chart(bbtc_qualidade.Grafico_Pizza_Relacao_Problema(df_grafico_relacao_problema))
        st.write('')
    st.divider()


    st.container()
    st.header('Quantidade de Reembolso por Setor')
    pizzas, barras = bbtc_qualidade.Grafico_Pizza_Qtde_Reembolso_MesxMes(df_Reembolso_filtrado_Relacao_Problema_Filtrado_Empresa)
    colunas = st.columns(2)
    for ind, (grafico_pizza, grafico_barras) in enumerate(zip(pizzas, barras)):
        with colunas[0]:
            st.plotly_chart(grafico_pizza, key=f"pizza_{ind}")
        with colunas[1]:
            st.plotly_chart(grafico_barras, key=f"barras_{ind}")

    st.divider()

    st.container()
    st.header('Comparativos por Motivos / Setor')
    col1, col2 = st.columns([6, 6])

    with col1:
        barra_reembolso = bbtc_qualidade.Grafico_Barra_Reembolso_Setor(df_Reembolso_Filtrado_Motivo_Setor)

        colunas_barras = st.columns(1)
        for ind_barra, grafico_barras in enumerate(barra_reembolso):
            with colunas_barras[ind_barra % 1]:
                st.plotly_chart(grafico_barras)

    with col2:
        pizza_reembolsos = bbtc_qualidade.Grafico_Pizza_Reembolso_Setor(df_Reembolso_Filtrado_Motivo_Setor)

        colunas_barras = st.columns(1)
        for ind_barra, grafico_pizza_motivo in enumerate(pizza_reembolsos):
            with colunas_barras[ind_barra % 1]:
                st.plotly_chart(grafico_pizza_motivo)




    

    
    
    
    






   

