from __future__ import absolute_import, unicode_literals
from celery import task
from celery.signals import celeryd_init,celeryd_after_setup
import paho.mqtt.client as mqtt #import the client1
import time

# LA IDEA POR AHORA ES TENER EN LA DB TODAS LAS MACETAS CREADAS (LAS QUE SE PRODUCEN) Y CUANDO
# UN CLIENTE LA REGISTRA, SE VALIDA EL SERIAL Y SE LE PONE UNA BANDERA EN LA BASE DE DATOS
# DESDE LA NODE, LA MACETA ENVIA LAS VARIABLES A UN TOPIC QUE CONTENGA SU SERIAL
# ENTONCES CADA VEZ QUE SE INICIA CELERY, EL CLIENTE MQTT SE SUSCRIBE A TODOS LOS SERIALES DE LAS MACETAS EXISTENTES
# TOCA HACER ESO YA QUE UNA VEZ INICIADO CELERY, NO SE PUEDEN CAMBIAR LOS PARAMETROS DEL CLIENTE MQTT, SIN PARAR EL CICLO


### Topics
temTopic = "maceta/vars/temperatura"
humTopic = "maceta/vars/humedad"
lumTopic = "maceta/vars/luminosidad"
nivTopic = "maceta/vars/nivel"

### Broker
broker_address="192.168.0.60"

### Aqui es donde se realizan todas las acciones cada vez que se
### actualizan las variables
def on_message(client, userdata, message):
    #print("message received " ,str(message.payload.decode("utf-8")))
    #print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)

	if message.topic == temTopic:
		print("Temperatura: ",str(message.payload.decode("utf-8")))
        
@celeryd_init.connect
def set_variables(sender=None, conf=None, **kwargs):
	client = mqtt.Client("P1") #create new instance
	client.on_message=on_message #attach function to callback
	client.connect(broker_address) #connect to broker
	client.subscribe(temTopic)
	client.subscribe(humTopic)
	client.subscribe(lumTopic)
	client.subscribe(nivTopic)
	client.loop_forever()


# @celeryd_init.connect
# def task_number_one(sender=None, conf=None, **kwargs):
# 	print("TASK DONEEEEEEEE")
# 	for i in range(0,1000):
# 		print(i)

# @celeryd_after_setup.connect
# def task_number_one(sender=None, conf=None, **kwargs):
# 	print("TASK DONEEEEEEEE")
# 	for i in range(0,1000):
# 		print(i)
