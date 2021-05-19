redis:
	docker run -p 6379:6379 -d --rm redis
postgres:
	docker run -e "POSTGRES_PASSWORD=password" -e "POSTGRES_USER=organizeit" -e "POSTGRES_DB=organizeit" -v pgdata:/var/lib/postgresql -p 5433:5432 --name=pg-organize-it --rm postgres
