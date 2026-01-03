# AI Civilization Atlas - 배포 가이드

## 배포 구조

| 구성요소 | 플랫폼 | URL |
|---------|--------|-----|
| 프론트엔드 | Cloudflare Pages | https://ai-atlas.tgsystem.kr |
| API | AWS Lambda | https://0gqxz2ps31.execute-api.ap-northeast-2.amazonaws.com/prod/v1/gendao/aiatlas |
| 데이터베이스 | DynamoDB | aiatlas_admin_config, aiatlas_events, aiatlas_roadmaps |

## Lambda 배포

Lambda는 GENDAO_AWS_API 스택에 통합되어 있습니다.

```bash
cd "D:\python_projects\genesis token\GENDAO_AWS_API"

# 빌드
sam build

# 배포
sam deploy --stack-name gendao-hq --resolve-s3 --no-confirm-changeset --capabilities CAPABILITY_IAM
```

## Cloudflare Pages 배포

### Git Bash / Linux / Mac
```bash
cd "D:\python_projects\ai-atlas"

# 배포 (환경변수 사용)
CLOUDFLARE_API_TOKEN=Vsv8uuJjo_T72ABmHNssD4BPOXBR-2PmG-hTB8jn npx wrangler pages deploy ./dist --project-name=ai-atlas --branch=main --commit-dirty=true
```

### PowerShell
```powershell
$env:CLOUDFLARE_API_TOKEN="Vsv8uuJjo_T72ABmHNssD4BPOXBR-2PmG-hTB8jn"
npx wrangler pages deploy ./dist --project-name=ai-atlas --branch=main --commit-dirty=true
```

### CMD
```cmd
set CLOUDFLARE_API_TOKEN=Vsv8uuJjo_T72ABmHNssD4BPOXBR-2PmG-hTB8jn
npx wrangler pages deploy ./dist --project-name=ai-atlas --branch=main --commit-dirty=true
```

## Cloudflare Pages 프로젝트 생성 (최초 1회)

```bash
# Wrangler 로그인
npx wrangler login

# 프로젝트 생성
npx wrangler pages project create ai-atlas --production-branch=main
```

## 커스텀 도메인 연결

Cloudflare 대시보드에서:
1. Pages > ai-atlas 프로젝트 선택
2. Custom domains > Add custom domain
3. `ai-atlas.tgsystem.kr` 입력
4. DNS 레코드 자동 생성 확인

## 배포 확인

```bash
# API 헬스체크
curl https://0gqxz2ps31.execute-api.ap-northeast-2.amazonaws.com/prod/v1/gendao/aiatlas/health

# 사이트 확인
curl -I https://ai-atlas.tgsystem.kr
```

## 캐시 퍼지 (배포 후 반영 안 될 때)

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/1cdf0e3e2abe06a56083a262c67770b4/purge_cache" \
  -H "Authorization: Bearer Vsv8uuJjo_T72ABmHNssD4BPOXBR-2PmG-hTB8jn" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

## 환경변수

Lambda에 필요한 환경변수:
- `AIATLAS_ADMIN_PASSWORD`: 관리자 비밀번호 (기본값: aiatlas2026)
- `ANTHROPIC_API_KEY`: Claude API 키 (콘텐츠 생성용)

AWS 콘솔 또는 SAM template.yaml에서 설정.

## 스케줄 Lambda 설정 (예정)

콘텐츠 자동 업데이트를 위한 EventBridge 규칙:

```yaml
# template.yaml에 추가
AIAtlasSchedule:
  Type: AWS::Events::Rule
  Properties:
    ScheduleExpression: "cron(0 0 * * ? *)"  # 매일 자정 (UTC)
    Targets:
      - Id: AIAtlasUpdater
        Arn: !GetAtt GendaoHqApiFunction.Arn
        Input: '{"path": "/v1/gendao/aiatlas/update", "httpMethod": "POST"}'
```

## 롤백

문제 발생 시:

1. **Lambda**: AWS 콘솔에서 이전 버전으로 롤백
2. **Cloudflare Pages**: 대시보드에서 이전 배포 선택 후 "Rollback"

## 모니터링

- **AWS CloudWatch**: Lambda 로그
- **Cloudflare Analytics**: 페이지 방문 통계

## 주의사항

- **프로젝트명**: `ai-atlas` (ai-civilization-atlas 아님!)
- **Production 브랜치**: `main` (master 아님!)
- GitHub 연동 배포가 아님 - Wrangler CLI로 직접 배포
