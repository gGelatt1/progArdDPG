import os.path

import serial
import dearpygui.dearpygui as dpg
import threading
import time
import json
from collections import OrderedDict


class DatiUtili:
    def __init__(self):
        self.tempo = []
        self.temperatura = []
        self.umidita = []
        self.rosso = False
        self.verde = False
        self.n_dati = 10

    def aggiungi_dati(self, _tempo, _temperatura, _umidita, _rosso, _verde):
        self.rosso = _rosso
        self.verde = _verde
        if len(self.tempo) == self.n_dati:
            self.tempo.pop(0)
            self.umidita.pop(0)
            self.temperatura.pop(0)
        self.tempo.append(_tempo)
        self.umidita.append(_umidita)
        self.temperatura.append(_temperatura)


class Grafico:
    def __init__(self, nome, lim_y_b, lim_y_h):
        self.nome = nome
        with dpg.plot(label="Grafico " + nome, height=400, width=800):
            self.y_axis = dpg.add_plot_axis(dpg.mvYAxis, label=nome)
            self.x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Tempo")
            self.graf = dpg.add_line_series([], [], label=nome, parent=self.y_axis)
            dpg.set_axis_limits(self.y_axis, lim_y_b, lim_y_h)

    def aggiorna(self, x, y):
        dpg.set_axis_limits(self.x_axis, x[0], x[-1])
        dpg.set_value(self.graf, [x, y])


class Thermostat:
    def __init__(self, porta):
        self.dati = DatiUtili()
        self.begin_time = time.time()
        self.n_dati = 10
        self.date = time.strftime("%d-%m-%Y")

        self.arduino = serial.Serial(porta, 9600)
        time.sleep(2)  # Attendi che il collegamento sia stabile

        dpg.create_context()

        with dpg.window(label="Thermostat", width=800, height=950):
            dpg.add_text("Temperatura:", tag="temperature")
            dpg.add_text("Umidità:", tag="humidity")
            self.graf_temp = Grafico("Temperatura", -10, 40)
            self.graf_umid = Grafico("Umidità", 0, 100)
            self.led_verde = dpg.draw_circle((200, 20), 10, color=(0, 255, 0, 255), fill=(0, 55, 0, 255))
            self.led_rosso = dpg.draw_circle((240, 20), 10, color=(255, 0, 0, 255), fill=(55, 0, 0, 255))

        if not os.path.exists("logs"):
            os.makedirs("logs")
        with open(f"logs/data_log_{self.date}.json", 'r') as f:
            self.dati_json = json.load(f)
        for i in self.dati_json:
            self.dati.aggiungi_dati(i['time'] - self.begin_time, int(i['temperature']), int(i['humidity']), False, False)
        dpg.create_viewport(title='Thermostat', width=800, height=950)
        dpg.setup_dearpygui()
        dpg.show_viewport()

        threading.Thread(target=self.update_data, daemon=True).start()

        dpg.start_dearpygui()
        dpg.destroy_context()

    def update_led(self):
        verde_chiaro = (0, 255, 0, 255)
        verde_scuro = (0, 55, 0, 255)
        rosso_chiaro = (255, 0, 0, 255)
        rosso_scuro = (55, 0, 0, 255)
        verde = verde_chiaro if self.dati.verde == 1 else verde_scuro
        rosso = rosso_chiaro if self.dati.rosso == 1 else rosso_scuro
        dpg.configure_item(self.led_verde, fill=verde)
        dpg.configure_item(self.led_rosso, fill=rosso)

    def update_data(self):
        while dpg.is_dearpygui_running():
            data = self.arduino.readline().decode('utf-8').strip()
            temperature, humidity, red_state, green_state = data.split('\t')

            dpg.set_value("temperature", f"Temperatura: {temperature} °C")
            dpg.set_value("humidity", f"Umidità: {humidity} %")
            data = {"time": time.time(), "temperature": temperature, "humidity": humidity}
            self.dati_json.append(data)

            # cancellare i dati in più
            curr_time = time.time() - self.begin_time
            self.dati.aggiungi_dati(curr_time, int(temperature), int(humidity), int(red_state), int(green_state))
            self.graf_temp.aggiorna(self.dati.tempo, self.dati.temperatura)
            self.graf_umid.aggiorna(self.dati.tempo, self.dati.umidita)
            self.update_led()
            time.sleep(1)
    def salva(self):
        with open(f"logs/data_log_{self.date}.json", 'w') as f:
            json.dump(self.dati_json, f)

if __name__ == "__main__":
    porta = input("Scrivi la porta: ")
    t = Thermostat(porta)
    t.salva()
