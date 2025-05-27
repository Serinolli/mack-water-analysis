# Mosquitto Commands

## Publisher
> mosquitto_pub -h test.mosquitto.org -t water/quality -m '{\"temperature\": 17.2, \"turbidity\": 0.5, \"ph\": 2}'

## Subscriber
> mosquitto_sub -h test.mosquitto.org -t water/quality

## UI 
> node-red