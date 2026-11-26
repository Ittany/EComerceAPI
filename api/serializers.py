from rest_framework import serializers as s
from django.contrib.auth.models import User
from django.utils import timezone
from .models import *
class CategoriaSerializer(s.ModelSerializer):
 class Meta: model=Categoria; fields='__all__'
class ProductoSerializer(s.ModelSerializer):
 categoria_detalle=CategoriaSerializer(source='categoria',read_only=True)
 disponible=s.SerializerMethodField()
 precio_con_descuento=s.SerializerMethodField()
 rating_promedio=s.SerializerMethodField()
 def get_disponible(self,o): return o.stock>0
 def get_precio_con_descuento(self,o): return o.precio*(100-o.descuento)/100
 def get_rating_promedio(self,o): return o.resenas.aggregate(v=m.Avg('calificacion'))['v'] or 0
 def validate_descuento(self,v):
  if v>100: raise s.ValidationError('Máximo 100')
  return v
 class Meta: model=Producto; fields='__all__'; read_only_fields=['vendedor']
class OrdenSerializer(s.ModelSerializer):
 tiempo_estimado_entrega=s.SerializerMethodField()
 def get_tiempo_estimado_entrega(self,o):
  from datetime import timedelta
  return [(o.fecha_creacion+timedelta(days=d)).date() for d in (3,5)]
 class Meta: model=Orden; fields='__all__'; read_only_fields=['usuario','items','total','numero_seguimiento']
class ResenaSerializer(s.ModelSerializer):
 es_compra_verificada=s.SerializerMethodField()
 def get_es_compra_verificada(self,o): return comprado(o.usuario,o.producto_id)
 def validate_calificacion(self,v):
  if not 1<=v<=5: raise s.ValidationError('Calificación de 1 a 5')
  return v
 def validate(self,data):
  if not comprado(self.context['request'].user,data['producto'].pk): raise s.ValidationError('Compra no verificada')
  return data
 class Meta: model=Resena; fields='__all__'; read_only_fields=['usuario']
def comprado(user,pk): return any(i['producto']==pk for o in Orden.objects.filter(usuario=user,estado__in=['pagada','enviada','entregada']) for i in o.items)
