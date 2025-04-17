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
    "🌱 육묘장 관리",
    "🧠 AI 생육 이미지 분석"
])

if page in ["🏠 기본정보 입력", "📷 생육 일자별 기록", "📊 생육 분석 요약"]:
    st.markdown('<div class="report-title">🌱 키르 스마트팜 생육 리포트</div>', unsafe_allow_html=True)

if page == "📷 생육 일자별 기록":
    st.subheader("📅 생육 일자별 기록")
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
    st.button("➕ 영농일지 추가 저장")

elif page == "📊 생육 분석 요약":
    st.subheader("📈 생육 분석 요약 - 주간 수확 예측 및 생육 비교")
    st.write("- 📅 주차별 생육 추세, 수확 예측일, 평균 엽록소, 평균 초장 등의 요약 제공")

elif page == "📦 동결건조 관리":
    st.markdown("<h2>📦 동결건조 관리 리포트</h2>", unsafe_allow_html=True)
    st.write("- 💡 동결건조 생산량 기록")
    st.write("- 📊 월별 평균 가격 추이 및 시장 대응 전략 기록")
    st.write("- 🧾 원료 투입량 대비 최종 수율 관리")

elif page == "🌱 육묘장 관리":
    st.markdown("<h2>🌱 육묘장 관리</h2>", unsafe_allow_html=True)
    st.write("- 🔹 일자별 관리 사항 기록")
    st.write("- 🌡️ 온습도, 급액, 광량, 환기 기록")
    st.write("- 📷 상태 사진 기록 및 이전 데이터 비교")
    st.date_input("관리 일자", datetime.date.today())
    st.text_input("육묘 품종")
    st.number_input("온도(℃)")
    st.number_input("습도(%)")
    st.number_input("광량(lux)")
    st.number_input("급액량(ml)")
    st.text_area("관리 내용 및 특이사항")
    st.file_uploader("📸 상태 사진", type=["jpg", "jpeg", "png"])

elif page == "🧠 AI 생육 이미지 분석":
    st.subheader("🧠 AI 기반 생육 이미지 진단")
    st.write("- 사진을 업로드하면 AI가 병해충 여부, 엽색 이상, 과실 상태 등을 분석합니다.")
    uploaded_img = st.file_uploader("📤 진단할 생육 이미지 업로드", type=["jpg", "jpeg", "png"])
    if uploaded_img:
        st.image(uploaded_img, caption="업로드된 이미지", use_column_width=True)
        st.success("✅ 이미지 분석 기능은 추후 AI 모델 연동 시 적용 예정입니다.")
