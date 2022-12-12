import pandas as pd
import folium 
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout='wide' )


df_ler = pd.read_csv('dataset/train.csv')

df = df_ler.copy()

#________________________
#funções 
#________________________

def clean_code(df):

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
    
    df = df.loc[df['Delivery_person_Age'] != 'NaN ', :]
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
    
    df = df.loc[df['multiple_deliveries'] != 'NaN ', :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    #remover (min)

    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min) ' )[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype( int )
    
    return df

def order_metric (df):
    
    fig = px.bar(df.loc[:, ['ID', 'Order_Date']]
                   .groupby('Order_Date').count()
                   .reset_index(), x='Order_Date', y='ID')
    return fig


def traffic_order_share(df):
    df_trafego = (df.loc[:, ['ID', 'Road_traffic_density']]
                    .groupby('Road_traffic_density')
                    .count()
                    .reset_index())


    fig = px.pie(df_trafego, values='ID', names='Road_traffic_density')
    return fig

def traffic_order_city(df):
            
    df_city_trafego = (df.loc[:, ['ID', 'City','Road_traffic_density']]
                         .groupby(['City','Road_traffic_density'])
                         .count()
                         .reset_index())


    fig = px.scatter(df_city_trafego, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def order_by_week(df):

    df['week_of_year'] = df['Order_Date'].dt.strftime( "%U" )
    graf = px.line(df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index(), x='week_of_year', y='ID')    
    return graf

def order_shar_by_week(df):
        
        
    df_aux1 = (df.loc[:, ['ID', 'week_of_year']]
                 .groupby('week_of_year')
                 .count()
                 .reset_index())
    df_aux2 = (df.loc[:, ['Delivery_person_ID', 'week_of_year']]
                 .groupby('week_of_year')
                 .nunique()
                 .reset_index())

    df_aux = pd.merge(df_aux1, df_aux2, how='inner', on='week_of_year')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']


    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig

def country_maps(df):
    df_aux = (df.loc[:,['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                .groupby(['City','Road_traffic_density'])
                .median().reset_index())


    map = folium.Map(location=[22.745049, 75.892471],zoom_start=5)

    for index, location_info in df_aux.iterrows():
        folium.Marker ([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']]).add_to (map)

    folium_static (map, width=1024, height=600)    

    return None
#________________________________


#limpando codigo
df = clean_code( df )


#======================================================
# barra lateral
#======================================================


st.header('Marketplace - Visão Cliente')


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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geografica'])
                    
with tab1:
    with st.container():
        
        st.markdown('# Order by Day')
        fig = order_metric(df)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            
            st.header('Traffic Order Share')
            fig = traffic_order_share (df)
            st.plotly_chart(fig, use_container_width=True)
        
        
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df)
            st.plotly_chart(fig, use_container_width=True)


with tab2:
    with st.container():
        st.markdown('# order by week')
        graf = order_by_week(df)
        st.plotly_chart(graf, use_container_width=True)
        
    with st.container():
        
        st.markdown('# Order share by week')
        fig = order_shar_by_week(df)
        st.plotly_chart(fig, use_container_width=True)
    
with tab3:
    st.markdown('# Country Maps')
    country_maps(df)
    
    