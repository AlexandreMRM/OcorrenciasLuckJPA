import pandas as pd
import streamlit as st
from . import bbtc_qualidade
from datetime import datetime
import calendar


def BD_Reclamacoes():

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
            margin-left: 0px;
            min-height: 0px;
            padding: 10px;
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

    if 'df_Reclamacao' not in st.session_state:
        st.session_state['df_Reclamacao'] = bbtc_qualidade.Chamada_Reclamacoes()
    df_Reclamacao = st.session_state.df_Reclamacao

    contagem_por_mes_ano = df_Reclamacao['Mes_Ano'].value_counts().reset_index()
    contagem_por_mes_ano.columns = ['Mes_Ano', 'Quantidade']
    df_Reclamacao['Qtde_Reclamacoes'] = df_Reclamacao['Mes_Ano'].map(contagem_por_mes_ano.set_index('Mes_Ano')['Quantidade'])


    # Obter o primeiro dia do mês e ano atual
    datainicio_usuario = datetime(datetime.today().year, datetime.today().month, 1) #datetime 64 - pd.to_datetime datetime
    ultimo_dia = calendar.monthrange(datetime.today().year, datetime.today().month)[1]
    datafim_usuario = datetime(datetime.today().year, datetime.today().month, ultimo_dia)

    st.container()
    col1, col2, col3, col4, col5 = st.columns([2, 2.5, 2.5, 3, 3])
    with col1:
        st.markdown("<h3 style='text-align:center; font-size: 26px; '>Selecione o Periodo</h3>", unsafe_allow_html=True)
        datainicio = st.date_input('Data de Inicio', value=datainicio_usuario, format='DD/MM/YYYY', key='botao006')
        datafim = st.date_input('Data de Final', value=datafim_usuario, format='DD/MM/YYYY', key='botao007')

    datainicio = pd.to_datetime(datainicio)
    datafim = pd.to_datetime(datafim)

    df_Reclamacoesfiltrado = df_Reclamacao[
        (df_Reclamacao['Data_Reclamacao'] >= datainicio) &
        (df_Reclamacao['Data_Reclamacao'] <= datafim)
    ]

    if df_Reclamacoesfiltrado.empty:
        st.warning('SEM RECLAMACOES NO PERIODO')
        return
    
    qtde_meses = df_Reclamacoesfiltrado['Mes_Ano'].unique().size

    with col2:
        st.markdown("<h3 style='text-align:center; font-size: 26px; '>Total de Reclamações</h3>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="custom-box">
                <h2>{df_Reclamacoesfiltrado['Data_Reclamacao'].count()}</h2>
            </div>
            """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("<h3 style='text-align:center; font-size: 26px; '>Média de Reclamações</h3>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="custom-box">
                <h2>{round(df_Reclamacoesfiltrado['Data_Reclamacao'].count() / qtde_meses)}</h2>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.subheader('Quantidade de Reclamacoes por Mes')
    st.plotly_chart(bbtc_qualidade.Grafico_Linha_Reembolsos_Geral(df_Reclamacao, df_Reclamacao['Qtde_Reclamacoes'], 20, 'Quantidade Mes'))
    st.divider()

    df_ReclamacoesfiltradoCategoria = df_Reclamacoesfiltrado.groupby(["Categoria"]).agg({
    'Data_Reclamacao': 'count'
    }).reset_index()

    st.subheader('Reclamações por Categoria - Periodo')
    st.plotly_chart(bbtc_qualidade.Grafico_Barra_Simples_Geral(df_ReclamacoesfiltradoCategoria['Categoria'], df_ReclamacoesfiltradoCategoria['Data_Reclamacao'], 'Quantidade Reclamacoes / Categoria'))
    st.divider()

    df_ReclamacoesfiltradoSubcategoria = df_Reclamacoesfiltrado.groupby(["Categoria", "Subcategoria"]).agg({
    'Data_Reclamacao': 'count'
    }).reset_index()
    st.subheader('Reclamações por Subcategoria - Periodo')
    st.plotly_chart(bbtc_qualidade.Grafico_Barra_Simples_Geral(df_ReclamacoesfiltradoSubcategoria['Subcategoria'], df_ReclamacoesfiltradoSubcategoria['Data_Reclamacao'], 'Quantidade Reclamacoes / Subcategoria'))
    st.divider()

    with col4:
        st.markdown("<h3 style='text-align:center; font-size: 26px; '>TOP 5 - Subcategorias</h3>", unsafe_allow_html=True)
        top_motivos = df_ReclamacoesfiltradoSubcategoria.groupby(["Categoria", "Subcategoria"])["Data_Reclamacao"].sum().nlargest(5).reset_index()
        top_motivos = top_motivos.rename(columns={'Data_Reclamacao': 'Quantidade'})
        st.dataframe(top_motivos[['Subcategoria', 'Quantidade']], hide_index=True, use_container_width=True)

    df_ReclamacoesfiltradoColaborador = df_Reclamacoesfiltrado.groupby(["Colaborador"]).agg({
    'Data_Reclamacao': 'count'
    }).reset_index()

    df_ReclamacoesfiltradoColaborador = df_ReclamacoesfiltradoColaborador[df_ReclamacoesfiltradoColaborador["Colaborador"] != "SEM GUIA"]
    top_reclamacoes = df_ReclamacoesfiltradoColaborador.groupby('Colaborador')["Data_Reclamacao"].sum().nlargest(5).reset_index()
    with col5:
        st.markdown("<h3 style='text-align:center; font-size: 26px; '>TOP 5 - Colaboradores</h3>", unsafe_allow_html=True)
        st.dataframe(top_reclamacoes, hide_index=True, use_container_width=True)


    df_canal = df_Reclamacoesfiltrado.groupby(["Canal_Reclamacao"]).agg({
    'Data_Reclamacao': 'count'
    }).reset_index()

    st.subheader('Reclamações por Canal')
    st.plotly_chart(bbtc_qualidade.Grafico_Barra_Simples_Geral(df_canal['Canal_Reclamacao'], df_canal['Data_Reclamacao'], 'Quantidade Reclamacoes / Canal'))
    st.divider()

    df_setor = df_Reclamacoesfiltrado.groupby(['Setor_Relacionado']).agg({
        'Data_Reclamacao': 'count'
    }).reset_index()

    st.subheader('Reclamações por Setor')
    st.plotly_chart(bbtc_qualidade.Grafico_Barra_Simples_Geral(df_setor['Setor_Relacionado'], df_setor['Data_Reclamacao'], 'Quantidade Reclamacoes / Setor'))
    st.divider()

    df_categoria_Geral = df_Reclamacao.groupby(['Mes_Ano', 'Categoria']).agg({
    'Data_Reclamacao': 'count',
    }).reset_index()

    st.subheader('Historico de Reclamações por Categoria')
    pizza_reclamacao, valor_reclamacao, valor_categoria = bbtc_qualidade.Grafico_Pizza_Categoria_SubCategoria(df_ReclamacoesfiltradoSubcategoria)
    for grafico_pizza, mark_valor, dado_cat in zip(pizza_reclamacao, valor_reclamacao, valor_categoria):
        col1, col2 = st.columns([8, 2])
        with col1:
            st.plotly_chart(grafico_pizza, use_container_width=True, key=f'pizza_{grafico_pizza}')
        
        with col2:
            st.subheader('Quantidade de Reclamações')
            st.markdown(f"""
            <div class="custom-box">
                <h2>{mark_valor}</h2>
            </div>
            """, unsafe_allow_html=True)
            st.write('')
            print_df = df_categoria_Geral[df_categoria_Geral['Categoria'] == dado_cat]
            print_df = print_df.rename(columns={'Data_Reclamacao': 'Quantidade'})
            print_df = print_df.sort_values('Quantidade', ascending=False)
            
            st.dataframe(print_df[['Mes_Ano', 'Quantidade']], hide_index=True, use_container_width=True, height=255)
        



