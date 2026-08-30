# Деплой приложения на PaaS (Devops)

[![hexlet-check](https://github.com/VorobyevAM/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/VorobyevAM/devops-engineer-from-scratch-project-313/actions)
[![CI](https://github.com/VorobyevAM/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/VorobyevAM/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml)

Создайте и задеплойте веб-приложение, подключите базу данных и настройке мониторинг с алертингом

Учебный проект Хекслета: https://ru.hexlet.io/programs/devops-engineer-from-scratch


## Стек

- Python
- FastAPI
- SQLModel
- PostgreSQL
- Node.js
- uv
- Docker
- Nginx
- Render

## Установка

```bash
git clone https://github.com/VorobyevAM/devops-engineer-from-scratch-project-313.git
cd devops-engineer-from-scratch-project-313
uv sync --group dev
npm install
```

Основные переменные окружения:

- `DATABASE_URL` — строка подключения к базе данных
- `BASE_URL` — базовый адрес приложения для формирования `short_url`
- `SENTRY_DSN` — DSN для мониторинга ошибок
- `PORT` — порт запуска приложения

Для локальной UI-проверки нужен Node.js LTS не ниже 20.

## Использование

Запуск приложения:

```bash
DATABASE_URL=sqlite:///./app.db BASE_URL=http://127.0.0.1:8080 make run FRAMEWORK=fastapi
```

Бэкенд стартует на `http://127.0.0.1:8080`, фронтенд на `http://localhost:5173`.

Проверка маршрута:

```bash
curl http://127.0.0.1:8080/ping
```

Ожидаемый ответ:

```text
pong
```

Примеры API:

```bash
curl http://127.0.0.1:8080/api/links
```

```bash
curl -X POST http://127.0.0.1:8080/api/links \
  -H "Content-Type: application/json" \
  -d '{"original_url":"https://example.com/long-url","short_name":"exmpl"}'
```

```bash
curl -i http://127.0.0.1:8080/r/exmpl
```

Фронтенд можно запускать отдельно:

```bash
make run-frontend
```

Бэкенд можно запускать отдельно:

```bash
make run-backend FRAMEWORK=fastapi
```

Запуск тестов:

```bash
make test
```

Запуск линтера:

```bash
make lint
```

CI запускает `pytest` и `ruff` автоматически через GitHub Actions workflow [`.github/workflows/ci.yml`](/Users/anatoly/PycharmProjects/devops-engineer-from-scratch-project-313/.github/workflows/ci.yml).

Сборка Docker-образа:

```bash
docker build -t devops-engineer-from-scratch-project-313 .
```

Запуск контейнера:

```bash
docker run --rm -p 8080:80 \
  -e PORT=80 \
  -e DATABASE_URL=sqlite:///./app.db \
  -e BASE_URL=http://127.0.0.1:8080 \
  devops-engineer-from-scratch-project-313
```

## Деплой

Приложение развернуто на Render:

- Ссылка будет добавлена после создания сервиса на Render

Для Render Web Service используется `Dockerfile`. В настройках сервиса нужно задать:

- `PORT=80`
- `DATABASE_URL`
- `BASE_URL`
- `SENTRY_DSN`

Для PostgreSQL на Render можно использовать внутренний URL базы, а приложение само нормализует схему `postgres://` в формат, который понимает SQLAlchemy.

## UI

Для локальной разработки фронтенд-пакет запускается командой `start-hexlet-devops-deploy-crud-frontend`, а запросы к API разрешены через CORS для `http://localhost:5173`.

В production UI раздаётся Nginx из каталога `/app/public`, а запросы к `/api/*`, `/r/*` и `/ping` проксируются в backend внутри того же контейнера.

После деплоя на Render нужно проверить:

- корень `/` открывает веб-интерфейс
- `/api/links` отвечает через Nginx без ошибок
- короткие ссылки `/r/{short_name}` редиректят корректно

---

<details>
<summary>Автоматические тесты Хекслета</summary>

Тесты запускаются на каждый коммит. За запуск отвечает файл `.github/workflows/hexlet-check.yml` — не удаляйте и не переименовывайте ни его, ни репозиторий.

</details>

## О Хекслете

[Хекслет](https://ru.hexlet.io/) — школа программирования: авторские программы обучения с практикой, поддержкой наставников и реальными проектами, которые остаются в резюме. Этот репозиторий — один из таких проектов.
