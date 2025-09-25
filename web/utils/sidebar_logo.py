from PIL import Image
import streamlit as st


def add_sidebar_logo():
    logo_img = Image.open("web/static/verizon_logo.png")
    icon_img = Image.open("web/static/verizon_logo.png")

    st.logo(logo_img, icon_image=icon_img)
