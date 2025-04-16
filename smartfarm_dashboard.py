import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px

st.set_page_config(
    page_title="📡 스마트팜 환경 리포트 | 키르기스스탄 딸기·토마토",
    layout="wide",
    page_icon="🍓"
)

# 제목
st.markdown("<h1 style='color:#2E86C1'>🌱 키르기스스탄 스마트팜 생육 대시보드</h1>", unsafe_allow_html=True)

# 입력
col1, col2 = st.columns(2)
with col1:
    crop_type = st.selectbox("작물 선택", ["설향 딸기", "핑크 토마토"])
with col2:
    flower_date = st.date_input("개화일 입력", dt.date.today())

# 예시 센서 데이터
df = pd.DataFrame({
    "날짜": pd.date_range(start=flower_date, periods=30),
    "평균온도": [22 + i*0.1 for i in range(30)],
    "야간최저온도": [10 + (i % 3) for i in range(30)],
    "EC": [1.1 + (i % 5) * 0.05 for i in range(30)],
})

# 생육 예측
def simulate_growth(data, crop):
    base_days = 35 if crop == "설향 딸기" else 50
    optimal_temp = 25
    delay_night_temp = 12 if crop == "설향 딸기" else 15

    def score(row):
        t = max(0.2, 1 - abs(row["평균온도"] - optimal_temp) / 15)
        d = 1.15 if row["야간최저온도"] < delay_night_temp else 1.0
        return t * d

    data["생육지수"] = data.apply(score, axis=1)
    cumulative = data["생육지수"].cumsum()
    threshold = base_days
    predicted_day = cumulative[cumulative >= threshold].first_valid_index()
    harvest_date = data.iloc[predicted_day]["날짜"] if predicted_day is not None else None
    return harvest_date, data

predicted_harvest, df = simulate_growth(df, crop_type)

# 요약 카드
st.subheader("📊 생육 예측 요약")
col1, col2, col3 = st.columns(3)
col1.metric("평균 온도", f"{df['평균온도'].mean():.1f}℃")
col2.metric("야간 최저온도", f"{df['야간최저온도'].min():.1f}℃")
col3.metric("예상 수확일", predicted_harvest.strftime('%Y-%m-%d') if predicted_harvest else "예측불가")

# 그래프
st.subheader("📈 환경 변화 그래프")
fig1 = px.line(df, x="날짜", y=["평균온도", "야간최저온도"], title="온도 추이")
fig2 = px.line(df, x="날짜", y="EC", title="EC 추이")
st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)

# 리포트 다운로드
st.subheader("📄 리포트 다운로드")
st.download_button("CSV 다운로드", df.to_csv(index=False).encode('utf-8'), file_name="smartfarm_data.csv")
