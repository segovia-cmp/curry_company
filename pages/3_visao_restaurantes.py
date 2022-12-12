# Libraries

import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import folium
import pandas as pd
import numpy  as np
import streamlit as st
from PIL import Image
from haversine import haversine

from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽️', layout='wide' )

# Import dataset
df = pd.read_csv( 'dataset/train.csv' )

df1 = df.copy()

# 1. convertando a coluna Age de texto para numero
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


# =======================================
# Barra Lateral
# =======================================
st.header( 'Marketplace - Visão Restaurantes' )

image_path = 'imagem.png'
image = Image.open( image_path )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider( 
    'Até qual valor?',
    value=pd.datetime( 2022, 4, 13 ),
    min_value=pd.datetime(2022, 2, 11 ),
    max_value=pd.datetime( 2022, 4, 6 ),
    format='DD-MM-YYYY' )

st.sidebar.markdown( """---""" )


traffic_options = st.sidebar.multiselect( 
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'], 
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro de data
linhas_selecionadas = df['Order_Date'] <  date_slider 
df = df.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[linhas_selecionadas, :]


# =======================================
# Layout no Streamlit
# =======================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', ' ', ' '] )

with tab1:
    with st.container():
        st.title( "Overal Metrics" )
        
        col1, col2, col3, col4, col5, col6 = st.columns( 6, gap='large')
        with col1:
            delivery_unique = len( df.loc[:, 'Delivery_person_ID'].unique() )
            col1.metric( 'Entregadores', delivery_unique )
                
        with col2:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df['distance'] = df.loc[:, cols].apply( lambda x: 
                                        haversine(  (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

            avg_distance = np.round( df['distance'].mean(), 2 )
            col2.metric( 'A distancia media', avg_distance )

            
        with col3:
            df_aux = ( df.loc[:, ['Time_taken(min)', 'Festival']]
                          .groupby( 'Festival' )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'], 2 )
            col3.metric( 'Tempo Médio', df_aux )

        with col4:
            df_aux = ( df.loc[:, ['Time_taken(min)', 'Festival']]
                          .groupby( 'Festival' )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'], 2 )
            col4.metric( 'STD Entrega', df_aux )
            
        with col5:
            df_aux = ( df.loc[:, ['Time_taken(min)', 'Festival']]
                          .groupby( 'Festival' )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'], 2 )
            col5.metric( 'Tempo Médio', df_aux )
            
        with col6:
            df_aux = ( df.loc[:, ['Time_taken(min)', 'Festival']]
                          .groupby( 'Festival' )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round( df_aux.loc[df_aux['Festival'] == 'No', 'std_time'], 2 )
            col6.metric( 'STD Entrega', df_aux )
        
    
    with st.container():
        st.markdown( """---""" )
        col1, col2 = st.columns( 2 )
        
        with col1:
            df_aux = df.loc[:, ['City', 'Time_taken(min)']].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = go.Figure() 
            fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time']))) 
            fig.update_layout(barmode='group') 

            st.plotly_chart(fig, use_container_width = True)
            
        with col2:
            df_aux = ( df.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                          .groupby( ['City', 'Type_of_order'] )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            st.dataframe( df_aux )
        

        
    with st.container():
        st.markdown( """---""" )
        st.title( "Distribuição do Tempo" )
        
        col1, col2 = st.columns( 2 )
        with col1:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df['distance'] = df.loc[:, cols].apply( lambda x: 
                                        haversine(  (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

            avg_distance = df.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
            fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart(fig, use_container_width = True)

            
        with col2:
            df_aux = ( df.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                          .groupby( ['City', 'Road_traffic_density'] )
                          .agg( {'Time_taken(min)': ['mean', 'std']} ) )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time'] ) )
            st.plotly_chart(fig, use_container_width = True)