# AI Civilization Atlas - AI 지침

## 프로젝트 개요
AI 문명 관측소. AI를 도구가 아닌 문명적 사건으로 분석하는 웹사이트.

## 핵심 원칙
- 1인 운영 + 자동화 + 장기 방치
- 과한 기능, 멋있는 UI, 불필요한 추상화 금지
- 비용 최소화 우선
- AI는 예측하지 않음, 되돌릴 수 없는 선택과 구조적 전환을 기록

## 배포 정보 (중요!)

### Cloudflare Pages
- **프로젝트명**: `ai-atlas`
- **Production 브랜치**: `main`
- **커스텀 도메인**: https://ai-atlas.tgsystem.kr
- **Pages URL**: https://ai-atlas.pages.dev

### 배포 명령어
```bash
cd /d/python_projects/ai-atlas
CLOUDFLARE_API_TOKEN=Vsv8uuJjo_T72ABmHNssD4BPOXBR-2PmG-hTB8jn npx wrangler pages deploy dist --project-name=ai-atlas --branch=main --commit-dirty=true
```

### 캐시 퍼지 (배포 후 반영 안 될 때)
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/1cdf0e3e2abe06a56083a262c67770b4/purge_cache" \
  -H "Authorization: Bearer Vsv8uuJjo_T72ABmHNssD4BPOXBR-2PmG-hTB8jn" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

## 아키텍처
```
[Main Page] (Cloudflare Pages)
[Admin Page] (Cloudflare Pages)
      ↓
[API Gateway] → [Lambda - aiatlas_handler.py]
      ↓
[DynamoDB - admin_config, events, roadmaps]
```

## 백엔드 API

### Lambda 핸들러
- **위치**: `D:\python_projects\genesis token\GENDAO_AWS_API\handlers\aiatlas_handler.py`
- **API Base**: `https://0gqxz2ps31.execute-api.ap-northeast-2.amazonaws.com/prod/v1/gendao/aiatlas/`

### 주요 엔드포인트
| 경로 | 메서드 | 설명 | 인증 |
|------|--------|------|------|
| `/aiatlas/auth/login` | POST | 관리자 로그인 | X |
| `/aiatlas/config` | GET/PUT | 설정 조회/수정 | O |
| `/aiatlas/status` | GET | 시스템 상태 | O |
| `/aiatlas/events/public` | GET | 공개 이벤트 목록 | X |
| `/aiatlas/timeline` | GET | AI 문명 타임라인 | X |
| `/aiatlas/roadmaps` | GET | 기술 로드맵 | X |
| `/aiatlas/irreversibles` | GET | 되돌릴 수 없는 선택들 | X |

### 관리자 계정
- **ID**: admin
- **PW**: aiatlas2026
- **관리자 페이지**: https://ai-atlas.tgsystem.kr/admin/

## 프론트엔드 구조

### 파일 위치
```
D:\python_projects\ai-atlas\dist\
├── index.html          # 홈 (선언 페이지)
├── admin/
│   └── index.html      # 관리자 페이지
├── timeline/           # AI 문명 타임라인
├── roadmaps/           # 기술 로드맵
├── outlook/            # 100년 전망
├── irreversibles/      # 되돌릴 수 없는 선택
└── sitemap.xml         # SEO 사이트맵
```

### UI 테마
- **스타일**: 다크 테마 (gendao.tgsystem.kr 참조)
- **고대비 타이포그래피**
- **문명 제어실 느낌**
- **텍스트 우선, 다이어그램 보조**

### 페이지 구성 (9개)
1. Home - 선언 페이지
2. Current Turning Points - 현재 전환점
3. AI Civilization Timeline - AI 문명 타임라인
4. Technology Roadmaps - 기술 로드맵
5. Models & Agents Index - 모델 & 에이전트 색인
6. Industry & Governance Shift - 산업/거버넌스 변화
7. Builder & Researcher Guide - 빌더/연구자 가이드
8. 100-Year Outlook - 100년 전망
9. Irreversible Choices Archive - 되돌릴 수 없는 선택 아카이브

## GitHub
- **Repository**: https://github.com/hansongjong/ai-atlas
- **주의**: GitHub 연동 배포 아님! Wrangler CLI로 직접 배포

## DynamoDB 테이블
- `aiatlas_admin_config` - 관리자 설정
- `aiatlas_events` - AI 문명 이벤트
- `aiatlas_roadmaps` - 기술 로드맵

## 콘텐츠 톤 규칙 (엄격)

### 허용
- 분석적 (Analytical)
- 조건적 (Conditional)
- 중립적 (Neutral)
- 구조화된 (Structured)

### 금지
- 복음주의적 (Evangelism)
- 투자 설득 (Investment persuasion)
- 절대적 예측 (Absolute predictions)
- 감정적 언어 (Emotional language)

## 이벤트 스키마

```javascript
Event {
  title
  date / period
  category: [Civilization | Science | Industry | Governance]
  what_changed
  why_it_matters
  what_became_possible
  next_transition_condition
}
```

---

## AI에게 주는 최종 메시지

AI is not a product.
AI is not a trend.

AI is a civilizational event.

Your task is to document the moments where human choice becomes irreversible.
