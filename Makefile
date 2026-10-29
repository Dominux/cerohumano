up:
	docker compose up -d --build --force-recreate

down:
	docker compose down

run_dev_front:
	cd frontend && pnpm dev

rebuild_n_deploy_front:
	docker compose up -d cerohumano_nginx --build
