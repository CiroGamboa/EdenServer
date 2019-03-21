import paho.mqtt.client as paho
import random 

broker="iot.eclipse.org"
port=1883

#create function for callback
def on_publish(client,userdata,result): 
    print("MACETA REGADA \n")
    pass

#create client object
client1= paho.Client("potcontroller")

#assign function to callback
client1.on_publish = on_publish

#establish connection
client1.connect(broker,port)

#publish
# Regar maceta
client1.publish("pot/irrigate","on")

# Simular publicacion de variables por maceta
client1.publish("pot/temperature",random.randint(10,40))
client1.publish("pot/luminosity",random.randint(10,50))
client1.publish("pot/humedity",random.randint(10,60))
client1.publish("pot/water_level",random.randint(1,100))

