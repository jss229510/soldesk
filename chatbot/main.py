# =========================================================
# PartZone 챗봇 서버 (FastAPI, 8000번 포트)
# 실행 : uvicorn main:app --reload --port 8000
# =========================================================
from dotenv import load_dotenv

# chat.py 가 import 될 때 환경변수를 읽으므로, 가장 먼저 .env 를 불러온다
load_dotenv()

from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

import chat

app = FastAPI(title="PartZone Chatbot")

# 질문 최대 글자 수 (React ChatWidget 의 MAX_LENGTH 와 같은 값)
MAX_QUESTION_LENGTH = 500
# OpenAI 에 보낼 최근 대화 수 (길어질수록 비용이 늘어난다)
MAX_HISTORY = 10


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=3000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)


@app.get("/health")
def health():
    """서버가 켜져 있는지 확인 : http://localhost:8000/health"""
    return {"status": "ok"}


@app.post("/chat")
def chat_endpoint(req: ChatRequest, authorization: str | None = Header(default=None)):
    # 1) 로그인 확인 (Spring 에 토큰 검사를 맡긴다)
    try:
        member = chat.fetch_member(authorization)
    except Exception:
        raise HTTPException(503, "로그인 확인을 못 했어요. 8080번 Spring 서버가 실행 중인지 확인하세요.")
    if member is None:
        raise HTTPException(401, "로그인한 회원만 챗봇을 사용할 수 있어요.")

    # 2) 마지막 메시지는 회원의 질문이어야 한다
    last = req.messages[-1]
    if last.role != "user" or len(last.content) > MAX_QUESTION_LENGTH:
        raise HTTPException(400, f"질문은 {MAX_QUESTION_LENGTH}자 이내로 입력해 주세요.")

    # 3) 사이트 데이터로 시스템 프롬프트 만들기
    try:
        system_prompt = chat.build_system_prompt(member.get("nickname"))
    except Exception:
        raise HTTPException(503, "상품 데이터를 불러오지 못했어요. DB 연결을 확인하세요.")

    # 4) OpenAI 에 질문
    history = [m.model_dump() for m in req.messages[-MAX_HISTORY:]]
    try:
        reply = chat.ask(system_prompt, history)
    except ValueError as e:
        raise HTTPException(500, str(e))
    except Exception:
        raise HTTPException(502, "AI 답변 서버에 문제가 생겼어요. 잠시 후 다시 시도해 주세요.")

    return {"reply": reply}
