import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Image
from reportlab.lib.utils import ImageReader
from PIL import Image as PILImage
import base64
import pydeck as pdk

st.set_page_config(
    page_title="📡 스마트팜 환경 리포트 | 키르기스스탄 딸기·토마토",
    layout="wide",
    page_icon="🍓"
)

st.markdown("""
    <style>
    .report-title { font-size:36px !important; font-weight:bold; color:#2E86C1; }
    </style>
""", unsafe_allow_html=True)

def load_logo():
    try:
        with open("dohwa_logo.png", "rb") as f:
            return f.read()
    except FileNotFoundError:
        st.warning("⚠️ 로고 파일이 없어 기본 로고가 표시됩니다.")
        return None

logo_bytes = load_logo()
if logo_bytes:
    st.image(logo_bytes, width=180)

page = st.sidebar.radio("페이지 선택", [
    "🏠 기본정보 입력",
    "📷 생육 일자별 기록",
    "📊 생육 분석 요약",
    "📦 동결건조 관리",
    "🌱 육묘장 관리"
])

if page in ["🏠 기본정보 입력", "📷 생육 일자별 기록", "📊 생육 분석 요약"]:
    st.markdown('<div class="report-title">🌱 키르 스마트팜 생육 리포트</div>', unsafe_allow_html=True)

if page == "📷 생육 일자별 기록":
    import streamlit_calendar as calendar
    st.subheader("📅 달력 기반 생육 일자별 기록")
    selected_date = st.date_input("작성일", datetime.date.today())
    st.text_input("재배 품목")
    st.text_input("품종")
    st.text_input("작업 구역")
    st.selectbox("작업 단계", ["정식", "수확", "방제", "양액관리", "온습도관리", "점검", "기타"])
    st.radio("활동 유형", ["농약", "비료", "인력"], horizontal=True)
    st.selectbox("농약 분류 선택", ["살균제", "살충제", "살균,살충제", "살충,제초제", "제초제", "생장조정제", "기타", "친환경 농약"])
    st.text_input("살포량")
    st.selectbox("단위", ["kg", "g", "mg", "l", "ml", "dl"])
    st.text_area("작업 내용")
    st.selectbox("날씨", ["맑음", "흐림", "비", "눈"])
    st.number_input("최저기온(℃)")
    st.number_input("최고기온(℃)")
    st.number_input("습도(%)")
    st.number_input("강수량(mm)")
    st.radio("공개 여부", ["공개", "비공개"])
    st.file_uploader("📸 생육 사진 첨부", type=["jpg", "jpeg", "png"])
    
    calendar.calendar_component(events=[
        {"title": "영농일지 기록", "start": str(datetime.date.today()), "end": str(datetime.date.today())}
    ])
