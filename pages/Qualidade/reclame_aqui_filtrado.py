import pandas as pd
import streamlit as st
import bbtc_qualidade as bbtc_qualidade
from datetime import datetime
import calendar
import plotly.graph_objects as go

#st.set_page_config(layout='wide')

def BD_Reclame_Aqui():

    if 'df_Reclame_Aqui' not in st.session_state:
        st.session_state.df_Reclame_Aqui = bbtc_qualidade.Chamada_Reclame_Aqui()
    df_Reclame_Aqui = st.session_state.df_Reclame_Aqui


    df_Reclame_Aqui
# Criar uma coluna auxiliar que recebe 1 se "VOLTARIA A FAZER NEGÓCIO?" for "SIM" e 0 caso contrário
    df_Reclame_Aqui['VALIDACAO_NEGOCIO'] = df_Reclame_Aqui['VOLTARIA A FAZER NEGÓCIO?'].apply(lambda x: 1 if x == 'SIM' else 0)

    df_Reclame_Aqui['MEDIA_NOTA'] = df_Reclame_Aqui['NOTA DO CLIENTE'].mean()
    
# Remover linhas com valores vazios ou None nas colunas especificadas
    df_Reclame_Aqui_Filtrado = df_Reclame_Aqui.dropna(subset=['NOTA DO CLIENTE', 'VOLTARIA A FAZER NEGÓCIO?', 'AVALIAÇÃO DA SOLUÇÃO'])
    st.dataframe(df_Reclame_Aqui_Filtrado)
    

    