SHELL := /bin/sh

.PHONY: dev docker-up docker-down start worker-local test

dev:
	# Start dev orchestrator (PowerShell helper)
	@powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start_all.ps1

docker-up:
	@docker compose up --build -d redis worker

docker-down:
	@docker compose down

start:
	@streamlit run app.py

worker-local:
	@python scripts/worker.py

test:
	@python -m pytest -q tests
