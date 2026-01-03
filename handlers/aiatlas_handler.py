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

    # 경로 정규화
    path = path.replace('/v1/gendao/aiatlas', '').rstrip('/')
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

        # 404
        return json_response(404, {'error': 'Not found', 'path': path})

    except Exception as e:
        return json_response(500, {'error': str(e)})


# Lambda 진입점
def lambda_handler(event, context):
    return handler(event, context)
