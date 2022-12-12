
import pandas as pd
import folium
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static


df_ler = pd.read_csv('dataset/train.csv')

df = df_ler.copy()

# Remover spaco da string

df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()


#Conversao de texto/categoria/string para numeros inteiros



# Excluir as linhas com a idade dos entregadores vazia
# ( Conceitos de seleção condicional )
linhas_vazias = df['Delivery_person_Age'] != 'NaN '
df = df.loc[linhas_vazias, :]
df = df.loc[df['City']!= 'NaN', :]
df = df.loc[df['Road_traffic_density']!= 'NaN', :]
df = df.loc[df['City'] != 'NaN', :]
df = df.loc[df['Festival'] != 'NaN', :]


# Conversao de texto/categoria/strings para numeros decimais
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

# Conversao de texto para data
df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

# Remove as linhas da culuna multiple_deliveries que tenham o 
# conteudo igual a 'NaN '
linhas_vazias = df['multiple_deliveries'] != 'NaN '
df = df.loc[linhas_vazias, :]
df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

#remover (min)

df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1])
df['Time_taken(min)'] = df['Time_taken(min)'].astype( int )


#======================================================
# barra lateral
#======================================================


st.header('Marketplace - Visão Entregadores')


image_path = 'imagem.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)


st.sidebar.markdown('### Cury Companhy')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYY')



st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
                    'Quais as condições do trânsito', 
                    ['Low', 'Medium', 'High', 'Jam'],
                    default=['Low', 'Medium', 'High', 'Jam'])

linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#=======================
#Layout no streamlit
#=============================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'])
                    
with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            
            df_idade_maior = df['Delivery_person_Age'].max()
            col1.metric ('Maior de idade', df_idade_maior)

            
        with col2:
            
            df_idade_menor = df['Delivery_person_Age'].min()
            col2.metric ('Menor de idade', df_idade_menor)
            
        with col3:
            df_melho_condicao = df['Vehicle_condition'].max()
            col3.metric('Melhor condição', df_melho_condicao)

            
        with col4:
            df_pior_condicao = df['Vehicle_condition'].min()
            col4.metric('Pior condição', df_pior_condicao)
            
    with st.container():
        st.markdown("""___""")
        st.subheader('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação media por entreador')
            df_media_entregador = (df.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']]
                                    .groupby('Delivery_person_ID')
                                    .mean()
                                    .reset_index())
            st.dataframe(df_media_entregador)

            
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            df_media_std = (df.loc[:,['Road_traffic_density', 'Delivery_person_Ratings']]
                              .groupby('Road_traffic_density')
                              .agg({'Delivery_person_Ratings':['mean', 'std']}))

            df_media_std.columns = ['Mean', 'sdt']
            df_media_std = df_media_std.reset_index()
            
            st.dataframe(df_media_std)
            
            
            st.markdown('##### Avaliação média por clima')
            df_media_std = (df.loc[:,['Delivery_person_Ratings', 'Weatherconditions']]
                              .groupby('Weatherconditions')
                              .agg({'Delivery_person_Ratings':['mean', 'std']}))

            df_media_std.columns = ['Mean', 'sdt']
            df_media_std = df_media_std.reset_index()
            st.dataframe(df_media_std)
            
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de entrega')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rápido')
            df_rapidos = (df.loc[:,['City', 'Delivery_person_ID','Time_taken(min)']]
                            .groupby(['City', 'Delivery_person_ID'])
                            .mean()
                            .sort_values(['City', 'Time_taken(min)'], ascending=True).reset_index())


            df_aux1 = df_rapidos.loc[df_rapidos['City'] == 'Urban', :].head(10)
            df_aux2 = df_rapidos.loc[df_rapidos['City'] == 'Metropolitian', :].head(10)
            df_aux3 = df_rapidos.loc[df_rapidos['City'] == 'Semi-Urban', :].head(10)


            df1 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
            st.dataframe(df1)
            
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df_lentos = (df.loc[:,['City', 'Delivery_person_ID','Time_taken(min)']]
                .groupby(['City', 'Delivery_person_ID']).mean()
                .sort_values(['City', 'Time_taken(min)'], ascending=False).reset_index())


            df_aux1 = df_lentos.loc[df_lentos['City'] == 'Urban', :].head(10)
            df_aux2 = df_lentos.loc[df_lentos['City'] == 'Metropolitian', :].head(10)
            df_aux3 = df_lentos.loc[df_lentos['City'] == 'Semi-Urban', :].head(10)


            df1 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
            st.dataframe(df1)
        
            
            