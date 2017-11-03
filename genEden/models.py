from django.db import models

class Maceta(models.Model):

    tipoPlanta = models.ForeignKey('Planta', on_delete= models.CASCADE,related_name='macetas_planta',default=2)
    fechaPlantacion= models.DateTimeField(null=True)
    primeraCosecha = models.DateTimeField(null=True)
    usuario = models.ForeignKey('User', on_delete=models.CASCADE,related_name='macetas')

class Planta(models.Model):
    nombre = models.CharField(max_length=32)

class LogsValvula(models.Model):
    maceta =  models.ForeignKey('Maceta',on_delete=models.CASCADE,related_name='valvula')
    fecha = models.DateTimeField(auto_now=True)
    valor = models.FloatField()

class LogsTemperatura(models.Model):
    maceta =  models.ForeignKey('Maceta',on_delete=models.CASCADE,related_name='temperatura')
    fecha = models.DateTimeField(auto_now=True)
    valor = models.FloatField()

class LogsLuminosidad(models.Model):
    maceta =  models.ForeignKey('Maceta',on_delete=models.CASCADE,related_name='luminosidad')
    fecha = models.DateTimeField(auto_now=True)
    valor = models.FloatField()

class LogsHumedad(models.Model):
    maceta =  models.ForeignKey('Maceta',on_delete=models.CASCADE,related_name='humedad')
    fecha = models.DateTimeField(auto_now=True)
    valor = models.FloatField()

class LogsNivel(models.Model):
    maceta =  models.ForeignKey('Maceta',on_delete=models.CASCADE,related_name='nivel')
    fecha = models.DateTimeField(auto_now=True)
    valor = models.FloatField()


class User(models.Model):
    passw = models.CharField(max_length=32)
    nombre = models.CharField(max_length=32)
    email =  models.CharField(max_length=32)
    pais =  models.CharField(max_length=32,null=True)
    ciudad = models.CharField(max_length=32,null=True)
    fechaNacimiento = models.DateField(null=True)

class Foto(models.Model):
    fotoUrl = models.CharField(max_length=32)
    usuario = models.ForeignKey('User',on_delete=models.CASCADE)

class LibroUser(models.Model):
    usuario = models.ForeignKey('User',on_delete=models.CASCADE)
    libro = models.ForeignKey('Libro',on_delete=models.CASCADE)

class Libro(models.Model):
    titulo = models.CharField(max_length=32)
    cuerpo = models.CharField(max_length=300)
    autor = models.CharField(max_length=32)
    precio =  models.FloatField()
    editorial = models.CharField(max_length=32)
    fechaPublicacion = models.DateTimeField()
