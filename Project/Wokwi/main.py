print("Iniciando ESP32 - Monitoramento da Qualidade da Água")

from machine import Pin, ADC
import onewire, ds18x20
import time
import network
import ujson
from umqtt.simple import MQTTClient

# --- Configuração dos pinos ---
ph_sensor = ADC(Pin(32))
turbidity_sensor = ADC(Pin(33))

ds_pin = Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
print('Found DS devices: ', roms)

relay = Pin(17, Pin.OUT)

# --- ADC: 12 bits (0-4095), tensão até 3.6V ---
for adc in [ph_sensor, turbidity_sensor]:
    adc.atten(ADC.ATTN_11DB)
    adc.width(ADC.WIDTH_12BIT)

# --- Wi-Fi ---
SSID = "Wokwi-GUEST"
PASSWORD = ""

# --- MQTT ---
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
    print("Conectado! IP:", wlan.ifconfig()[0])

def connect_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("Conectado ao MQTT.")
    return client

def read_adc(adc, samples=10):
    total = 0
    for _ in range(samples):
        total += adc.read()
        time.sleep_ms(5)
    return total // samples

def read_ph():
    raw = read_adc(ph_sensor)
    voltage = raw * 3.6 / 4095
    ph = 3.5 * voltage
    return round(ph, 2)

def read_turbidity():
    raw = read_adc(turbidity_sensor)
    voltage = raw * 3.6 / 4095
    turbidity = voltage * 100
    return round(turbidity, 2)

def read_temperature():
    try:
        ds_sensor.convert_temp()
        temp = ds_sensor.read_temp(roms[0])
        time.sleep(5)
        return round(temp, 2)
    except:
        return 25.0

def main(client):
    while True:
        print("\n--- Novo Ciclo ---")

        # Liga bomba 
        relay.value(1)
        print("Bomba ligada")
        time.sleep(2)

        # Leitura dos sensores
        ph = read_ph()
        turbidity = read_turbidity()
        temp = read_temperature()

        # Desliga bomba 
        relay.value(0)
        print("Bomba desligada")

        # Publica dados
        payload = ujson.dumps({
            "temperature": temp,
            "turbidity": turbidity,
            "ph": ph
        })

        try:
            client.publish(MQTT_TOPIC, payload)
            print("Publicado:", payload)
        except Exception as e:
            print("Erro MQTT:", e)

        time.sleep(5)


try:
    connect_wifi()
    mqtt_client = connect_mqtt()
    main(mqtt_client)
except Exception as e:
    print("Erro principal:", e)
    while True:
        time.sleep(1)
