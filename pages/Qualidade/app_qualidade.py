import streamlit as st
import pages.Qualidade.reembolso as reembolso
import pages.Qualidade.uber as uber
import  pages.Qualidade.reclamacoes as reclamacoes
import  pages.Qualidade.elogios as elogios
import pages.Qualidade.reclame_aqui as reclame_aqui
import pages.Qualidade.nps as nps


def APP_Qualidade():

    #st.set_page_config(layout='wide')
    st.title('Setor Qualidade')

    st.markdown("""
                    <style>
                    .stApp{
                        background-color: #047c6c;
                    }
                    <style>
        """, unsafe_allow_html=True)
    

    abas = st.tabs(['KPI_Reembolsos', 'KPI_Reclamacoes', 'KPI_Elogios', 'KPI_Uber', 'Reclame_Aqui', 'NPS'])

    with abas[0]:
        reembolso.BD_Reembolsos()

    with abas[1]:
        reclamacoes.BD_Reclamacoes()

    with abas[2]:
        elogios.BD_Elogios()

    with abas[3]:
        uber.BD_Uber()

    with abas[4]:
        reclame_aqui.BD_Reclame_Aqui()

    with abas[5]:
        nps.BD_NPS()

