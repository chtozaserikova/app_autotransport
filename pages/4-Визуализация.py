from tkinter.tix import PopupMenu
from turtle import width
import streamlit as st
import leafmap
import pandas as pd
from streamlit_folium import folium_static, st_folium
import geemap.colormaps as cm
import geemap.foliumap as geemap
from geopy.geocoders import Nominatim


st.set_page_config(page_title="🗺️")
st.title("🗺️Визуализация на картах🗺️")
st.markdown(
    "Загрузите файл с координатами выберите параметры для отображения на картах"
)
BASEMAPS = ['Satellite', 'Roadmap', 'Terrain', 'Hybrid']
ADDRESS_DEFAULT = "Moscow, Russia"

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

with st.sidebar:
    st.title("Выберите настройки параметров")
    basemap = st.selectbox("Выберите вид карты", BASEMAPS)
    if basemap in BASEMAPS:
        basemap=basemap.upper()

uploaded_file = st.file_uploader(
        label='Загрузите полученный ранее файл', 
        type=['csv','xlsx'],accept_multiple_files=False,key="fileUploader")

if uploaded_file is not None:
    df=pd.read_excel(uploaded_file)
    selection = st.selectbox("Выберите столбец с широтой", df.columns.tolist())
    df["end_station_latitude"] = df[selection]
    selection = st.selectbox("Выберите столбец с долготой", df.columns.tolist())
    df["end_station_longitude"] = df[selection]
    
    if df["end_station_latitude"].dtype == 'float64' \
    and df["end_station_longitude"].dtype == 'float64':
        df=df.dropna(subset=['end_station_longitude'])
        df=df.dropna(subset=['end_station_latitude'])
        df = df.drop_duplicates(['end_station_latitude', 'end_station_longitude'])
        df = df.reset_index()
        df.drop(columns='index', inplace=True)
        m = leafmap.Map(center=[df["end_station_latitude"][0], df["end_station_longitude"][0]], zoom=16)
        m.add_basemap('HYBRID')
        m.add_basemap('SATELLITE')
        m.add_basemap('ROADMAP')
        for i in df.index:
            lat = df['end_station_latitude'][i]
            long = df['end_station_longitude'][i]
            m.add_marker(location=(lat, long))
        m.to_streamlit()
        df = df.drop(columns=['end_station_latitude', 'end_station_longitude'])
        st.write(df)
        
       
        # для скачивания html'ки карты
        # if st.checkbox("Сохранить карту"):
        MAP_FILE = 'google_map.html'
        m.to_html(MAP_FILE)
            
        with open(MAP_FILE, "rb") as file:
                btn = st.download_button(
                label="Скачать карту в формате HTML",
                data=file,
                file_name=MAP_FILE,
                mime='text/html'
        ) 
    else:
        st.warning('Выберите все колонки с координатами')
else:
    st.warning('Загрузите файл в формате XLSX')