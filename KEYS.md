# AI Civilization Atlas - API 키 및 인증 정보

## 관리자 접속

| 항목 | 값 |
|------|-----|
| URL | https://ai-atlas.tgsystem.kr/admin |
| 비밀번호 | `aiatlas2026` |

## AWS

| 항목 | 값 |
|------|-----|
| Region | ap-northeast-2 (서울) |
| Stack Name | gendao-hq |
| API Gateway | 0gqxz2ps31.execute-api.ap-northeast-2.amazonaws.com |

### DynamoDB 테이블
- `aiatlas_admin_config`
- `aiatlas_events`
- `aiatlas_roadmaps`

## Cloudflare

| 항목 | 값 |
|------|-----|
| Account ID | 2d2d412262fa63c0c327c0352f25f60c |
| Zone (tgsystem.kr) | 1cdf0e3e2abe06a56083a262c67770b4 |
| Pages Project | ai-atlas |

### API 토큰
```
CLOUDFLARE_API_TOKEN=Vsv8uuJjo_T72ABmHNssD4BPOXBR-2PmG-hTB8jn
```

## 외부 API (콘텐츠 생성용)

### Claude API (Anthropic)
- 환경변수: `ANTHROPIC_API_KEY`
- Lambda 환경변수로 설정 필요

### 이미지 API (저작권 프리)
| 서비스 | API 문서 |
|--------|----------|
| Unsplash | https://unsplash.com/developers |
| Pexels | https://www.pexels.com/api/ |
| Pixabay | https://pixabay.com/api/docs/ |

## API 엔드포인트

### 공개 (인증 불필요)
```
GET /v1/gendao/aiatlas/health
GET /v1/gendao/aiatlas/events/public
GET /v1/gendao/aiatlas/timeline
GET /v1/gendao/aiatlas/roadmaps
GET /v1/gendao/aiatlas/irreversibles
```

### 관리자 (Bearer 토큰 필요)
```
POST /v1/gendao/aiatlas/auth/login
GET  /v1/gendao/aiatlas/config
PUT  /v1/gendao/aiatlas/config
GET  /v1/gendao/aiatlas/events
POST /v1/gendao/aiatlas/events
GET  /v1/gendao/aiatlas/status
```

## 토큰 생성 방식

로그인 시 비밀번호를 SHA256 해시하여 앞 32자를 토큰으로 사용:

```python
import hashlib
token = hashlib.sha256(password.encode()).hexdigest()[:32]
```

## GitHub

| 항목 | 값 |
|------|-----|
| Repository | https://github.com/hansongjong/ai-atlas |
| 배포 방식 | Wrangler CLI (GitHub Actions 아님) |
