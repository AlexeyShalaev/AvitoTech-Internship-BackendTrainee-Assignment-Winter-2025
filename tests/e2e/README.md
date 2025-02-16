# End to End Testing

## Установка зависимостей
```bash
make install
```

## Запуск
```bash
make test
```

## Пример работы:
```python
============================================================================================== test session starts ==============================================================================================
platform win32 -- Python 3.12.2, pytest-8.2.2, pluggy-1.5.0
rootdir: C:\Users\Alex Shalaev\YandexDisk\IT\Проекты\AvitoTech-Internship-BackendTrainee-Assignment-Winter-2025\tests\e2e
configfile: pytest.ini
plugins: anyio-4.8.0, asyncio-0.23.8, cov-5.0.0, deadfixtures-2.2.1, mock-3.14.0, repeat-0.9.3
asyncio: mode=Mode.STRICT
collected 2 items                                                                                                                                                                                                

tests/scenarios/test_buying_merch.py::test_buying_merch 
------------------------------------------------------------------------------------------------ live log setup -------------------------------------------------------------------------------------------------
INFO     httpx:_client.py:1740 HTTP Request: POST http://localhost:8081/api/auth "HTTP/1.1 200 OK"
INFO     httpx:_client.py:1740 HTTP Request: POST http://localhost:8081/api/auth "HTTP/1.1 200 OK"
INFO     httpx:_client.py:1740 HTTP Request: POST http://localhost:8081/api/auth "HTTP/1.1 200 OK"
------------------------------------------------------------------------------------------------- live log call -------------------------------------------------------------------------------------------------
INFO     httpx:_client.py:1740 HTTP Request: GET http://localhost:8080/api/info "HTTP/1.1 200 OK"
INFO     httpx:_client.py:1740 HTTP Request: POST http://localhost:8080/api/merch/buy/hoody "HTTP/1.1 200 OK"
INFO     httpx:_client.py:1740 HTTP Request: POST http://localhost:8080/api/merch/buy/hoody "HTTP/1.1 200 OK"
INFO     httpx:_client.py:1740 HTTP Request: POST http://localhost:8080/api/merch/buy/hoody "HTTP/1.1 200 OK"
INFO     httpx:_client.py:1740 HTTP Request: GET http://localhost:8080/api/info "HTTP/1.1 200 OK"
INFO     httpx:_client.py:1740 HTTP Request: POST http://localhost:8080/api/merch/buy/hoody "HTTP/1.1 412 Precondition Failed"
PASSED                                                                                                                                                                                                     [ 50%]
tests/scenarios/test_send_coins.py::test_sending_coins
------------------------------------------------------------------------------------------------- live log call -------------------------------------------------------------------------------------------------
INFO     httpx:_client.py:1740 HTTP Request: GET http://localhost:8080/api/info "HTTP/1.1 200 OK"
INFO     httpx:_client.py:1740 HTTP Request: GET http://localhost:8080/api/info "HTTP/1.1 200 OK"
INFO     httpx:_client.py:1740 HTTP Request: POST http://localhost:8080/api/coins/send "HTTP/1.1 200 OK"
INFO     httpx:_client.py:1740 HTTP Request: GET http://localhost:8080/api/info "HTTP/1.1 200 OK"
INFO     httpx:_client.py:1740 HTTP Request: GET http://localhost:8080/api/info "HTTP/1.1 200 OK"
PASSED                                                                                                                                                                                                     [100%]

============================================================================================== 2 passed in 12.31s ===============================================================================================
```