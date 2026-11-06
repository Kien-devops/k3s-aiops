from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.core.context_builder import context_builder
from app.core.llm_gateway import llm_gateway
from app.config import settings

router = APIRouter(prefix="/api/aiops", tags=["AIOps Chat"])

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = 0.4

@router.post("/chat")
async def chat_with_copilot(req: ChatRequest):
    """
    Live AI SRE Chatbot infused with real-time K3s cluster telemetry.
    """
    ctx = await context_builder.build_cluster_context()
    context_str = context_builder.format_context_for_llm(ctx)

    system_message = {
        "role": "system",
        "content": f"""Bạn là AIOps Copilot thông minh phục vụ cho cụm Kubernetes/K3s on-premises của người dùng.
Bạn có quyền truy cập dữ liệu thời gian thực của cụm:
{context_str}

Quy tắc phản hồi:
- Luôn trả lời ngắn gọn, chuẩn xác, tự tin, mang phong cách kỹ sư SRE cấp cao.
- Sử dụng tiếng Việt rõ ràng, kèm các code block `kubectl` hoặc lệnh Linux cụ thể khi người dùng hỏi cách khắc phục.
- Nắm rõ các ứng dụng đang chạy trong cụm: `anhvan` (DevOps English app, port 3000, Ingress `anhvan.onprem.site`), `microservices-demo` (app1, Ingress `app1.onprem.site`), và hệ thống đo điện năng monitor trên `server-tang3`.
"""
    }

    formatted_messages = [system_message]
    for m in req.messages:
        formatted_messages.append({"role": m.role, "content": m.content})

    chosen_model = req.model or settings.ROUTER_MODEL
    resp = await llm_gateway.chat(
        messages=formatted_messages,
        model=chosen_model,
        temperature=req.temperature,
        max_tokens=2048
    )

    return resp
