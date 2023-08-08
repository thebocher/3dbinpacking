# Installation
1. Install [docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script)
2. Install docker [compose](https://docs.docker.com/compose/install/linux/#install-using-the-repository)

# Running
This will download mysql image and download dependencies for project
```
docker compose up --build -d
```

# Maintaining
## Check logs
```
docker compose logs api              # show all logs
docker compose logs api --tail 100   # show only last 100 rows
docker compose logs api -f           # follow new logs
```
## Stopping
```
docker compose down       # stop both db and server
docker compose down api   # stop only server
```
## Entering container
If it is already running:
```
docker compose exec -it api bash
```
If it's stopped:
```
docker compose run api bash
```
