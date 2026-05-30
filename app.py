import streamlit as st
from datetime import date
import pandas as pd
from sales_data import (
    load_sales_data,
    get_default_reporting_date,
    CHANNELS,
    WLF_BRAND,
    OTHER_BRANDS,
    compute_daily_sales_by_channel,
    compute_monthly_cumulative_by_channel,
    compute_eland_store_daily_rank,
    compute_eland_month_to_date_store_rank,
    compute_eland_total_daily_wlf,
    compute_eland_warning_stores,
    compute_eland_store_cumulative_rank,
    read_sales_excel,
    merge_sales_data,
)

st.set_page_config(page_title="위라이크패션 매출 대시보드", layout="wide")

st.title("위라이크패션 오프라인 유통 매출 대시보드")

header_col, upload_col = st.columns([3, 1])
with upload_col:
    uploaded_file = st.file_uploader(
        "일일 엑셀 업로드",
        type=["xls", "xlsx"],
        help="업로드된 엑셀 파일을 읽어 대시보드 데이터를 업데이트합니다.",
    )

report_date = st.date_input("기준일 선택", value=get_default_reporting_date())

st.markdown(
    "- 자동 D-1 기준일: 컴퓨터 시간 기준으로 전일 데이터를 기본 표시합니다."
    "\n- 엑셀 파일 업로드 시 해당 데이터가 기존 자료에 병합되어 대시보드에 반영됩니다."
    "\n- 조회 채널: 현대아울렛, 이랜드리테일, 롯데백화점, 마리오아울렛, lf몰, 세이브존, 한국중소기업벤처기업유통원, 와이스퀘어, 스퀘어원, 신세계아울렛"
)

try:
    df = load_sales_data()
except FileNotFoundError:
    st.error("데이터 파일을 찾을 수 없습니다. data/sample_sales.csv 또는 실제 데이터 경로를 확인하세요.")
    st.stop()

if uploaded_file is not None:
    try:
        uploaded_df = read_sales_excel(uploaded_file)
        df = merge_sales_data(df, uploaded_df)
        st.success(f"업로드된 엑셀 데이터를 반영했습니다. 추가 데이터 {uploaded_df.shape[0]}개 행, 누적 데이터 {len(df)}개 행")
    except Exception as exc:
        st.error(f"엑셀 파일 처리 오류: {exc}")
        st.stop()

with st.expander("데이터 요약", expanded=True):
    st.write(f"총 데이터 행: {len(df)}")
    st.write("채널 목록:", ", ".join(CHANNELS))
    st.write("브랜드 기준: 위라이크패션")

with st.expander("데이터 요약", expanded=True):
    st.write(f"총 데이터 행: {len(df)}")
    st.write("채널 목록:", ", ".join(CHANNELS))
    st.write("브랜드 기준: 위라이크패션")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1-1. 이랜드리테일 위라이크패션 일매출 점포 순위")
    eland_rank = compute_eland_store_daily_rank(df, report_date, WLF_BRAND)
    st.dataframe(eland_rank.style.format({"daily_sales": "{:,}"}))

with col2:
    st.subheader("1-2. 유통 채널별 월누적 위라이크패션 매출 순위")
    channel_rank = compute_monthly_cumulative_by_channel(df, report_date, WLF_BRAND)
    st.dataframe(channel_rank.style.format({"month_to_date_sales": "{:,}"}))

st.subheader("1-3. 유통 채널별 위라이크패션 일매출 현황")
channel_daily = compute_daily_sales_by_channel(df, report_date, WLF_BRAND)
st.dataframe(channel_daily.style.format({"daily_sales": "{:,}"}))

st.markdown("---")

st.header("이랜드리테일 기준 점포/브랜드 매출 대시보드")

st.subheader("2-1. 이랜드리테일 오늘 위라이크패션 총매출")
eland_total = compute_eland_total_daily_wlf(df, report_date, WLF_BRAND)
st.metric(label="오늘 이랜드리테일 위라이크패션 총매출", value=f"{eland_total:,.0f}원")

st.subheader("2-2. 전주 대비 30% 이상 매출 급감 경보 (위라이크패션 매장만)")
warning_df = compute_eland_warning_stores(df, report_date, WLF_BRAND)
if warning_df.empty:
    st.success("현재 전주 대비 30% 이상 매출 급감 경보 매장이 없습니다.")
else:
    st.dataframe(
        warning_df.sort_values("pct_change").style.format(
            {"current_week_sales": "{:,}", "previous_week_sales": "{:,}", "pct_change": "{:.1f}%"}
        )
    )

st.subheader("2-3. 이랜드리테일 점포별 위라이크패션 누적 매출 순위")
eland_cumulative_rank = compute_eland_store_cumulative_rank(df, report_date, WLF_BRAND)
st.dataframe(eland_cumulative_rank.style.format({"month_to_date_sales": "{:,}"}))

st.markdown("---")

st.subheader("데이터 필터: 이랜드리테일, 위라이크패션 외 브랜드 매출 포함")
st.write("다음 브랜드가 데이터에 포함되어 있어 비교 및 분석이 가능합니다:")
st.write(", ".join(OTHER_BRANDS))

st.caption("실제 데이터가 준비될 경우 data/sample_sales.csv를 동일한 컬럼 구조로 교체하세요.")
