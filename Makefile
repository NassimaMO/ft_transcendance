all:
	docker compose up --build -d

clean:
	@echo "Stoping containers..."
	-@docker stop $$(docker ps -a -q)

fclean: clean
	@rm -rf postgres_data
	@rm -rf srcs/staticfiles
	@-docker rm $$(docker ps -a -q)
	@docker system prune -af

re : fclean all