# fuente: http://levipy.com/crear-api-rest-con-django-rest-framework/
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('passw','nombre','email','pais','ciudad','fechaNacimiento')


class MacetaSerializer(serializers.ModelSerializer):
	class Meta:
		model = Maceta
		fields = ('tipoPlanta','fechaPlantacion','usuario')

class TemperaturaSerializer(serializers.ModelSerializer):
	class Meta:
		model = LogsTemperatura
		fields = ('maceta','fecha','valor')


class LuminosidadSerializer(serializers.ModelSerializer):
	class Meta:
		model = LogsLuminosidad
		fields = ('maceta','fecha','valor')


class HumedadSerializer(serializers.ModelSerializer):
	class Meta:
		model = LogsHumedad
		fields = ('maceta','fecha','valor')


class NivelSerializer(serializers.ModelSerializer):
	class Meta:
		model = LogsNivel
		fields = ('maceta','fecha','valor')

class VariablesSerializer(serializers.ModelSerializer):
	temperatura = serializers.StringRelatedField()
	luminosidad = serializers.StringRelatedField()
	humedad = serializers.StringRelatedField()
	nivel = serializers.StringRelatedField()

	class Meta:
		model = Maceta
		fields = ('temperatura','humedad','luminosidad','nivel')


