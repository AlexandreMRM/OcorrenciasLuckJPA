import streamlit as st
import pages.Historico.ocorrencias as ocorrencias
import pages.Historico.inclusao_historico as inclusao_historico


def APP_Historico():

    #st.set_page_config(layout='wide')
    st.title('Painel de Ocorrências / Histórico')

    st.markdown("""
                    <style>
                    .stApp{
                        background-color: #047c6c;
                    }
                    <style>
        """, unsafe_allow_html=True)
    

    abas = st.tabs(['Analise Ocorrências', 'Inclusão Histórico'])

    with abas[0]:
        ocorrencias.Main_Ocorrencias()

    with abas[1]:
        inclusao_historico.Main_Inclusao_Historico()

