# 테라스타(Terrastar) · KT 공식 인증 대리점 랜딩 페이지

하루 10명 신규가입/번호이동 상담 전환을 목표로 한 단일 페이지(One-page) 랜딩입니다.
정적 HTML 한 파일이라 **빌드 없이 Vercel에 바로 배포**됩니다.

```
terrastar/
├─ index.html     # 랜딩 페이지 본체 (CSS/JS 인라인, 의존성 없음)
├─ vercel.json    # Vercel 정적 배포 설정 (cleanUrls + 보안 헤더)
└─ README.md      # 이 문서
```

---

## 1. 배포 전에 바꿔야 할 3가지 (필수)

`index.html`을 열어서 아래 3곳만 본인 매장 값으로 바꾸면 됩니다.

### ① 전화번호
파일 전체에서 `0000000000`(tel 링크용)과 `0000-0000`(표시용)을 찾아 매장 번호로 변경하세요.

- 에디터에서 **찾기·바꾸기**:
  - `tel:0000000000` → `tel:021234567` (지역번호·숫자만, 하이픈 없이)
  - `0000-0000` → `02-1234-5678` (화면 표시용, 하이픈 포함)

### ② 구글폼 임베드 (상담 신청 폼)
1. 구글폼 작성 (추천 항목: **이름 / 연락처 / 가입유형(신규·번호이동) / 관심 단말 / 희망 요금제 / 개인정보 수집·이용 동의**)
2. 구글폼 우측 상단 **보내기 → `< >`(임베드 HTML)** 클릭
3. 나오는 `<iframe src="https://docs.google.com/forms/d/e/.../viewform?embedded=true" ...>` 에서 **`src` 값만 복사**
4. `index.html`의 `id="leadForm"` iframe 에서 `src=""` → 복사한 주소를 붙여넣기

```html
<iframe id="leadForm"
  src="https://docs.google.com/forms/d/e/FORM_ID/viewform?embedded=true"
  ...>
```

> `src`가 채워지면 폼이 자동 표시되고, 비어 있으면 "전화/카카오로 상담" 대체 박스가 보입니다.
> 폼 높이(`min-height:1100px`)는 항목 수에 맞게 `index.html` `.form-wrap iframe` 에서 조절하세요.

### ③ 카카오 채널 (선택)
`https://pf.kakao.com/` (data-kakao 표시) 를 본인 카카오톡 채널 주소로 바꾸세요. 미사용 시 해당 버튼을 삭제해도 됩니다.

추가로 푸터의 **사업자 정보**(상호·대표자·사업자등록번호·주소·영업시간)도 실제 값으로 채워주세요. (전자상거래/단통법 표시 의무)

---

## 2. Vercel 배포 (새 저장소 권장)

이 폴더는 기존 RPA 저장소와 무관한 독립 사이트입니다. 랜딩 전용 새 저장소로 분리해 배포하는 것을 권장합니다.

### 방법 A — GitHub 새 저장소 + Vercel 연결 (권장)
```bash
# terrastar 폴더 내용만 새 저장소로
mkdir kt-terrastar-landing && cp terrastar/* kt-terrastar-landing/
cd kt-terrastar-landing
git init && git add . && git commit -m "init: KT 테라스타 랜딩"
# GitHub에 빈 저장소 생성 후
git remote add origin https://github.com/<you>/kt-terrastar-landing.git
git push -u origin main
```
→ [vercel.com](https://vercel.com) → **Add New → Project** → 해당 저장소 Import → 별도 설정 없이 **Deploy**.
(Framework Preset은 자동으로 "Other/Static"으로 잡힙니다.)

### 방법 B — Vercel CLI로 이 폴더만 즉시 배포
```bash
npm i -g vercel
cd terrastar
vercel        # 미리보기 배포
vercel --prod # 운영 배포
```

배포 후 받은 `*.vercel.app` 주소를 카카오/문자/전단지 QR로 뿌리면 됩니다.
커스텀 도메인은 Vercel 프로젝트 → Settings → Domains 에서 연결하세요.

---

## 3. 전환율(하루 10명)을 끌어올리는 운영 팁
- **유입은 폼으로 모으기**: 광고/카톡 메시지의 링크는 `#apply` 로 바로 보내세요. 예) `https.../#apply`
- **응답 속도가 전환을 좌우**: 구글폼 응답에 **이메일 알림**을 켜두고(스프레드시트 → 도구 → 알림 규칙), 신청 즉시 전화하세요.
- **A/B로 헤드라인 테스트**: 히어로 `h1` 문구·혜택 금액을 주 단위로 바꿔 클릭/신청률 비교.
- **광고 추적**: GA4나 Meta 픽셀 스니펫을 `</head>` 직전에 추가하면 캠페인별 전환을 측정할 수 있습니다.

---

## 4. 표시 책임 안내(중요)
혜택 금액(공시지원금·추가지원금·사은품 등)은 **단통법** 및 KT 정책 범위 내에서만 표기하세요.
추가지원금은 공시지원금의 **15% 이내**입니다. 과장·확정 표현은 피하고 "단말·요금제별 상이, 상담 시 안내"를 유지하는 것이 안전합니다. 현재 문구는 이를 반영해 작성돼 있습니다.
