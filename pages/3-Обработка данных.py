import os
import warnings
import datetime
import fiona
import io
import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import xlsxwriter
from scipy.spatial import distance
import geopy.distance
import time
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

st.set_page_config(
    page_title="🚩Обработка данных для поиска отклонений🚩",
    page_icon="🚫",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title('🚩Обработка данных🚩')
st.info('Данный модуль позволяет интерактивно обработать данные любого типа и объединить таблицы по признаку пространственной близости', icon="ℹ️")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def filter_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # перевод дат в нормальный единый формат без временных зон
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()
    with modification_container:
        to_filter_columns = st.multiselect("Добавить фильтры по следующим столбцам:", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Принимаем колонки с <= 20 уникальных значений как категориальные
            if is_categorical_dtype(df[column]) or df[column].nunique() <= 20:
                user_cat_input = right.multiselect(
                    f"Значения столбца «{column}»",
                    df[column].unique(),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Значения столбца «{column}»",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Значения столбца «{column}»",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Подстрока для столбца «{column}»",
                )
                if user_text_input:
                    df = df[df[column].str.lower().str.contains(user_text_input.lower())]
    return df

def closest_node(node, nodes):
    closest_index = distance.cdist([node], nodes).argmin()
    latitude = nodes[closest_index][0]
    longitude = nodes[closest_index][1]
    return df_true[(df_true['Широта'] == latitude) & (df_true['Долгота'] == longitude)]['Наименование объекта'].iloc[0], \
            geopy.distance.geodesic(node, nodes[closest_index]).km

uploaded_file = st.file_uploader(
        label='Выберите файл с данными', 
        type=['xlsx'],accept_multiple_files=False,key="fileUploader")

if uploaded_file is not None:
    df=pd.read_excel(uploaded_file)
    selection = st.selectbox("Выберите столбец с широтой", df.columns.tolist())
    df["latitude"] = df[selection]
    selection = st.selectbox("Выберите столбец с долготой", df.columns.tolist())
    df["longitude"] = df[selection]
    
    if st.checkbox("Добавить фильтры"):
        location_found_cnt = filter_df(df)
        location_found_cnt = location_found_cnt.drop(['Долгота', 'Широта', 'Unnamed:0', 'Unnamed:0.1'], axis=1, errors='ignore')
        st.write(len(location_found_cnt))
        st.write(location_found_cnt)
        st.success(
            f'Успешно выбраны {len(location_found_cnt)} из {len(df)} строк'
        )
        df = location_found_cnt
    uploaded_file_vsp = st.file_uploader(
        label='Выберите файл для поиска ближайших объектов и расстояний до них', 
        type=['xlsx'],accept_multiple_files=False,key="objectfile")
    if uploaded_file_vsp is not None:
        df_true=pd.read_excel(uploaded_file_vsp)
        st.table(df_true.head())
        selection = st.selectbox("Выберите столбец с широтой объекта", df_true.columns.tolist())
        df_true["Широта"] = df_true[selection]
        selection = st.selectbox("Выберите столбец с долготой объекта", df_true.columns.tolist())
        df_true["Долгота"] = df_true[selection]
        
        selection = st.selectbox("Выберите столбец с наименованием объекта", df_true.columns.tolist())
        df_true["Наименование объекта"] = df_true[selection]
        
        if df["latitude"].dtype == 'float64' \
        and df["longitude"].dtype == 'float64' \
        and df_true["Широта"].dtype == 'float64' \
        and df_true["Долгота"].dtype == 'float64' :
            near_add = []
            dist_list = []
            lat_vsp = []
            long_vsp = []
            latitude_df = []
            longitude_df = []
            names = []
            
            with st.spinner('Ожидайте, идет поиск ближайших объектов и расчет расстояния до них...'):    
                for i in range(len(df)):
                    close_node = closest_node(df[['latitude', 'longitude']].values[i], \
                                        df_true[['Широта', 'Долгота']].values)
                    near_add.append(close_node[0])
                    dist_list.append(close_node[1])
                    lat_vsp.append(df_true[df_true['Наименование объекта'] == close_node[0]]['Широта'].iloc[0])
                    long_vsp.append(df_true[df_true['Наименование объекта'] == close_node[0]]['Долгота'].iloc[0])
                    
                df['Наименование объекта'] = near_add
                df['Минимальная дистанция до объекта'] = dist_list
                df['Широта объекта'] = lat_vsp
                df['Долгота объекта'] = long_vsp
                df = pd.merge(df, df_true, on='Наименование объекта')

            if near_add is not None:
                st.info('Выберите ползунком диапазон расстояния до объектов в километрах', icon="ℹ️")
                selected_dist_range = st.slider('Дистанция до объекта (в км):',
                                                float(df['Минимальная дистанция до объекта'].min()), 
                                                float(df['Минимальная дистанция до объекта'].max()),
                                                (
                                                    df['Минимальная дистанция до объекта'].min(), 
                                                    df['Минимальная дистанция до объекта'].max())
                                                )

                location_found = df[(df['Минимальная дистанция до объекта'] >= selected_dist_range[0]) \
                                        &(df['Минимальная дистанция до объекта'] <= selected_dist_range[1])]
                st.success(
                        f'Успешно выбраны {len(location_found)} из {len(df)} строк'
                    )
               
    if st.checkbox("Данные готовы к выгрузке"):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            
            location_found.to_excel(writer,index=False)
            writer.save()
            st.download_button(
                label="📥 Нажмите, чтобы скачать полученную выборку",
                data=buffer,
                file_name=f"Обработанный_'{os.path.splitext(uploaded_file.name)[0]}'.xlsx",
                mime="application/vnd.ms-excel"
            )
    else:
        st.warning('Вы не выбрали координаты для поиска блиайших объектов')
else:
    st.warning('Загрузите файл в формате XLSX')