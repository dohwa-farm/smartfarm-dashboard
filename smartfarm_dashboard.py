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
    st.header("📷 생육 일자별 영농일지 기록")
    st.markdown("""
    시설 양액재배에 맞춘 영농일지 입력 양식입니다. 농업ON 영농일지 포맷을 참고하여 현장 작업 내용을 체계적으로 기록할 수 있도록 구성하였습니다.
    """)

    start_date = st.date_input("기록 시작일", datetime.date.today())
    num_days = st.number_input("기록할 일 수", min_value=1, max_value=30, value=7)
    logs = []

    for i in range(num_days):
        date = start_date + datetime.timedelta(days=i)
        with st.expander(f"📅 {date} 영농일지"):
            col1, col2 = st.columns(2)
            with col1:
                crop = st.text_input(f"재배 품목", key=f"crop{i}")
                variety = st.text_input(f"품종", key=f"variety{i}")
                area = st.text_input(f"작업 구역", key=f"zone{i}")
                work_type = st.selectbox(f"작업 단계", ["정식", "수확", "방제", "양액관리", "온습도관리", "점검", "기타"], key=f"worktype{i}")
                activity = st.text_area(f"작업 내용", key=f"activity{i}")
            with col2:
                weather = st.selectbox(f"날씨", ["맑음", "흐림", "비", "눈"], key=f"weather{i}")
                temp_low = st.number_input(f"최저기온(℃)", key=f"temp_low{i}")
                temp_high = st.number_input(f"최고기온(℃)", key=f"temp_high{i}")
                humidity = st.number_input(f"습도(%)", key=f"humid{i}")
                rainfall = st.number_input(f"강수량(mm)", key=f"rain{i}")
                is_public = st.radio(f"공개 여부", ["공개", "비공개"], key=f"public{i}")

            logs.append({
                "날짜": date,
                "재배 품목": crop,
                "품종": variety,
                "작업 구역": area,
                "작업 단계": work_type,
                "작업 내용": activity,
                "날씨": weather,
                "최저기온": temp_low,
                "최고기온": temp_high,
                "습도": humidity,
                "강수량": rainfall,
                "공개 여부": is_public
            })

        df = pd.DataFrame(logs)
    st.session_state["logs_df"] = df

    st.subheader("📸 생육 사진 업로드")
    photo_upload = st.file_uploader("해당 일자 사진 업로드 (선택)", accept_multiple_files=True)
    if photo_upload:
        for uploaded_file in photo_upload:
            st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)

    st.subheader("📅 월별/구역별 영농일지 요약")
    if not df.empty:
        month_option = st.selectbox("월 선택", sorted(df["날짜"].dt.month.unique()))
        area_option = st.selectbox("작업 구역 선택", ["전체"] + sorted(df["작업 구역"].dropna().unique()))

        filtered_df = df[df["날짜"].dt.month == month_option]
        if area_option != "전체":
            filtered_df = filtered_df[filtered_df["작업 구역"] == area_option]

        st.dataframe(filtered_df, use_container_width=True)

    if st.button("📄 영농일지 PDF로 출력하기"):
        from reportlab.pdfgen.canvas import Canvas
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 40, "시설 스마트팜 영농일지 리포트")
        y = height - 70

        for entry in logs:
            c.setFont("Helvetica", 11)
            for key, value in entry.items():
                c.drawString(50, y, f"{key}: {value}")
                y -= 16
                if y < 100:
                    c.showPage()
                    c.setFont("Helvetica", 11)
                    y = height - 70
            c.line(50, y, width - 50, y)
            y -= 20

        c.save()
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="smartfarm_diary.pdf">📥 영농일지 PDF 다운로드</a>'
        st.markdown(href, unsafe_allow_html=True)

    if st.button("📄 PDF로 출력하여 저장하기"):
        from reportlab.pdfgen.canvas import Canvas
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 40, "키르 스마트팜 영농일지 리포트")
        y = height - 70
        for entry in logs:
            for key, value in entry.items():
                c.drawString(50, y, f"{key}: {value}")
                y -= 18
                if y < 100:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y = height - 70
            c.line(50, y, width - 50, y)
            y -= 20
        c.save()
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="smartfarm_diary.pdf">📥 영농일지 PDF 다운로드</a>'
        st.markdown(href, unsafe_allow_html=True)

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
    st.plotly_chart(fig_price, use_container_width=True, key="fig_price_chart")
