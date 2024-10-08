LOCAL_IP	:= $(shell ./get_ip.sh)
PROFILE		:= development
ENV_FILE	:= dev.env
DOCKER_FILE	:= docker-compose.dev.yml

all: dev

dev: PROFILE=development
dev: ENV_FILE=dev.env
dev: DOCKER_FILE=docker-compose.dev.yml
dev: get_ip docker
	@echo "You can now go to : \n - http://localhost:8000 in this device\n - http://$(LOCAL_IP):8000 in another device"

prod: PROFILE=production
prod: ENV_FILE=prod.env
prod: DOCKER_FILE=docker-compose.prod.yml
prod: get_ip docker
	@echo "You can now go to : \n - https://localhost in this device\n - https://$(LOCAL_IP) in another device"

get_ip:
	@chmod 777 get_ip.sh
	@grep -qF "DJANGO_ALLOWED_HOSTS=" $(ENV_FILE) || echo "\nDJANGO_ALLOWED_HOSTS=$(LOCAL_IP)" >> $(ENV_FILE)

docker:
	-docker compose --env-file $(ENV_FILE) -f docker-compose.yml -f $(DOCKER_FILE) --profile $(PROFILE) up --build -d --wait

cli: PROFILE=development
cli: ENV_FILE=dev.env
cli: DOCKER_FILE=docker-compose.dev.yml
cli: get_ip docker
	docker compose --env-file $(ENV_FILE) -f docker-compose.yml -f $(DOCKER_FILE) --profile $(PROFILE) run cli python srcs/api_play.py

clean:
	@-docker compose -f docker-compose.yml -f $(DOCKER_FILE) --profile $(PROFILE) down

fclean: clean
#	@-docker system prune -af
	@-docker volume rm postgres_volume_dev postgres_volume_prod static_volume media_volume

re: fclean all

.PHONY: all clean fclean re
