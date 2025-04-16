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

logo_path = "1. CI_레터마크_PNG"
st.image(logo_path, width=180)

st.markdown('<div class="report-title">🌱 키르 스마트팜 생육 리포트</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    manager_name = st.text_input("담당자 이름", "이한승")
with col2:
    farm_name = st.text_input("농장명", "IWS-Agro")

st.subheader("📍 농장 구역 선택 (지도 기반)")
farm_options = {
    "A동 토마토": "42.950226, 74.719877",
    "B동 딸기": "42.950200, 74.719900",
    "C동": "42.950000, 74.719850",
    "D동 토마토": "42.950100, 74.719950",
    "E동 토마토": "42.950300, 74.719700",
    "F동": "42.950400, 74.719600",
    "G동 토마토": "42.950500, 74.719500"
}
selected_zone = st.selectbox("농장 내 위치 선택:", list(farm_options.keys()))
zone_coords = farm_options[selected_zone]
farm_location = f"{selected_zone} - {zone_coords}"

map_df = pd.DataFrame({"lat": [float(zone_coords.split(",")[0])], "lon": [float(zone_coords.split(",")[1])]})
st.map(map_df, zoom=18)

uploaded_photo = st.file_uploader("📷 생육 사진 업로드 (선택)", type=["jpg", "jpeg", "png"])
activity_log = st.text_area("📝 생육 일지 메모", "")

col1, col2 = st.columns(2)
with col1:
    crop_type = st.selectbox("작물 선택", ["설향 딸기", "핑크 토마토"])
with col2:
    flower_date = st.date_input("개화일 입력", dt.date.today())

# 생육 환경 수동 입력 테이블
df = st.data_editor(pd.DataFrame({
    "날짜": pd.date_range(start=flower_date, periods=7),
    "평균온도": [None]*7,
    "야간최저온도": [None]*7,
    "EC": [None]*7,
}), use_container_width=True, num_rows="dynamic")

# 생육 예측 계산
@st.cache_data(ttl=60)
def simulate_growth(data, crop):
    base_days = 35 if crop == "설향 딸기" else 50
    optimal_temp = 25
    delay_night_temp = 12 if crop == "설향 딸기" else 15

    def score(row):
        if pd.isna(row["평균온도"]): return 0
        t = max(0.2, 1 - abs(row["평균온도"] - optimal_temp) / 15)
        d = 1.15 if row["야간최저온도"] < delay_night_temp else 1.0
        return t * d

    data["생육지수"] = data.apply(score, axis=1)
    cumulative = data["생육지수"].cumsum()
    predicted_day = cumulative[cumulative >= base_days].first_valid_index()
    harvest_date = data.iloc[predicted_day]["날짜"] if predicted_day is not None else None
    return harvest_date, data

predicted_harvest, df = simulate_growth(df, crop_type)

st.subheader("📊 생육 예측 요약")
col1, col2, col3 = st.columns(3)
col1.metric("평균 온도", f"{df['평균온도'].mean():.1f}℃")
col2.metric("야간 최저온도", f"{df['야간최저온도'].min():.1f}℃")
col3.metric("예상 수확일", predicted_harvest.strftime('%Y-%m-%d') if predicted_harvest else "예측불가")

st.subheader("🧠 생육 분석 코멘트")
comments = []
if df['야간최저온도'].min(skipna=True) < 10:
    comments.append("⚠️ 야간 기온이 10℃ 이하로 낮아 생육 지연 우려가 있습니다.")
if df['EC'].mean(skipna=True) > 1.8:
    comments.append("⚠️ EC가 1.8 이상으로 염류장해 가능성이 있습니다. 양액 희석 필요.")
if (dt.date.today() - flower_date).days > 30:
    comments.append("✅ 개화 후 30일 이상 경과, 수확 적기 진입 중입니다.")
if not comments:
    comments.append("✅ 생육 환경이 양호합니다.")
for c in comments:
    st.write(c)

st.subheader("📈 생육 환경 변화 그래프")
if "평균온도" in df.columns and df["평균온도"].notna().any():
    fig1 = px.line(df, x="날짜", y=["평균온도", "야간최저온도"], title="온도 추이")
    fig2 = px.line(df, x="날짜", y="EC", title="EC 추이")
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)


def generate_pdf(data, crop, harvest):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    logo = ImageReader(logo_path)
    c.drawImage(logo, 50, 770, width=120, preserveAspectRatio=True, mask='auto')
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 800, f"SmartFarm 생육 리포트 - {crop}")
    c.setFont("Helvetica", 12)
    c.drawString(50, 740, f"담당자: {manager_name} | 농장명: {farm_name}")
    c.drawString(50, 720, f"농장 위치: {farm_location}")
    c.drawString(50, 700, f"작성일: {dt.date.today().strftime('%Y-%m-%d')}")
    c.drawString(50, 680, f"개화일: {flower_date.strftime('%Y-%m-%d')}")
    c.drawString(50, 660, f"예상 수확일: {harvest.strftime('%Y-%m-%d') if harvest else '예측불가'}")
    c.drawString(50, 640, f"평균 온도: {data['평균온도'].mean(skipna=True):.1f}℃")
    c.drawString(50, 620, f"야간 최저온도: {data['야간최저온도'].min(skipna=True):.1f}℃")
    c.drawString(50, 600, f"평균 EC: {data['EC'].mean(skipna=True):.2f} mS/cm")
    c.drawString(50, 580, "[코멘트 요약]")
    y = 560
    for cmt in comments:
        c.drawString(60, y, f"- {cmt}")
        y -= 20
    if activity_log:
        c.drawString(50, y - 20, "[생육 일지 메모]")
        text = c.beginText(60, y - 40)
        for line in activity_log.split("\n"):
            text.textLine(line)
        c.drawText(text)
    c.save()
    buffer.seek(0)
    return buffer

st.subheader("📄 리포트 다운로드")
st.download_button("데이터 요약 다운로드 (CSV)", df.to_csv(index=False).encode('utf-8'), file_name="smartfarm_data.csv")
pdf = generate_pdf(df, crop_type, predicted_harvest)
st.download_button("PDF 리포트 다운로드", pdf, file_name="smartfarm_report.pdf")
