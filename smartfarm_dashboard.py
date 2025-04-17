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

page = st.sidebar.radio("페이지 선택", ["🏠 기본정보 입력", "📷 생육 일자별 기록", "📊 생육 분석 요약", "📦 동결건조 관리"])

if page != "📦 동결건조 관리":
    st.markdown('<div class="report-title">🌱 키르 스마트팜 생육 리포트</div>', unsafe_allow_html=True)

# 사이드바로 챕터 구분
page = st.sidebar.radio("페이지 선택", ["🏠 기본정보 입력", "📷 생육 일자별 기록", "📊 생육 분석 요약", "📦 동결건조 관리"])

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

    if not map_data.empty:
        selected_zone = st.selectbox("농장 내 위치 선택:", map_data["위치명"].tolist())
        zone_coords = map_data[map_data["위치명"] == selected_zone][["lat", "lon"]].values[0]
        farm_location = f"{selected_zone} - {zone_coords[0]}, {zone_coords[1]}"

        selected_df = map_data[map_data["위치명"] == selected_zone]
        lat, lon = zone_coords
        square = [[
            [lon - 0.00005, lat - 0.00005],
            [lon + 0.00005, lat - 0.00005],
            [lon + 0.00005, lat + 0.00005],
            [lon - 0.00005, lat + 0.00005]
        ]]

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/satellite-v9',
            initial_view_state=pdk.ViewState(
                latitude=lat,
                longitude=lon,
                zoom=19,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "PolygonLayer",
                    data=pd.DataFrame({'coordinates': [square]}),
                    get_polygon="coordinates",
                    get_fill_color='[255, 0, 0, 40]',
                    get_line_color='[255, 0, 0]',
                    line_width_min_pixels=2,
                ),
                pdk.Layer(
                    "TextLayer",
                    data=selected_df,
                    get_position='[lon, lat]',
                    get_text='위치명',
                    get_size=14,
                    get_color='[255, 255, 255]',
                    get_alignment_baseline='bottom',
                )
            ],
            tooltip={"text": "{위치명}"}
        ))
    else:
        st.info("지도 데이터를 불러오는 중이거나 비어 있습니다.")

elif page == "📷 생육 일자별 기록":
    st.header("📷 생육 일자별 기록")
    start_date = st.date_input("기록 시작일", dt.date.today())
    num_days = st.number_input("기록할 일 수", min_value=1, max_value=30, value=7)
    logs = []
    for i in range(num_days):
        date = start_date + dt.timedelta(days=i)
        with st.expander(f"{date} 생육기록"):
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_temp = st.number_input(f"{date} 평균온도 (℃)", key=f"t{i}")
            with col2:
                night_temp = st.number_input(f"{date} 야간최저온도 (℃)", key=f"n{i}")
            with col3:
                ec = st.number_input(f"{date} EC", key=f"e{i}")
            memo = st.text_area(f"{date} 메모", key=f"memo{i}")
            logs.append({"날짜": date, "평균온도": avg_temp, "야간최저": night_temp, "EC": ec, "메모": memo})
    st.session_state["logs_df"] = pd.DataFrame(logs)

elif page == "📊 생육 분석 요약":
    df = st.session_state.get("logs_df", pd.DataFrame())
    if df.empty:
        st.warning("생육 기록을 먼저 입력해주세요.")
    else:
        st.subheader("📈 생육 환경 변화")
        fig = px.line(df, x="날짜", y=["평균온도", "야간최저", "EC"], title="환경 데이터 추이")
        st.plotly_chart(fig, use_container_width=True)

elif page == "📦 동결건조 관리":
    st.markdown('<div class="report-title">📦 동결건조 관리 리포트</div>', unsafe_allow_html=True)
    st.subheader("🧊 월별 동결건조 생산현황 및 유통 가격 분석")
    with st.expander("📦 생산량 및 가격 추이"):
        freeze_data = pd.DataFrame({
            "월": ["1월", "2월", "3월", "4월"],
            "생산량(kg)": [120, 135, 150, 170],
            "평균가격(₩/kg)": [40000, 42000, 41000, 43000]
        })
        st.dataframe(freeze_data)
        fig2 = px.bar(freeze_data, x="월", y="생산량(kg)", title="월별 생산량")
        fig3 = px.line(freeze_data, x="월", y="평균가격(₩/kg)", title="월별 가격 추이")
        st.plotly_chart(fig2, use_container_width=True)
        st.plotly_chart(fig3, use_container_width=True)
