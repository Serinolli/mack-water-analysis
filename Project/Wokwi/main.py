print("Code started at target ESP32!")

from machine import Pin, ADC
import time
import network
import ujson
from umqtt.simple import MQTTClient

ph_sensor = ADC(Pin(32))  # Potenciômetro para pH (GPIO32)
turbidity_sensor = ADC(Pin(33))  # Potenciômetro para turbidez (GPIO33)
relay = Pin(17, Pin.OUT)  # Relé (GPIO17)

for adc in [ph_sensor, turbidity_sensor]:
    adc.atten(ADC.ATTN_11DB)  # Atenuação para 0-3.6V
    adc.width(ADC.WIDTH_10BIT)  # Resolução de 10 bits (0-1023)

# Wi-fi
SSID = "Wokwi-GUEST"  
PASSWORD = ""

# MQTT
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "water/quality"
MQTT_CLIENT_ID = "esp32_water_monitor"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Conectando ao Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(0.5)
    print("Conectado:", wlan.ifconfig())

def connect_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("MQTT conectado.")
    return client

def read_ph():
    value = ph_sensor.read()  # Valor bruto (0-1023)
    print("pH raw value:", value)  # Debug: valor bruto do ADC
    voltage = value * 3.6 / 1023  # Converte para tensão (0-3.6V)
    ph = 3.5 * voltage  # Aproximação linear para pH (0-14)
    return ph

def read_turbidity():
    value = turbidity_sensor.read()  # Valor bruto (0-1023)
    print("Turbidity raw value:", value)  # Debug: valor bruto do ADC
    voltage = value * 3.6 / 1023  # Converte para tensão (0-3.6V)
    turbidity = voltage * 100  # Aproximação para turbidez (0-100 NTU)
    return turbidity

def main(client=None):
    while True:
        print("Starting new cycle...")

        # Liga a bomba (relé) e simula o tempo de amostragem
        relay.value(1)
        print("Bomba ligada")
        time.sleep(2)  

        # Lê os sensores
        ph = read_ph()
        turbidity = read_turbidity()
        temp = 25.0  # Valor fixo para temperatura

        relay.value(0)
        print("Bomba desligada")

        payload = ujson.dumps({
            "temperature": temp,
            "turbidity": turbidity,
            "ph": ph
        })
        print(f"Enviado: {payload}")
     
        try:
            client.publish(MQTT_TOPIC, payload)
        except Exception as e:
            print("Erro ao publicar MQTT:", e)

        time.sleep(5) 

try:
    connect_wifi()
    mqtt_client = connect_mqtt()
    main(mqtt_client)
except Exception as e:
    print("Erro geral:", e)
    while True:
        time.sleep(1) 
