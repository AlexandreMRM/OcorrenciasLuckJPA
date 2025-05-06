import pages.Logistica.app_ocupacao as app_ocupacao
import pages.Logistica.app_titularidade as app_titularidade
import streamlit as st


def app_logistica():

    st.markdown("""
                <style>
                .stApp{
                    background-color: #047c6c;
                }
                <style>
    """, unsafe_allow_html=True)

    abas = st.tabs(['Ocupação Veicular', 'Titularidade'])

    with abas[0]:
        app_ocupacao.app_ocupacao()

    with abas[1]:
        app_titularidade.app_titularidade()