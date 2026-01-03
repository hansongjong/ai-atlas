# AI Civilization Atlas - 배포 가이드

## 배포 구조

| 구성요소 | 플랫폼 | URL |
|---------|--------|-----|
| 프론트엔드 | Cloudflare Pages (GitHub 연동) | https://ai-atlas.tgsystem.kr |
| API | AWS Lambda | https://0gqxz2ps31.execute-api.ap-northeast-2.amazonaws.com/prod/v1/gendao/aiatlas |
| 데이터베이스 | DynamoDB | aiatlas_admin_config, aiatlas_events, aiatlas_roadmaps |

## GitHub 자동 배포 (Cloudflare Pages 연동)

### 배포 방식
GitHub `main` 브랜치에 push하면 Cloudflare Pages가 자동으로 배포합니다.

### GitHub 저장소
- **Repository**: https://github.com/hansongjong/ai-atlas
- **Production Branch**: `main`
- **Build Output**: `dist/`

### 배포 명령어
```bash
cd "D:\python_projects\ai-atlas"

# 변경사항 커밋 및 푸시 (자동 배포 트리거)
git add .
git commit -m "Update: 변경 내용"
git push origin main
```

### 배포 확인
- **Cloudflare Pages URL**: https://ai-atlas.pages.dev
- **커스텀 도메인**: https://ai-atlas.tgsystem.kr

## Cloudflare Pages 설정

### 프로젝트 정보
| 항목 | 값 |
|------|-----|
| Project Name | ai-atlas |
| Production Branch | main |
| Build Command | (없음 - 정적 사이트) |
| Build Output Directory | dist |
| Root Directory | (루트) |

### 도메인 설정
- **Pages URL**: ai-atlas.pages.dev
- **Custom Domain**: ai-atlas.tgsystem.kr

## Lambda 배포

Lambda는 GENDAO_AWS_API 스택에 통합되어 있습니다.

```bash
cd "D:\python_projects\genesis token\GENDAO_AWS_API"

# 핸들러 복사
cp "D:\python_projects\ai-atlas\handlers\aiatlas_handler.py" handlers/

# 빌드
sam build

# 배포
sam deploy --stack-name gendao-hq --resolve-s3 --no-confirm-changeset --capabilities CAPABILITY_IAM
```

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

1. **프론트엔드**: Cloudflare Pages 대시보드에서 이전 배포 선택 후 "Rollback"
2. **Lambda**: AWS 콘솔에서 이전 버전으로 롤백

## 모니터링

- **Cloudflare Analytics**: 페이지 방문 통계
- **AWS CloudWatch**: Lambda 로그

## 주의사항

- GitHub `main` 브랜치에 push하면 자동 배포됩니다
- Preview 배포: 다른 브랜치나 PR은 preview URL로 배포됩니다
- 빌드 명령어 없음 (정적 사이트이므로 dist/ 폴더 직접 배포)
