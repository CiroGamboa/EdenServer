from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from genEden.models import *
from genEden.serializers import *
import paho.mqtt.client as mqtt
from django.db.models import Avg,Max,Min
#import coreapi
#guia: http://levipy.com/crear-api-rest-con-django-rest-framework/

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)




################################################################
################################################################
# METODOS FINALES

@csrf_exempt
def registrar_usuario(request,passw,nombre,email):
	if request.method == 'GET':
		try:
			User.objects.create(passw=passw,nombre=nombre,email=email)
			idUsuario = User.objects.order_by('-id')[0].id
		except User.DoesNotExist:
			return HttpResponse(status=404)

		return JSONResponse(idUsuario)

@csrf_exempt
def login_usuario(request,email,passw):
	if request.method == 'GET':
		try:
			usuario = User.objects.get(email=email,passw=passw)
			idUsuario = usuario.id
		except User.DoesNotExist:
			return JSONResponse('0')

		return JSONResponse(idUsuario)

# Esto es poco eficiente pero es una solucion rapida
@csrf_exempt
def get_maceta(request,idUsuario):
	if request.method == 'GET':
		try:
			usuario = User.objects.get(id=idUsuario)
			maceta = Maceta.objects.get(usuario=usuario)
			idMaceta = maceta.id
		except User.DoesNotExist:
			return JSONResponse('0')

		return JSONResponse(idMaceta)


@csrf_exempt
def registrar_maceta(request,idUsuario):
	"""
	Registrar un nueva maceta
	"""
	if request.method == 'GET':

		try:
			usuario = User.objects.get(id=idUsuario)
			#planta = Planta.objects.get(id=2)
			#Maceta.objects.create(tipoPlanta=planta,usuario=usuario)
			Maceta.objects.create(usuario=usuario)
			maceta = Maceta.objects.order_by('-id')[0]
			#El id=2 para tipo planta indica que no se ha escogido una semilla
		except User.DoesNotExist:
			return JSONResponse(status=400)

		#conec = conectar_maceta()

		# Crear primer registro en la DB asociado a esa maceta
		LogsTemperatura.objects.create(maceta=maceta,valor=25)
		LogsLuminosidad.objects.create(maceta=maceta,valor=57)
		LogsHumedad.objects.create(maceta=maceta,valor=35)
		LogsNivel.objects.create(maceta=maceta,valor=100)

		return JSONResponse(maceta.id)

	else:
		return JSONResponse(status=400)

@csrf_exempt
def get_variables(request,pkUsuario,pkMaceta):
	"""
	Obtener el ultimo registro de las variables, request hecho por al app
	"""
	if request.method == 'GET':
		try:
			usuario = User.objects.get(id=pkUsuario)
			maceta = Maceta.objects.get(id=pkMaceta)	

		except User.DoesNotExist:
			return HttpResponse(status=404)

		try:
			temperatura=LogsTemperatura.objects.filter(maceta=maceta).order_by('-id')[0]
			luminosidad=LogsLuminosidad.objects.filter(maceta=maceta).order_by('-id')[0]
			humedad=LogsHumedad.objects.filter(maceta=maceta).order_by('-id')[0]
			nivel=LogsNivel.objects.filter(maceta=maceta).order_by('-id')[0]

		except User.DoesNotExist:
			return HttpResponse(status=404)

		serializer = data={
			'temperatura':temperatura.valor,'luminosidad':luminosidad.valor,
			'humedad':humedad.valor,'nivel':nivel.valor}

		return JSONResponse(serializer)

	else:
		return JSONResponse(status=400)


@csrf_exempt
def get_stats_h(request,pkUsuario,pkMaceta):

	#Orden:
	# Temperatura : min, max, prom
	# Humedad: min, max, prom
	# Luminosidad: min, max, prom
	if request.method == 'GET':
		try:
			tasaEnvio = 3 # Tasa de envio de variables por parte de la maceta (en segundos)
			muestras = 3600/tasaEnvio # Segundos en una hora

			usuario = User.objects.get(id=pkUsuario)
			maceta = Maceta.objects.get(id=pkMaceta)

			promtem = round(LogsTemperatura.objects.filter(maceta=maceta).order_by('-id')[:muestras].aggregate(Avg('valor'))['valor__avg'],1)
			promlum = round(LogsLuminosidad.objects.filter(maceta=maceta).order_by('-id')[:muestras].aggregate(Avg('valor'))['valor__avg'],1)
			promhum = round(LogsHumedad.objects.filter(maceta=maceta).order_by('-id')[:muestras].aggregate(Avg('valor'))['valor__avg'],1)

			maxtem = round(LogsTemperatura.objects.filter(maceta=maceta).order_by('-id')[:muestras].aggregate(Max('valor'))['valor__max'],1)
			maxlum = round(LogsLuminosidad.objects.filter(maceta=maceta).order_by('-id')[:muestras].aggregate(Max('valor'))['valor__max'],1)
			maxhum = round(LogsHumedad.objects.filter(maceta=maceta).order_by('-id')[:muestras].aggregate(Max('valor'))['valor__max'],1)

			mintem = round(LogsTemperatura.objects.filter(maceta=maceta).order_by('-id')[:muestras].aggregate(Min('valor'))['valor__min'],1)
			minlum = round(LogsLuminosidad.objects.filter(maceta=maceta).order_by('-id')[:muestras].aggregate(Min('valor'))['valor__min'],1)
			minhum = round(LogsHumedad.objects.filter(maceta=maceta).order_by('-id')[:muestras].aggregate(Min('valor'))['valor__min'],1)

		except User.DoesNotExist:
			return HttpResponse(status=404)

		serializer = data={
			'tem_min':mintem,'tem_max':maxtem,'tem_prom':promtem,
			'hum_min':minhum,'hum_max':maxhum,'hum_prom':promhum,
			'lum_min':minlum,'lum_max':maxlum,'lum_prom':promlum}

		return JSONResponse(serializer)

#### MQTT
def on_message(client, userdata, message):
	print("Message received ",str(message.payload.decode("utf-8")))
	print("Message topic = ",message.topic)


@csrf_exempt
def regar_maceta(request,pkUsuario,pkMaceta):
	# Regar la maceta....'echarle aguita a la matica'
	if request.method == 'GET':
		try:
			usuario = User.objects.get(id=pkUsuario)
			maceta = Maceta.objects.get(id=pkMaceta)

			topic = "maceta/actions/regar/"+maceta.serial
			broker_address="192.168.1.17"
			client = mqtt.Client("P2")
			client.connect(broker_address)
			client.loop_start()
			print("Publishing message to topic:",topic)
			client.publish(topic,'1') #Encender la bomba
			#time.sleep(4) # No se porque es necesario esto
			client.loop_stop()

		except User.DoesNotExist:
			return JSONResponse({"regar":0},status=404)


		except User.DoesNotExist:
			return JSONResponse({"regar":0},status=404)

		return JSONResponse({"regar":1},status=200)

	else:
		return JSONResponse({"regar":0},status=404)
#	send_vars(18,30,70,60)
#	return JSONResponse({"regar":1},status=200)

#def conectar_maceta():



@csrf_exempt
def agregar_semilla(request,pkUsuario,pkMaceta,pkPlanta):
	"""
	Indicar la semilla que sera plantada
	"""
	if request.method == 'GET':
		try: 
			usuario = User.objects.get(id=pkUsuario)
			maceta = Maceta.objects.get(id=pkMaceta)
			planta = Planta.objects.get(id=pkPlanta)


		except User.DoesNotExist:
		 	return HttpResponse(status=404)

		maceta.tipoPlanta = planta
		maceta.save()

		return HttpResponse(status=200)

	else:
		return HttpResponse(status=400)
################################################################
def init_db():
 ##	  Creacion de usuarios
 # 	  passw = models.CharField(max_length=32)
 #    nombre = models.CharField(max_length=32)
 #    email =  models.CharField(max_length=32)
 #    pais =  models.CharField(max_length=32,null=True)
 #    ciudad = models.CharField(max_length=32,null=True)
 #    fechaNacimiento = models.DateField(null=True)

	ciro = User.objects.create(passw="123",nombre="Ciro",email="ciro@eden.com",pais="Colombia",ciudad="Bucaramanga")
	alix = User.objects.create(passw="123",nombre="Alix",email="alix@eden.com",pais="Colombia",ciudad="Bucaramanga")
	alvaro = User.objects.create(passw="123",nombre="Alvaro",email="alvaro@eden.com",pais="Colombia",ciudad="Bucaramanga")
	brian = User.objects.create(passw="123",nombre="Brian",email="brian@eden.com",pais="Colombia",ciudad="Bucaramanga")
	hernan = User.objects.create(passw="123",nombre="Hernan",email="hernan@eden.com",pais="Colombia",ciudad="Bucaramanga")

 ##	Creacion de tipos de planta
 #	nombre = models.CharField(max_length=32)

	tomate = Planta.objects.create(nombre="Tomate")
	fresa = Planta.objects.create(nombre="Fresa")

 ## Creacion de macetas
  #   tipoPlanta = models.ForeignKey('Planta', on_delete= models.CASCADE,related_name='macetas_planta',default=1) #Tomate por defecto
  #   fechaPlantacion= models.DateTimeField(null=True)
  #   primeraCosecha = models.DateTimeField(null=True)
  #   usuario = models.ForeignKey('User', on_delete=models.CASCADE,related_name='macetas')
	#planta = Planta.objects.get(nombre="Tomate")
	#usuario = User.objects.get(nombre="Ciro")
	macetaCiro = Maceta.objects.create(tipoPlanta=tomate,usuario=ciro,serial="eden1")
	macetaAlix = Maceta.objects.create(tipoPlanta=tomate,usuario=alix,serial="eden2")
	macetaAlvaro = Maceta.objects.create(tipoPlanta=tomate,usuario=alvaro,serial="eden3")
	macetaBrian = Maceta.objects.create(tipoPlanta=tomate,usuario=brian,serial="eden4")
	macetaHernan = Maceta.objects.create(tipoPlanta=tomate,usuario=hernan,serial="eden5")

 ## Creacion de logs

	LogsTemperatura.objects.create(maceta=macetaCiro,valor=25)
	LogsLuminosidad.objects.create(maceta=macetaCiro,valor=57)
	LogsHumedad.objects.create(maceta=macetaCiro,valor=35)
	LogsNivel.objects.create(maceta=macetaCiro,valor=100)

	LogsTemperatura.objects.create(maceta=macetaAlix,valor=25)
	LogsLuminosidad.objects.create(maceta=macetaAlix,valor=57)
	LogsHumedad.objects.create(maceta=macetaAlix,valor=35)
	LogsNivel.objects.create(maceta=macetaAlix,valor=100)

	LogsTemperatura.objects.create(maceta=macetaAlvaro,valor=25)
	LogsLuminosidad.objects.create(maceta=macetaAlvaro,valor=57)
	LogsHumedad.objects.create(maceta=macetaAlvaro,valor=35)
	LogsNivel.objects.create(maceta=macetaAlvaro,valor=100)

	LogsTemperatura.objects.create(maceta=macetaBrian,valor=25)
	LogsLuminosidad.objects.create(maceta=macetaBrian,valor=57)
	LogsHumedad.objects.create(maceta=macetaBrian,valor=35)
	LogsNivel.objects.create(maceta=macetaBrian,valor=100)

	LogsTemperatura.objects.create(maceta=macetaHernan,valor=25)
	LogsLuminosidad.objects.create(maceta=macetaHernan,valor=57)
	LogsHumedad.objects.create(maceta=macetaHernan,valor=35)
	LogsNivel.objects.create(maceta=macetaHernan,valor=100)



################################################################
# @csrf_exempt
# def registrar_usuario(request):
# 	"""
# 	Registrar un nuevo usuario
# 	"""

# 	if request.method == 'POST':
# 		data = JSONParser().parse(request)
# 		serializer = UserSerializer(data=data)


# 		if serializer.is_valid():
# 			#guardar en la DB
# 			serializer.save()
# 			return JSONResponse(serializer.data, status=201)
# 		return JSONResponse(serializer.errors, status=400)
# 	else:
# 		return JSONResponse(status=400)
# ################################################################

################################################################



# ################################################################
# @csrf_exempt
# def registrar_maceta(request):
# 	"""
# 	Registrar un nueva maceta
# 	"""
# 	if request.method == 'POST':
# 		data = JSONParser().parse(request)
# 		try:
# 			planta = Planta.objects.get(id=data['tipoPlanta'])
# 			usuario = User.objects.get(id=data['usuario'])
# 		except Planta.DoesNotExist:
# 			return HttpResponse(status=404)

# 		serializer = MacetaSerializer(data=data)
# 		serializer.tipoPlanta = planta
# 		serializer.usuario = usuario

# 		if serializer.is_valid():
# 			#guardar en la DB
# 			serializer.save()
# 			return JSONResponse(serializer.data, status=201)
# 		return JSONResponse(serializer.errors, status=400)
# 	else:
# 		return JSONResponse(status=400)
# ################################################################

################################################################

################################################################

################################################################


################################################################
def send_vars(tem,lum,hum,niv):
	maceta = Maceta.objects.order_by('-id')[0]
	# Variables normales
	LogsTemperatura.objects.create(maceta=maceta,valor=tem)
	LogsLuminosidad.objects.create(maceta=maceta,valor=lum)
	LogsHumedad.objects.create(maceta=maceta,valor=hum)
	LogsNivel.objects.create(maceta=maceta,valor=niv)

def reg_vars(case):
	maceta = Maceta.objects.order_by('-id')[0]
	if case == 0: # Variables normales
		LogsTemperatura.objects.create(maceta=maceta,valor=25)
		LogsLuminosidad.objects.create(maceta=maceta,valor=67)
		LogsHumedad.objects.create(maceta=maceta,valor=52)
		LogsNivel.objects.create(maceta=maceta,valor=100)

	if case == 1: # Hay que llenar el tanque
		LogsTemperatura.objects.create(maceta=maceta,valor=30)
		LogsLuminosidad.objects.create(maceta=maceta,valor=65)
		LogsHumedad.objects.create(maceta=maceta,valor=30)
		LogsNivel.objects.create(maceta=maceta,valor=10)

	if case == 2: # Se lleno el tanque
		#LogsTemperatura.objects.create(maceta=maceta,valor=20)
		#LogsLuminosidad.objects.create(maceta=maceta,valor=60)
		#LogsHumedad.objects.create(maceta=maceta,valor=60)
		LogsNivel.objects.create(maceta=maceta,valor=100)

	if case == 3: # Hay que regar la maceta
		LogsTemperatura.objects.create(maceta=maceta,valor=35)
		LogsLuminosidad.objects.create(maceta=maceta,valor=67)
		LogsHumedad.objects.create(maceta=maceta,valor=10)
		LogsNivel.objects.create(maceta=maceta,valor=100)

	if case == 4: # Se rego la maceta
		LogsTemperatura.objects.create(maceta=maceta,valor=22)
		LogsLuminosidad.objects.create(maceta=maceta,valor=67)
		LogsHumedad.objects.create(maceta=maceta,valor=60)
		LogsNivel.objects.create(maceta=maceta,valor=70)

	
################################################################
#def registrar_variables(ipMaceta):
	"""
	Obtener las variables de temperatura, luminosidad, enviadas desde la maceta
	# """
	# ip = ipMaceta
	# client = coreapi.Client()
	# response = client.get('http://'+ip+'/')
	# data = response['variables']

	# try:
	# 	maceta = Maceta.objects.get(id=data['idMaceta'])
	# 	usuario = User.objects.get(id=data['idUsuario'])

	# 	if maceta.usuario.id is not usuario.id:
	# 		return None

	# except Maceta.DoesNotExist:
	# 	return None
	# print(data)
	# temperatura = LogsTemperatura.objects.create(maceta=maceta,valor=data['temperatura'])
	# luminosidad = LogsLuminosidad.objects.create(maceta=maceta,valor=data['luminosidad'])
	# humedad = LogsHumedad.objects.create(maceta=maceta,valor=data['humedad'])
	# nivel = LogsNivel.objects.create(maceta=maceta,valor=data['nivel'])

	# temperatura.save()
	# luminosidad.save()
	# humedad.save()
	# nivel.save()
#	return 0

################################################################

################################################################
#@csrf_exempt
#def regar_maceta(request,pkUsuario,pkMaceta):
	"""
	Regar la maceta
	"""
	# if request.method == 'GET':
	# 	try:
	# 		usuario = User.objects.get(id=pkUsuario)
	# 		maceta = Maceta.objects.get(id=pkMaceta)	

	# 	except User.DoesNotExist:
	# 		return JSONResponse({"regar":0},status=404)

	# 	# Asumiendo que sabemos la ip de la maceta
	# 	try:
	# 		ip = '192.168.1.17'
	# 		client = coreapi.Client()
	# 		response = client.get('http://'+ip+'/digital/5/1')

	# 	except User.DoesNotExist:
	# 		return JSONResponse({"regar":0},status=404)

	# 	return JSONResponse({"regar":1},status=200)

	# else:
	# 	return JSONResponse({"regar":0},status=404)
#	send_vars(18,30,70,60)
#	return JSONResponse({"regar":1},status=200)
################################################################

################################################################
#@csrf_exempt
#def conectar_maceta():

		# try:
		# 	ip = '192.168.1.17'
		# 	client = coreapi.Client()
		# 	response = client.get('http://'+ip+'/digital/3/1')
		# except User.DoesNotExist:
		#  	return 0
#		return 1
################################################################

################################################################


################################################################





