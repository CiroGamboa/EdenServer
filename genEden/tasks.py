from __future__ import absolute_import, unicode_literals
from celery import task
from celery.signals import celeryd_init,celeryd_after_setup
import paho.mqtt.client as mqtt #import the client1
import time
from genEden.models import *

# LA IDEA POR AHORA ES TENER EN LA DB TODAS LAS MACETAS CREADAS (LAS QUE SE PRODUCEN) Y CUANDO
# UN CLIENTE LA REGISTRA, SE VALIDA EL SERIAL Y SE LE PONE UNA BANDERA EN LA BASE DE DATOS
# DESDE LA NODE, LA MACETA ENVIA LAS VARIABLES A UN TOPIC QUE CONTENGA SU SERIAL
# ENTONCES CADA VEZ QUE SE INICIA CELERY, EL CLIENTE MQTT SE SUSCRIBE A TODOS LOS SERIALES DE LAS MACETAS EXISTENTES
# TOCA HACER ESO YA QUE UNA VEZ INICIADO CELERY, NO SE PUEDEN CAMBIAR LOS PARAMETROS DEL CLIENTE MQTT, SIN PARAR EL CICLO


### Topics
temTopic = "maceta/vars/temperatura/"
humTopic = "maceta/vars/humedad/"
lumTopic = "maceta/vars/luminosidad/"
nivTopic = "maceta/vars/nivel/"

### Broker
broker_address="192.168.1.16"

# Maceta real
maceta = Maceta.objects.get(serial="eden1")

### Aqui es donde se realizan todas las acciones cada vez que se
### actualizan las variables
def on_message(client, userdata, message):
    #print("message received " ,str(message.payload.decode("utf-8")))
    #print("message topic=",message.topic)
    #print("message qos=",message.qos)
    #print("message retain flag=",message.retain)
	var = message.payload.decode("utf-8")
	if message.topic == temTopic+"eden1": # Esto es solo para la primera maceta, que tiene el serial 'eden1'
		print("Temperatura: ",str(var))
		LogsTemperatura.objects.create(maceta=maceta,valor=var)

	elif message.topic == humTopic+"eden1":
		print("Humedad: ",str(var))
		LogsLuminosidad.objects.create(maceta=maceta,valor=var)

	elif message.topic == lumTopic+"eden1":
		print("Luminosidad: ",str(var))
		LogsHumedad.objects.create(maceta=maceta,valor=var)

	elif message.topic == nivTopic+"eden1":
		print("Nivel: ",str(var))
		LogsNivel.objects.create(maceta=maceta,valor=var)


@celeryd_init.connect
def set_variables(sender=None, conf=None, **kwargs):
	client = mqtt.Client("P1") #create new instance
	client.on_message=on_message #attach function to callback
	client.connect(broker_address) #connect to broker

	macetas = Maceta.objects.all()
	for maceta in macetas:
		client.subscribe(temTopic+maceta.serial)
		client.subscribe(humTopic+maceta.serial)
		client.subscribe(lumTopic+maceta.serial)
		client.subscribe(nivTopic+maceta.serial)
	client.loop_forever()
        
# @celeryd_init.connect
# def set_variables(sender=None, conf=None, **kwargs):
# 	client = mqtt.Client("P1") #create new instance
# 	client.on_message=on_message #attach function to callback
# 	client.connect(broker_address) #connect to broker
# 	client.subscribe(temTopic)
# 	client.subscribe(humTopic)
# 	client.subscribe(lumTopic)
# 	client.subscribe(nivTopic)
# 	client.loop_forever()




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
