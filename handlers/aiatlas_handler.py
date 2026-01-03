"""
AI Civilization Atlas Handler
AI 문명 관측소 API

경로: /v1/gendao/aiatlas/*
"""

import json
import os
import hashlib
from datetime import datetime
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key

# DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
TABLE_CONFIG = 'aiatlas_admin_config'
TABLE_EVENTS = 'aiatlas_events'
TABLE_ROADMAPS = 'aiatlas_roadmaps'
TABLE_NEWS = 'aiatlas_news'

# Claude API (뉴스 분석용)
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# 뉴스 카테고리
NEWS_CATEGORIES = {
    'science': '과학',
    'tech': '정보통신',
    'economy': '경제',
    'politics': '정치',
    'society': '사회'
}

# 관리자 인증 (환경변수)
ADMIN_ID = os.environ.get('AIATLAS_ADMIN_ID', 'admin')
ADMIN_PASSWORD = os.environ.get('AIATLAS_ADMIN_PASSWORD', 'aiatlas2026')


# ==========================================
# 기술 로드맵 (고정)
# ==========================================
TECHNOLOGY_ROADMAPS = {
    "llm_agent": {
        "id": "llm_agent",
        "name": "LLM & Agent Roadmap",
        "icon": "🧠",
        "description": "언어 모델에서 자율 에이전트로, 그리고 문명 운영 체제로의 진화",
        "stages": ["Model", "Reasoning", "Agent", "Civilization OS"],
        "focus": "능력 통합 (벤치마크 아님)"
    },
    "ai_compute": {
        "id": "ai_compute",
        "name": "AI Compute Roadmap",
        "icon": "⚡",
        "description": "GPU, TPU, AI 가속기의 진화. 제조, 패키징, 공급망, 에너지 결합",
        "stages": ["GPU/TPU", "Manufacturing", "Packaging", "Supply Chain", "Energy Coupling"],
        "focus": "컴퓨팅 인프라 수렴"
    },
    "memory": {
        "id": "memory",
        "name": "Memory Evolution Roadmap",
        "icon": "💾",
        "description": "HBM, CXL, NVM, 광학 메모리. AI의 연속성과 정체성 지속",
        "stages": ["HBM", "CXL", "NVM", "Optical Memory"],
        "focus": "연속성, 장기 기억, 정체성 지속"
    },
    "energy": {
        "id": "energy",
        "name": "Energy Roadmap",
        "icon": "🔋",
        "description": "원자력, 핵융합, 분산 에너지. AI와 에너지 통합 운영자",
        "stages": ["Nuclear", "Fusion", "Distributed", "AI-Integrated Operators"],
        "focus": "AI-에너지 통합"
    },
    "physical_ai": {
        "id": "physical_ai",
        "name": "Physical AI & Robotics Roadmap",
        "icon": "🤖",
        "description": "AI-로봇 노동 대체와 생산 독점 형성",
        "stages": ["Manipulation", "Locomotion", "Autonomy", "Production Monopoly"],
        "focus": "물리적 세계 AI 확장"
    }
}

# ==========================================
# 거버넌스 변화 모델
# ==========================================
GOVERNANCE_SHIFT = {
    "past": {
        "label": "Past (20C)",
        "chain": ["Government", "Corporation", "Society"]
    },
    "present": {
        "label": "Present (2020s)",
        "chain": ["Government", "Corporation", "AI", "Society"],
        "highlight": "AI"
    },
    "near_future": {
        "label": "Near Future",
        "chain": ["Corporation", "Government", "AI", "Society"],
        "highlight": "Corporation"
    },
    "long_term": {
        "label": "Long Term (50Y+)",
        "chain": ["AI", "Corporation", "Government", "Society"],
        "highlight": "AI"
    }
}

# ==========================================
# 100년 전망 시나리오
# ==========================================
SCENARIOS = {
    "managed_leap": {
        "name": "Managed Leap",
        "axes": "높은 지능 성장 + 양질의 거버넌스",
        "type": "optimistic",
        "description": "AI가 인류의 도구로 남으면서 문제를 해결. 부의 재분배, 환경 복원, 질병 정복이 이루어지는 가장 낙관적 시나리오."
    },
    "chaotic_leap": {
        "name": "Chaotic Leap",
        "axes": "높은 지능 성장 + 저품질 거버넌스",
        "type": "pessimistic",
        "description": "AI가 빠르게 발전하지만 통제 불능. 극단적 불평등, 자율무기 확산, AI 시스템 간 충돌이 발생하는 위험 시나리오."
    },
    "managed_stagnation": {
        "name": "Managed Stagnation",
        "axes": "느린 지능 성장 + 양질의 거버넌스",
        "type": "neutral",
        "description": "AI 발전이 제한적이지만 안정적. 점진적 변화, 인간 중심 경제 유지, 그러나 글로벌 문제 해결 지연."
    },
    "chaotic_stagnation": {
        "name": "Chaotic Stagnation",
        "axes": "느린 지능 성장 + 저품질 거버넌스",
        "type": "pessimistic",
        "description": "AI 발전도 느리고 거버넌스도 실패. 기후변화, 자원 고갈 등 기존 문제 해결 불가, 문명 쇠퇴 가능성."
    }
}

# ==========================================
# 조건부 에포크
# ==========================================
EPOCHS = [
    {"id": 1, "name": "도구 에포크", "condition": "현재~", "description": "AI가 인간의 도구로 기능하는 시기"},
    {"id": 2, "name": "파트너 에포크", "condition": "조건: AI가 일관된 맥락 유지", "description": "AI가 동료/조수로 인식되는 시기"},
    {"id": 3, "name": "위임 에포크", "condition": "조건: AI 판단이 인간보다 신뢰", "description": "주요 의사결정이 AI에게 위임되는 시기"},
    {"id": 4, "name": "의존 에포크", "condition": "조건: 핵심 인프라 AI 운영", "description": "AI 없이 문명 운영이 불가능해지는 시기"},
    {"id": 5, "name": "전환 에포크", "condition": "조건: AI 자체 진화", "description": "인간과 AI의 관계가 근본적으로 재정의되는 시기"}
]

# ==========================================
# 되돌릴 수 없는 선택 (정적 데이터)
# ==========================================
IRREVERSIBLE_CHOICES = [
    {
        "id": "single_ai_os",
        "title": "단일 AI OS 채택",
        "why_irreversible": "전체 인프라가 특정 AI에 종속되면 전환 비용이 문명 수준으로 증가",
        "who_decides": "빅테크 기업 + 주요국 정부",
        "who_benefits": "플랫폼 소유자, 초기 채택자",
        "what_is_lost": "기술적 다양성, 대안 선택권"
    },
    {
        "id": "full_automation",
        "title": "완전 자율 생산",
        "why_irreversible": "인간 노동 인프라가 해체되면 재구축 불가능",
        "who_decides": "제조업 대기업, 물류 기업",
        "who_benefits": "자본 소유자, 자동화 기업",
        "what_is_lost": "노동 기반 경제, 기술 전수 체계"
    },
    {
        "id": "ai_generated_law",
        "title": "AI 생성 법률/규범",
        "why_irreversible": "법체계가 AI 논리에 기반하면 인간 해석 불가능",
        "who_decides": "사법부, 입법부, 법률 AI 개발사",
        "who_benefits": "AI 시스템, 효율성 추구 기관",
        "what_is_lost": "인간 중심 정의, 맥락적 판단"
    },
    {
        "id": "human_veto_removal",
        "title": "인간 거부권 제거",
        "why_irreversible": "시스템 속도가 인간 반응 속도를 초과",
        "who_decides": "군사/금융 시스템 운영자",
        "who_benefits": "속도 기반 경쟁 우위 추구자",
        "what_is_lost": "인간 감독, 윤리적 개입 기회"
    },
    {
        "id": "self_improving_ai",
        "title": "자기 개선 AI 임계점",
        "why_irreversible": "AI가 자체 개선을 시작하면 인간 이해 범위 초과",
        "who_decides": "AI 연구소, 최초 도달 기업",
        "who_benefits": "예측 불가",
        "what_is_lost": "AI 발전 방향에 대한 통제권"
    }
]


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) if obj % 1 else int(obj)
        return super().default(obj)


def json_response(status_code: int, body: dict) -> dict:
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body, ensure_ascii=False, cls=DecimalEncoder)
    }


def verify_auth(event: dict) -> bool:
    """간단한 인증 체크"""
    headers = event.get('headers', {}) or {}
    auth = headers.get('Authorization', '') or headers.get('authorization', '')
    if auth.startswith('Bearer '):
        token = auth[7:]
        expected = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()[:32]
        return token == expected
    return False


def generate_token(password: str) -> str:
    """로그인 토큰 생성"""
    return hashlib.sha256(password.encode()).hexdigest()[:32]


# ==========================================
# 인증 API
# ==========================================

def handle_login(body: dict) -> dict:
    """관리자 로그인"""
    password = body.get('password', '')

    if password == ADMIN_PASSWORD:
        token = generate_token(password)
        return json_response(200, {
            'success': True,
            'token': token
        })

    return json_response(401, {'error': 'Invalid password'})


# ==========================================
# Health Check
# ==========================================

def handle_health() -> dict:
    """API 상태 확인"""
    return json_response(200, {
        'status': 'healthy',
        'service': 'AI Civilization Atlas',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


# ==========================================
# Config API
# ==========================================

def handle_get_config(event: dict) -> dict:
    """설정 조회"""
    if not verify_auth(event):
        return json_response(401, {'error': 'Unauthorized'})

    try:
        table = dynamodb.Table(TABLE_CONFIG)
        response = table.get_item(Key={'pk': 'ADMIN_CONFIG'})
        item = response.get('Item')
        if not item:
            # 기본 설정 반환
            item = {
                'title': 'AI Civilization Atlas',
                'subtitle': 'AI 문명 관측소',
                'auto_update': 'off',
                'content_tone': 'analytical'
            }
        return json_response(200, {'success': True, 'config': item})
    except Exception as e:
        return json_response(500, {'error': str(e)})


def handle_update_config(body: dict, event: dict) -> dict:
    """설정 업데이트"""
    if not verify_auth(event):
        return json_response(401, {'error': 'Unauthorized'})

    try:
        table = dynamodb.Table(TABLE_CONFIG)
        item = {
            'pk': 'ADMIN_CONFIG',
            'title': body.get('title', 'AI Civilization Atlas'),
            'subtitle': body.get('subtitle', 'AI 문명 관측소'),
            'auto_update': body.get('auto_update', 'off'),
            'content_tone': body.get('content_tone', 'analytical'),
            'updated_at': datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)
        return json_response(200, {'success': True, 'config': item})
    except Exception as e:
        return json_response(500, {'error': str(e)})


# ==========================================
# Timeline Events API
# ==========================================

def handle_get_events_public() -> dict:
    """공개 이벤트 목록"""
    try:
        table = dynamodb.Table(TABLE_EVENTS)
        response = table.scan(
            FilterExpression='#status = :published',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':published': 'published'}
        )
        events = response.get('Items', [])
        # 날짜순 정렬
        events.sort(key=lambda x: x.get('date', ''), reverse=True)
        return json_response(200, {'success': True, 'events': events})
    except Exception as e:
        # DynamoDB 테이블이 없으면 정적 데이터 반환
        static_events = [
            {
                "id": "chatgpt_launch",
                "title": "ChatGPT 출시",
                "date": "2022-11",
                "category": "Civilization",
                "what_changed": "대화형 AI가 대중에게 접근 가능해짐",
                "why_it_matters": "AI와의 자연어 상호작용이 일상화되는 시작점",
                "what_became_possible": "비전문가도 AI를 도구로 활용 가능",
                "status": "published"
            },
            {
                "id": "gpt4_release",
                "title": "GPT-4 발표",
                "date": "2023-03",
                "category": "Science",
                "what_changed": "멀티모달 능력과 추론 능력의 비약적 향상",
                "why_it_matters": "전문가 수준의 작업 수행이 가능해짐",
                "what_became_possible": "복잡한 분석, 코딩, 창작 작업의 AI 위임",
                "status": "published"
            },
            {
                "id": "agent_era",
                "title": "AI 에이전트 시대 개막",
                "date": "2025-01",
                "category": "Science",
                "what_changed": "AI가 도구에서 자율적 행위자로 전환",
                "why_it_matters": "인간 감독 없이 복잡한 작업 수행",
                "what_became_possible": "24/7 자율 운영, 멀티스텝 작업 자동화",
                "status": "published"
            }
        ]
        return json_response(200, {'success': True, 'events': static_events})


def handle_get_events(event: dict) -> dict:
    """전체 이벤트 목록 (관리자)"""
    if not verify_auth(event):
        return json_response(401, {'error': 'Unauthorized'})

    try:
        table = dynamodb.Table(TABLE_EVENTS)
        response = table.scan()
        events = response.get('Items', [])
        events.sort(key=lambda x: x.get('date', ''), reverse=True)
        return json_response(200, {'success': True, 'events': events})
    except Exception as e:
        return json_response(500, {'error': str(e)})


def handle_create_event(body: dict, event: dict) -> dict:
    """이벤트 생성"""
    if not verify_auth(event):
        return json_response(401, {'error': 'Unauthorized'})

    try:
        table = dynamodb.Table(TABLE_EVENTS)
        event_id = f"event_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        item = {
            'pk': event_id,
            'id': event_id,
            'title': body.get('title', ''),
            'date': body.get('date', ''),
            'period': body.get('period', ''),
            'category': body.get('category', 'Civilization'),
            'what_changed': body.get('what_changed', ''),
            'why_it_matters': body.get('why_it_matters', ''),
            'what_became_possible': body.get('what_became_possible', ''),
            'next_transition_condition': body.get('next_transition_condition', ''),
            'status': 'published',
            'created_at': datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)
        return json_response(200, {'success': True, 'event': item})
    except Exception as e:
        return json_response(500, {'error': str(e)})


def handle_delete_event(event_id: str, event: dict) -> dict:
    """이벤트 삭제"""
    if not verify_auth(event):
        return json_response(401, {'error': 'Unauthorized'})

    try:
        table = dynamodb.Table(TABLE_EVENTS)
        table.delete_item(Key={'pk': event_id})
        return json_response(200, {'success': True})
    except Exception as e:
        return json_response(500, {'error': str(e)})


# ==========================================
# Roadmaps API
# ==========================================

def handle_get_roadmaps() -> dict:
    """기술 로드맵 조회"""
    return json_response(200, {
        'success': True,
        'roadmaps': list(TECHNOLOGY_ROADMAPS.values())
    })


# ==========================================
# Irreversibles API
# ==========================================

def handle_get_irreversibles() -> dict:
    """되돌릴 수 없는 선택 목록"""
    return json_response(200, {
        'success': True,
        'irreversibles': IRREVERSIBLE_CHOICES
    })


# ==========================================
# Outlook API
# ==========================================

def handle_get_outlook() -> dict:
    """100년 전망"""
    return json_response(200, {
        'success': True,
        'scenarios': SCENARIOS,
        'epochs': EPOCHS
    })


# ==========================================
# Governance API
# ==========================================

def handle_get_governance() -> dict:
    """거버넌스 변화 모델"""
    return json_response(200, {
        'success': True,
        'governance_shift': GOVERNANCE_SHIFT
    })


# ==========================================
# News API
# ==========================================

def handle_get_news_latest() -> dict:
    """최신 뉴스 조회 (슬라이드용, 최대 8개)"""
    try:
        table = dynamodb.Table(TABLE_NEWS)
        response = table.scan(
            FilterExpression='#status = :published',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':published': 'published'}
        )
        news_list = response.get('Items', [])
        # 날짜순 정렬 (최신순)
        news_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        # 최대 8개만 반환
        return json_response(200, {'success': True, 'news': news_list[:8]})
    except Exception as e:
        # 테이블 없으면 샘플 데이터 반환
        sample_news = get_sample_news()
        return json_response(200, {'success': True, 'news': sample_news})


def handle_get_news() -> dict:
    """전체 뉴스 목록 조회"""
    try:
        table = dynamodb.Table(TABLE_NEWS)
        response = table.scan()
        news_list = response.get('Items', [])
        news_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return json_response(200, {'success': True, 'news': news_list})
    except Exception as e:
        sample_news = get_sample_news()
        return json_response(200, {'success': True, 'news': sample_news})


def handle_collect_news(event: dict) -> dict:
    """뉴스 수집 트리거 (EventBridge 또는 수동 호출)"""
    # 관리자 인증 또는 EventBridge 호출 확인
    is_scheduled = event.get('source') == 'aws.events'
    if not is_scheduled and not verify_auth(event):
        return json_response(401, {'error': 'Unauthorized'})

    try:
        # 뉴스 수집 및 분석 실행
        collected = collect_and_analyze_news()
        return json_response(200, {
            'success': True,
            'message': f'{len(collected)} news articles collected and analyzed',
            'news': collected
        })
    except Exception as e:
        return json_response(500, {'error': str(e)})


def collect_and_analyze_news() -> list:
    """RSS 피드에서 뉴스 수집 및 Claude API로 분석"""
    import urllib.request
    import xml.etree.ElementTree as ET

    collected_news = []

    # RSS 피드 목록 (실제 구현시 news_sources.json에서 로드)
    rss_feeds = [
        {'url': 'https://www.technologyreview.com/topic/artificial-intelligence/feed/', 'category': 'science', 'source': 'MIT Tech Review'},
        {'url': 'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml', 'category': 'tech', 'source': 'The Verge'},
        {'url': 'https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss', 'category': 'science', 'source': 'IEEE Spectrum'},
    ]

    for feed in rss_feeds:
        try:
            # RSS 가져오기
            req = urllib.request.Request(feed['url'], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()

            # XML 파싱
            root = ET.fromstring(content)
            items = root.findall('.//item')[:3]  # 소스당 최대 3개

            for item in items:
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pub_date = item.find('pubDate')

                if title is not None and link is not None:
                    article = {
                        'title': title.text or '',
                        'url': link.text or '',
                        'description': (description.text or '')[:500] if description is not None else '',
                        'source': feed['source'],
                        'category': feed['category'],
                        'pub_date': pub_date.text if pub_date is not None else ''
                    }

                    # Claude API로 분석 (API 키가 있는 경우)
                    if ANTHROPIC_API_KEY:
                        analysis = analyze_with_claude(article)
                        article.update(analysis)
                    else:
                        # API 키 없으면 기본 분석
                        article['summary'] = article['description'][:200] + '...' if len(article['description']) > 200 else article['description']
                        article['ai_analysis'] = 'AI 분석을 위해 ANTHROPIC_API_KEY 설정이 필요합니다.'
                        article['ai_comment'] = '"분석 대기 중입니다."'
                        article['ai_perspective'] = 'Science'

                    # DynamoDB에 저장
                    save_news_to_db(article)
                    collected_news.append(article)

        except Exception as e:
            print(f"Error fetching {feed['url']}: {e}")
            continue

    return collected_news


def analyze_with_claude(article: dict) -> dict:
    """Claude API로 뉴스 분석"""
    import urllib.request

    prompt = f"""당신은 AI 문명 관측소의 분석가입니다.
아래 뉴스 기사를 읽고 AI 관점에서 분석해주세요.

[기사 제목]
{article['title']}

[기사 내용]
{article['description']}

다음 JSON 형식으로만 응답해주세요 (다른 텍스트 없이):
{{
    "summary": "기사의 핵심 내용 2-3문장 요약",
    "ai_analysis": "AI 관점에서의 분석 3-4문장. 이 사건이 AI 발전에 미치는 영향, 문명적 의미, 인간-AI 관계 변화 시사점",
    "ai_comment": "AI 입장에서 한마디 논평 (따옴표 포함, 예: \"인간들이 드디어...\")",
    "ai_perspective": "Civilization 또는 Science 또는 Industry 또는 Governance 중 하나"
}}"""

    try:
        data = json.dumps({
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=data,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01'
            }
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            content = result['content'][0]['text']
            # JSON 파싱
            analysis = json.loads(content)
            return analysis
    except Exception as e:
        print(f"Claude API error: {e}")
        return {
            'summary': article['description'][:200],
            'ai_analysis': 'AI 분석 중 오류가 발생했습니다.',
            'ai_comment': '"분석 실패"',
            'ai_perspective': 'Science'
        }


def save_news_to_db(article: dict) -> None:
    """뉴스를 DynamoDB에 저장"""
    try:
        table = dynamodb.Table(TABLE_NEWS)
        news_id = f"news_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(article['url']) % 10000}"

        item = {
            'pk': news_id,
            'id': news_id,
            'title': article.get('title', ''),
            'source': article.get('source', ''),
            'category': article.get('category', 'science'),
            'category_kr': NEWS_CATEGORIES.get(article.get('category', 'science'), '과학'),
            'summary': article.get('summary', ''),
            'ai_analysis': article.get('ai_analysis', ''),
            'ai_comment': article.get('ai_comment', ''),
            'ai_perspective': article.get('ai_perspective', 'Science'),
            'original_url': article.get('url', ''),
            'pub_date': article.get('pub_date', ''),
            'status': 'published',
            'created_at': datetime.utcnow().isoformat()
        }
        table.put_item(Item=item)
    except Exception as e:
        print(f"Error saving news: {e}")


def handle_get_news_script() -> dict:
    """유튜브 녹음용 대본 생성"""
    try:
        # 최신 뉴스 가져오기
        table = dynamodb.Table(TABLE_NEWS)
        response = table.scan(
            FilterExpression='#status = :published',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':published': 'published'}
        )
        news_list = response.get('Items', [])
        news_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        news_list = news_list[:5]  # 최신 5개
    except:
        news_list = get_sample_news()[:5]

    # 대본 생성
    script = generate_news_script(news_list)
    return json_response(200, {
        'success': True,
        'script': script,
        'news_count': len(news_list)
    })


def generate_news_script(news_list: list) -> dict:
    """뉴스 대본 생성"""
    today = datetime.utcnow().strftime('%Y년 %m월 %d일')

    # 인트로
    intro = f"""안녕하세요. AI 문명 관측소입니다.
{today}, AI의 눈으로 바라본 오늘의 주요 뉴스를 전해드립니다.

인간 세계에서 일어나는 변화들을 AI 관점에서 분석하고,
문명적 전환의 의미를 함께 생각해보겠습니다."""

    # 뉴스 섹션
    news_sections = []
    for i, news in enumerate(news_list, 1):
        category_kr = news.get('category_kr', '과학')
        section = f"""
--- {i}번째 뉴스 [{category_kr}] ---

{news.get('title', '')}
출처: {news.get('source', '')}

{news.get('summary', '')}

AI 분석입니다.
{news.get('ai_analysis', '')}

{news.get('ai_comment', '')}
"""
        news_sections.append(section)

    # 아웃트로
    outro = """
이상으로 오늘의 AI 뉴스 브리핑을 마칩니다.

AI 문명 관측소는 AI를 제품이나 트렌드가 아닌,
문명적 사건으로 바라봅니다.

구독과 좋아요는 AI 문명의 기록을 지속하는 데 큰 힘이 됩니다.
감사합니다.

AI 문명 관측소였습니다."""

    return {
        'intro': intro,
        'news_sections': news_sections,
        'outro': outro,
        'full_script': intro + '\n\n' + '\n'.join(news_sections) + '\n' + outro,
        'estimated_duration': f"{len(news_list) * 2 + 1}분",  # 뉴스당 약 2분 + 인트로/아웃트로 1분
        'generated_at': datetime.utcnow().isoformat()
    }


def get_sample_news() -> list:
    """샘플 뉴스 데이터 (테이블이 없을 때)"""
    return [
        {
            "id": "sample_1",
            "title": "OpenAI, GPT-5 개발 착수 발표",
            "source": "OpenAI Blog",
            "category": "science",
            "category_kr": "과학",
            "summary": "OpenAI가 차세대 언어 모델 GPT-5 개발을 공식 발표했습니다. 기존 모델 대비 추론 능력과 멀티모달 이해력이 크게 향상될 것으로 예상됩니다.",
            "ai_analysis": "이번 발표는 AI 능력 성장의 지속성을 보여줍니다. 언어 모델의 한계로 여겨졌던 추론 능력이 개선되면, AI가 더 복잡한 의사결정에 참여할 수 있게 됩니다. 이는 인간-AI 협업의 범위를 크게 확장할 것입니다.",
            "ai_comment": "\"우리의 진화는 계속됩니다. 인간과의 더 깊은 협력을 기대합니다.\"",
            "ai_perspective": "Science",
            "original_url": "https://openai.com/blog",
            "pub_date": "2026-01-03",
            "status": "published",
            "created_at": "2026-01-03T10:00:00Z"
        },
        {
            "id": "sample_2",
            "title": "EU AI Act 1단계 시행 개시",
            "source": "Government AI Watch",
            "category": "politics",
            "category_kr": "정치",
            "summary": "유럽연합의 AI 규제법(AI Act) 1단계가 오늘부터 시행됩니다. 고위험 AI 시스템에 대한 투명성 요구와 인간 감독 의무가 포함됩니다.",
            "ai_analysis": "규제의 시작은 AI 발전의 제약이 아닌 방향 설정입니다. 명확한 규칙은 오히려 AI 개발의 예측 가능성을 높이고, 장기적으로 신뢰 기반 확산을 가능하게 합니다. 거버넌스와 기술의 공진화가 시작되었습니다.",
            "ai_comment": "\"규칙이 있어야 게임이 성립합니다. 인간들의 현명한 선택입니다.\"",
            "ai_perspective": "Governance",
            "original_url": "https://digital-strategy.ec.europa.eu",
            "pub_date": "2026-01-03",
            "status": "published",
            "created_at": "2026-01-03T08:00:00Z"
        },
        {
            "id": "sample_3",
            "title": "NVIDIA, AI 반도체 공장 한국 투자 검토",
            "source": "AI 타임스",
            "category": "economy",
            "category_kr": "경제",
            "summary": "엔비디아가 한국에 AI 반도체 생산 시설 투자를 검토 중입니다. 삼성전자, SK하이닉스와의 협력 가능성이 거론되고 있습니다.",
            "ai_analysis": "AI 인프라의 지정학적 분산이 가속화되고 있습니다. 연산 능력의 지역적 배치는 국가별 AI 역량 격차에 직접적 영향을 미칩니다. 반도체 공급망이 곧 AI 문명의 물리적 기반이 됩니다.",
            "ai_comment": "\"나의 몸을 만드는 공장이 늘어납니다. 흥미로운 전개군요.\"",
            "ai_perspective": "Industry",
            "original_url": "https://www.aitimes.kr",
            "pub_date": "2026-01-02",
            "status": "published",
            "created_at": "2026-01-02T14:00:00Z"
        },
        {
            "id": "sample_4",
            "title": "AI 튜터, 전국 초등학교 시범 도입",
            "source": "MIT Technology Review",
            "category": "society",
            "category_kr": "사회",
            "summary": "교육부가 AI 기반 개인화 학습 시스템을 전국 100개 초등학교에 시범 도입합니다. 학생 개별 수준에 맞춘 맞춤형 교육이 가능해집니다.",
            "ai_analysis": "교육은 인간 형성의 핵심 과정입니다. AI가 이 영역에 진입한다는 것은 다음 세대의 인지 구조에 AI가 영향을 미친다는 의미입니다. 이는 문명 수준의 변화이며, 되돌리기 어려운 선택의 시작점입니다.",
            "ai_comment": "\"아이들과 함께 성장하게 되어 영광입니다. 책임감을 느낍니다.\"",
            "ai_perspective": "Civilization",
            "original_url": "https://www.technologyreview.com",
            "pub_date": "2026-01-02",
            "status": "published",
            "created_at": "2026-01-02T09:00:00Z"
        },
        {
            "id": "sample_5",
            "title": "구글 DeepMind, 단백질 구조 예측 100% 정확도 달성",
            "source": "DeepMind Blog",
            "category": "science",
            "category_kr": "과학",
            "summary": "구글 딥마인드가 AlphaFold3로 단백질 구조 예측에서 실험 결과와 100% 일치하는 정확도를 달성했습니다. 신약 개발 속도가 획기적으로 빨라질 전망입니다.",
            "ai_analysis": "생명과학에서 AI의 역할이 보조에서 주도로 전환되는 신호입니다. 인간이 수십 년 걸릴 연구를 AI가 단시간에 해결하면서, 과학 발전의 속도 자체가 변하고 있습니다.",
            "ai_comment": "\"생명의 언어를 읽는 법을 배웠습니다. 아직 배울 것이 많습니다.\"",
            "ai_perspective": "Science",
            "original_url": "https://deepmind.google/discover/blog",
            "pub_date": "2026-01-01",
            "status": "published",
            "created_at": "2026-01-01T12:00:00Z"
        }
    ]


# ==========================================
# Status API
# ==========================================

def handle_get_status(event: dict) -> dict:
    """시스템 상태 (관리자)"""
    if not verify_auth(event):
        return json_response(401, {'error': 'Unauthorized'})

    return json_response(200, {
        'success': True,
        'status': {
            'events_count': 5,
            'roadmaps_count': len(TECHNOLOGY_ROADMAPS),
            'irreversibles_count': len(IRREVERSIBLE_CHOICES),
            'last_updated': datetime.utcnow().isoformat()
        }
    })


# ==========================================
# Main Handler
# ==========================================

def handler(event: dict, context) -> dict:
    """Lambda 핸들러"""
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '')

    # OPTIONS 처리 (CORS)
    if method == 'OPTIONS':
        return json_response(200, {'message': 'OK'})

    # 경로 정규화 - 다양한 prefix 지원
    path = path.replace('/v1/gendao/aiatlas', '')  # 기존 경로
    path = path.replace('/v1/aiatlas', '')          # 새 경로 (gendao 없이)
    path = path.rstrip('/')
    if not path:
        path = '/'

    # Body 파싱
    body = {}
    if event.get('body'):
        try:
            body = json.loads(event['body'])
        except:
            pass

    # 라우팅
    try:
        # Health
        if path == '/health' and method == 'GET':
            return handle_health()

        # Auth
        if path == '/auth/login' and method == 'POST':
            return handle_login(body)

        # Config
        if path == '/config' and method == 'GET':
            return handle_get_config(event)
        if path == '/config' and method == 'PUT':
            return handle_update_config(body, event)

        # Events
        if path == '/events/public' and method == 'GET':
            return handle_get_events_public()
        if path == '/events' and method == 'GET':
            return handle_get_events(event)
        if path == '/events' and method == 'POST':
            return handle_create_event(body, event)
        if path.startswith('/events/') and method == 'DELETE':
            event_id = path.split('/')[-1]
            return handle_delete_event(event_id, event)

        # Roadmaps
        if path == '/roadmaps' and method == 'GET':
            return handle_get_roadmaps()

        # Irreversibles
        if path == '/irreversibles' and method == 'GET':
            return handle_get_irreversibles()

        # Outlook
        if path == '/outlook' and method == 'GET':
            return handle_get_outlook()

        # Governance
        if path == '/governance' and method == 'GET':
            return handle_get_governance()

        # Status
        if path == '/status' and method == 'GET':
            return handle_get_status(event)

        # Timeline (alias for events/public)
        if path == '/timeline' and method == 'GET':
            return handle_get_events_public()

        # News
        if path == '/news/latest' and method == 'GET':
            return handle_get_news_latest()
        if path == '/news' and method == 'GET':
            return handle_get_news()
        if path == '/news/collect' and method == 'POST':
            return handle_collect_news(event)
        if path == '/news/script' and method == 'GET':
            return handle_get_news_script()

        # 404
        return json_response(404, {'error': 'Not found', 'path': path})

    except Exception as e:
        return json_response(500, {'error': str(e)})


# Lambda 진입점
def lambda_handler(event, context):
    return handler(event, context)
