import pages.Historico.app_historico
import pages.Qualidade.app_qualidade
import streamlit as st

# CSS DEFINITIVO para esconder a navegação

st.set_page_config(layout='wide')

hide_menu_style = """
    <style>
        /* Ocultar barra lateral completa */
        [data-testid="stSidebar"] {
            display: none;
        }
        /* Ocultar Seta (SVG) da Navegação Lateral */
        svg[class*="st-emotion-cache"] {
            display: none;
            visibility: hidden;
        }
    </style>
    """

st.markdown(hide_menu_style, unsafe_allow_html=True)

query_params = st.query_params
app = query_params.get('app', ['']).strip().lower()

if app == 'ocorrencias':
    from pages.Historico.app_historico import APP_Historico as Historico_LuckJPA
    Historico_LuckJPA()

if app == 'qualidade':
    from pages.Qualidade.app_qualidade import APP_Qualidade as Qualidade_LuckJPA
    Qualidade_LuckJPA()

    