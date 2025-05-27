import time
import paho.mqtt.client as mqtt
from sensors import get_fake_ph, get_fake_turbidity, get_fake_temperature
from pump import activate_pump

def publish_data():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect("test.mosquitto.org", 1883, 60)

    ph = get_fake_ph()
    turbidity = get_fake_turbidity()
    temp = get_fake_temperature()

    client.publish("monitoramento/ph", ph)
    client.publish("monitoramento/turbidez", turbidity)
    client.publish("monitoramento/temperatura", temp)

    print(f"Publicado: pH={ph}, Turbidez={turbidity}, Temperatura={temp}")

if __name__ == "__main__":
    while True:
        activate_pump(duration=5)
        publish_data()
        time.sleep(10)  