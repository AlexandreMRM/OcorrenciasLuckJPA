import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
from st_aggrid import AgGrid, GridOptionsBuilder
from . import bbtc_historico

def Main_Ocorrencias():
        #st.set_page_config(layout="wide")

        st.markdown("""
                <style>
                .stApp{
                background-color: #047c6c;
                }
                h1{
                font-size: 48pt;
                color: #d17d7f;
                }
                h2, h3, .stMarkdown, .stRadio label, .stSelectbox label{
                font-size: 24pt;
                color: black;
                }
                .stDateInput label {
                font-size: 38pt;
                color: black;
                }
                <style>
        """, unsafe_allow_html=True)


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
                min-height: 0px;
                padding: 10px;
                }
                
                .custom-box-2 {
                background-color: #f0f0f5;
                border-radius: 10px;
                border: 2px solid #ccc;
                text-align: center;
                max-width: 300px;
                margin: 0px auto;
                
                }
                </style>
                """, unsafe_allow_html=True)

        if 'df_Historico' not in st.session_state:
                st.session_state.df_Historico = bbtc_historico.Chamada_Historico()
        df_Historico = st.session_state.df_Historico

        if 'df_Admissao_Colaborador' not in st.session_state:
                st.session_state.df_Admissao_Colaborador = bbtc_historico.Chamada_Colaborador_Admissao()
        df_Admissao_Colaborador = st.session_state.df_Admissao_Colaborador

        st.title("HISTÓRICO DE OCORRÊNCIAS")

        # Agrupar por setor e contar ocorrências
        df_ocorrencias_por_setor = df_Historico.groupby("Setor")["Colaborador"].count().reset_index()

        #Agrupar por tipo e contar ocorrências
        df_tipo_ocorrencia = df_Historico.groupby("Tipo_da_Ocorrencia")["Colaborador"].count().reset_index().sort_values(by="Colaborador", ascending=False)

        #Agrupar por colaborador e contar ocorrências
        df_colaborador = df_Historico.groupby("Colaborador")["Setor"].count().reset_index().sort_values(by="Setor", ascending=False)


        botao_radio = st.radio("Selecione uma opção", ("Geral","Colaborador","Setor/Empresa"), key="botao_radio") 
        st.divider()

        if botao_radio == "Geral":
                #Aparecer apenas dados da data selecionada
                datainicio = st.date_input("Selecione uma data de início", datetime.date(2024, 1, 1), format='DD/MM/YYYY',key="datainicio")
                datafim = st.date_input("Selecione uma data de fim", datetime.date.today(), format='DD/MM/YYYY', key="datafim")
                datainicio = pd.to_datetime(datainicio)
                datafim = pd.to_datetime(datafim)
                df_ocorrencias_por_setor_filtrado = df_Historico[
                (df_Historico['Data_Ocorrencia'] >= datainicio) & 
                (df_Historico['Data_Ocorrencia'] <= datafim)
                ]
                df_ocorrencias_por_setor_filtrado_contagem = df_ocorrencias_por_setor_filtrado.groupby("Setor")["Colaborador"].count().reset_index()
                df_tipo_ocorrencia_filtrado = df_Historico[
                (df_Historico['Data_Ocorrencia'] >= datainicio) & 
                (df_Historico['Data_Ocorrencia'] <= datafim)        
                ]

                df_tipo_ocorrencia_contagem = df_tipo_ocorrencia_filtrado.groupby("Tipo_da_Ocorrencia")["Colaborador"].count().reset_index().sort_values(by="Colaborador", ascending=False)
                df_tipo_ocorrencia_Mes = df_tipo_ocorrencia_filtrado.groupby("Mes_Ano")["Colaborador"].count().reset_index().sort_values(by="Colaborador", ascending=False)
                df_ocorrencia_op_mes = df_tipo_ocorrencia_filtrado.groupby(["Mes_Ano", "Tipo_da_Ocorrencia"])["Colaborador"].count().reset_index().sort_values(by="Colaborador", ascending=False)
                df_ocorrencia_mes_tipo_setor = df_tipo_ocorrencia_filtrado.groupby(["Tipo_da_Ocorrencia", "Setor"])["Colaborador"].count().reset_index().sort_values(by="Colaborador", ascending=False)

                st.subheader("Quantidade de Ocorrências Mês x Mês")
                st.plotly_chart(bbtc_historico.Grafico_Linha_Simples(df_tipo_ocorrencia_Mes['Mes_Ano'], "Mês", df_tipo_ocorrencia_Mes['Colaborador'], "Quantidade de Ocorrências", "Quantidade de Ocorrências por Mês"), key='grafico_mes_linha')
                col1, col2 = st.columns(2)
                with col1:
                        st.subheader(f"Quantidade de Ocorrências por Setor - Periodo")
                        st.plotly_chart(bbtc_historico.Grafico_Pizza(df_ocorrencias_por_setor_filtrado_contagem['Setor'], df_ocorrencias_por_setor_filtrado_contagem['Colaborador'], "Quantidade de Ocorrências por Setores"), key='grafico_setor_pizza')
                with col2:
                        st.subheader(f"Quantidade de Ocorrências por Tipo - Periodo")
                        st.plotly_chart(bbtc_historico.Grafico_Pizza(df_tipo_ocorrencia_contagem['Tipo_da_Ocorrencia'], df_tipo_ocorrencia_contagem['Colaborador'], "Quantidade por tipo de Ocorrências"), key='grafico_tipo_pizza')
                
                st.divider()


                lista_tipo_ocorrencias = df_tipo_ocorrencia_filtrado['Tipo_da_Ocorrencia'].unique().tolist()
                for tipo_ocorrencia in lista_tipo_ocorrencias:
                        df_ocorrencia_op_mes_filtrado = df_ocorrencia_op_mes[df_ocorrencia_op_mes['Tipo_da_Ocorrencia'] == tipo_ocorrencia]
                        df_ocorrencia_mes_tipo_setor_filtrado = df_ocorrencia_mes_tipo_setor[df_ocorrencia_mes_tipo_setor['Tipo_da_Ocorrencia'] == tipo_ocorrencia]
                        st.subheader(f"Quantidade de Ocorrências Mês x Mês - {tipo_ocorrencia}")
                        col1, col2 = st.columns([8, 4])
                        with col1:
                                st.plotly_chart(bbtc_historico.Grafico_Linha_Simples(df_ocorrencia_op_mes_filtrado['Mes_Ano'], "Mês", df_ocorrencia_op_mes_filtrado['Colaborador'], "Quantidade de Ocorrências", f"Quantidade de Ocorrências por Mês - {tipo_ocorrencia}"), key=f'grafico_tipo{tipo_ocorrencia}')
                        with col2:
                                st.plotly_chart(bbtc_historico.Grafico_Pizza(df_ocorrencia_mes_tipo_setor_filtrado['Setor'], df_ocorrencia_mes_tipo_setor_filtrado['Colaborador'], "Geral Periodo Setor"), key=f'Grafico_pizza_setor_{tipo_ocorrencia}')

        if botao_radio == "Colaborador": 
                st.subheader("Quantidade de Ocorrências por Colaborador")

                #Criar lista de colaboradores
                colaboradores = df_Admissao_Colaborador['Apelido'].unique().tolist()

                col1, col2 = st.columns([8, 4])
                with col1:
                        colaborador_selecionado = st.selectbox("Selecione um colaborador", colaboradores)
                        st.divider()
                hoje = datetime.date.today()
                
                df_colaborador_selecionado = df_Historico[df_Historico['Colaborador'] == colaborador_selecionado].copy()
                numero_ocorrencias = df_colaborador_selecionado['Data_Ocorrencia'].count()
                df_Admissao_Colaborador_selecionado = df_Admissao_Colaborador[df_Admissao_Colaborador['Apelido'] == colaborador_selecionado].copy()
                if df_Admissao_Colaborador_selecionado['Data_Admissão'].notna().any():
                        diaadmissao = df_Admissao_Colaborador_selecionado['Data_Admissão'].iloc[0].date()
                        diademissao = df_Admissao_Colaborador_selecionado['Data_Demissão'].iloc[0].date()
                        dias_trabalhados = (hoje - diaadmissao).days
                        DiasTrimestre = dias_trabalhados / 90
                        MediaOcorrencias = round(numero_ocorrencias / DiasTrimestre, 2)
                else:
                        diaadmissao = 'Autonomo'

                if df_colaborador_selecionado.empty:
                        st.warning("Sem Histórico de Ocorrencias.")
                else:
                        st.divider()
                        st.subheader("Histórico")
                        # colcar df_colaborador_selecionado['Data_Ocorrencia'] no formato DD/MM/YYYY
                        df_colaborador_selecionado['Data_Ocorrencia'] = pd.to_datetime(df_colaborador_selecionado['Data_Ocorrencia'], errors='coerce').dt.strftime('%d/%m/%Y')
                        df_colaborador_selecionado = df_colaborador_selecionado[['Setor', 'Data_Ocorrencia', 'Tipo_da_Ocorrencia', 'Observação']]
                        gb = GridOptionsBuilder.from_dataframe(df_colaborador_selecionado)
                        gb.configure_pagination(paginationAutoPageSize=True)
                        gb.configure_default_column(resizable=True)
                        gb.configure_column("Setor", width=100)
                        gb.configure_column("Data_Ocorrencia", width=100)
                        gb.configure_column("Tipo_da_Ocorrencia", width=150)
                        gb.configure_column("Observação", width=400, wrapText=True, autoHeight=True)
                        gridOptions = gb.build()
                        gridOptions["pagination"] = False
                        gridOptions["defaultColDef"] = {"cellStyle": {"fontSize": "24px", "borderBottom": "3px solid black"}, "headerClass": "header-style"}
                        
                        AgGrid(df_colaborador_selecionado, gridOptions=gridOptions, fit_columns_on_grid_load=True, height=1000,)
                        
                if df_Admissao_Colaborador_selecionado['Data_Demissão'].isna().sum() > 0:
                        with col2:
                                st.markdown("<h3 style='text-align:center; font-size: 34px; '>Situação</h3>", unsafe_allow_html=True)
                                st.markdown(f"""
                                <div class="custom-box">
                                <h2>Ativo</h2>
                                </div>
                                </br>
                                """, unsafe_allow_html=True)

                        if diaadmissao == 'Autonomo':
                                with col1:
                                        col1_1, col2_1, col3_1 = st.columns([0.3, 0.4, 0.3])
                                        with col1_1:
                                                st.markdown("""
                                                        <div style="text-align: center;">
                                                        <span style="font-size: 32px; font-weight: bold;">Tipo de Contrato:</span>
                                                        <span style="font-size: 24px; font-weight: normal;"> Autônomo</span>
                                                        </div>
                                                        """,
                                                        unsafe_allow_html=True)
                        else:
                                with col1:
                                        col1_1, col2_1, col3_1 = st.columns([0.3, 0.4, 0.3])
                                        with col1_1:
                                                st.markdown(f"""
                                                        <div style="text-align: center;">
                                                        <span style="font-size: 32px; font-weight: bold;">Data de Admissão: </span>
                                                        <span style="font-size: 24px; font-weight: normal;"> {df_Admissao_Colaborador_selecionado['Data_Admissão'].iloc[0].strftime('%d/%m/%Y')}</span>
                                                        </div>
                                                        """,
                                                        unsafe_allow_html=True)

                                        with col2_1:
                                                st.markdown(f"""
                                                        <div style="text-align: center;">
                                                        <span style="font-size: 32px; font-weight: bold;">Média de Ocorrências p/ TRI: </span>
                                                        <span style="font-size: 24px; font-weight: normal;"> {MediaOcorrencias}</span>
                                                        </div>
                                                        """,
                                                        unsafe_allow_html=True)

                                        with col3_1:
                                                st.markdown(f"""
                                                        <div style="text-align: center;">
                                                        <span style="font-size: 32px; font-weight: bold;">Dias trabalhados: </span>
                                                        <span style="font-size: 24px; font-weight: normal;"> {dias_trabalhados}</span>
                                                        </div>
                                                        """,
                                                        unsafe_allow_html=True)
                                
                else:
                        with col2:
                                st.markdown("<h3 style='text-align:center; font-size: 34px; '>Situação</h3>", unsafe_allow_html=True)
                                st.markdown(f"""
                                <div class="custom-box">
                                <h2>Inativo</h2>
                                </div>
                                </br>
                                """, unsafe_allow_html=True)

                        with col1:
                                col1_1, col2_1, col3_1 = st.columns([0.3, 0.4, 0.3])
                                with col1_1:
                                        st.markdown(f"""
                                                <div style="text-align: center;">
                                                <span style="font-size: 32px; font-weight: bold;">Data de Admissão: </span>
                                                <span style="font-size: 24px; font-weight: normal;"> {df_Admissao_Colaborador_selecionado['Data_Admissão'].iloc[0].strftime('%d/%m/%Y')}</span>
                                                </div>
                                                """,
                                                unsafe_allow_html=True)
                                with col2_1:
                                        st.markdown(f"""
                                                <div style="text-align: center;">
                                                <span style="font-size: 32px; font-weight: bold;">Data de Demissão: </span>
                                                <span style="font-size: 24px; font-weight: normal;"> {df_Admissao_Colaborador_selecionado['Data_Demissão'].iloc[0].strftime('%d/%m/%Y')}</span>
                                                </div>
                                                """,
                                                unsafe_allow_html=True)
                                with col3_1:
                                        st.markdown(f"""
                                                <div style="text-align: center;">
                                                <span style="font-size: 32px; font-weight: bold;">Média de Ocorrências: </span>
                                                <span style="font-size: 24px; font-weight: normal;"> {MediaOcorrencias}</span>
                                                </div>
                                                """,
                                                unsafe_allow_html=True)
                                        
                #st.write(df_colaborador_selecionado)
                
        if botao_radio == "Setor/Empresa": 
                
                Setor = df_Historico['Setor'].unique().tolist()
                setor_selecionado = st.selectbox("Selecione um Setor",Setor)
                st.divider()

                # Filtrar os dados para o Setor selecionado
                df_ocorrencias_por_setor_filtrado = df_Historico[df_Historico['Setor'] == setor_selecionado]

                #Aparecer no filtro apenas Colaborador, Data e Tipo da Ocorrencia
                df_ocorrencias_por_setor_filtrado_group = df_ocorrencias_por_setor_filtrado[['Colaborador','Setor', 'Data_Ocorrencia', 'Tipo_da_Ocorrencia', 'Mes_Ano']]
                data_min = df_ocorrencias_por_setor_filtrado_group['Data_Ocorrencia'].min().date()
                
                df_ocorrencia_colaborador = df_ocorrencias_por_setor_filtrado_group.groupby("Colaborador")["Data_Ocorrencia"].count().reset_index().sort_values(by="Data_Ocorrencia", ascending=False)
                #Top 5 maiores colaboradores
                df_ocorrencia_colaborador = df_ocorrencia_colaborador.head(10)
                
                hoje = datetime.date.today()
                dias_geral = (hoje - data_min).days / 90

                #Media de Ocorrência do Setor por Trimestre
                numero_ocorrencias = round(df_ocorrencias_por_setor_filtrado_group['Data_Ocorrencia'].count() / dias_geral, 2)
                
                df_tipo_ocorrencia_filtrado = df_Historico[df_Historico['Setor'] == setor_selecionado]
                df_tipo_ocorrencia_contagem = df_tipo_ocorrencia_filtrado.groupby(['Tipo_da_Ocorrencia', 'Mes_Ano'])['Colaborador'].count().reset_index().sort_values(by="Colaborador", ascending=False)
                df_tipo_ocorrencia_contagem_mes = df_tipo_ocorrencia_contagem.groupby('Mes_Ano')['Colaborador'].sum().reset_index()
                df_tipo_ocorrencia_contagem_tipo = df_tipo_ocorrencia_filtrado.groupby(['Tipo_da_Ocorrencia'])['Colaborador'].count().reset_index().sort_values(by="Colaborador", ascending=False)

                df_Admissao_Colaborador_setor = df_Admissao_Colaborador[df_Admissao_Colaborador['Setor'] == setor_selecionado].copy()
                quantidade_colaboradores_ativos = df_Admissao_Colaborador_setor['Data_Demissão'].isna().sum()
                
                #Quantidade de Ocorrencia por Setor
                media_ocorrencia_setor = df_ocorrencias_por_setor_filtrado_group['Data_Ocorrencia'].count()

                #Media de Ocorrencia por Colaborador Ativo
                media_ocorrencia_colab_ativo = round(media_ocorrencia_setor / quantidade_colaboradores_ativos, 2)

                #Plotagem

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                        st.container()
                        st.markdown("<h3 style='text-align:center; font-size: 34px; '>Colaboradores Ativos</h3>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="custom-box-2">
                        <h2>{quantidade_colaboradores_ativos}</h2>
                        </div>
                        </br>
                        """, unsafe_allow_html=True)
                
                with col2:
                        st.container()
                        st.markdown("<h3 style='text-align:center; font-size: 34px; '>Total Ocorrências</h3>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="custom-box-2">
                        <h2>{media_ocorrencia_setor}</h2>
                        </div>
                        </br>
                        """, unsafe_allow_html=True)

                with col3:
                        st.container()
                        st.markdown("<h3 style='text-align:center; font-size: 34px; '>Ocorrência p/ Colaborador</h3>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="custom-box-2">
                        <h2>{media_ocorrencia_colab_ativo}</h2>
                        </div>
                        </br>
                        """, unsafe_allow_html=True)

                with col4:
                        st.container()
                        st.markdown("<h3 style='text-align:center; font-size: 34px; '>Ocorrências p/ TRI</h3>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="custom-box-2">
                        <h2>{numero_ocorrencias}</h2>
                        </div>
                        </br>
                        """, unsafe_allow_html=True)

                

                st.divider()

                
                st.markdown("<h3 style='text-align:left; font-size: 34px; '>Ocorrências por Periodo</h3>", unsafe_allow_html=True)
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                        st.plotly_chart(bbtc_historico.Grafico_Linha_Simples(df_tipo_ocorrencia_contagem_mes['Mes_Ano'], "Mês", df_tipo_ocorrencia_contagem_mes['Colaborador'], "Quantidade de Ocorrências", "Quantidade de Ocorrências por Mês"), key='grafico_linha')
                
                with col2:
                        st.plotly_chart(bbtc_historico.Grafico_Pizza(df_tipo_ocorrencia_contagem_tipo['Tipo_da_Ocorrencia'], df_tipo_ocorrencia_contagem_tipo['Colaborador'], "Ocorrências por Tipo"), key='grafico_pizza')
                
                st.divider()

                st.markdown("<h3 style='text-align:left; font-size: 34px; '>TOP 5 Colaboradores</h3>", unsafe_allow_html=True)
                st.plotly_chart(bbtc_historico.Grafico_Barras_Simples(df_ocorrencia_colaborador['Colaborador'], 'Colaborador', df_ocorrencia_colaborador['Data_Ocorrencia'], "Quantidade", "Colaboradores com mais Ocorrências - (TOP 5)"), key='grafico_colaborador_barras')

                


                
                
        

        

        
      

      
        

