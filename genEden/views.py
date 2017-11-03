from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from genEden.models import *
from genEden.serializers import *
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
@csrf_exempt
def registrar_usuario(request,passw,nombre,email):

	if request.method == 'GET':
		try:
			User.objects.create(passw=passw,nombre=nombre,email=email)
			idUsuario = User.objects.order_by('-id')[0].id
		except User.DoesNotExist:
			return HttpResponse(status=404)

		return JSONResponse(idUsuario)


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
@csrf_exempt
def registrar_maceta(request,idUsuario):
	"""
	Registrar un nueva maceta
	"""
	if request.method == 'GET':

		try:
			usuario = User.objects.get(id=idUsuario)
			planta = Planta.objects.get(id=2)
			Maceta.objects.create(tipoPlanta=planta,usuario=usuario)
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
################################################################

################################################################

@csrf_exempt
def get_variables(request,pkUsuario,pkMaceta):
	"""
	Obtener el ultimo registro de las variables
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
def registrar_variables(ipMaceta):
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
	return 0

################################################################

################################################################
@csrf_exempt
def regar_maceta(request,pkUsuario,pkMaceta):
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
	send_vars(18,30,70,60)
	return JSONResponse({"regar":1},status=200)
################################################################

################################################################
@csrf_exempt
def conectar_maceta():

		# try:
		# 	ip = '192.168.1.17'
		# 	client = coreapi.Client()
		# 	response = client.get('http://'+ip+'/digital/3/1')
		# except User.DoesNotExist:
		#  	return 0
		return 1
################################################################

################################################################

@csrf_exempt
def agregar_semilla(request,pkUsuario,pkMaceta,pkPlanta):
	"""
	Obtener el ultimo registro de las variables
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

