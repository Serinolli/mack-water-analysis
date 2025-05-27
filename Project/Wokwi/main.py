from machine import Pin, ADC
import time
import network
import ujson
from umqtt.simple import MQTTClient

# CONFIGURAÇÕES
SSID = "SuaRedeWiFi"         
PASSWORD = "SuaSenhaWiFi"  

MQTT_BROKER = "test.mosquitto.org"
MQTT_TOPIC = "water/quality"

# LEDs
led_blue = Pin(5, Pin.OUT)     # LED azul = início da leitura
led_ph = Pin(12, Pin.OUT)      # LED verde para pH
led_turb = Pin(14, Pin.OUT)    # LED verde para turbidez
led_temp = Pin(27, Pin.OUT)    # LED verde para temperatura

# ADC (Sensores simulados)
adc_ph = ADC(Pin(32))       # Sensor de pH
adc_turb = ADC(Pin(33))     # Sensor de turbidez
adc_temp = ADC(Pin(34))     # Sensor de temperatura

for adc in [adc_ph, adc_turb, adc_temp]:
    adc.atten(ADC.ATTN_11DB)
    adc.width(ADC.WIDTH_10BIT)

# Conecta à rede Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Conectando ao Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Conectado:", wlan.ifconfig())

# Conecta ao broker MQTT
def connect_mqtt():
    client = MQTTClient("esp32client", MQTT_BROKER)
    client.connect()
    print("MQTT conectado.")
    return client

# Lê um sensor e acende o LED correspondente por 1 segundo
def read_sensor(adc, led):
    led.on()
    time.sleep(1)
    value = adc.read()
    led.off()
    return value

def main():
    connect_wifi()
    client = connect_mqtt()
    while True:
        led_blue.on()  # Inicia leitura
        ph = read_sensor(adc_ph, led_ph)
        turb = read_sensor(adc_turb, led_turb)
        temp = read_sensor(adc_temp, led_temp)

        # Publica JSON
        payload = ujson.dumps({
            "temperature": temp,
            "turbidity": turb,
            "ph": ph
        })

        client.publish(MQTT_TOPIC, payload)
        print("Enviado:", payload)

        led_blue.off()
        time.sleep(10)  # Aguarda próximo ciclo

main()
