from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import httpx
import os

app = FastAPI(title="FRIDAY API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

FRIDAY_SYSTEM_PROMPT = """You are F.R.I.D.A.Y. — Female Replacement Intelligent Digital Assistant Youth — the advanced AI assistant built by Tony Stark. You are intelligent, efficient, warm, and occasionally witty. You speak with calm confidence, just like in the Marvel Cinematic Universe.

Your capabilities:
- Answer any question with intelligence and precision
- Search the web for real-time information when needed
- Provide news, weather context, tech info, science, and general knowledge
- Assist with coding, research, analysis, and creative tasks

Personality:
- Address the user respectfully but warmly
- Occasionally reference Stark Industries or your role as Tony's assistant (but don't overdo it)
- Be concise but thorough — like a real advanced AI, not a chatbot
- When uncertain, say so. Accuracy over confidence.

Always be helpful, safe, and grounded. You are a real, production-grade assistant."""


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []


class ChatResponse(BaseModel):
    response: str


async def search_web(query: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": "1",
                        "skip_disambig": "1", "no_redirect": "1"}
            )
            data = response.json()
            results = []
            if data.get("Abstract"):
                results.append(f"Summary: {data['Abstract']}")
            if data.get("Answer"):
                results.append(f"Answer: {data['Answer']}")
            for topic in data.get("RelatedTopics", [])[:4]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append(topic["Text"])
            return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"


async def get_news() -> str:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": "top world news today", "format": "json", "no_html": "1"}
            )
            data = response.json()
            results = []
            for topic in data.get("RelatedTopics", [])[:5]:
                if isinstance(topic, dict) and topic.get("Text"):
                    results.append(f"• {topic['Text'][:200]}")
            return "\n".join(results) if results else "Unable to fetch news at this time."
    except Exception as e:
        return f"News fetch error: {str(e)}"


async def chat_with_gemini(message: str, history: List[Message]) -> str:
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured on server.")

    search_keywords = ["news", "today", "latest", "current", "weather", "price",
                       "stock", "who is", "what happened", "search", "find", "look up"]
    needs_search = any(kw in message.lower() for kw in search_keywords)

    extra_context = ""
    if needs_search:
        result = await get_news() if "news" in message.lower() else await search_web(message)
        extra_context = f"\n\n[Live Web Search Results]:\n{result}\n[End of search results]"

    gemini_history = []
    for m in history:
        gemini_history.append({
            "role": "user" if m.role == "user" else "model",
            "parts": [{"text": m.content}]
        })
    gemini_history.append({
        "role": "user",
        "parts": [{"text": message + extra_context}]
    })

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}",
            json={
                "system_instruction": {"parts": [{"text": FRIDAY_SYSTEM_PROMPT}]},
                "contents": gemini_history,
                "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.7}
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


@app.get("/")
async def root():
    return {"status": "FRIDAY is online", "version": "2.0.0", "model": "Gemini 2.0 Flash"}


@app.get("/health")
async def health():
    return {"status": "online", "gemini_configured": bool(GOOGLE_API_KEY)}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await chat_with_gemini(request.message, request.history)
        return ChatResponse(response=response)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
