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
broker_address="ec2-54-68-33-120.us-west-2.compute.amazonaws.com" #Local: "192.168.1.16"

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
		temperatura = round(0.225*var - 157.03)
		if temperatura > 50:
			temperatura = 50
		elif temperatura < 0:
			temperatura = 0
		print("Temperatura : ",str(temperatura))
		LogsTemperatura.objects.create(maceta=maceta,valor=temperatura)

	elif message.topic == humTopic+"eden1":
		humedad = round(-0.2353*var + 171.76)
		if humedad > 100:
			humedad = 100
		elif humedad < 0:
			humedad = 0
		print("Humedad: ",str(humedad))
		LogsLuminosidad.objects.create(maceta=maceta,valor=humedad)

	elif message.topic == lumTopic+"eden1":
		luminosidad = 0.8621*var - 3.4483
		if luminosidad > 100:
			luminosidad = 100
		elif luminosidad < 0:
			luminosidad = 0

		print("Luminosidad: ",str(luminosidad))
		LogsHumedad.objects.create(maceta=maceta,valor=luminosidad)

	#elif message.topic == nivTopic+"eden1":
	#	print("Nivel: ",str(var))
	#	LogsNivel.objects.create(maceta=maceta,valor=var)


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
		#client.subscribe(nivTopic+maceta.serial) # Ya que no se va a usar sensor de nivel, no es necesario suscribirse a el topic
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
