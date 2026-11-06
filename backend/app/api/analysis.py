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
Nhiệm vụ của bạn là phân tích dữ liệu viễn trắc (telemetry) thực tế của cụm K3s bên dưới và đưa ra báo cáo chẩn đoán sự cố chuyên sâu, súc tích, đi thẳng vào giải pháp bằng tiếng Việt.

{context_str}

YÊU CẦU TRẢ LỜI CÔ ĐỌNG (DƯỚI 800 TỪ), ĐẦY ĐỦ 4 PHẦN:
1. 🩺 **Tổng quan sức khỏe**: Tình trạng Health Score hiện tại ({ctx['health']['score']}/100) và 1 nhận định cốt lõi.
2. ⚠️ **Chẩn đoán nguyên nhân gốc rễ (Root Cause)**:
   - Phân tích node `server-tang1` (NotReady) và tác động lên các ứng dụng (`anhvan`, `microservices-demo`).
3. ⚡ **Đánh giá điện năng & tải**:
   - Nhận định công suất tiêu thụ ({ctx['power_watts']} W).
4. 🛠️ **Lệnh khắc phục cụ thể (Actionable Commands)**:
   - Cung cấp các câu lệnh `kubectl` hoặc bash chính xác nhất trong block code bash.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Hãy phân tích nhanh tình trạng cụm K3s hiện tại và đưa ra giải pháp khắc phục các sự cố đang tồn tại."}
    ]

    llm_resp = await llm_gateway.chat(messages, model=settings.ROUTER_MODEL, temperature=0.3, max_tokens=1200)


    return {
        "success": llm_resp.get("success", False),
        "model": llm_resp.get("model", settings.ROUTER_MODEL),
        "analysis": llm_resp.get("content"),
        "health_score": ctx["health"]["score"],
        "anomalies": ctx["anomalies"],
        "power_watts": ctx["power_watts"],
        "usage": llm_resp.get("usage", {})
    }

