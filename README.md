# Sistema de Riego Automático con bot de Telegram

Este proyecto es un sistema de riego automatizado controlado a través de un **bot de Telegram**. Permite controlar un sistema de riego manualmente, así como programar el riego en días y horarios específicos. El sistema se implementa en una Raspberry Pi y utiliza la biblioteca de Python `telebot` para interactuar con la API de Telegram. 
Para encender y apagar el riego, se hace uso de los puertos GPIO de la Raspberry Pi, que nos permite controlar un relé que active o desactive el mecanismo de riego. Como podría ser una bomba de agua en el caso de usar un depósito o una electroválvula si es agua corriente.
## Configuración

Para comenzar a utilizar el sistema de riego automático, necesitará configurar el bot de Telegram y los pines GPIO de la Raspberry Pi.
# Bot de Telegram

Primero, deberá crear un nuevo bot de Telegram. Para hacer esto, siga estos pasos:

1. Abra la aplicación de Telegram y busque a BotFather.
2. Inicie una conversación con BotFather y utilice el comando `/newbot` para crear un nuevo bot.
3. BotFather le pedirá un nombre para su bot y un nombre de usuario único.
4. Una vez que haya proporcionado esta información, BotFather le proporcionará un token API para su bot.

Una vez que tenga su token API, reemplácelo en la siguiente línea de código en el script:
```
API_KEY = 'your-telegram-bot-api-key'
```

También necesitará proporcionar su **chat_id** para restringir el acceso al bot a un chat específico. Para obtener su chat_id, puede usar el comando /start en su bot y le responderá con su chat_id.

Si el bot va a ser usado por varias personas se puede crear un grupo de telegram y añadir a las personas que lo vayan a usar, incluido el bot, será necesario incluir el chat_id del grupo.

Reemplace chat_id en la siguiente línea:

```
CHAT_ID = 'your-chat-id'
```

## Pines GPIO

Para controlar el sistema de riego, necesitará conectarlo a los pines GPIO de la Raspberry Pi. Puede referirse al diagrama de pines de la Raspberry Pi para conectar correctamente su sistema de riego.

Los pines GPIO utilizados en el script son:

```
PIN_RELAY = 17
```

## Uso

Para iniciar el bot, ejecute el script de Python. Una vez que el bot esté en funcionamiento, puede usar los siguientes comandos en el chat de Telegram:

- /help - Muestra la lista de comandos.
- /start - Muestra el chat ID.
- /regar <minutos> - Activa el riego manual por una duración específica (en minutos), por ejemplo, /regar 5.
- /detener - Detiene el riego.
- /consultar_riego - Muestra la programación de riego actual.
- /editar_riego <día> <sí|no> - Edita la programación de riego, por ejemplo, /editar_riego lunes sí.
- /editar_hora_riego <hora>:<minuto> - Edita la hora de riego programada, por ejemplo, /editar_hora_riego 07:30.
- /editar_tiempo_riego <Minutos> - Edita el tiempo que dura el riego (en minutos)

## Programación de horarios
Por defecto la programación de riego se encuentra desactivada, podremos activar o desactivar los días de riego mediante comandos en telegram.
Para consultar el estado de la programación se utiliza el siguiente comando:
```
/consultar_riego
```
El bot responderá con la programación:

![programacion de riego](https://github.com/villeparamio/BotRiegoTelegram/blob/main/images/programacion_de_riego.png)

Podemos configurar los días de la semana que se activará el riego, la hora a la que se activará y los minutos que estará el riego activo.

Para editar los días de riego se puede usar el siguiente comando:
```
/editar_riego <día> <sí|no>
```
Si quisiéramos activar el riego los miércoles tendríamos que enviar `/editar_riego miercoles si`

Cuando el riego se active de forma automática también nos enviará un mensaje para saber que ha regado.

## Logs
El bot cuenta con un sistema de logs que nos permitirá obtener la hora exacta en que:
- Se activa el bot
- Alguien envía un comando al bot
- El riego automático es ejecutado
- Finalización del riego

## Contribuir

Las contribuciones son bienvenidas. Por favor, abra una solicitud con sus cambios.
## Licencia

Este proyecto está licenciado bajo la Licencia MIT.

## Donaciones

Si encuentras este proyecto útil y te gustaría apoyar su desarrollo y mantenimiento, considera hacer una donación. Tu apoyo será muy apreciado.

### PayPal
Puedes realizar tu donación a través de PayPal haciendo clic en el siguiente botón:

[![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?business=95M7L3UZENS6Q&no_recurring=0&currency_code=EUR)

### Bitcoin

**Bitcoin (BTC):** `13Sp4LwbDC1NQv17p3NN9w2yodog8KGtda`

**Ethereum (ETH):** `0x1939f4ba76adc18378533965857494e5f19ef4a4`

Gracias por tu apoyo.
