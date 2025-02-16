# Load Testing

## Запуск Яндекс Танка

```docker
docker run -v ./:/var/loadtest --net host -it yandex/yandex-tank
```

```bash
yandex-tank -c /load.yaml ammo.txt
```