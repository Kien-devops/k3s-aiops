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
Nhiệm vụ của bạn là phân tích dữ liệu viễn trắc (telemetry) thực tế của cụm K3s bên dưới và đưa ra báo cáo chẩn đoán sự cố chuyên sâu, súc tích, đi thẳng vào giải pháp bằng tiếng Việt dựa trên bằng chứng (evidence-based).

{context_str}

QUY TẮC PHÂN TÍCH:
1. KHÔNG giả định hoặc nhắc đến sự cố của bất kỳ thành phần nào nếu dữ liệu bên trên không ghi nhận.
2. Mọi kết luận nguyên nhân gốc rễ (Root Cause) PHẢI liên kết trực tiếp với bằng chứng cụ thể (Node, Pod, Log hoặc Event có timestamp).
3. Đánh giá mức độ tin cậy của chẩn đoán (Confidence: High / Medium / Low).

YÊU CẦU TRẢ LỜI CÔ ĐỌNG (DƯỚI 800 TỪ), ĐẦY ĐỦ 4 PHẦN:
1. 🩺 **Tổng quan sức khỏe**: Tình trạng Health Score hiện tại ({ctx['health']['score']}/100) và nhận định chính.
2. ⚠️ **Chẩn đoán nguyên nhân gốc rễ (Root Cause & Evidence)**:
   - Liệt kê các bất thường thực tế đang diễn ra kèm bằng chứng cụ thể.
   - Đánh giá tác động đến các dịch vụ người dùng (`anhvan`, `microservices-demo`, ingress).
   - Mức độ tin cậy (Confidence).
3. ⚡ **Đánh giá điện năng & tải cụm**:
   - Nhận định công suất tiêu thụ ({ctx['power_watts']} W) và tài nguyên CPU/RAM.
4. 🛠️ **Hành động & Lệnh khắc phục (Runbook & Commands)**:
   - Cung cấp các câu lệnh `kubectl` hoặc bash chính xác nhất trong block code bash để SRE có thể copy-paste xử lý ngay.
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

