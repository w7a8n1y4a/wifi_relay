# WiFi Relay

Parameter | Implementation
-- | --
Description | Управляет состоянием реле или транзистора при помощи `PWM`. Принимает управляющие команды в топик `relay_command/pepeunit`
Lang | `Micropython`
Hardware | `esp8266`, `esp32`, `esp32c3`, `esp32s3`, `relay`
Firmware | [RELEASE-1.1.1](https://git.pepemoss.com/pepe/pepeunit/libs/pepeunit_micropython_client/-/releases/1.1.1)
Stack | `pepeunit_micropython_client`
Version | 1.1.1
License | AGPL v3 License
Authors | Ivan Serebrennikov <admin@silberworks.com>

## Schema

<div align="center"><img align="center" src="https://minio.pepemoss.com/public-data/schema/wifi_relay.png"></div>

## Physical IO

Key | Description
-- | --
`client.settings.PIN_RELAY` | Управляющий `PWM` вывод реле или транзистора

## Env variable assignment

Variable | Description
-- | --
`FF_TIMER_COMMAND_ENABLE` | Доступно ли управление по таймеру: `true` или `false`
`PIN_RELAY` | Номер пина к которому подключается реле или транзистор
`PIN_RELAY_PWM_FREQUENCY` | Частота `PWM` сигнала в герцах
`PUBLISH_SEND_INTERVAL` | Частота публикации данных в `last_command/pepeunit` в миллисекундах
`PUC_WIFI_SSID` | Имя сети `WiFi`
`PUC_WIFI_PASS` | Пароль от сети `WiFi`

## Assignment of Device Topics

Topic | Description
-- | --
`last_command/pepeunit` | Отправляет последнюю полученную команду каждые `PUBLISH_SEND_INTERVAL` миллисекунд
`relay_command/pepeunit` | Принимает внешние команды управления

## Work algorithm

1. Подключение к `WiFi`
2. Подключение к `MQTT` Брокеру
3. Инициализация `PWM` пина
4. Запуск ожидания команды из топика `relay_command/pepeunit`
5. Каждые `PUBLISH_SEND_INTERVAL` миллисекунд публикуются последняя полученная команда в `last_command/pepeunit`
6. Команды могут иметь разный `command_type`: `set`, `duration`, `timer`
7. `set` - устанавливает `duty` для `PWM` пина на постояной основе. Пример: `{"command_type": "set", "target_duty": 65536}`
8. `duration` - устанавливает `duty` для `PWM` пина на `duration` миллисекунд. Пример: `{"command_type": "duration", "duration": 3000, "target_duty": 65536}`
9. `timer` - устанавливает `duty` для `PWM` пина на `duration` миллисекунд, но начнёт выполенение команды после наступления `time_run` в миллисекундах. Требует, чтобы `FF_TIMER_COMMAND_ENABLE` был `true`. Пример: `{"command_type": "timer", "duration": 1000, "target_duty": 65536, "time_run": 1766966077037}`
10. `target_duty` внутри команд - указывает скважность `PWM` в диапазоне от `0` до `65536` включительно

## Installation

1. Установите образ `Micropython` указанный в `firmware` на `esp8266`, как это сделано в [руководстве](https://micropython.org/download/ESP8266_GENERIC/)
2. Создайте `Unit` в `Pepeunit`
3. Установите переменные окружения в `Pepeunit`
4. Скачайте архив c программой из `Pepeunit`
5. Распакуйте архив в директорию
6. Загрузите файлы из директории на физическое устройство, например командой: `ampy -p /dev/ttyUSB0 -b 115200 put ./ .`
7. Запустить устройство нажатием кнопки `reset`
