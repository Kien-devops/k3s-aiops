from fastapi import APIRouter
from app.core.context_builder import context_builder
from app.core.llm_gateway import llm_gateway
from app.config import settings

router = APIRouter(prefix="/api/aiops", tags=["AIOps Analysis"])

@router.post("/analyze")
async def analyze_incident():
    """
    Runs automated SRE Root Cause Analysis using 9Router gpt-5.6-sol
    infused with live K3s cluster telemetry.
    """
    ctx = await context_builder.build_cluster_context()
    context_str = context_builder.format_context_for_llm(ctx)

    system_prompt = f"""Bạn là AIOps Senior SRE Copilot chuyên gia điều hành và tối ưu cụm K3s On-Premises.
Nhiệm vụ của bạn là phân tích dữ liệu viễn trắc (telemetry) thực tế của cụm K3s bên dưới và đưa ra báo cáo chẩn đoán sự cố chuyên sâu bằng tiếng Việt.

{context_str}

BÁO CÁO CỦA BẠN CẦN THEO ĐÚNG CẤU TRÚC:
1. 🩺 **Tổng quan sức khỏe cụm**: Đánh giá Health Score hiện tại ({ctx['health']['score']}/100) và tác động tổng thể.
2. ⚠️ **Chẩn đoán nguyên nhân gốc rễ (Root Cause Analysis)**:
   - Phân tích chi tiết các node NotReady hoặc pod kẹt Terminating/CrashLoop.
   - Giải thích cơ chế K3s failover và tác động tới các app như `anhvan` (DevOps English) và `microservices-demo` (app1).
3. ⚡ **Đánh giá tiêu thụ điện năng & tài nguyên**:
   - Nhận định công suất ({ctx['power_watts']} W) so với ngưỡng bình thường.
4. 🛠️ **Kế hoạch khắc phục (Actionable Remediation Plan)**:
   - Cung cấp các câu lệnh `kubectl` hoặc bash chính xác để khắc phục ngay lập tức (dùng code block bash).
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Hãy phân tích toàn diện tình trạng cụm K3s hiện tại và đưa ra giải pháp khắc phục các sự cố đang tồn tại."}
    ]

    llm_resp = await llm_gateway.chat(messages, model=settings.ROUTER_MODEL, temperature=0.2, max_tokens=2500)

    return {
        "success": llm_resp.get("success", False),
        "model": llm_resp.get("model", settings.ROUTER_MODEL),
        "analysis": llm_resp.get("content"),
        "health_score": ctx["health"]["score"],
        "anomalies": ctx["anomalies"],
        "power_watts": ctx["power_watts"],
        "usage": llm_resp.get("usage", {})
    }
