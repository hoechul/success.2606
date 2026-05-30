from datetime import datetime, date, timedelta
import pandas as pd

CHANNELS = [
    "현대아울렛",
    "이랜드리테일",
    "롯데백화점",
    "마리오아울렛",
    "lf몰",
    "세이브존",
    "한국중소기업벤처기업유통원",
    "와이스퀘어",
    "스퀘어원",
    "신세계아울렛",
]

WLF_BRAND = "위라이크패션"
OTHER_BRANDS = [
    "어노이드",
    "더블88",
    "더블jd",
    "리트머스",
    "아크로셀렉트",
    "나인마이너스투",
    "에드호크",
    "프로젝트M",
    "인터크루",
    "행텐",
    "프라임에이트",
    "바인드",
    "마레드",
    "멤버할리데이",
    "그루브라임",
    "라이프워크",
]


def get_default_reporting_date() -> date:
    return date.today() - timedelta(days=1)


def load_sales_data(path: str = "data/sample_sales.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df["channel"] = df["channel"].astype(str)
    df["store"] = df["store"].astype(str)
    df["brand"] = df["brand"].astype(str)
    df["sales_amount"] = pd.to_numeric(df["sales_amount"], errors="coerce").fillna(0)
    return df


def filter_by_brand(df: pd.DataFrame, brand: str) -> pd.DataFrame:
    return df[df["brand"] == brand].copy()


def filter_by_channel(df: pd.DataFrame, channel: str) -> pd.DataFrame:
    return df[df["channel"] == channel].copy()


def filter_by_date(df: pd.DataFrame, target_date: date) -> pd.DataFrame:
    return df[df["date"] == pd.to_datetime(target_date)].copy()


def compute_daily_sales_by_channel(df: pd.DataFrame, target_date: date, brand: str) -> pd.DataFrame:
    daily = filter_by_date(df, target_date)
    daily = filter_by_brand(daily, brand)
    result = (
        daily.groupby("channel", as_index=False)["sales_amount"].sum()
        .rename(columns={"sales_amount": "daily_sales"})
        .sort_values("daily_sales", ascending=False)
    )
    return result


def compute_monthly_cumulative_by_channel(df: pd.DataFrame, target_date: date, brand: str) -> pd.DataFrame:
    df = df[(df["date"].dt.year == target_date.year) & (df["date"].dt.month == target_date.month)]
    df = filter_by_brand(df, brand)
    result = (
        df.groupby("channel", as_index=False)["sales_amount"].sum()
        .rename(columns={"sales_amount": "month_to_date_sales"})
        .sort_values("month_to_date_sales", ascending=False)
    )
    return result


def compute_eland_store_daily_rank(df: pd.DataFrame, target_date: date, brand: str) -> pd.DataFrame:
    daily = filter_by_date(df, target_date)
    daily = filter_by_channel(daily, "이랜드리테일")
    daily = filter_by_brand(daily, brand)
    result = (
        daily.groupby("store", as_index=False)["sales_amount"].sum()
        .rename(columns={"sales_amount": "daily_sales"})
        .sort_values("daily_sales", ascending=False)
    )
    return result


def compute_eland_month_to_date_store_rank(df: pd.DataFrame, target_date: date, brand: str) -> pd.DataFrame:
    month = df[(df["channel"] == "이랜드리테일") & (df["date"].dt.year == target_date.year) & (df["date"].dt.month == target_date.month)]
    month = filter_by_brand(month, brand)
    result = (
        month.groupby("store", as_index=False)["sales_amount"].sum()
        .rename(columns={"sales_amount": "month_to_date_sales"})
        .sort_values("month_to_date_sales", ascending=False)
    )
    return result


def compute_eland_total_daily_wlf(df: pd.DataFrame, target_date: date, brand: str) -> float:
    daily = filter_by_date(df, target_date)
    daily = filter_by_channel(daily, "이랜드리테일")
    daily = filter_by_brand(daily, brand)
    return float(daily["sales_amount"].sum())


def compute_eland_warning_stores(df: pd.DataFrame, target_date: date, brand: str, threshold: float = 0.3) -> pd.DataFrame:
    if target_date < date(2000, 1, 1):
        return pd.DataFrame(columns=["store", "current_week_sales", "previous_week_sales", "pct_change"])

    current_end = pd.to_datetime(target_date)
    current_start = current_end - timedelta(days=6)
    previous_end = current_start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=6)

    current = df[(df["channel"] == "이랜드리테일") & (df["brand"] == brand) & (df["date"] >= current_start) & (df["date"] <= current_end)]
    previous = df[(df["channel"] == "이랜드리테일") & (df["brand"] == brand) & (df["date"] >= previous_start) & (df["date"] <= previous_end)]

    current_sum = current.groupby("store", as_index=False)["sales_amount"].sum().rename(columns={"sales_amount": "current_week_sales"})
    previous_sum = previous.groupby("store", as_index=False)["sales_amount"].sum().rename(columns={"sales_amount": "previous_week_sales"})

    combined = pd.merge(current_sum, previous_sum, on="store", how="left").fillna(0)
    combined["pct_change"] = combined.apply(
        lambda row: ((row.current_week_sales - row.previous_week_sales) / row.previous_week_sales * 100)
        if row.previous_week_sales > 0 else -100.0,
        axis=1,
    )
    warnings = combined[combined["pct_change"] <= -threshold * 100].copy()
    warnings = warnings.sort_values("pct_change")
    return warnings


def compute_eland_store_cumulative_rank(df: pd.DataFrame, target_date: date, brand: str) -> pd.DataFrame:
    return compute_eland_month_to_date_store_rank(df, target_date, brand)


def read_sales_excel(uploaded_file) -> pd.DataFrame:
    """Read Excel in either standard or pivot format."""
    df_raw = pd.read_excel(uploaded_file, sheet_name=0, header=None)

    # Check if it's pivot format (first column should have "점포별" or be empty, then data with channel headers)
    first_col_val = df_raw.iloc[0, 0] if len(df_raw) > 0 else None
    if len(df_raw) >= 3 and (pd.isna(first_col_val) or str(first_col_val).strip() in ["점포별", "유통채널", ""]):
        # Check if row 0 has channel-like values (starting from column 1)
        if any(str(v).strip() in CHANNELS for v in df_raw.iloc[0, 1:]):
            return _parse_pivot_excel(df_raw)

    # Otherwise, parse as standard format
    return _parse_standard_excel(df_raw)


def _parse_standard_excel(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Parse standard format: header row + data rows with date, channel, store, brand, sales_amount columns."""
    df = df_raw.iloc[0:].copy()
    df.columns = df.iloc[0]
    df = df.iloc[1:].copy()
    df.reset_index(drop=True, inplace=True)

    def norm(s: str) -> str:
        return (
            str(s)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

    col_map = {}
    normalized_to_col = {norm(c): c for c in df.columns}

    candidates = {
        "date": ["date", "날짜", "일자", "기준일"],
        "channel": ["channel", "채널", "유통채널", "유통"],
        "store": ["store", "매장", "점포", "지점", "매장명", "점포명"],
        "brand": ["brand", "브랜드", "브랜드명", "상품브랜드"],
        "sales_amount": ["salesamount", "sales", "매출", "매출액", "금액", "amount", "판매금액"],
    }

    for canon, keys in candidates.items():
        found = None
        for k in keys:
            nk = norm(k)
            if nk in normalized_to_col:
                found = normalized_to_col[nk]
                break
        if not found:
            for ncol, orig in normalized_to_col.items():
                for k in keys:
                    if norm(k) in ncol:
                        found = orig
                        break
                if found:
                    break
        if found:
            col_map[canon] = found

    required_columns = {"date", "channel", "store", "brand", "sales_amount"}
    missing = required_columns - set(col_map.keys())
    if missing:
        raise ValueError(f"필수 컬럼 누락: {', '.join(sorted(missing))}")

    df2 = pd.DataFrame()
    df2["date"] = pd.to_datetime(df[col_map["date"]], errors="coerce")
    df2["channel"] = df[col_map["channel"]].astype(str)
    df2["store"] = df[col_map["store"]].astype(str)
    df2["brand"] = df[col_map["brand"]].astype(str)

    raw = df[col_map["sales_amount"]].astype(str)
    cleaned = raw.str.replace(r"[\,\s\₩\$\€\£\(\)]", "", regex=True)
    df2["sales_amount"] = pd.to_numeric(cleaned.str.replace(r"[^0-9\.-]", "", regex=True), errors="coerce").fillna(0)

    df2 = df2.dropna(subset=["date", "channel", "store", "brand"])
    return df2


def _parse_pivot_excel(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Parse pivot format where rows are dates, columns grouped by channel with store/brand sub-headers."""
    # Row 0: channel names  
    # Row 1: store names
    # Row 2: brand names
    # Row 3+: dates and sales data

    records = []

    # Extract header structure
    channel_row = df_raw.iloc[0, 1:]
    store_row = df_raw.iloc[1, 1:]
    brand_row = df_raw.iloc[2, 1:]

    # Data rows start from row 3
    dates_col = df_raw.iloc[3:, 0]

    for idx, date_val in enumerate(dates_col):
        date_parsed = pd.to_datetime(date_val, errors="coerce")
        if pd.isna(date_parsed):
            continue

        # Iterate through data columns (skip first column which is date)
        for col_num in range(1, len(df_raw.columns)):
            channel = str(channel_row.iloc[col_num - 1]).strip()
            store = str(store_row.iloc[col_num - 1]).strip()
            brand = str(brand_row.iloc[col_num - 1]).strip()

            # Validate channel
            if channel not in CHANNELS:
                continue

            # Get sales value
            sales = df_raw.iloc[3 + idx, col_num]
            if pd.isna(sales):
                continue

            # Clean sales amount
            try:
                sales_str = str(sales).replace(",", "").replace("₩", "").strip()
                sales_num = pd.to_numeric(sales_str, errors="coerce")
                if pd.notna(sales_num) and sales_num >= 0:
                    records.append({
                        "date": date_parsed,
                        "channel": channel,
                        "store": store if store else "Unknown",
                        "brand": brand if brand else WLF_BRAND,
                        "sales_amount": float(sales_num),
                    })
            except Exception:
                pass

    if not records:
        raise ValueError("피벗 형식 파싱 실패: 유효한 데이터를 찾을 수 없습니다.")

    result = pd.DataFrame(records)
    result = result.dropna(subset=["date", "channel", "store", "brand"])
    return result


def merge_sales_data(base_df: pd.DataFrame, uploaded_df: pd.DataFrame) -> pd.DataFrame:
    merged = pd.concat([base_df, uploaded_df], ignore_index=True)
    merged = (
        merged.groupby(["date", "channel", "store", "brand"], as_index=False, sort=False)["sales_amount"]
        .sum()
    )
    return merged
