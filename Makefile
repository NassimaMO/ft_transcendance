all: dev

dev:
	docker compose -f docker-compose.yml --env-file dev.env up --build -d
	@echo You can now go to http://localhost:8000

prod:
	docker compose -f docker-compose.prod.yml --env-file prod.env up --build -d
	@echo You can now go to https://localhost

clean:
	@echo "Stoping containers..."
	-@docker stop $$(docker ps -a -q)

fclean: clean
	@docker compose down -v
	@-docker rm $$(docker ps -a -q)
	@docker system prune -af

re : fclean all