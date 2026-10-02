FROM python:3.12-slim

# Giữ log hiển thị ngay lập tức và không tạo file .pyc trong container.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Cài dependency ở layer riêng để tận dụng Docker build cache.
COPY requirements.txt ./
RUN pip install --no-cache-dir --requirement requirements.txt

# Không chạy web server bằng tài khoản root.
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser

# Chỉ source code ứng dụng được đưa vào image.
COPY --chown=appuser:appgroup app/ ./app/

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
