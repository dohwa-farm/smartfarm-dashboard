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

page = st.sidebar.radio("페이지 선택", ["🏠 기본정보 입력", "📷 생육 일자별 기록", "📊 생육 분석 요약", "📦 동결건조 관리"])

if page != "📦 동결건조 관리":
    st.markdown('<div class="report-title">🌱 키르 스마트팜 생육 리포트</div>', unsafe_allow_html=True)

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
    start_date = st.date_input("기록 시작일", datetime.date.today())
    num_days = st.number_input("기록할 일 수", min_value=1, max_value=30, value=7)
    logs = []
    for i in range(num_days):
        date = start_date + datetime.timedelta(days=i)
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

    st.markdown("""
    동결건조 공정은 스마트팜 내에서 고부가가치를 창출할 수 있는 핵심 단계입니다. 아래의 리포트는 월별 생산 실적과 유통 가격 데이터를 기반으로 수익성 및 시장 동향을 종합적으로 보여줍니다.
    """)

    st.subheader("📦 생산 실적 개요")
    st.markdown("""
    아래는 1월부터 4월까지의 동결건조 딸기 생산량을 정리한 표입니다. 생산량은 점진적으로 증가하는 추세를 보이고 있으며, 이는 재배 기술 안정화 및 수요 증가에 기인한 것으로 분석됩니다.
    """)
    production_data = pd.DataFrame({
        "월": ["1월", "2월", "3월", "4월"],
        "생산량(kg)": [120, 135, 150, 170]
    })
    st.dataframe(production_data, use_container_width=True)
    fig_prod = px.bar(production_data, x="월", y="생산량(kg)", title="📊 월별 동결건조 생산량", text_auto=True)
    st.plotly_chart(fig_prod, use_container_width=True)

    st.subheader("💰 유통 가격 동향 분석")
    st.markdown("""
    다음은 월별 동결건조 제품의 평균 유통 단가입니다. 가격은 전체적으로 상승세를 보이고 있으며,
    이는 품질 인식 제고 및 판로 다변화의 영향으로 해석됩니다. 

    유통 가격의 변화는 재배 원가와 비교해 수익성을 결정하는 중요한 지표입니다. 특히 원자재, 에너지 비용,
    물류비 등의 변동성과 연동하여 가격 데이터를 분석하면 향후 수익률 시뮬레이션과 판매 전략 수립에 유용합니다.

    - 3월 가격 하락은 공급 일시 증가 및 시장 반응이 복합적으로 작용했을 가능성이 있음.
- 가격 대비 생산량의 증가폭을 감안할 때, 단위당 수익률의 안정성 확보가 필요한 구간임.
- 다음 분기 가격 전략 수립을 위해 시장 내 경쟁 제품의 가격 추이를 모니터링할 필요 있음.
    """)
    price_data = pd.DataFrame({
        "월": ["1월", "2월", "3월", "4월"],
        "평균가격(₩/kg)": [40000, 42000, 41000, 43000]
    })
    st.dataframe(price_data, use_container_width=True)
    fig_price = px.line(price_data, x="월", y="평균가격(₩/kg)", markers=True, title="💹 월별 평균 유통 가격 추이")
    st.plotly_chart(fig_price, use_container_width=True)
