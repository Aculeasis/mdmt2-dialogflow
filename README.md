## Dialogflow for mdmTerminal2
Направляет запросы в [Dialogflow](https://dialogflow.cloud.google.com/).

## Установка
### Только для armv6l (Raspberry Pi Zero W)
Перед установкой нужно собрать пакет `grpcio` из исходников, установка бинарного пакета приведет к ошибке **Illegal Instruction** [issue#235](https://github.com/googlesamples/assistant-sdk-python/issues/235):
```
mdmTerminal2/env/bin/python -m pip install --upgrade --no-binary :all: grpcio
```
---
После создания агента в консоли Dialogflow нужно перейти по ссылке `Service Account`, выбрать в действиях создание ключа и создать ключ в JSON.
Скачанный файл сохранить в `mdmTerminal2/src/data` под именем `dialogflow-credentials.json`.

Установить зависимости и плагин:
```
mdmTerminal2/env/bin/python -m pip install dialogflow==1.1.0
cd mdmTerminal2/src/plugins
git clone https://github.com/Aculeasis/mdmt2-dialogflow
```
И перезапустить [терминал](https://github.com/Aculeasis/mdmTerminal2).

## Настройки
Можно отключить интеграцию с MJD в `settings.ini`:
```ini
[smarthome]
disable_http = on
```

## Использование
Плагин только проговаривает `fulfillment_text` или переспрашивает с ним (если `all_required_params_present == False`).
Если нужна обработка сценариев, то лучше всего форкнуть репозиторий и реализовать ее [самостоятельно](https://github.com/Aculeasis/mdmt2-dialogflow/blob/master/main.py#L91).
