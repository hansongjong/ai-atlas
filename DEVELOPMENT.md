# AI Civilization Atlas - 개발 가이드

## 로컬 개발 환경

### 요구사항
- Python 3.10+
- Node.js 18+ (Wrangler CLI용)
- AWS CLI (설정 완료)

### 설치

```bash
# Python 의존성 (Lambda용)
pip install boto3 anthropic feedparser

# Wrangler CLI
npm install -g wrangler
```

## 프로젝트 구조

### Lambda 핸들러
위치: `D:\python_projects\genesis token\GENDAO_AWS_API\handlers\aiatlas_handler.py`

통합된 GENDAO_AWS_API 스택에 포함되어 있음.

### API 엔드포인트

| 엔드포인트 | 메서드 | 인증 | 설명 |
|-----------|--------|------|------|
| `/aiatlas/health` | GET | 없음 | 헬스체크 |
| `/aiatlas/auth/login` | POST | 없음 | 로그인 |
| `/aiatlas/config` | GET | 필요 | 설정 조회 |
| `/aiatlas/config` | PUT | 필요 | 설정 수정 |
| `/aiatlas/events/public` | GET | 없음 | 공개 이벤트 목록 |
| `/aiatlas/events` | GET | 필요 | 전체 이벤트 목록 |
| `/aiatlas/timeline` | GET | 없음 | AI 문명 타임라인 |
| `/aiatlas/roadmaps` | GET | 없음 | 기술 로드맵 |
| `/aiatlas/irreversibles` | GET | 없음 | 되돌릴 수 없는 선택들 |
| `/aiatlas/status` | GET | 필요 | 시스템 상태 |

### DynamoDB 테이블

1. **aiatlas_admin_config**
   - PK: `ADMIN_CONFIG` (단일 row)
   - 로드맵, 설정, 게시 정책 저장

2. **aiatlas_events**
   - PK: `EVENT#YYYY-MM-DD`
   - SK: `TIMELINE#slug`
   - 문명 이벤트 저장

3. **aiatlas_roadmaps**
   - PK: `ROADMAP#category`
   - SK: `VERSION#timestamp`
   - 기술 로드맵 저장

## 이벤트 데이터 모델

### 이벤트 스키마 (고정)

```javascript
Event {
  title: string,
  date: string,           // YYYY-MM-DD 또는 YYYY
  period: string,         // optional, 기간 표시
  category: enum,         // Civilization | Science | Industry | Governance
  what_changed: string,
  why_it_matters: string,
  what_became_possible: string,
  next_transition_condition: string
}
```

### 카테고리
- **Civilization**: 문명적 관점 (AI as historical event)
- **Science**: 과학적 관점 (hardware & software evolution)
- **Industry**: 산업/경제적 관점 (governance, labor, production)
- **Governance**: 거버넌스 변화

## 기술 로드맵

### A. LLM & Agent Roadmap
Model → Reasoning → Agent → Civilization OS

### B. AI Compute Roadmap
GPU / TPU / AI Accelerators, 제조, 패키징, 공급망, 에너지

### C. Memory Evolution Roadmap
HBM, CXL, NVM, optical memory

### D. Energy Roadmap
Nuclear, fusion, distributed energy

### E. Physical AI & Robotics Roadmap
AI-Robot labor replacement, 생산 독점 형성

## 콘텐츠 생성 로직

### 1. 뉴스 소스 수집
- RSS 피드 파싱 (feedparser)
- 웹 스크래핑 (필요시)
- `config/news_sources.json` 참조

### 2. AI 이벤트 분석
Claude API 사용. 프롬프트:

```
You are the analysis AI of AI Civilization Atlas.
You analyze AI developments from four perspectives:
- Civilizational (AI as a historical event)
- Scientific (hardware & software evolution)
- Industrial & economic (governance, labor, production)
- Builder (founders, researchers, AI users)

Extract structured events, not opinions.
```

### 3. 중요도 판단
- importance_score: 0~1
- 0.6 미만: 게시 안 함 (설정에 따라)

## 코드 수정 시

1. `aiatlas_handler.py` 수정
2. SAM 빌드 및 배포:
   ```bash
   cd "D:\python_projects\genesis token\GENDAO_AWS_API"
   sam build
   sam deploy --stack-name gendao-hq --resolve-s3 --no-confirm-changeset --capabilities CAPABILITY_IAM
   ```

3. 프론트엔드 수정 시:
   ```bash
   cd "D:\python_projects\ai-atlas"
   npx wrangler pages deploy ./dist --project-name=ai-atlas --branch=main --commit-dirty=true
   ```

## 페이지 구조

### 핵심 페이지 (9개)

1. **Home (Declaration Page)**
   - 프로젝트 선언문
   - 핵심 가설 표시

2. **Current Turning Points**
   - 2026년 전환점 테시스
   - 현재 진행 중인 변화

3. **AI Civilization Timeline**
   - 이벤트 기반 타임라인
   - 카테고리별 필터링

4. **Technology Roadmaps**
   - 5개 독립적 로드맵
   - 상호 수렴 포인트 표시

5. **Models & Agents Index**
   - 모델 버전 추적
   - 능력 통합 중심 (벤치마크 아님)

6. **Industry & Governance Shift**
   - 거버넌스 변화 도식
   - 산업 구조 변화

7. **Builder & Researcher Guide**
   - 경쟁하지 말아야 할 곳
   - 레버리지 구축 포인트

8. **100-Year Outlook**
   - 시나리오 매트릭스 (4개)
   - 5개 조건부 에포크

9. **Irreversible Choices Archive**
   - 되돌릴 수 없는 결정들
   - Why/Who/What 분석

## UI 원칙

- 다크 테마
- 고대비 타이포그래피
- 중앙 집중 히어로 선언
- 카드 기반 정보 블록
- 스크롤 기반 내러티브 흐름
- 문명 제어실 느낌
- 최소 장식, 최대 의미
- 텍스트 우선, 다이어그램 보조
