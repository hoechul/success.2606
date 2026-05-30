# 위라이크패션 매출 대시보드

이 프로젝트는 위라이크패션 기준의 오프라인 유통 채널별 매출 대시보드를 Streamlit으로 구현한 템플릿입니다.

## 주요 기능

- 오프라인 유통 채널별 일매출 및 월누적 매출 순위
- 이랜드리테일 기준 점포별 위라이크패션 일매출 순위
- 이랜드리테일 위라이크패션 일간 총매출 및 매장별 누적 매출 순위
- 전주 대비 30% 이상 매출 급감 경보 (위라이크패션 매장만)
- 기준일 자동 `D-1` 설정 (컴퓨터 시간 기준)

## 설치

```powershell
python -m pip install -r requirements.txt
```

## 실행

```powershell
streamlit run app.py
```

## Vercel 배포 준비

1. Vercel CLI 설치 및 로그인

```powershell
npm install -g vercel
vercel login
```

2. 프로젝트 루트에서 배포

```powershell
vercel
```

3. 배포 후 생성된 URL로 접속

```powershell
vercel open
```

> Vercel 경로는 `api/index.py`로 설정되어 있어, 배포 후 웹에서 위라이크패션 매출 대시보드를 확인할 수 있습니다.

## 데이터 형식

기본 데이터 파일: `data/sample_sales.csv`

파일 업로드:

- 대시보드 상단 우측에서 `xls`, `xlsx` 파일을 업로드할 수 있습니다.
- 업로드된 엑셀 파일은 기존 데이터와 병합되어 대시보드에 즉시 반영됩니다.

필요한 컬럼:

- `date` (YYYY-MM-DD)
- `channel`
- `store`
- `brand`
- `sales_amount`

## 유통 채널 목록

- 현대아울렛
- 이랜드리테일
- 롯데백화점
- 마리오아울렛
- lf몰
- 세이브존
- 한국중소기업벤처기업유통원
- 와이스퀘어
- 스퀘어원
- 신세계아울렛

## 브랜드 목록

- 위라이크패션 (기준 브랜드)
- 어노이드
- 더블88
- 더블jd
- 리트머스
- 아크로셀렉트
- 나인마이너스투
- 에드호크
- 프로젝트M
- 인터크루
- 행텐
- 프라임에이트
- 바인드
- 마레드
- 멤버할리데이
- 그루브라임
- 라이프워크
