import streamlit as st
import pandas as pd
from . import bbtc_historico


def Main_Inclusao_Historico():
    #st.set_page_config(layout="wide")
    st.title('Cadastro de Ocorrencias')

    if 'logado' not in st.session_state:
        st.session_state.logado = False

    if 'dados_login_senha' not in st.session_state:
        st.session_state.dados_login_senha = bbtc_historico.Usuario_Senha()
    dados_login_senha = st.session_state.dados_login_senha

    login = dados_login_senha['Usuario'].tolist()
    senha = dados_login_senha['Senha'].tolist()

    if not st.session_state.logado:
        usuario = st.text_input("Usuário")
        usuario_verificar = usuario.upper()
        senha_inserida = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if bbtc_historico.verificar_login(usuario_verificar, senha_inserida, login, senha):
                st.session_state.logado = True
                st.session_state.usuario = usuario_verificar
                st.success(f"Bem-vindo(a), {usuario}!")
            else:
                st.error('Usuário ou senha inválidos')

    if st.session_state.logado:

        if 'base' not in st.session_state:
            st.session_state.base = bbtc_historico.Chamada_Historico_leitura()
        df_base = st.session_state.base

        if 'df_colaboradores' not in st.session_state:
            st.session_state.df_colaboradores = bbtc_historico.Carregar_Colaboradores_Setores_Funcao()
        df_colaboradores = st.session_state.df_colaboradores

        status_ocorrencia = 'Finalizado'
        inserido_por = st.session_state.usuario

        lista_colaboradores = df_colaboradores['Apelido'].unique().tolist()
        lista_colaboradores.sort()
        lista_setor = df_colaboradores['Setor'].unique().tolist()
        lista_setor.sort()
        lista_funcao = df_colaboradores['Função'].unique().tolist()
        lista_funcao.sort()
        lista_tipo = ['', 'Atestado', 'Comportamental', 'Elogio', 'Falta Injustificada', 'Ponto', 'Erro Operacional', 'Promoção / Contratação']
        lista_tipo.sort()
        lista_solucao = ['', 'Apenas Histórico', 'Advertência Verbal', 'Advertência por Escrito', 'Suspensão', 'Demissão']
        lista_solucao.sort()

        col1, col2, col3 = st.columns(3)
        with col1:
            entrada_colaborador = st.selectbox('Colaborador', [''] + lista_colaboradores, key='colaborador')
            data_ocorrencia = st.date_input('Data da Ocorrencia', 'today', format="DD/MM/YYYY", key='data_ocorrencia')
        with col2:
            entrada_setor = st.selectbox('Setor', [''] + lista_setor, key='setor')
            entrada_tipo = st.selectbox('Tipo da Ocorrência', lista_tipo, key='entrada_tipo')
        with col3:
            entrada_funcao = st.selectbox('Função', [''] + lista_funcao, key='funcao')
            entrada_solucao = st.selectbox('Solução da Ocorrência', lista_solucao, key='entrada_solucao')

        entrada_observacao = st.text_area('Insira a Observação', value="", max_chars=5000, key='entradaobs', height=480)

        col1, col2, col3 = st.columns([1 ,1, 24])
        with col1:
            botao_lancar = st.button('Lançar', key='botao_lancar')
        with col2:
            botao_sair = st.button("Sair", key='botao_sair')

        if botao_lancar:

            if '' in [entrada_colaborador, entrada_setor, entrada_funcao, entrada_tipo, entrada_solucao]:
                st.warning('Será necessário selecionar todos os campos')
            else: 
                nova_ocorrencia = {
                'Colaborador': entrada_colaborador,
                'Setor': entrada_setor,
                'Função': entrada_funcao,
                'Data_Ocorrencia': data_ocorrencia.strftime('%d/%m/%Y'),
                'Tipo_da_Ocorrencia': entrada_tipo,
                'Solução': entrada_solucao,
                'Status_da_Ocorrencia': status_ocorrencia,
                'Observação': entrada_observacao,
                'Inserido_por': inserido_por,
                }

                nova_linha = pd.DataFrame([nova_ocorrencia])
                df_base_novo = pd.concat([df_base, nova_linha], ignore_index=True)
                
                status_lancamento = bbtc_historico.Salvar_Dados(df_base_novo)
                if status_lancamento is True:
                    st.success(f'Ocorrência do Colaborador {entrada_colaborador} inserida')
                    st.session_state.df_base = pd.DataFrame() 
                else:
                    st.error(f'Erro no Lançamento, {status_lancamento} TENTE NOVAMENTE')

        if botao_sair:
            st.session_state.logado = False
            st.session_state.usuario = None
            st.success("Você foi deslogado com sucesso!")
            st.rerun()


