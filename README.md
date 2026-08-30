# Деплой приложения на PaaS (Devops)

[![hexlet-check](https://github.com/VorobyevAM/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/VorobyevAM/devops-engineer-from-scratch-project-313/actions)
[![CI](https://github.com/VorobyevAM/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/VorobyevAM/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml)

Создайте и задеплойте веб-приложение, подключите базу данных и настройке мониторинг с алертингом

Учебный проект Хекслета: https://ru.hexlet.io/programs/devops-engineer-from-scratch


## Стек

- Python
- Flask
- uv
- Docker
- Render

## Установка

```bash
git clone https://github.com/VorobyevAM/devops-engineer-from-scratch-project-313.git
cd devops-engineer-from-scratch-project-313
uv sync --group dev
```

Для запуска с мониторингом ошибок можно задать переменную окружения `SENTRY_DSN`.

## Использование

Запуск приложения:

```bash
make run
```

Приложение стартует на порту `8080`.

Проверка маршрута:

```bash
curl http://127.0.0.1:8080/ping
```

Ожидаемый ответ:

```text
pong
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
docker run --rm -p 8080:8080 -e PORT=8080 devops-engineer-from-scratch-project-313
```

## Деплой

Приложение развернуто на Render:

- Ссылка будет добавлена после создания сервиса на Render

Для Render Web Service используется `Dockerfile`. В настройках сервиса нужно задать:

- `PORT=8080`
- `DATABASE_URL`
- `SENTRY_DSN`

---

<details>
<summary>Автоматические тесты Хекслета</summary>

Тесты запускаются на каждый коммит. За запуск отвечает файл `.github/workflows/hexlet-check.yml` — не удаляйте и не переименовывайте ни его, ни репозиторий.

</details>

## О Хекслете

[Хекслет](https://ru.hexlet.io/) — школа программирования: авторские программы обучения с практикой, поддержкой наставников и реальными проектами, которые остаются в резюме. Этот репозиторий — один из таких проектов.
