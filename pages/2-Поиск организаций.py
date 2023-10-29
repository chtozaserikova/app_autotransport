import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import math
import io
import os
import xlsxwriter
import geopandas as gpd
import geopy
import osmnx as ox
import plotly.express as px
import plotly.graph_objects as go
from geopy.distance import geodesic as GD
import re
from streamlit_folium import st_folium
import numpy as np
from shapely.geometry import Point, LineString, Polygon
import matplotlib.pyplot as plt
import folium

st.set_page_config(page_title="Ищем бары💃")
st.title('🌐Поиск организаций🌐')
st.info('Данный модуль помогает найти организации любого типа в заданном радиусе от выбранных географических координат', icon="ℹ️")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def flatten_list(_2d_list):
        flat_list = []
        for element in _2d_list:
                if type(element) is list:
                        for item in element:
                                flat_list.append(item)
                else:
                        flat_list.append(element)
        return flat_list

excel_file = st.file_uploader("Upload File", type=['xls','xlsx'])
buffer = io.BytesIO()
if excel_file is not None:
        file_name = os.path.splitext(excel_file.name)[0]

def choose_object(df):
        st.header("Настройте фильтры для поиска организаций:")
        modification_container = st.container()
        df_select = pd.DataFrame()
        amenity = None
        
        with modification_container:
                category_options = df['Категория'].unique()
                to_filter_columns = st.multiselect("Выберите интересующую категорию организаций:", category_options)
                select_changed = False
                
                if to_filter_columns:
                        select_changed = True
                        df_select = df[df['Категория'].isin(to_filter_columns)]    
                        types_options = df_select['Тип объекта'].unique()
                        amenity = st.multiselect("Тип объекта:", 
                                                options=types_options.tolist(), 
                                                key='amenity')
                        st.write('Вы выбрали следующие организации:', amenity)
        
                        df_select = df[df['Тип объекта'].isin(amenity)]
                        
                if amenity and not select_changed:
                        amenity = st.multiselect("Тип объекта:", 
                                                options=list(df[df['Категория'].isin(to_filter_columns)]['Тип объекта'].unique()), 
                                                default="all")
                        st.write(amenity)
                       
                        if "all" in amenity:
                                amenity = df[df['Тип объекта'].isin(amenity)]["amenity"].unique()
                                df_select = df.query("amenity == @amenity")
                        df_select = df.query("amenity == @amenity")
                        st.write(df_select)
        return df_select

if excel_file is not None:
        df = pd.read_excel(excel_file)
        st.write(df.head())
        selection = st.selectbox("Выберите столбец с широтой", df.columns.tolist())
        df["Lat"] = df[selection]
        selection = st.selectbox("Выберите столбец с долготой", df.columns.tolist())
        df["Long"] = df[selection]
        number = st.number_input('Введите радиус поиска объектов (в метрах)')
        
        if df["Lat"].dtype == 'float64' and df["Long"].dtype == 'float64' and number > 0:
                df_amn = pd.read_excel('data/amenity.xlsx')
                df_select = choose_object(df_amn)
                if len(df_select) > 0:
                        gdf_list = []
                        last_lats, last_longs = [], []
                        tags = {'amenity': df_select['amenity'].values.tolist()}
                        if st.checkbox("Выбраны данные и организации"):
                                with st.spinner('Ожидайте, идет поиск...'):    
                                        for i in df.index:
                                                try:
                                                        point = (df["Lat"][i], df["Long"][i])
                                                        gdf = ox.geometries.geometries_from_point(point, tags, dist=number).reset_index()
                                                        gdf = gdf.loc[:, gdf.isin([' ','NULL',0]).mean() <= .5]
                                                        gdf['Lat'] = df["Lat"][i]
                                                        gdf['Long'] = df["Long"][i]
                                                        gdf_list.append(gdf)
                                                except:
                                                        pass
                                st.success('Готово!') 
                                try:
                                        gdf_all = pd.concat(gdf_list)
                                        gdf_all[['Долгота организации','Широта организации']] = gdf_all['geometry'].reset_index().get_coordinates().reset_index().drop_duplicates('index', keep='first').drop(columns='index').values
                                        gdf_all['Lat'] = gdf_all['Lat'].astype(float)
                                        gdf_all['Long'] = gdf_all['Long'].astype(float)
                                        df['Lat'] = df['Lat'].astype(float)
                                        df['Long'] = df['Long'].astype(float)
                                        gdf_all = gdf_all.drop(columns='geometry')
                                        gdf_all = pd.merge(df, gdf_all, on = ['Lat', 'Long'])
                                        gdf_all = gdf_all[gdf_all['Широта организации'].notna()]
                                        
                                        distances = []
                                        for i in gdf_all.index:
                                                dist = GD((gdf_all['Lat'][i], gdf_all['Long'][i]), 
                                                                                        (gdf_all['Широта организации'][i], gdf_all['Долгота организации'][i])).meters
                                                distances.append(dist)
                                        gdf_all['Расстояние между объектом и искомой точкой (в метрах)'] = distances
                                        
                                        st.write(gdf_all)
                                        
                                        try:
                                                point = (float(gdf_all["Широта организации"][0]), float(gdf_all["Долгота организации"][0]))
                                                map = folium.Map(location = [float(gdf_all["Широта организации"].mean()), float(gdf_all["Долгота организации"].mean())], 
                                                                zoom_start=13,
                                                                tiles = 'cartodbpositron',)
                                                for lat, lon in zip(gdf_all['Широта организации'], gdf_all['Долгота организации']):
                                                        folium.Circle(location = [lat, lon], 
                                                                radius = number, 
                                                                color = 'cadetblue', 
                                                                fill=True, 
                                                                weight = 0.5).add_to(map)
                                                for lat, lon, name in zip(gdf_all['Широта организации'], gdf_all['Долгота организации'], gdf_all['name']):
                                                        folium.CircleMarker(location = [lat, lon], 
                                                                        tooltip = name,
                                                                        radius = 3,                                                     
                                                                        color = 'cadetblue', 
                                                                        fill_opacity=1).add_to(map)
                                                for lat, lon in zip(gdf_all['Lat'], gdf_all['Long']):
                                                        folium.CircleMarker(location = [lat, lon], 
                                                                        radius = 3,
                                                                        color = 'gray', 
                                                                        fill_opacity=1).add_to(map)
                                                m = st_folium(map)

                                                # для скачивания html'ки карты
                                                if st.checkbox("Сохранить карту"):
                                                        MAP_FILE = 'map.html'
                                                        map.save(MAP_FILE)
                                                        
                                                        with open(MAP_FILE, "rb") as file:
                                                                btn = st.download_button(
                                                                label="Скачать карту в формате HTML",
                                                                data=file,
                                                                file_name=MAP_FILE,
                                                                mime='text/html'
                                                        )
                                        except:
                                                print('Не удалось скачать карту')
                                        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                                gdf_all.to_excel(writer, sheet_name='Sheet1', index=False)
                                                writer.close()
                                                download2 = st.download_button(
                                                label="📥 Нажмите, чтобы скачать данные с координатами",
                                                data=buffer,
                                                file_name=f"Организации_'{file_name}'.xlsx",
                                                mime='application/vnd.ms-excel'
                                                )
                                except:
                                        st.warning('Нет найденных объектов, попробуйте добавить типы организаций или увеличить диапазон посика')
     
else:
        st.warning('Вы не выбрали загрузочный файл')