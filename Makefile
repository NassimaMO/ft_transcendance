LOCAL_IP	:= $(shell ./get_ip.sh)
ENV_FILE	:= dev.env
DOCKER_FILE	:= docker-compose.yml

all: dev

dev: get_ip docker
	@echo "You can now go to : \n - http://localhost:8000 in this device\n - http://$(LOCAL_IP):8000 in another device"

prod: ENV_FILE=prod.env DOCKER_FILE=docker-compose.prod.yml
prod: get_ip docker
	@echo "You can now go to : \n - https://localhost in this device\n - https://$(LOCAL_IP) in another device"

get_ip:
	@grep -qF "LOCAL_IP=" $(ENV_FILE) || echo "\nLOCAL_IP=$(LOCAL_IP)" >> $(ENV_FILE)

docker:
	docker compose -f $(DOCKER_FILE) --env-file $(ENV_FILE) up --build -d

clean:
	@-docker stop $$(docker ps -a -q)
	@-docker rm $$(docker ps -a -q)

fclean: clean
	@-docker volume rm $$(docker volume ls -q)
	@docker system prune -af

re: fclean all

.PHONY: all clean fclean re