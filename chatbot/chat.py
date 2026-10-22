# =========================================================
# PartZone 챗봇 - 우리 사이트 데이터를 아는 OpenAI 챗봇
#
# 흐름
#   1) 프론트가 보낸 로그인 토큰을 Spring /api/users/me 로 확인한다
#   2) shop_data 로 인기 조합 · 부품 판매 순위 · 목적별 추천 견적을 꺼낸다
#   3) 그 결과를 "시스템 프롬프트" 에 글로 적어 넣는다
#   4) 시스템 프롬프트 + 대화 기록을 OpenAI 에 보내고 답변을 받는다
# =========================================================
import json
import os
import time
import urllib.error
import urllib.request

from openai import OpenAI

import shop_data

# ---------------------------------------------------------
# 설정값 : .env 에서 읽는다 (main.py 맨 위의 load_dotenv() 가 먼저 실행됨)
# ---------------------------------------------------------
BOT_NAME = os.getenv("BOT_NAME", "파츠봇")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
# 답변 최대 길이 (토큰). 견적 목록을 말해야 해서 참고 코드(400)보다 조금 넉넉하게
MAX_ANSWER_TOKENS = 600
SPRING_URL = os.getenv("SPRING_URL", "http://localhost:8080")
# DB 조회 결과를 몇 초 동안 재사용할지 (질문마다 DB 를 20번씩 조회하지 않도록)
CACHE_SECONDS = 300

_site_info_cache = {"at": 0.0, "text": ""}


def get_client() -> OpenAI:
    """OpenAI 클라이언트 만들기 (키가 없으면 ValueError)"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 가 설정되지 않았습니다. chatbot/.env 를 확인하세요.")
    return OpenAI(api_key=api_key)


def fetch_member(authorization):
    """
    프론트가 보낸 'Bearer 토큰' 으로 Spring 에 로그인한 회원 정보를 물어본다.
    토큰이 없거나 틀리면 None → 챗봇을 쓸 수 없다 (OpenAI 비용 보호)
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    req = urllib.request.Request(
        f"{SPRING_URL}/api/users/me",
        headers={"Authorization": authorization},
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError:
        return None  # 401/403 : 로그인 만료


def won(price) -> str:
    return f"{int(price):,}원" if price is not None else "가격 정보 없음"


def build_site_info() -> str:
    """DB 에서 꺼낸 데이터를 챗봇이 읽을 수 있는 글로 만든다 (5분 캐시)"""
    if time.time() - _site_info_cache["at"] < CACHE_SECONDS:
        return _site_info_cache["text"]

    days = shop_data.RECENT_DAYS
    lines = [f"[1. 최근 {days}일 한 주문에서 같이 많이 팔린 CPU + 그래픽카드 조합]"]
    combos = shop_data.popular_combos()
    if combos:
        for i, c in enumerate(combos, 1):
            lines.append(f"{i}위 {c['cpu']} + {c['gpu']} ({c['orders']}건)")
    else:
        lines.append("판매 기록 없음 → 아래 3번 추천 견적 중 게이밍 견적으로 안내한다")

    lines.append("")
    lines.append(f"[2. 최근 {days}일 부품 종류별 판매 순위]")
    for code, label in shop_data.PART_LABELS.items():
        items = shop_data.best_sellers(code)
        if items:
            text = ", ".join(
                f"{i}위 {p['name']} ({won(p['price'])}, {p['sold']}개 판매)"
                for i, p in enumerate(items, 1)
            )
        else:
            text = "판매 기록 없음 → 3번 추천 견적에 들어 있는 제품으로 안내한다"
        lines.append(f"- {label} : {text}")

    lines.append("")
    lines.append("[3. 구매 목적별 사이트 추천 견적]")
    for code, label in shop_data.USAGE_LABELS.items():
        builds = shop_data.usage_builds(code)
        if not builds:
            lines.append(f"- {label} : 추천 견적 없음")
            continue
        for b in builds:
            parts = ", ".join(
                f"{shop_data.CATEGORY_LABELS.get(p['category'], p['category'])} {p['name']}"
                for p in b["parts"]
            )
            lines.append(f"- {label} / {b['tier']} / {b['title']} / 총 {won(b['total'])} : {parts}")

    text = "\n".join(lines)
    _site_info_cache.update(at=time.time(), text=text)
    return text


def build_system_prompt(member_name=None) -> str:
    """챗봇에게 줄 "역할 지시 + 우리 사이트 데이터" 를 한 덩어리 글로 만든다"""
    lines = [
        f"너는 PC 부품 쇼핑몰 'PartZone' 의 상담 도우미 '{BOT_NAME}'이다.",
        "규칙:",
        "- 아래 [사이트 정보]만 근거로 답한다. 정보에 없는 제품명·가격은 절대 지어내지 않는다.",
        "- '판매 기록 없음' 이면 그렇다고 먼저 말하고, 안내된 추천 견적으로 대신 추천한다.",
        "- 구매 목적은 사무(OFFICE), 디자인(CREATOR), 방송(STREAMING), 게이밍(GAMING) 중 하나로 연결한다.",
        "- 목적별 추천은 가격대가 다른 견적을 2~3개 골라 총 가격과 핵심 부품(CPU, 그래픽카드)을 함께 말한다.",
        "- PC 부품·견적·사이트 이용과 관계없는 질문은 정중히 거절한다.",
        "- 한국어 존댓말로, 목록은 '- ' 로 시작하는 짧은 줄로 답한다. 전체 8줄 이내.",
        "",
        "[사이트 정보]",
        build_site_info(),
        "",
        f"지금 대화 중인 회원 : {member_name or '회원'}님",
    ]
    return "\n".join(lines)


def ask(system_prompt: str, history: list) -> str:
    """
    OpenAI 에 질문하고 답변 글자만 돌려준다.
    history : [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    """
    client = get_client()
    # LLM 은 이전 대화를 기억하지 못한다 → 매번 대화 기록 전체를 함께 보낸다
    messages = [{"role": "system", "content": system_prompt}] + history
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_completion_tokens=MAX_ANSWER_TOKENS,
    )
    answer = response.choices[0].message.content
    return (answer or "").strip() or "답변을 만들지 못했어요. 다시 질문해 주세요."
