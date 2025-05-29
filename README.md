# Monitoramento da Qualidade da Água com IoT e Protocolo MQTT

Este projeto apresenta um sistema embarcado baseado no ESP32 para o monitoramento contínuo da qualidade da água. O sistema é capaz de medir parâmetros ambientais como **pH**, **turbidez** e **temperatura**, com publicação dos dados via protocolo **MQTT** para integração em plataformas remotas (como dashboards no Node-RED).

A implementação foi feita em **MicroPython**, com simulação no ambiente [Wokwi](https://wokwi.com/) e testes reais viabilizados via broker público MQTT.

## Funcionalidades
- Leitura periódica dos sensores de pH, turbidez e temperatura
- Controle automatizado de uma bomba (via relé)
- Envio de dados em formato JSON para o broker MQTT
- Simulação completa via Wokwi
- Visualização dos dados em tempo real com Node-RED

---

## Como usar

### 1. Simulação via Wokwi
Abra o projeto na plataforma Wokwi com suporte ao ESP32 (arquivo `diagram.json`):
- Conecte os sensores simulados e o relé conforme o circuito
- Rode o código `main.py` com MicroPython

### 2. Execução com hardware real
- Alimente o ESP32 com 5V
- Conecte sensores reais (pH, turbidez, DS18B20) aos pinos especificados
- Certifique-se de que o ESP32 esteja conectado a uma rede Wi-Fi com acesso à internet

---

## 🔧 Hardware Utilizado

| Componente | Modelo / Simulação |
|------------|---------------------|
| Microcontrolador | ESP32 DevKit v4 |
| Sensor de pH     | Simulado via potenciômetro |
| Sensor de turbidez | Simulado via potenciômetro |
| Sensor de temperatura | DS18B20 |
| Atuador | Módulo Relé |
| Resistor de pull-up | 4,7kΩ (para DS18B20) |

---

## 🛠 Protocolo de Comunicação

- **Protocolo:** MQTT
- **Broker:** `test.mosquitto.org` (público)
- **Porta:** 1883
- **Tópico:** `water/quality`
- **Payload (JSON):**

```json
{
  "ph": 6.7,
  "turbidity": 40.5,
  "temperature": 22.1
}
