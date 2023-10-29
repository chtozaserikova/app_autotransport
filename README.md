
# Порядок использования:
* Клонировать репозиторий :
```
git clone https://sbrf-bitbucket.sigma.sbrf.ru/scm/~20716895/geo_app.git 
```
* Переместиться в папку репозитория :
```
cd geo_app/ 
```
* Установить все библиотеки :
```
python -m pip install --index-url=https://token:{ваш токен}@sberosc.sigma.sbrf.ru/repo/pypi/simple --trusted-host=sberosc.sigma.sbrf.ru -r requirements.txt
```
* Запустить приложение на локальном сервере :
```
streamlit run Home.py
```