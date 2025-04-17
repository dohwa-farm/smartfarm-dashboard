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
import numpy as np

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

st.title("📡 스마트팜 환경 리포트")
st.markdown("이 대시보드는 키르기스스탄 스마트팜(딸기/토마토) 생육, 환경, 생산, 육묘, 동결건조 상태를 통합 관리하고 보고서로 추출하기 위한 시스템입니다.")

page = st.sidebar.radio("페이지 선택", ["📋 생육 일자별 기록", "🧬 생육 분석 요약", "❄️ 동결건조 관리", "🌱 육묘장 관리"])

if page == "📋 생육 일자별 기록":
    st.header("📅 생육 일자별 기록")
    col1, col2 = st.columns(2)
    with col1:
        crop = st.text_input("재배 품목")
        section = st.text_input("작업 구역")
        date = st.date_input("작업 일자", datetime.date.today())
        weather = st.selectbox("날씨", ["맑음", "흐림", "비", "눈"])
        temp_min = st.number_input("최저기온(℃)", value=0.0)
        temp_max = st.number_input("최고기온(℃)", value=0.0)
    with col2:
        humidity = st.number_input("습도(%)", value=0.0)
        ec = st.number_input("EC", value=0.0)
        growth = st.text_area("작업 내용")
        image_file = st.file_uploader("📸 생육 사진 첨부 (선택)", type=["jpg", "png", "jpeg"])

        if image_file:
            image = PILImage.open(image_file)
            st.image(image, caption="업로드된 생육 사진", use_column_width=True)

            def analyze_plant_health(image):
                img = image.resize((100, 100)).convert("RGB")
                arr = np.array(img)
                avg_green = arr[:, :, 1].mean()
                avg_red = arr[:, :, 0].mean()
                avg_blue = arr[:, :, 2].mean()
                suggestions = []

                if avg_green < 80:
                    diagnosis = "⚠️ 생육 불량 (엽색 저조)"
                    suggestions.append("의심되는 질병: 질소 결핍")
                    suggestions.append("조치: 요소비료 0.2% 엽면시비")
                elif avg_green > 180:
                    diagnosis = "✅ 건강 양호 (엽색 짙음)"
                else:
                    diagnosis = "🔍 정상 범위"
                    suggestions.append("주의: 생육 변동 가능성 있음")
                    suggestions.append("관수량과 환기 빈도 점검")

                if avg_red > 150:
                    suggestions.append("❗ 과실 조기 성숙 가능성")
                if avg_blue > 130:
                    suggestions.append("🔍 잎색 변색 또는 해충 피해 의심")

                return diagnosis, suggestions

            diagnosis, suggestions = analyze_plant_health(image)
            st.markdown(f"**AI 진단 결과:** {diagnosis}")
            if suggestions:
                st.markdown("**📌 자동 분석 제안:**")
                for s in suggestions:
                    st.markdown(f"- {s}")

elif page == "🧬 생육 분석 요약":
    st.header("📈 생육 분석 요약")
    st.markdown("주간 생육 데이터 분석 및 수확 예측입니다.")
    df = pd.DataFrame({
        "주차": ["1주차", "2주차", "3주차", "4주차"],
        "평균온도": [22.5, 23.0, 21.8, 22.1],
        "EC": [1.2, 1.3, 1.3, 1.4],
        "수확량예측(kg)": [100, 120, 110, 130]
    })
    st.dataframe(df)
    fig = px.line(df, x="주차", y="수확량예측(kg)", title="주차별 수확량 예측")
    st.plotly_chart(fig)

elif page == "❄️ 동결건조 관리":
    st.header("❄️ 동결건조 관리 리포트")
    st.markdown("동결건조기 가동 기록, 투입량, 회수량, 단가, 생산 수익 등 관리합니다.")
    df = pd.DataFrame({
        "월": ["1월", "2월", "3월", "4월"],
        "생산량(kg)": [20, 25, 22, 30],
        "평균 단가(원)": [40000, 42000, 41000, 43000]
    })
    st.dataframe(df)
    fig1 = px.bar(df, x="월", y="생산량(kg)", title="월별 생산량")
    fig2 = px.line(df, x="월", y="평균 단가(원)", title="월별 평균 단가")
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)

elif page == "🌱 육묘장 관리":
    st.header("🌱 육묘장 관리 리포트")
    st.markdown("모종 관리, 육묘 환경, 급액/관수 관리, 유묘 상태 등을 일자별로 기록하세요.")
    date = st.date_input("기록 일자", datetime.date.today())
    tray_count = st.number_input("트레이 수량", min_value=0)
    water_volume = st.number_input("관수량 (L)", min_value=0.0)
    nutrient_ratio = st.text_input("양액 비율 (예: 1:1000)")
    note = st.text_area("비고 또는 특이사항")
    st.success("기록 완료! (DB 연동은 후속 구현 예정)")
