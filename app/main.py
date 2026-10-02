import logging
import math
import re
import unicodedata
from collections import Counter, defaultdict
from html import escape

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("ai-guru-54")


TRAINING_DATA = {
    "tich_cuc": [
        "sản phẩm rất tốt và dễ sử dụng",
        "mình cực kỳ hài lòng với dịch vụ",
        "ứng dụng chạy nhanh giao diện đẹp",
        "trải nghiệm tuyệt vời hỗ trợ nhiệt tình",
        "kết quả chính xác hơn mong đợi",
        "bài hướng dẫn rõ ràng và hữu ích",
    ],
    "trung_tinh": [
        "mình đã nhận được sản phẩm hôm nay",
        "ứng dụng có ba chức năng chính",
        "đơn hàng đang được vận chuyển",
        "phiên bản mới được phát hành tuần này",
        "hệ thống trả về một kết quả",
        "tài liệu gồm nhiều phần khác nhau",
    ],
    "tieu_cuc": [
        "ứng dụng quá chậm và thường xuyên lỗi",
        "mình thất vọng vì kết quả không chính xác",
        "dịch vụ tệ và phản hồi rất lâu",
        "giao diện khó dùng trải nghiệm không tốt",
        "sản phẩm bị hỏng ngay khi mở hộp",
        "hướng dẫn thiếu rõ ràng và gây nhầm lẫn",
    ],
}

LABELS = {
    "tich_cuc": "Tích cực",
    "trung_tinh": "Trung tính",
    "tieu_cuc": "Tiêu cực",
}


def normalize_text(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFC", text.lower())
    return re.findall(r"[a-zà-ỹđ]+", normalized, flags=re.IGNORECASE)


class SentimentEngine:
    """A compact multinomial Naive Bayes model trained at startup."""

    def __init__(self, data: dict[str, list[str]]) -> None:
        self.document_count = sum(len(items) for items in data.values())
        self.class_documents = {label: len(items) for label, items in data.items()}
        self.word_counts: dict[str, Counter[str]] = {}
        self.total_words: dict[str, int] = {}
        vocabulary: set[str] = set()

        for label, sentences in data.items():
            counts: Counter[str] = Counter()
            for sentence in sentences:
                counts.update(normalize_text(sentence))
            self.word_counts[label] = counts
            self.total_words[label] = sum(counts.values())
            vocabulary.update(counts)

        self.vocabulary = vocabulary
        logger.info(
            "Sentiment model ready: %s documents, %s vocabulary terms",
            self.document_count,
            len(self.vocabulary),
        )

    def predict(self, text: str) -> tuple[str, dict[str, float], list[str]]:
        tokens = normalize_text(text)
        if not tokens:
            raise ValueError("Văn bản cần có ít nhất một từ hợp lệ.")

        scores: dict[str, float] = {}
        vocab_size = len(self.vocabulary)
        for label in TRAINING_DATA:
            prior = self.class_documents[label] / self.document_count
            score = math.log(prior)
            denominator = self.total_words[label] + vocab_size
            for token in tokens:
                score += math.log((self.word_counts[label][token] + 1) / denominator)
            scores[label] = score

        max_score = max(scores.values())
        exponentials = {label: math.exp(score - max_score) for label, score in scores.items()}
        total = sum(exponentials.values())
        probabilities = {label: value / total for label, value in exponentials.items()}
        predicted = max(probabilities, key=probabilities.get)

        contributions = defaultdict(float)
        for token in set(tokens):
            own = self.word_counts[predicted][token] + 1
            other = sum(
                self.word_counts[label][token] + 1
                for label in TRAINING_DATA
                if label != predicted
            ) / 2
            contributions[token] = math.log(own / other)
        keywords = [word for word, _ in sorted(contributions.items(), key=lambda item: item[1], reverse=True)[:5]]
        return predicted, probabilities, keywords


engine = SentimentEngine(TRAINING_DATA)
app = FastAPI(
    title="AI Guru #54 - Vietnamese Sentiment Mini AI",
    version="1.0.0",
    description="Ứng dụng AI nhỏ dùng mô hình Naive Bayes để phân loại cảm xúc tiếng Việt.",
)


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=2, max_length=1000, examples=["Ứng dụng chạy nhanh và rất dễ dùng"])


class AnalyzeResponse(BaseModel):
    label: str
    label_code: str
    confidence: float
    probabilities: dict[str, float]
    keywords: list[str]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": "multinomial-naive-bayes"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    predicted, probabilities, keywords = engine.predict(payload.text)
    confidence = probabilities[predicted]
    logger.info(
        "Prediction label=%s confidence=%.4f text_length=%s",
        predicted,
        confidence,
        len(payload.text),
    )
    return AnalyzeResponse(
        label=LABELS[predicted],
        label_code=predicted,
        confidence=round(confidence, 4),
        probabilities={LABELS[key]: round(value, 4) for key, value in probabilities.items()},
        keywords=keywords,
    )


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    examples = [
        "Ứng dụng chạy nhanh, giao diện đẹp và rất dễ dùng",
        "Đơn hàng của mình đang được vận chuyển",
        "Mình thất vọng vì hệ thống thường xuyên bị lỗi",
    ]
    example_buttons = "".join(
        f'<button class="example" data-text="{escape(item)}">{escape(item)}</button>'
        for item in examples
    )
    return f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Vietnamese Sentiment Mini AI</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, system-ui, sans-serif; }}
    body {{ margin: 0; background: #f4f7fb; color: #10233f; }}
    main {{ max-width: 860px; margin: 60px auto; padding: 24px; }}
    .card {{ background: white; border-radius: 18px; padding: 32px; box-shadow: 0 18px 60px #17335f1f; }}
    h1 {{ margin-top: 0; color: #004aad; }}
    p {{ line-height: 1.65; }}
    textarea {{ box-sizing: border-box; width: 100%; min-height: 130px; padding: 16px; border: 1px solid #b7c5d8; border-radius: 10px; font: inherit; resize: vertical; }}
    .actions {{ display: flex; gap: 12px; margin-top: 14px; align-items: center; }}
    #analyze {{ border: 0; border-radius: 9px; padding: 12px 22px; background: #004aad; color: white; font-weight: 700; cursor: pointer; }}
    .examples {{ display: grid; gap: 8px; margin: 20px 0; }}
    .example {{ text-align: left; padding: 10px 12px; border: 1px solid #d8e0eb; border-radius: 8px; background: #f9fbfe; cursor: pointer; }}
    #result {{ display: none; margin-top: 22px; padding: 18px; border-radius: 10px; background: #eef5ff; }}
    .metric {{ font-size: 1.2rem; font-weight: 700; }}
    code {{ background: #e7edf5; border-radius: 4px; padding: 2px 5px; }}
    footer {{ margin-top: 18px; color: #61728b; font-size: .92rem; }}
  </style>
</head>
<body>
<main>
  <section class="card">
    <h1>Vietnamese Sentiment Mini AI</h1>
    <p>Nhập một câu tiếng Việt. Mô hình Naive Bayes nhỏ sẽ dự đoán cảm xúc tích cực, trung tính hoặc tiêu cực.</p>
    <div class="examples">{example_buttons}</div>
    <textarea id="text" maxlength="1000" placeholder="Ví dụ: Mình rất hài lòng với trải nghiệm này"></textarea>
    <div class="actions"><button id="analyze">Phân tích</button><span id="status"></span></div>
    <div id="result"></div>
    <footer>API docs: <code>/docs</code> - Health check: <code>/health</code></footer>
  </section>
</main>
<script>
  const text = document.querySelector('#text');
  const status = document.querySelector('#status');
  const result = document.querySelector('#result');
  document.querySelectorAll('.example').forEach(button => button.addEventListener('click', () => text.value = button.dataset.text));
  document.querySelector('#analyze').addEventListener('click', async () => {{
    if (text.value.trim().length < 2) {{ status.textContent = 'Hãy nhập một câu.'; return; }}
    status.textContent = 'Đang phân tích...';
    result.style.display = 'none';
    try {{
      const response = await fetch('/api/analyze', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{text: text.value}}) }});
      const data = await response.json();
      if (!response.ok) throw new Error(JSON.stringify(data));
      const probabilities = Object.entries(data.probabilities).map(([label, value]) => `<li>${{label}}: ${{(value * 100).toFixed(1)}}%</li>`).join('');
      result.innerHTML = `<div class="metric">Kết quả: ${{data.label}} (${{(data.confidence * 100).toFixed(1)}}%)</div><ul>${{probabilities}}</ul><div>Từ nổi bật: ${{data.keywords.join(', ') || 'không có'}}</div>`;
      result.style.display = 'block';
      status.textContent = '';
    }} catch (error) {{ status.textContent = 'Không thể gọi API. Hãy xem log container.'; }}
  }});
</script>
</body>
</html>"""