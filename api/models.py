from django.db import models as m
from django.contrib.auth.models import User
from django.utils import timezone
class Categoria(m.Model):
 nombre=m.CharField(max_length=100,unique=True)
 descripcion=m.TextField(blank=True)
 imagen=m.URLField(blank=True)
class Producto(m.Model):
 sku=m.CharField(max_length=30,unique=True)
 nombre=m.CharField(max_length=200)
 descripcion=m.TextField(blank=True)
 marca=m.CharField(max_length=100)
 categoria=m.ForeignKey(Categoria,on_delete=m.PROTECT)
 vendedor=m.ForeignKey(User,on_delete=m.PROTECT)
 precio=m.DecimalField(max_digits=12,decimal_places=2)
 descuento=m.PositiveIntegerField(default=0)
 stock=m.PositiveIntegerField(default=0)
 imagenes=m.JSONField(default=list)
 especificaciones=m.JSONField(default=dict)
 fecha_creacion=m.DateTimeField(auto_now_add=True)
class Carrito(m.Model):
 usuario=m.OneToOneField(User,on_delete=m.CASCADE)
class Item(m.Model):
 carrito=m.ForeignKey(Carrito,on_delete=m.CASCADE,related_name='items')
 producto=m.ForeignKey(Producto,on_delete=m.CASCADE)
 cantidad=m.PositiveIntegerField(default=1)
 class Meta: unique_together=('carrito','producto')
class Orden(m.Model):
 usuario=m.ForeignKey(User,on_delete=m.PROTECT)
 items=m.JSONField(default=list)
 direccion_envio=m.CharField(max_length=250)
 metodo_pago=m.CharField(max_length=50)
 estado=m.CharField(max_length=15,default='pendiente')
 total=m.DecimalField(max_digits=12,decimal_places=2)
 fecha_creacion=m.DateTimeField(auto_now_add=True)
 numero_seguimiento=m.CharField(max_length=50,blank=True)
class Resena(m.Model):
 usuario=m.ForeignKey(User,on_delete=m.CASCADE)
 producto=m.ForeignKey(Producto,on_delete=m.CASCADE,related_name='resenas')
 calificacion=m.PositiveIntegerField()
 titulo=m.CharField(max_length=100)
 comentario=m.TextField()
 fecha_creacion=m.DateTimeField(auto_now_add=True)
 class Meta: unique_together=('usuario','producto')
