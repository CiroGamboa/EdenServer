import paho.mqtt.client as mqtt
import xlsxwriter
import datetime

broker = "iot.eclipse.org"
port = 1883

#init variables
temperature = 0
luminosity = 0
humedity = 0
water_level = 0

# Seria buena idea hacer un for para iterar sobre los topics y asignarlos
# General workbook and worksheet (xlsx file)
gen_workbook = {
        "pot/temperature" : None,
        "pot/luminosity"  : None,
        "pot/humedity"    : None,
        "pot/water_level" : None

    }
gen_worksheet = {
        "pot/temperature" : None,
        "pot/luminosity"  : None,
        "pot/humedity"    : None,
        "pot/water_level" : None
    }


# Counter for registerint in the xlsx file
row = 1


# Topics related to the pot variables
topics = {
        "pot/temperature",
        "pot/luminosity",
        "pot/humedity",
        "pot/water_level"
    }

# Method for creating a new xlsx file
def new_file(topic,date):

    #Create the file and write initial settings
    workbook = xlsxwriter.Workbook(topic.split('/')[1]+date+'.xlsx')
    worksheet = workbook.add_worksheet()
    bg_format = workbook.add_format()
    bg_format.set_pattern(1)  
    bold = workbook.add_format({'bold': True}) # Agregar negrilla para titulos

    #Create the titles of the columns
    worksheet.write(0, 0,"Time",bold)
    worksheet.write(0, 1,topic,bold)

    gen_workbook[topic] = workbook
    gen_worksheet[topic] =  worksheet
    #gen_workbook.close()
    

# Method to write on a given xlsx file
def write_file(time,topic,value):

    gen_worksheet[topic].write(row,0,time)
    gen_worksheet[topic].write(row,1,value)

    op = ["22:41:40","22:41:41","22:41:42","22:41:43","22:41:44","22:41:45"]
    if time is "23:59:59" or time in op:
        gen_workbook[topic].close()
        row = 1
    else:
        row = row + 1


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.

    # Create a new file when connecting
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.strftime("%Y-%m-%d")

    for topic in topics:
        client.subscribe(topic)
        new_file(topic,current_date)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    
    # Receive message
    value = str(msg.payload)
    print(msg.topic+" "+ value)
    topics[msg.topic] = value

    # Get current date and time
    current_datetime = datetime.datetime.now()
    current_time = current_datetime.strftime("%H:%M:%S")
    
    if current_time is "00:00:00" or current_time is "22:42:00":
        current_date = current_datetime.strftime("%Y-%m-%d")
        for topic in topics:
            new_file(topic,current_date)

    write_file(current_time, msg.topic, value)
    

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker,port)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
