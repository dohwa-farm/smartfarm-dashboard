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
    .block-container { padding: 1rem 2rem; }
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
    st.image(logo_bytes, width=160)

# 페이지 선택을 가로 radio로 변경
page = st.radio("페이지 선택", [
    "🏠 기본정보 입력",
    "📒 영농일지",
    "📅 영농일지 달력",
    "📊 생육 분석 요약",
    "📦 동결건조 관리",
    "🌱 육묘장 관리",
    "🧠 AI 생육 이미지 분석"
], horizontal=True)

if page in ["🏠 기본정보 입력", "📊 생육 분석 요약"]:
    st.markdown('<div class="report-title">🌱 키르 스마트팜 생육 리포트</div>', unsafe_allow_html=True)

if page == "📒 영농일지":
    st.markdown("<h2 style='color:#2E86C1;'>📒 영농일지 등록</h2>", unsafe_allow_html=True)
    with st.form("diary_form"):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작일", datetime.date.today())
            crop_type = st.selectbox("품목", ["딸기", "토마토"])
            crop_field = st.text_input("필지")
            crop_name = st.text_input("품종")
        with col2:
            end_date = st.date_input("종료일", datetime.date.today())
            sowing_name = st.text_input("모임명")
            work_stage = st.selectbox("작업단계 선택", ["정식", "수확", "방제", "관리", "기타"])

        work_content = st.text_area("작업내용")
        st.button("이전 작업내용 가져오기")

        st.markdown("#### 활동유형")
        act_type = st.radio("활동유형", ["농약", "비료", "인력"], horizontal=True)
        pesticide_category = st.selectbox("농약 분류 선택", ["살균제", "살충제", "살균,살충제", "살충,제초제", "제초제", "생장조정제", "기타", "친환경 농약"])
        cols = st.columns([2, 1])
        pesticide_amount = cols[0].text_input("살포량을 입력하세요")
        pesticide_unit = cols[1].selectbox("단위를 선택하세요.", ["kg", "g", "mg", "l", "ml", "dl"])

        st.markdown("#### 날씨정보")
        weather = st.selectbox("날씨", ["맑음", "흐림", "비", "눈"])
        col5, col6, col7 = st.columns(3)
        min_temp = col5.text_input("최저기온")
        max_temp = col6.text_input("최고기온")
        rainfall = col7.text_input("강수량")
        humidity = st.text_input("습도")

        st.markdown("#### 사진첨부")
        st.file_uploader("파일선택", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

        st.markdown("#### 영농일지 공개 여부")
        public = st.radio("공개여부", ["비공개", "공개"], horizontal=True)

        st.markdown("#### 예약 알림 여부")
        notify = st.radio("예약 알림 여부", ["아니오", "예"], horizontal=True)

        submitted = st.form_submit_button("제출하기")
        if submitted:
            st.success("✅ 영농일지가 저장되었습니다.")
