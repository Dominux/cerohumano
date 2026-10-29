up:
	docker compose up -d --build --force-recreate

down:
	docker compose down

run_dev_front:
	cd frontend && pnpm dev
