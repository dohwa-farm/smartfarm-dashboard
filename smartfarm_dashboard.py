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

if page in ["🏠 기본정보 입력", "📷 생육 일자별 기록", "📊 생육 분석 요약"]:
    st.markdown('<div class="report-title">🌱 키르 스마트팜 생육 리포트</div>', unsafe_allow_html=True)

if page == "📒 영농일지":
    st.markdown("<h2 style='color:#2E86C1;'>📒 영농일지 작성</h2>", unsafe_allow_html=True)
    st.subheader("📅 생육 일자별 기록 달력")
    selected_date = st.date_input("작성일자", datetime.date.today(), key="growth_date")
    with st.expander(f"📌 {selected_date} 생육일지 작성"):
        with st.form(key="growth_log"):
            col1, col2 = st.columns(2)
            with col1:
                crop = st.text_input("재배 품목")
                variety = st.text_input("품종")
                section = st.multiselect("작업 구역", ["A동 토마토", "B동 딸기", "C동", "D동 토마토", "E동 토마토", "F동", "G동 토마토"])
                work_stage = st.selectbox("작업 단계", ["정식", "수확", "방제", "양액관리", "온습도관리", "점검", "기타"])
                activity_type = st.radio("활동 유형", ["농약", "비료", "인력"], horizontal=True)
            with col2:
                pesticide_type = st.selectbox("농약 분류 선택", ["살균제", "살충제", "살균,살충제", "살충,제초제", "제초제", "생장조정제", "기타", "친환경 농약"])
                with st.columns([2, 1]) as cols:
    pesticide_amount = cols[0].text_input("살포량")
    pesticide_unit = cols[1].selectbox("단위", ["kg", "g", "mg", "l", "ml", "dl"])
                weather = st.selectbox("날씨", ["맑음", "흐림", "비", "눈"])
                temp_min = st.number_input("최저기온(℃)", format="%.2f")
                temp_max = st.number_input("최고기온(℃)", format="%.2f")
                humidity = st.number_input("습도(%)", format="%.2f")
                rain = st.number_input("강수량(mm)", format="%.2f")
            st.text_area("작업 내용")
            st.radio("공개 여부", ["공개", "비공개"], horizontal=True)
            st.file_uploader("📸 생육 사진 첨부", type=["jpg", "jpeg", "png"])
            if st.form_submit_button("➕ 영농일지 저장"):
    st.success("✅ 자동 저장 완료")
    df_saved = pd.DataFrame({
        "일자": [selected_date],
        "작목": [crop],
        "품종": [variety],
        "구역": [', '.join(section)],
        "작업단계": [work_stage],
        "날씨": [weather],
        "최저기온": [temp_min],
        "최고기온": [temp_max],
        "습도": [humidity],
        "강수량": [rain]
    })
    towrite = BytesIO()
    df_saved.to_excel(towrite, index=False)
    towrite.seek(0)
    st.download_button(
        label="📥 엑셀로 다운로드",
        data=towrite,
        file_name=f"{selected_date}_영농일지.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    # 간단한 예시 데이터 저장
    df_saved = pd.DataFrame({
        "일자": [selected_date],
        "작목": [crop],
        "품종": [variety],
        "구역": [section],
        "작업단계": [work_stage]
    })
    towrite = BytesIO()
    df_saved.to_excel(towrite, index=False)
    towrite.seek(0)
    st.download_button(
        label="📥 엑셀로 다운로드",
        data=towrite,
        file_name=f"{selected_date}_영농일지.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif page == "📅 영농일지 달력":
    import calendar
    import random
    today = datetime.date.today()
    year, month = today.year, today.month
    st.markdown(f"### 📆 {year}년 {month}월 영농일지")
    st.markdown("💡 기록이 있는 날짜는 ✅ 표시됩니다.")
    calendar_dates = []
    for i in range(1, 32):
        try:
            d = datetime.date(year, month, i)
            has_data = random.choice([True, False])  # 예시 랜덤
            label = f"{d.strftime('%Y-%m-%d')} {'✅' if has_data else ''}"
            st.button(label)
        except:
            pass
    import calendar
    today = datetime.date.today()
    year, month = today.year, today.month
    st.markdown(f"### 📆 {year}년 {month}월 영농일지")
    st.markdown("_※ 달력 UI 및 일자별 마킹은 곧 연동됩니다_ 📅")
    for i in range(1, 32):
        try:
            d = datetime.date(year, month, i)
            st.button(f"{d.strftime('%Y-%m-%d')} 일지 작성")
        except:
            pass
    st.subheader("📅 영농일지 목록 (달력 기반)")
    st.success("💡 각 날짜를 클릭하면 해당 일자의 영농일지를 작성하거나 수정할 수 있습니다.")
    # 달력은 시각적으로 표현 어려워 placeholder만 둠
    st.markdown("_※ 달력 UI 및 일자별 마킹은 추후 연동 예정_ 📅")

elif page == "📊 생육 분석 요약":
    st.subheader("📈 생육 분석 요약")
    df = pd.DataFrame({
        "주차": ["1주차", "2주차", "3주차", "4주차"],
        "평균온도": [22.5, 23.0, 21.8, 22.1],
        "EC": [1.2, 1.3, 1.3, 1.4],
        "예상수확량(kg)": [100, 120, 110, 130]
    })
    st.dataframe(df, use_container_width=True)
    fig = px.line(df, x="주차", y="예상수확량(kg)", markers=True)
    st.plotly_chart(fig, use_container_width=True)

elif page == "📦 동결건조 관리":
    st.markdown("<h2>📦 동결건조 관리</h2>", unsafe_allow_html=True)
    df = pd.DataFrame({
        "월": ["1월", "2월", "3월", "4월"],
        "생산량(kg)": [22, 25, 27, 30],
        "단가(원)": [40000, 41000, 42000, 43000]
    })
    st.dataframe(df, use_container_width=True)
    st.bar_chart(df.set_index("월"))

elif page == "🌱 육묘장 관리":
    st.subheader("🌱 육묘장 관리")
    selected_date = st.date_input("작성일자", datetime.date.today(), key="nursery_date")
    with st.expander(f"📌 {selected_date} 육묘장 기록"):
        with st.form(key="nursery_log"):
            tray = st.text_input("육묘 품종")
            zone = st.selectbox("육묘장 구역", ["A동", "B동", "C동", "D동", "E동", "F동", "G동"])
            staff_count = st.number_input("투입 인원 수", min_value=0, step=1)
            col1, col2 = st.columns(2)
            with col1:
                st.number_input("온도(℃)")
                st.number_input("광량(lux)")
                st.number_input("급액량(ml)")
            with col2:
                st.number_input("습도(%)")
                st.text_area("관리 내용 및 특이사항")
            st.file_uploader("📸 생육 사진", type=["jpg", "jpeg", "png"])
            st.form_submit_button("➕ 육묘장 저장")

elif page == "🧠 AI 생육 이미지 분석":
    st.subheader("🧠 AI 생육 이미지 분석")
    st.markdown("""
AI 분석 기능은 시범 운영 중입니다.

🧠 적용 기능:
- 엽색 분석
- 반점 인식
- 병해충 탐지

📸 생육 이미지를 업로드하면 자동 분석 결과가 제공됩니다.
(지속 업데이트 중)
""")

elif page == "🏠 기본정보 입력":
    st.subheader("📍 스마트팜 위치 지도")
    map_data = pd.DataFrame({
        'lat': [42.950370, 42.950310, 42.950250, 42.950600, 42.950770, 42.950880, 42.951050],
        'lon': [74.719870, 74.720060, 74.720250, 74.719800, 74.719900, 74.720150, 74.720400],
        '구역': ['A동 토마토', 'B동 딸기', 'C동', 'D동 토마토', 'E동 토마토', 'F동', 'G동 토마토']
    })

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position='[lon, lat]',
        get_fill_color='[200, 30, 0, 160]',
        get_radius=10,
        pickable=True,
        auto_highlight=True
    )

    view_state = pdk.ViewState(
        latitude=42.9506,
        longitude=74.7200,
        zoom=18,
        pitch=0
    )

    st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/satellite-v9",
    initial_view_state=view_state,
    layers=[pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position='[lon, lat]',
        get_fill_color='[30, 144, 255, 160]',
        get_radius=10,
        pickable=True,
        auto_highlight=True
    )],
    tooltip={"text": "{구역}"}
))

    st.subheader("🧠 AI 생육 이미지 진단")
    uploaded_img = st.file_uploader("진단할 생육 이미지 업로드", type=["jpg", "jpeg", "png"], key="ai_upload")
    if uploaded_img:
        st.image(uploaded_img, caption="업로드된 이미지", use_column_width=True)
        st.success("✅ AI 진단 기능은 추후 추가 예정입니다.")
