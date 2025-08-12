# llm\_api\_assistant

Проект `llm_api_assistant` — минимальный бекенд на FastAPI, который оборачивает локальный LLM-сервер (Ollama) в REST API, сохраняет историю чатов в PostgreSQL и предоставляет простую JWT-аутентификацию.

README даёт инструкции по развёртыванию через Docker Compose, использованию API и устранению типичных проблем с Ollama.

---

# Содержание

1. Что в проекте
2. Быстрый старт (Docker Compose)
3. Переменные окружения
4. API — конечные точки
5. Работа с Ollama (модели, загрузка, кэш)
6. Отладка и типичные проблемы
7. Тестирование
8. Структура проекта

---

# 1. Что в проекте

* FastAPI приложение (эндпоинты `auth` и `chat`).
* Хранение пользователей и сообщений в PostgreSQL (SQLAlchemy Async).
* Вызов локального LLM через Ollama HTTP API (`http://ollama:11434` внутри Docker-сети).
* Dockerfile и docker-compose.yml для локальной разработки.
* Простейшая JWT-аутентификация (login endpoint использует OAuth2PasswordRequestForm).
* Логирование запросов/ответов (включая request\_id для отладки).

---

# 2. Быстрый старт (Docker Compose)

1. Клонируйте репозиторий и перейдите в папку проекта:

```bash
git clone https://github.com/<your>/llm_api_assistant.git
cd llm_api_assistant
```

2. Скопируйте пример .env:

```bash
cp .env.example .env
# отредактируйте .env при необходимости
```

3. Запустите контейнеры:

```bash
docker compose up --build -d
```

4. Проверьте статус:

```bash
docker compose ps
curl http://localhost:8000/docs   # Swagger UI
curl http://localhost:11434       # Ollama: ожидание ответа "Ollama is running"
curl http://localhost:11434/api/tags  # список моделей
```

> Примечание: если Ollama поднят внутри контейнера, в `api` должен использоваться URL `http://ollama:11434`. Если запускаете FastAPI на хосте — используйте `http://localhost:11434`.

---

# 3. Переменные окружения

Файл `.env.example` (пример):

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/llm_db
OLLAMA_API_URL=http://ollama:11434/api/generate
SECRET_KEY=your_secret_key_here
```

* `DATABASE_URL` — URL для подключения к PostgreSQL (используется `asyncpg`).
* `OLLAMA_API_URL` — адрес Ollama API (в Docker: `http://ollama:11434/api/generate`).
* `SECRET_KEY` — секрет для подписи JWT.

---

# 4. API — конечные точки

> Все запросы описаны в Swagger UI: `http://localhost:8000/docs`

## Auth

* `POST /auth/login`
  Параметры: `username`, `password` (OAuth2PasswordRequestForm).
  Возвращает: `{ "access_token": "...", "token_type": "bearer" }`.

> Примечание: регистрация/создание пользователя можно реализовать либо через админ-скрипт, либо добавить endpoint `/auth/register` при необходимости.

## Chat

* `POST /chat/` — защищённый endpoint (требуется Authorization: Bearer <token>)
  Тело (пример):

  ```json
  {
    "prompt": "Hello LLM"
  }
  ```

  Ответ (пример):

  ```json
  {
    "request_id": "uuid",
    "prompt": "Hello LLM",
    "response": "текст ответа LLM"
  }
  ```

---

# 5. Работа с Ollama (загрузка моделей, кэш и поведение)

* Ollama в образе `ollama/ollama` не содержит модели по умолчанию — модели скачиваются отдельно (`ollama pull <model>` или `ollama run <model>`).
* В `docker-compose.yml` мы монтируем volume `ollama_data:/root/.ollama` — модели и их кэш сохраняются в этом томе и сохраняются между перезапусками контейнера (не удаляются при `docker compose down`, если не использовать `-v`).

### Как загрузить модель (в контейнере):

```bash
docker exec -it <ollama_container_name> ollama pull llama3
# или
docker exec -it <ollama_container_name> ollama run llama3
```

### Проверить список доступных моделей:

```bash
curl http://localhost:11434/api/tags
# -> {"models":[...]}
```

---

# 6. Отладка и типичные проблемы

### 6.1. Ошибка: `Error communicating with LLM server: All connection attempts failed`

* Проверь, запущен ли Ollama:

  ```bash
  curl http://localhost:11434
  # должно вернуть "Ollama is running"
  ```
* Проверь, доступен ли `ollama` из контейнера `api`:

  ```bash
  docker exec -it <api_container> sh
  # затем внутри контейнера
  wget -qO- http://ollama:11434
  ```
* Убедись, что в `docker-compose.yml` контейнеры в одной сети и `api` зависит от `ollama`.

### 6.2. Ошибка: `listen tcp 0.0.0.0:11434: bind: address already in use`

* Порт уже занят локальным процессом или другим контейнером. Найди процесс, освободи порт, или используй другой порт.


### 6.3. Модель не загружается / таймауты

* Проверяй доступную память и CPU для Docker (через Docker Desktop → Resources). Большим моделям требуется много RAM.
* В `docker-compose.yml` можно задать `OLLAMA_MODEL_LOAD_TIMEOUT` (например, `10m`).

---

# 7. Тестирование

* Проект содержит заготовку для тестов в `tests/` (используется `pytest`, `pytest-asyncio`, `httpx`).
* Пример запуска тестов:

```bash
# внутри виртуального окружения / контейнера с тестами
pytest -q
```

* В `tests/conftest.py` используется `httpx.ASGITransport` для интеграционного тестирования FastAPI без запуска сервера.

---

# 8. Структура проекта

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py           # включает роуты
│   ├── auth.py           # JWT/login
│   ├── chat.py           # endpoint /chat (вызов Ollama)
│   ├── models.py         # SQLAlchemy модели User, Message
│   └── database.py       # создание async engine / session
├── tests/
│   ├── conftest.py
│   └── test_chat.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

# Примеры curl-запросов

1. Проверка Ollama:

```bash
curl http://localhost:11434
# -> "Ollama is running"
curl http://localhost:11434/api/tags
# -> {"models":[...]}
```

2. Генерация (пример):

```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3", "prompt":"Hello", "stream":false, "context": []}'
```

3. Вызов FastAPI `/chat/` (после получения токена):

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Do you speak Russian?"}'
```

# Заключение и рекомендации

* Для стабильности LLM в продакшен-приложениях рассмотрите использование vLLM / TGI / HF TGI (под GPU) — эти решения лучше управляют мультипользовательским обслуживанием и изоляцией сессий.
* При любых нестабильностях — сначала проверяйте логи Ollama (`docker logs -f ollama`) и наличие ошибок загрузки модели.

