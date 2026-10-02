# AI Guru #54 - Docker hóa ứng dụng AI FastAPI

Repository đi kèm tutorial #54, minh họa cách đóng gói một ứng dụng phân loại cảm xúc tiếng Việt bằng FastAPI và Docker.

Ứng dụng dùng mô hình Multinomial Naive Bayes nhỏ được huấn luyện khi khởi động. Không cần GPU, API key hoặc dịch vụ AI bên ngoài.

## Yêu cầu

- Docker Desktop hoặc Docker Engine
- Git
- Git Bash hoặc WSL nếu chạy `run.sh` trên Windows

## Chạy toàn bộ bằng một lệnh

```bash
chmod +x run.sh
./run.sh
```

Mở ứng dụng tại `http://localhost:8000`.

Các địa chỉ hữu ích:

- Giao diện: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## Chạy thủ công

```bash
docker build -t ai-guru-54-dockerize-ai-fastapi:latest .
docker run -d \
  --name ai-guru-54-app \
  -p 8000:8000 \
  ai-guru-54-dockerize-ai-fastapi:latest
```

Xem log:

```bash
docker logs --follow ai-guru-54-app
```

Dừng container:

```bash
docker stop ai-guru-54-app
```

## Gọi API

```bash
curl -s -X POST http://localhost:8000/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":"Ứng dụng chạy nhanh và rất dễ dùng"}'
```

## Kiểm thử cục bộ

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Cấu trúc repository

```text
.
├── app/
│   ├── __init__.py
│   └── main.py
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── run.sh
└── test_app.py
```