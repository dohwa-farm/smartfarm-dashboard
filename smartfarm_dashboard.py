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

page = st.sidebar.radio("페이지 선택", ["🏠 기본정보 입력", "📷 생육 일자별 기록", "📊 생육 분석 요약", "📦 동결건조 관리", "🌱 육묘장 관리"])

if page in ["🏠 기본정보 입력", "📷 생육 일자별 기록", "📊 생육 분석 요약"]:
    st.markdown('<div class="report-title">🌱 키르 스마트팜 생육 리포트</div>', unsafe_allow_html=True)

if page == "📷 생육 일자별 기록":
    st.header("📷 생육 일자별 영농일지 기록")
    st.markdown("""
    시설 양액재배에 맞춘 영농일지 입력 양식입니다. 농업ON 영농일지 포맷을 참고하여 현장 작업 내용을 체계적으로 기록할 수 있도록 구성하였습니다.
    """)

    selected_date = st.date_input("작성일", datetime.date.today())
    with st.container():
        st.markdown("""
        <style>
        .custom-table td { padding: 6px 10px; vertical-align: top; }
        .custom-table input, .custom-table select, .custom-table textarea { width: 100%; }
        </style>
        """, unsafe_allow_html=True)
        st.markdown("""
        <table class="custom-table">
        <tr><td><b>재배 품목</b></td><td>{}</td><td><b>품종</b></td><td>{}</td></tr>
        <tr><td><b>작업 구역</b></td><td>{}</td><td><b>작업 단계</b></td><td>{}</td></tr>
        <tr><td><b>활동 유형</b></td><td>{}</td><td><b>농약 분류</b></td><td>{}</td></tr>
        <tr><td><b>살포량</b></td><td>{}</td><td><b>단위</b></td><td>{}</td></tr>
        <tr><td colspan="4"><b>작업 내용</b><br>{}</td></tr>
        <tr><td><b>날씨</b></td><td>{}</td><td><b>최저기온</b></td><td>{}</td></tr>
        <tr><td><b>최고기온</b></td><td>{}</td><td><b>습도</b></td><td>{}</td></tr>
        <tr><td><b>강수량</b></td><td>{}</td><td><b>공개 여부</b></td><td>{}</td></tr>
        <tr><td colspan="4"><b>생육 사진</b><br>{}</td></tr>
        </table>
        """.format(
            crop := st.text_input("재배 품목"),
            variety := st.text_input("품종"),
            area := st.text_input("작업 구역"),
            work_type := st.selectbox("작업 단계", ["정식", "수확", "방제", "양액관리", "온습도관리", "점검", "기타"]),
            activity_type := st.radio("활동 유형", ["농약", "비료", "인력"], horizontal=True),
            pesticide_type := st.selectbox("농약 분류 선택", ["살균제", "살충제", "살균,살충제", "살충,제초제", "제초제", "생장조정제", "기타", "친환경 농약"])
                if activity_type == "농약" else "-",
            pesticide_amount := st.text_input("살포량") if activity_type == "농약" else "-",
            pesticide_unit := st.selectbox("단위", ["kg", "g", "mg", "l", "ml", "dl"]) if activity_type == "농약" else "-",
            activity := st.text_area("작업 내용"),
            weather := st.selectbox("날씨", ["맑음", "흐림", "비", "눈"]),
            temp_low := st.number_input("최저기온(℃)"),
            temp_high := st.number_input("최고기온(℃)"),
            humidity := st.number_input("습도(%)"),
            rainfall := st.number_input("강수량(mm)"),
            is_public := st.radio("공개 여부", ["공개", "비공개"]),
            photo := st.file_uploader("📸 생육 사진 첨부 (선택)", type=["jpg", "png", "jpeg"])
        )

if page == "📊 생육 분석 요약":
    st.header("📊 생육 분석 요약")
    st.markdown("""
    생육 데이터를 주 단위로 분석하여 다음 정보를 제공합니다:

    - 📈 생육 속도 추이 분석 (초장, 엽수 증가율 등)
    - 🌡️ 환경 변화 대비 생육 안정성 평가
    - 🕒 예상 수확 가능 시점 추정
    - ⚠️ 이상 생육 경고 알림 (생육 정체/과도한 스트레스 등)
    - 📊 시각화 차트를 통한 월별 비교

    ※ 스마트팜 로그 기반으로 자동 분석됩니다. 외부 센서 연동 시 실시간 반영 가능.
    """)

if page == "🌱 육묘장 관리":
    st.header("🌱 육묘장 관리 리포트")
    st.markdown("""
    육묘장에서는 초기 생육 단계의 관리가 매우 중요합니다. 다음 항목들을 기반으로 매일 관리 상태를 점검하고 기록하세요:
    
    - 📌 육묘 품종 및 일령
    - 🌱 초장, 엽수, 엽색 상태
    - 🐛 병해충 발생 여부
    - 🌡️ 온도, 습도, 조도, 환기 상태
    - 💧 관수 및 양액 공급
    - 🧴 농약/비료 처방
    - 📸 생육 사진 업로드
    - 📝 작업 메모 및 특이사항
    """)

    selected_nursery_date = st.date_input("기록일", datetime.date.today())
    if st.button("📌 새로운 영농일지 추가하기"):
        st.session_state["add_nursery_log"] = True

    if st.session_state.get("add_nursery_log", True):
        st.subheader(f"📝 {selected_nursery_date.strftime('%Y년 %m월 %d일')} 육묘장 관리 기록")

        col1, col2 = st.columns(2)
        with col1:
            nursery_crop = st.text_input("육묘 품종")
            seedling_age = st.number_input("일령 (일수)", min_value=1, step=1)
            height = st.number_input("초장 (cm)")
            leaf_count = st.number_input("엽수 (장)", step=1)
            leaf_color = st.selectbox("엽색 상태", ["정상", "연녹색", "황화", "적색 변화"])
            pest_status = st.radio("병해충 발생 여부", ["없음", "의심", "확인됨"])

        with col2:
            temp = st.number_input("온도(℃)")
            humidity = st.number_input("습도(%)")
            light = st.number_input("조도(lux)")
            ventilation = st.selectbox("환기 상태", ["적정", "과다", "부족"])
            water = st.text_input("관수 및 양액 공급 내용")
            fert_pesticide = st.text_area("농약/비료 처방 내용")

        st.subheader("📸 생육 사진 첨부")
        nursery_photo = st.file_uploader("육묘 생육 사진 업로드", type=["jpg", "png", "jpeg"])

        st.subheader("🗒️ 기타 특이사항")
        notes = st.text_area("작업 메모 및 특이사항")

if page == "🌱 육묘장 관리":
    st.header("🌱 육묘장 관리 리포트")
    st.markdown("""
    육묘장에서는 초기 생육 단계의 관리가 매우 중요합니다. 다음 항목들을 기반으로 매일 관리 상태를 점검하고 기록하세요:
    """)

        st.subheader(f"📝 {selected_nursery_date.strftime('%Y년 %m월 %d일')} 육묘장 관리 기록")
    selected_nursery_date = st.date_input("기록일", datetime.date.today())
    if st.button("📌 새로운 영농일지 추가하기"):
        st.session_state["add_nursery_log"] = True

    if st.session_state.get("add_nursery_log", True):

    col1, col2 = st.columns(2)
    with col1:
        nursery_crop = st.text_input("육묘 품종")
        seedling_age = st.number_input("일령 (일수)", min_value=1, step=1)
        height = st.number_input("초장 (cm)")
        leaf_count = st.number_input("엽수 (장)", step=1)
        leaf_color = st.selectbox("엽색 상태", ["정상", "연녹색", "황화", "적색 변화"])
        pest_status = st.radio("병해충 발생 여부", ["없음", "의심", "확인됨"])

    with col2:
        temp = st.number_input("온도(℃)")
        humidity = st.number_input("습도(%)")
        light = st.number_input("조도(lux)")
        ventilation = st.selectbox("환기 상태", ["적정", "과다", "부족"])
        water = st.text_input("관수 및 양액 공급 내용")
        fert_pesticide = st.text_area("농약/비료 처방 내용")

    st.subheader("📸 생육 사진 첨부")
    nursery_photo = st.file_uploader("육묘 생육 사진 업로드", type=["jpg", "png", "jpeg"])

    st.subheader("🗒️ 기타 특이사항")
    notes = st.text_area("작업 메모 및 특이사항")
