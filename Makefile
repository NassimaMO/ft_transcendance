all:
	docker compose up --build -d

clean:
	-docker stop $$(docker ps -a -q)

fclean: clean
	-docker rm $$(docker ps -a -q)
	docker system prune -af

re : fclean all