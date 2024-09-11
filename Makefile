LOCAL_IP	:= $(shell ./get_ip.sh)
PROFILE		:= development
ENV_FILE	:= dev.env
DOCKER_FILE	:= docker-compose.dev.yml
WAIT		:=

all: dev

dev: get_ip docker
	@echo "You can now go to : \n - http://localhost:8000 in this device\n - http://$(LOCAL_IP):8000 in another device"

prod: WAIT=--wait
prod: PROFILE=production
prod: ENV_FILE=prod.env
prod: DOCKER_FILE=docker-compose.prod.yml
prod: get_ip docker
	@echo "You can now go to : \n - https://localhost in this device\n - https://$(LOCAL_IP) in another device"

get_ip:
	@grep -qF "DJANGO_ALLOWED_HOSTS=" $(ENV_FILE) || echo "\nDJANGO_ALLOWED_HOSTS=$(LOCAL_IP)" >> $(ENV_FILE)

docker:
	docker compose --env-file $(ENV_FILE) -f docker-compose.yml -f $(DOCKER_FILE) --profile $(PROFILE) up --build -d $(WAIT)

clean:
	@-docker compose down
	@-docker volume rm $$(docker volume ls -q)

fclean: clean
	@docker system prune -af

re: fclean all

.PHONY: all clean fclean re
