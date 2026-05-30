from datetime import datetime
from typing import Optional
from io import BytesIO
from fastapi import FastAPI, Query, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from sales_data import (
    load_sales_data,
    get_default_reporting_date,
    WLF_BRAND,
    OTHER_BRANDS,
    compute_daily_sales_by_channel,
    compute_monthly_cumulative_by_channel,
    compute_eland_store_daily_rank,
    compute_eland_total_daily_wlf,
    compute_eland_warning_stores,
    compute_eland_store_cumulative_rank,
    read_sales_excel,
    merge_sales_data,
)

app = FastAPI(title="위라이크패션 매출 대시보드")


def format_table(df):
    if df.empty:
        return "<p>데이터가 없습니다.</p>"
    return df.to_html(classes="table table-striped table-bordered", index=False, justify="left")


def render_page(target_date, df, message_html=""):
    channel_daily = compute_daily_sales_by_channel(df, target_date, WLF_BRAND)
    channel_monthly = compute_monthly_cumulative_by_channel(df, target_date, WLF_BRAND)
    eland_store_rank = compute_eland_store_daily_rank(df, target_date, WLF_BRAND)
    eland_total = compute_eland_total_daily_wlf(df, target_date, WLF_BRAND)
    warnings = compute_eland_warning_stores(df, target_date, WLF_BRAND)
    eland_cumulative = compute_eland_store_cumulative_rank(df, target_date, WLF_BRAND)

    # Calculate summary metrics
    channel_count = len(channel_daily)
    store_count = len(eland_store_rank)
    channel_month_total = channel_monthly["month_to_date_sales"].sum()

    # Format numbers for display
    eland_total_fmt = f"{eland_total:,.0f}"
    channel_month_total_fmt = f"{channel_month_total:,.0f}"

    # Create styled tables with formatting
    def format_sales_table(df, sale_col):
        """Format table with right-aligned and comma-separated sales"""
        if df.empty:
            return "<p>데이터가 없습니다.</p>"
        df_copy = df.copy()
        if sale_col in df_copy.columns:
            df_copy[sale_col] = df_copy[sale_col].apply(lambda x: f"{x:,.0f}")
        return df_copy.to_html(classes="data-table", index=False, justify="left", border=0)

    eland_store_html = format_sales_table(eland_store_rank, "daily_sales")
    channel_monthly_html = format_sales_table(channel_monthly, "month_to_date_sales")
    channel_daily_html = format_sales_table(channel_daily, "daily_sales")
    eland_cumulative_html = format_sales_table(eland_cumulative, "cumulative_sales")
    warnings_html = format_table(warnings) if not warnings.empty else "<p style='color:#888;'>⚠️ 경보 대상 매장 없음</p>"

    html = f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <title>위라이크패션 매출 대시보드</title>
        <style>
          * {{ margin: 0; padding: 0; box-sizing: border-box; }}
          body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif; background: #f0f2f5; color: #1f1f1f; }}
          .dashboard {{ max-width: 1400px; margin: 0 auto; padding: 24px 16px; }}
          
          /* Header */
          .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); color: white; padding: 32px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
          .header h1 {{ font-size: 28px; margin-bottom: 8px; font-weight: 600; }}
          .header-meta {{ display: flex; justify-content: space-between; align-items: center; margin-top: 16px; }}
          .header-date {{ font-size: 14px; opacity: 0.9; }}
          
          /* Upload Form */
          .uploader {{ background: #f8f9fa; padding: 16px 20px; border-radius: 8px; border-left: 4px solid #1e40af; margin-bottom: 24px; display: flex; gap: 12px; align-items: center; }}
          .uploader label {{ font-weight: 500; font-size: 14px; }}
          .uploader input[type=file] {{ padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 13px; flex: 1; max-width: 300px; }}
          .uploader button {{ background: #1e40af; color: white; border: none; padding: 8px 24px; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 14px; transition: background 0.2s; }}
          .uploader button:hover {{ background: #1e3a8a; }}
          
          /* Messages */
          .message {{ padding: 12px 16px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }}
          .message.success {{ background: #d1fae5; color: #065f46; border-left: 4px solid #10b981; }}
          .message.error {{ background: #fee2e2; color: #991b1b; border-left: 4px solid #ef4444; }}
          
          /* KPI Cards */
          .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 28px; }}
          .kpi-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-top: 4px solid #1e40af; }}
          .kpi-card.accent1 {{ border-top-color: #10b981; }}
          .kpi-card.accent2 {{ border-top-color: #f59e0b; }}
          .kpi-card.accent3 {{ border-top-color: #ef4444; }}
          .kpi-label {{ font-size: 12px; color: #6b7280; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
          .kpi-value {{ font-size: 26px; font-weight: 700; color: #1f1f1f; margin-bottom: 4px; }}
          .kpi-value.accent1 {{ color: #10b981; }}
          .kpi-value.accent2 {{ color: #f59e0b; }}
          .kpi-value.accent3 {{ color: #ef4444; }}
          .kpi-unit {{ font-size: 12px; color: #9ca3af; }}
          
          /* Section */
          .section {{ margin-bottom: 28px; }}
          .section-title {{ font-size: 18px; font-weight: 600; color: #1f1f1f; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid #e5e7eb; }}
          .section-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; }}
          .section-grid.full {{ grid-template-columns: 1fr; }}
          
          /* Tables */
          .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); overflow: auto; }}
          .data-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
          .data-table th {{ background: #f3f4f6; padding: 12px; text-align: left; font-weight: 600; color: #374151; border-bottom: 2px solid #e5e7eb; }}
          .data-table td {{ padding: 12px; border-bottom: 1px solid #e5e7eb; }}
          .data-table tbody tr:hover {{ background: #f9fafb; }}
          .data-table td:last-child, .data-table th:last-child {{ text-align: right; }}
          
          /* Warning Alert */
          .warning-alert {{ background: #fff8e1; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 8px; margin-top: 12px; }}
          .warning-alert p {{ color: #92400e; margin: 0; }}
          
          /* Footer */
          .footer {{ text-align: center; font-size: 12px; color: #9ca3af; margin-top: 32px; padding-top: 16px; border-top: 1px solid #e5e7eb; }}
          
          @media (max-width: 768px) {{
            .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .section-grid {{ grid-template-columns: 1fr; }}
            .header h1 {{ font-size: 22px; }}
            .header-meta {{ flex-direction: column; align-items: flex-start; gap: 12px; }}
          }}
        </style>
      </head>
      <body>
        <div class="dashboard">
          <!-- Header -->
          <div class="header">
            <h1>📊 위라이크패션 매출 대시보드</h1>
            <div class="header-meta">
              <div class="header-date">기준일: <strong>{target_date.isoformat()}</strong></div>
              <form action="/upload" method="post" enctype="multipart/form-data" style="display: flex; gap: 8px; align-items: center;">
                <input type="file" name="file" accept=".xls,.xlsx" required style="color: white; font-size: 12px;" />
                <input type="hidden" name="report_date" value="{target_date.isoformat()}" />
                <button type="submit" style="background: white; color: #1e40af; padding: 6px 16px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 12px;">업로드</button>
              </form>
            </div>
          </div>
          
          <!-- Message -->
          {message_html}
          
          <!-- KPI Cards -->
          <div class="kpi-grid">
            <div class="kpi-card">
              <div class="kpi-label">이랜드 어제 매출</div>
              <div class="kpi-value accent1">{eland_total_fmt}</div>
              <div class="kpi-unit">위라이크패션</div>
            </div>
            <div class="kpi-card accent1">
              <div class="kpi-label">월누적 매출</div>
              <div class="kpi-value accent1">{channel_month_total_fmt}</div>
              <div class="kpi-unit">전체 채널</div>
            </div>
            <div class="kpi-card accent2">
              <div class="kpi-label">활성 채널</div>
              <div class="kpi-value accent2">{channel_count}</div>
              <div class="kpi-unit">개 채널</div>
            </div>
            <div class="kpi-card accent2">
              <div class="kpi-label">이랜드 점포</div>
              <div class="kpi-value accent2">{store_count}</div>
              <div class="kpi-unit">개 점포</div>
            </div>
          </div>
          
          <!-- 이랜드리테일 섹션 -->
          <div class="section">
            <div class="section-title">🏪 이랜드리테일 - 어제 점포별 매출 현황</div>
            <div class="section-grid full">
              <div class="card">
                {eland_store_html}
              </div>
            </div>
          </div>
          
          <!-- 채널별 분석 섹션 -->
          <div class="section">
            <div class="section-title">📈 채널 분석</div>
            <div class="section-grid">
              <div class="card">
                <h3 style="font-size: 14px; color: #374151; margin-bottom: 12px; font-weight: 600;">월누적 매출 순위</h3>
                {channel_monthly_html}
              </div>
              <div class="card">
                <h3 style="font-size: 14px; color: #374151; margin-bottom: 12px; font-weight: 600;">어제 매출 현황</h3>
                {channel_daily_html}
              </div>
            </div>
          </div>
          
          <!-- 경보 섹션 -->
          <div class="section">
            <div class="section-title">⚠️ 주의 - 매출 급감 경보</div>
            <div class="section-grid full">
              <div class="card">
                {warnings_html}
              </div>
            </div>
          </div>
          
          <!-- 누적 순위 섹션 -->
          <div class="section">
            <div class="section-title">📊 이랜드리테일 - 월누적 점포 순위</div>
            <div class="section-grid full">
              <div class="card">
                {eland_cumulative_html}
              </div>
            </div>
          </div>
          
          <!-- Footer -->
          <div class="footer">
            <p>매출 기준: 위라이크패션 | 참고 브랜드: {', '.join(OTHER_BRANDS)}</p>
          </div>
        </div>
      </body>
    </html>
    """
    return html


@app.get("/", response_class=HTMLResponse)
async def dashboard(report_date: Optional[str] = Query(None, description="기준일 YYYY-MM-DD")):
    try:
        target_date = datetime.strptime(report_date, "%Y-%m-%d").date() if report_date else get_default_reporting_date()
    except ValueError:
        target_date = get_default_reporting_date()

    df = load_sales_data()
    return HTMLResponse(render_page(target_date, df))


@app.post("/upload", response_class=HTMLResponse)
async def upload_file(file: UploadFile = File(...), report_date: Optional[str] = Form(None)):
    try:
        target_date = datetime.strptime(report_date, "%Y-%m-%d").date() if report_date else get_default_reporting_date()
    except Exception:
        target_date = get_default_reporting_date()

    base_df = load_sales_data()
    try:
        content = await file.read()
        uploaded_df = read_sales_excel(BytesIO(content))
        merged = merge_sales_data(base_df, uploaded_df)
        # Try to persist merged data to disk for subsequent requests
        try:
          merged.to_csv('data/sample_sales.csv', index=False)
        except Exception as e:
          # Ignore file system errors (expected in serverless environment)
          pass

        message = (
          f"<div class='message success'>✅ <strong>업로드 성공!</strong> {file.filename} ({len(uploaded_df):,}개 행) - 데이터가 대시보드에 반영되었습니다.</div>"
        )
        return HTMLResponse(render_page(target_date, merged, message_html=message))
    except Exception as exc:
        message = f"<div class='message error'>❌ <strong>업로드 실패:</strong> {exc}</div>"
        return HTMLResponse(render_page(target_date, base_df, message_html=message))
