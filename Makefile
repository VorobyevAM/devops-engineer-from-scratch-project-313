FRAMEWORK ?= fastapi

run:
	@if [ -d node_modules/@hexlet/project-devops-deploy-crud-frontend ] && command -v npx >/dev/null 2>&1; then \
		npx concurrently -k -n backend,frontend "make run-backend FRAMEWORK=$(FRAMEWORK)" "make run-frontend"; \
	else \
		$(MAKE) run-backend FRAMEWORK=$(FRAMEWORK); \
	fi

run-dev:
	npx concurrently -k -n backend,frontend "make run-backend FRAMEWORK=$(FRAMEWORK)" "make run-frontend"

run-backend:
ifeq ($(FRAMEWORK),fastapi)
	uv run uvicorn main:app --host 0.0.0.0 --port 8080
else
	@echo "Unsupported FRAMEWORK: $(FRAMEWORK)"
	@exit 1
endif

run-frontend:
	npx start-hexlet-devops-deploy-crud-frontend

test:
	uv run python -m pytest

lint:
	uv run ruff check .
