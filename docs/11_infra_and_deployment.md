# 11. 인프라 및 배포

## 목적

이 문서는 DesignFlow AI Builder의 인프라 아키텍처와 배포 전략을 정의한다. 개발 환경, 컨테이너화, 환경 변수 관리를 포함한다.

---

## 핵심 결정 사항

### 1. Docker Compose 기반 개발 환경
모든 서비스(web, api, db)를 컨테이너로 실행하여 환경 일관성 보장.

### 2. 개발/프로덕션 환경 분리
- `docker-compose.yml`: 개발 (볼륨 마운트, 핫리로드)
- `docker-compose.prod.yml`: 프로덕션 (최적화 빌드)

### 3. 환경 변수 중앙 관리
`.env.example` 파일로 필수 변수 문서화. 실제 값은 `.gitignore` 처리.

---

## 선택 이유

| 결정 | 이유 |
|------|------|
| Docker Compose | 로컬-프로덕션 환경 일치, 설정 재현성 |
| PostgreSQL 16 | LTS, JSONB 성능 우수 |
| 분리된 컴포즈 파일 | 개발 편의성과 프로덕션 보안 분리 |

---

## 향후 영향

- Docker 기반으로 클라우드(GCP, AWS, Railway) 배포 용이
- 환경 변수 구조가 명확하므로 비밀 관리 서비스(Vault, AWS Secrets) 전환 용이

---

## 서비스 아키텍처

```
┌─────────────────────────────────────────────┐
│              Docker Network                  │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  web     │  │  api     │  │  db      │  │
│  │ Next.js  │  │ FastAPI  │  │ Postgres │  │
│  │ :3000    │  │ :8000    │  │ :5432    │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │        │
└───────┼──────────────┼──────────────┼────────┘
        │              │              │
     브라우저        웹 서버         내부
     직접 접근       → api          전용
```

---

## 컨테이너 설정

### docker-compose.yml (개발)

```yaml
version: '3.9'

services:
  web:
    build:
      context: ./apps/web
      dockerfile: ../../infra/docker/Dockerfile.web
    ports:
      - "3000:3000"
    volumes:
      - ./apps/web:/app
      - /app/node_modules
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - api

  api:
    build:
      context: ./apps/api
      dockerfile: ../../infra/docker/Dockerfile.api
    ports:
      - "8000:8000"
    volumes:
      - ./apps/api:/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://designflow:password@db:5432/designflow
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=designflow
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=designflow
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U designflow"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

---

## 환경 변수 명세

### 필수 변수

| 변수명 | 예시 값 | 설명 |
|--------|---------|------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | DB 연결 문자열 |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Claude API 키 |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | 프론트엔드가 API를 호출하는 URL |

### 선택 변수

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `AI_MODEL` | `claude-sonnet-4-6` | 사용할 AI 모델 |
| `AI_MAX_TOKENS` | `4096` | AI 응답 최대 토큰 |
| `LOG_LEVEL` | `INFO` | 로그 레벨 |
| `MAX_FILE_SIZE_MB` | `10` | 최대 업로드 파일 크기 |
| `CORS_ORIGINS` | `http://localhost:3000` | CORS 허용 오리진 |

---

## Dockerfile 설계

### Dockerfile.web (Next.js)

```dockerfile
FROM node:20-alpine AS base

# 의존성 설치
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# 개발 단계
FROM base AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

### Dockerfile.api (FastAPI)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

## 포트 매핑

| 서비스 | 내부 포트 | 외부 포트 | 용도 |
|--------|---------|---------|------|
| web | 3000 | 3000 | Next.js 개발 서버 |
| api | 8000 | 8000 | FastAPI |
| db | 5432 | 5432 | PostgreSQL (개발 시 직접 접근) |

---

_작성 에이전트: Infra Agent_
_최종 수정: 2026-03-26_
