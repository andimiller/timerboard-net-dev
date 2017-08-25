# timerboard-net-dev

```bash
# postgres db
docker run --name timerboard-postgres -e POSTGRES_PASSWORD=foobar -d postgres
# redis db
docker run --name timerboard-redis -d redis:3.2
# and the web service
docker run --link timerboard-postgres:postgres --link timerboard-redis:redis -v /home/andi/timerboard-net-dev/config:/config -e TIMERBOARD_SETTINGS=/config/config.json -p 8081:80 timerboard-net-dev
```
