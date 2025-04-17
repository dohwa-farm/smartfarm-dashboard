import streamlit as st
import pandas as pd
import datetime as dt
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

st.markdown('<div class="report-title">🌱 키르 스마트팜 생육 리포트</div>', unsafe_allow_html=True)

# 사이드바로 챕터 구분
page = st.sidebar.radio("페이지 선택", ["🏠 기본정보 입력", "📷 생육 일자별 기록", "📊 생육 분석 요약"])

if page == "🏠 기본정보 입력":
    col1, col2 = st.columns(2)
    with col1:
        manager_name = st.text_input("담당자 이름", "이한승")
    with col2:
        farm_name = st.text_input("농장명", "IWS-Agro")

    st.subheader("📍 농장 구역 선택 (지도 기반)")
    map_data = pd.DataFrame({
        "위치명": [
            "A동 토마토", "B동 딸기", "C동", "D동 토마토", "E동 토마토", "F동", "G동 토마토"
        ],
        "lat": [
            42.950400, 42.950180, 42.950000, 42.950150,
            42.950300, 42.950370, 42.950440
        ],
        "lon": [
            74.720100, 74.720250, 74.719850, 74.720300,
            74.719700, 74.719640, 74.719580
        ]
    })
    selected_zone = st.selectbox("농장 내 위치 선택:", map_data["위치명"].tolist())
    zone_coords = map_data[map_data["위치명"] == selected_zone][["lat", "lon"]].values[0]
    farm_location = f"{selected_zone} - {zone_coords[0]}, {zone_coords[1]}"

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/satellite-v9',
        initial_view_state=pdk.ViewState(
            latitude=42.9503,
            longitude=74.7199,
            zoom=18,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=map_data,
                get_position='[lon, lat]',
                get_color='[255, 0, 0, 160]',
                get_radius=4,
                pickable=True,
            ),
            pdk.Layer(
                'TextLayer',
                data=map_data,
                get_position='[lon, lat]',
                get_text='위치명',
                get_size=14,
                get_color='[0, 0, 0]',
                get_angle=0,
                get_alignment_baseline='bottom'
            )
        ],
        tooltip={"text": "{위치명}"}
    ))

if page == "📷 생육 일자별 기록":
    st.markdown("## 📷 생육 일자별 기록")
    photo_logs = []
    data_rows = []

    start_date = st.date_input("📅 시작일 입력", dt.date.today())
    num_days = st.number_input("기록할 일수", min_value=1, max_value=30, value=7)

    for i in range(num_days):
        date = start_date + dt.timedelta(days=i)
        with st.expander(f"📆 {date} 생육기록 보기 / 입력"):
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_temp = st.number_input(f"{date} 평균온도 (℃)", key=f"t{i}")
            with col2:
                night_temp = st.number_input(f"{date} 야간최저온도 (℃)", key=f"n{i}")
            with col3:
                ec = st.number_input(f"{date} EC", key=f"e{i}")
            uploaded = st.file_uploader(f"{date} 생육 사진 업로드", type=["jpg", "jpeg", "png"], key=f"img{i}")
            memo = st.text_area(f"{date} 생육 일지 메모", key=f"m{i}")
            photo_logs.append((date, uploaded))
            data_rows.append({"날짜": date, "평균온도": avg_temp, "야간최저온도": night_temp, "EC": ec, "메모": memo})

    df = pd.DataFrame(data_rows)
    st.session_state["daily_df"] = df

if page == "📊 생육 분석 요약":
    df = st.session_state.get("daily_df", pd.DataFrame())
    if df.empty:
        st.warning("먼저 생육 데이터를 입력해주세요. 왼쪽 메뉴에서 '📷 생육 일자별 기록'을 선택하세요.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            crop_type = st.selectbox("작물 선택", ["설향 딸기", "핑크 토마토"])
        with col2:
            flower_date = st.date_input("개화일 입력", dt.date.today())

        def simulate_growth(data, crop):
            base_days = 35 if crop == "설향 딸기" else 50
            optimal_temp = 25
            delay_night_temp = 12 if crop == "설향 딸기" else 15
            def score(row):
                t = max(0.2, 1 - abs(row["평균온도"] - optimal_temp) / 15)
                d = 1.15 if row["야간최저온도"] < delay_night_temp else 1.0
                return t * d
            data["생육지수"] = data.apply(score, axis=1)
