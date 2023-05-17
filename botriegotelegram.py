import time
import telebot
import RPi.GPIO as GPIO
import logging
import datetime
import json
import subprocess
import re
import requests
from unidecode import unidecode
from threading import Timer
from threading import Thread

# Configuración de la API de Telegram
API_KEY = '<SUSTITUIR_POR_EL_TOKEN_DE_TU_BOT>'
bot = telebot.TeleBot(API_KEY)

# Restringe el acceso a un chat específico
chat_id = '<SUSTITUIR_POR_EL_CHAT_ID>' # El bot solo responderá a este chat y a cualquier otro dirá que no tiene permiso

# Configurar el registro
fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d')
nombre_archivo_log = f"log_bot.log"
logging.basicConfig(filename=nombre_archivo_log, level=logging.INFO, format='%(asctime)s - %(message)s')

logging.info('Bot iniciado')  # Agrega el primer registro al archivo

# Configuración de los pines GPIO
PIN_RELE = 17  # Pin GPIO para el módulo de relé
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_RELE, GPIO.OUT)
GPIO.output(PIN_RELE, True)  # Establece el estado inicial del relé a HIGH (desactivado)

# Variable global para controlar el estado del riego
irrigation_active = False


def irrigation(irrigation_time):
    global irrigation_active
    irrigation_active = True
    start_time = time.time()

    while irrigation_active and (time.time() - start_time) < irrigation_time:
        GPIO.output(PIN_RELE, False)  # Cambia a LOW para activar el relé
        time.sleep(1)  # Revisamos el estado del riego cada segundo

    GPIO.output(PIN_RELE, True)  # Cambia a HIGH para desactivar el relé
    irrigation_active = False


@bot.message_handler(commands=['start'])
def start_handler(message):
    logging.info(f"Comando /start ejecutado por usuario: {message.from_user.username} en chat_id {message.chat.id}")
    if message.chat.id != chat_id:
        bot.reply_to(message, "No tienes permiso para ejecutar este bot.")
        return

    chat_id = message.chat.id
    bot.reply_to(message, f'Tu Chat ID es: {chat_id}')


@bot.message_handler(commands=['regar'])
def riego_handler(message):
    logging.info(f"Comando /regar ejecutado por usuario: {message.from_user.username} en chat_id {message.chat.id}")
    if message.chat.id != chat_id:
        bot.reply_to(message, "No tienes permiso para ejecutar este bot.")
        return

    # Extrae el número de minutos de la cadena de mensaje
    match = re.search(r'/regar\s+(\d+)', message.text)
    if match:
        minutos = int(match.group(1))
        duracion = minutos * 60  # Convierte los minutos en segundos
        bot.reply_to(message, f'Riego activado por {minutos} minutos.')

        irrigation(duracion)
        bot.send_message(chat_id, 'Riego Finalizado.')
    else:
        bot.reply_to(message,
                     "Por favor, ingrese un número de minutos válido después del comando /regar. Ejemplo: /regar 5")


@bot.message_handler(commands=['detener'])
def detener_handler(message):
    logging.info(f"Comando /detener ejecutado por usuario: {message.from_user.username} en chat_id {message.chat.id}")
    if message.chat.id != chat_id:
        bot.reply_to(message, "No tienes permiso para ejecutar este bot.")
        return

    global irrigation_active
    irrigation_active = False
    bot.reply_to(message, 'Riego detenido.')


@bot.message_handler(commands=['help'])
def help_handler(message):
    logging.info(f"Comando /help ejecutado por usuario: {message.from_user.username} en chat_id {message.chat.id}")
    if message.chat.id != chat_id:
        bot.reply_to(message, "No tienes permiso para ejecutar este bot.")
        return

    help_text = (
        "Lista de comandos disponibles:\n\n"
        "/help - Muestra esta lista de comandos.\n"
        "/start - Muestra el chat ID.\n"
        "/regar <minutos> - Activa el riego por una duración específica (en minutos), por ejemplo, /regar 5.\n"
        "/detener - Detiene el riego.\n"
        "/consultar_riego - Muestra la programación de riego actual.\n"
        "/editar_riego <día> <sí|no> - Edita la programación de riego, por ejemplo, /editar_riego lunes sí.\n"
        "/editar_hora_riego <hora>:<minuto> - Edita la hora de riego programada, por ejemplo, /editar_hora_riego 07:30.\n"
        "/editar_tiempo_riego <Minutos> - Edita el tiempo que dura el riego (en minutos)"
    )
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['consultar_riego'])
def consultar_riego_handler(message):
    logging.info(
        f"Comando /consultar_riego ejecutado por usuario: {message.from_user.username} en chat_id {message.chat.id}")
    if message.chat.id != chat_id:
        bot.reply_to(message, "No tienes permiso para ejecutar este bot.")
        return

    with open('config.json', 'r') as f:
        config = json.load(f)

    hora_riego = config['hora_riego']
    tiempo_riego = config['tiempo_riego']

    dias_en_espanol = {
        'monday': 'lunes',
        'tuesday': 'martes',
        'wednesday': 'miércoles',
        'thursday': 'jueves',
        'friday': 'viernes',
        'saturday': 'sábado',
        'sunday': 'domingo'
    }

    msg = "Programación de riego:\n\n"
    for dia in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
        activo = config[dia]
        msg += f"{dias_en_espanol[dia]}: {'Sí' if activo else 'No'}\n"
    msg += f"\nHora de riego: {hora_riego}"
    msg += f"\nMinutos de riego: {tiempo_riego}"

    bot.reply_to(message, msg)


@bot.message_handler(commands=['editar_riego'])
def editar_riego_handler(message):
    logging.info(
        f"Comando /editar_riego ejecutado por usuario: {message.from_user.username} en chat_id {message.chat.id}")
    if message.chat.id != chat_id:
        bot.reply_to(message, "No tienes permiso para ejecutar este bot.")
        return

    with open('config.json', 'r') as f:
        dias_de_riego = json.load(f)

    texto = message.text.split()
    if len(texto) != 3:
        bot.reply_to(message, "Por favor, utiliza el formato correcto: /editar_riego <día> <on|off>")
        return

    dia = unidecode(texto[1].lower())
    estado = texto[2].lower()

    dias = {
        "lunes": "monday",
        "martes": "tuesday",
        "miercoles": "wednesday",
        "jueves": "thursday",
        "viernes": "friday",
        "sabado": "saturday",
        "domingo": "sunday"
    }

    if dia not in dias or estado not in ["on", "off"]:
        bot.reply_to(message, "Por favor, utiliza el formato correcto: /editar_riego <día> <on|off>")
        return

    dias_de_riego[dias[dia]] = True if estado == "on" else False

    with open('config.json', 'w') as f:
        json.dump(dias_de_riego, f)

    bot.reply_to(message,
                 f"Riego programado para el {dia.capitalize()} actualizado a: {'Sí' if estado == 'on' else 'No'}.")


@bot.message_handler(commands=['editar_hora_riego'])
def editar_hora_riego_handler(message):
    logging.info(
        f"Comando /editar_hora_riego ejecutado por usuario: {message.from_user.username} en chat_id {message.chat.id}")
    if message.chat.id != chat_id:
        bot.reply_to(message, "No tienes permiso para ejecutar este bot.")
        return

    hora_riego = message.text.split()[1]

    if not hora_riego:
        bot.reply_to(message, "Por favor, utiliza el formato correcto: /editar_hora_riego <HH:MM>")
        return

    with open('config.json', 'r') as f:
        config = json.load(f)

    config['hora_riego'] = hora_riego

    with open('config.json', 'w') as f:
        json.dump(config, f)

    bot.reply_to(message, f'Hora de riego actualizada a {hora_riego}.')


@bot.message_handler(commands=['editar_tiempo_riego'])
def editar_hora_riego_handler(message):
    logging.info(
        f"Comando /editar_tiempo_riego ejecutado por usuario: {message.from_user.username} en chat_id {message.chat.id}")
    if message.chat.id != chat_id:
        bot.reply_to(message, "No tienes permiso para ejecutar este bot.")
        return

    tiempo_riego = message.text.split()[1]

    if not tiempo_riego:
        bot.reply_to(message, "Por favor, utiliza el formato correcto: /editar_tiempo_riego <Minutos>")
        return

    with open('config.json', 'r') as f:
        config = json.load(f)

    config['tiempo_riego'] = tiempo_riego

    with open('config.json', 'w') as f:
        json.dump(config, f)

    bot.reply_to(message, f'Tiempo de riego actualizada a {tiempo_riego} minutos.')


def verificar_riego_automatico():
    global irrigation_active
    while True:
        if irrigation_active:
            time.sleep(60)  # Espera un minuto antes de verificar de nuevo
            continue

        with open('config.json', 'r') as f:
            config = json.load(f)

        hora_riego = config['hora_riego']

        hoy = datetime.datetime.now().strftime('%A').lower()
        hora_actual = datetime.datetime.now().strftime('%H:%M')

        if config[hoy] and hora_actual == hora_riego:
            if isinstance(config['tiempo_riego'], str):
                config['tiempo_riego'] = int(config['tiempo_riego'])
            duracion = config['tiempo_riego'] * 60  # en segundos
            bot.send_message(chat_id,
                             text=f'Riego automático iniciado a las {hora_riego}. Duración: {duracion} segundos.')
            logging.info(f'Riego automático iniciado a las {hora_riego}. Duración: {duracion} segundos.')
            irrigation(duracion)
            bot.send_message(chat_id, text=f'Riego automático finalizado.')
            logging.info(f'Riego automático finalizado.')

        time.sleep(60)  # Revisamos cada minuto


if __name__ == '__main__':
    try:
        # Inicia el hilo de verificación de riego automático cuando el programa comienza
        Thread(target=verificar_riego_automatico).start()
        bot.polling(none_stop=True)
    except Exception as e:
        print(f'Error: {e}')
    finally:
        GPIO.cleanup()
