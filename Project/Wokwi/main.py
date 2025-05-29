print("Iniciando ESP32 - Monitoramento da Qualidade da Água")

from machine import Pin, ADC
import onewire, ds18x20
import time
import network
import ujson
from umqtt.simple import MQTTClient
import time

# --- Configuração dos pinos ---
ph_sensor = ADC(Pin(32))
turbidity_sensor = ADC(Pin(33))

ds_pin = Pin(4)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
print('Dispositivos DS encontrados:', roms)

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
    print("Wi-Fi conectado! IP:", wlan.ifconfig()[0])

def connect_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.connect()
    print("Conectado ao broker MQTT.")
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
        return round(temp, 2)
    except:
        return 25.0

def main(client):
    last_payload = None
    while True:
        print("\n--- Novo ciclo de leitura ---")

        # Medida do tempo de resposta do atuador (relé)
        start_relay = time.ticks_ms()
        relay.value(1)
        relay_end = time.ticks_ms()
        relay_time = time.ticks_diff(relay_end, start_relay)
        print(f"Tempo de resposta do atuador (relé): {relay_time} ms")

        time.sleep(2)  # bomba ligada

        # Medidas de tempo para sensores
        # Sensor de pH
        start_ph = time.ticks_ms()
        ph = read_ph()
        end_ph = time.ticks_ms()
        ph_duration = time.ticks_diff(end_ph, start_ph)
        print(f"Tempo de leitura do sensor de pH: {ph_duration} ms")

        # Sensor de turbidez
        start_turb = time.ticks_ms()
        turbidity = read_turbidity()
        end_turb = time.ticks_ms()
        turb_duration = time.ticks_diff(end_turb, start_turb)
        print(f"Tempo de leitura do sensor de turbidez: {turb_duration} ms")

        # Sensor de temperatura
        start_temp = time.ticks_ms()
        temp = read_temperature()
        end_temp = time.ticks_ms()
        temp_duration = time.ticks_diff(end_temp, start_temp)
        print(f"Tempo de leitura do sensor de temperatura: {temp_duration} ms")

        relay.value(0)
        print("Bomba desligada.")

        # Monta e envia os dados
        payload_dict = {
            "temperature": temp,
            "turbidity": turbidity,
            "ph": ph
        }
        payload = ujson.dumps(payload_dict)

        # Medida do tempo até publicação no MQTT
        start_pub = time.ticks_ms()
        try:
            client.publish(MQTT_TOPIC, payload)
            end_pub = time.ticks_ms()
            pub_time = time.ticks_diff(end_pub, start_pub)
            print(f"Dados publicados: {payload}")
            print(f"Tempo de envio MQTT: {pub_time} ms")
            last_payload = payload
        except Exception as e:
            print("Erro ao publicar no MQTT:", e)

        time.sleep(5)

try:
    connect_wifi()
    mqtt_client = connect_mqtt()
    main(mqtt_client)
except Exception as e:
    print("Erro na execução principal:", e)
    while True:
        time.sleep(1)
