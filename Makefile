all:
	docker compose up --build -d

clean:
	-docker stop $$(docker ps -a -q)

fclean: clean
	rm -rf postgres_data
	-docker rm $$(docker ps -a -q)
	docker system prune -af

re : fclean all