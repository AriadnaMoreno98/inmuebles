from django.db import models
from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from user_app.models import Account

# Create your models here.

class Empresa(models.Model):
    nombre = models.CharField(max_length=250)
    website = models.URLField(max_length=250)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre

class Inmueble(models.Model):
    direccion = models.CharField(max_length=250)
    pais = models.CharField(max_length=250)
    descripcion = models.CharField(max_length=250)
    imagen = models.CharField(max_length=900)
    avg_calificacion = models.FloatField(default=0)
    number_calificacion = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='inmuebleslist')
    
    def __str__(self):
        return self.direccion
    
class Comentario(models.Model):
    comentario_user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='comentario_user')
    calificacion = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    texto = models.CharField(max_length=250, null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    inmueble = models.ForeignKey(Inmueble, on_delete=models.CASCADE, related_name='comentarios')
    
    def __str__(self):
        return str(self.calificacion) + "-" + self.inmueble.direccion