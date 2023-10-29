import numpy as np
import pandas as pd
import requests
import io
import os
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
sns.set(style="whitegrid", palette="pastel", color_codes=True)
sns.mpl.rc("figure", figsize=(20,20))
from shapely import wkt
import streamlit as st
import streamlit as st
import pandas as pd 
import geopandas as gpd 
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim

st.set_page_config(
page_title="Геокодер адресов",
page_icon="🔎",
layout="wide",
initial_sidebar_state="expanded",
)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title('🔎Геокодер адресов🔎')
st.info('Данный модуль помогает найти координаты по адресам любого формата и привести их в нормализованный вид', icon="ℹ️")

def yandex_geocode(adress):
  url = 'https://geocode-maps.yandex.ru/1.x'
  params = {'geocode': adress, 
  'apikey': 'a1e72ca3-5b59-4034-8022-facc02acf203', 'format': 'json'}
  r = requests.get(url, params=params)
  results = r.json()
  #координаты
  try:
    pos = results['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
  except:
    pos = 'error'
  #нормализованный адрес
  try:
    ya_adress = results['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
  except:
    ya_adress = 'error'
  return pd.Series([pos, ya_adress])

def convertAdressToGPD(cities, col):
  cities[['coorditate', 'ya_adress']] = cities.apply(lambda x: yandex_geocode(x[col]))
  print('Координаты адресов найдены')
  if len(cities.coorditate) > 0:
    return cities
  else:
    print('Ошибка в работе геокодера')

def main():
  file = st.file_uploader("Загрузите файл в формате xlsx")
  if file is not None:
    file.seek(0)
    df_address = pd.read_excel(file)
    st.write(df_address.head())
    st.write(df_address.shape)
    if st.checkbox("Найти координаты по адресу"):
      address_name = st.selectbox("Выбрать столбец с адресом, координаты которого нужно найти", df_address.columns.tolist())
      # df_address = df.copy()
      df_address["geocode_col"] = df_address[address_name].astype(str)
      st.write(df_address["geocode_col"].head())
      if st.checkbox("Выбран корректный адрес"):
        with st.spinner('Ожидайте, идет поиск координат...'):
          lat = []
          long = []
          norm_add = []
          for i in df_address.index:
            try:
              resp = yandex_geocode(df_address['geocode_col'][i])
              lat.append(resp.iloc[0].split(' ')[1])
              long.append(resp.iloc[0].split(' ')[0])
              norm_add.append(resp.iloc[1])
            except:
              lat.append('')
              long.append('')
          df_address['Широта'] = lat
          df_address['Долгота'] = long
          df_address['Нормализованный адрес'] = norm_add
          df_address.drop('geocode_col', axis=1, inplace=True)
        st.success('Готово!')
        st.write(df_address.head())
    elif st.checkbox("Найти адрес по координатам"):
      geolocator = Nominatim(user_agent="geo_app")
      # df_address = df.copy()
      selection = st.selectbox("Выберите столбец с широтой", df_address.columns.tolist())
      df_address["latitude"] = df_address[selection]
      selection = st.selectbox("Выберите столбец с долготой", df_address.columns.tolist())
      df_address["longitude"] = df_address[selection]
      if st.checkbox("Выбраны данные и организации"):
        with st.spinner('Ожидайте, идет поиск...'):
          adresses = []
          for lat,lon in zip(df_address['latitude'], df_address['longitude']):
              adresses.append(geolocator.reverse((lat,lon)).address)
          df_address['Адрес'] = adresses
          st.success('Готово!')
          st.write(df_address.head())

    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
      df_address.to_excel(writer,index=False)
      writer.save()
      st.download_button(
      label="📥 Нажмите, чтобы скачать данные с координатами",
      data=buffer,
      file_name=f"Координаты_'{os.path.splitext(file.name)[0]}'.xlsx",
      mime="application/vnd.ms-excel"
      )

if __name__ == "__main__":
  main()