import streamlit as st

st.set_page_config(
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("Сервис для работы с координатами 🌆")
st.info("Нажмите на меню левой боковой панели, чтобы перейти к другим страницам")
st.markdown(
    """
    <style>
    textarea {
        font-size: 5rem !important;
    }
    input {
        font-size: 5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
hide_st_style = """
            <style>
            #MainMenu {visibility:hidden;}
            footer {visibility:hidden;}
            .leftbar-text {
                font-size:14px;
            }
            header {visibility:hidden;}
            [data-testid="stSidebarNav"] {
                background-image: url(https://play-lh.googleusercontent.com/FG1HquqP8Ka88CrE_Uh5Q-h8s4RRyCjbNyeUyXG0GQakW9CpATKqF9UROLbaDW1ZO7DW);
                background-size: cover;
                padding-top: 150px;
                background-position: 5px 5px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "Навигация";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 100px;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.subheader("Контактная информация")
st.info(
    """
    Автор - [Серикова Света](https://github.com/chtozaserikova) \n\n
      Контактный номер: [866031855](https://addressbook.sigma.sbrf.ru/search/profile/1978051)\n
      sigma: [SSSerikova@sberbank.ru](mailto:SSSerikova@sberbank.ru) \n
      alpha: [SSSerikova@omega.sbrf.ru](mailto:SSSerikova@omega.sbrf.ru)
    """
)