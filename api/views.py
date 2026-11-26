from rest_framework import viewsets,permissions,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError,PermissionDenied
from rest_framework.pagination import LimitOffsetPagination
from django.db import transaction
from django_filters import rest_framework as f
from .serializers import *
class StaffWrite(permissions.BasePermission):
 def has_permission(self,r,v):
  if r.method in permissions.SAFE_METHODS: return True
  if not r.user.is_authenticated: return False
  if r.method=='DELETE': return r.user.is_staff
  return r.user.is_staff or r.user.groups.filter(name=ROLE).exists()
ROLE='vendedor'
class ProductoFilter(f.FilterSet):
 categoria=f.CharFilter(field_name='categoria__nombre',lookup_expr='iexact')
 marca=f.CharFilter(lookup_expr='iexact')
 precio_min=f.NumberFilter(field_name='precio',lookup_expr='gte')
 precio_max=f.NumberFilter(field_name='precio',lookup_expr='lte')
 disponible=f.BooleanFilter(method='stock_filter')
 def stock_filter(self,q,n,v): return q.filter(stock__gt=0) if v else q.filter(stock=0)
 class Meta: model=Producto; fields=[]
class CategoriaView(viewsets.ReadOnlyModelViewSet):
 queryset=Categoria.objects.all(); serializer_class=CategoriaSerializer
class ProductoView(viewsets.ModelViewSet):
 queryset=Producto.objects.select_related('categoria','vendedor').annotate(rating_promedio=m.Avg('resenas__calificacion')).order_by('id'); serializer_class=ProductoSerializer; permission_classes=[StaffWrite]; filterset_class=ProductoFilter; search_fields=['nombre','descripcion','marca']; ordering_fields=['precio','rating_promedio','fecha_creacion']
 def perform_create(self,s): s.save(vendedor=self.request.user)
 def perform_update(self,s):
  if not self.request.user.is_staff and s.instance.vendedor!=self.request.user: raise PermissionDenied()
  s.save()
 @action(detail=True,url_path='reseñas')
 def resenas(self,r,pk=None): return Response(ResenaSerializer(self.get_object().resenas.all(),many=True).data)
class CarritoView(viewsets.ViewSet):
 permission_classes=[permissions.IsAuthenticated]
 def cart(self): return Carrito.objects.get_or_create(usuario=self.request.user)[0]
 def list(self,r):
  c=self.cart(); items=[{'producto':i.producto_id,'cantidad':i.cantidad,'precio':str(i.producto.precio*(100-i.producto.descuento)/100)} for i in c.items.select_related('producto')]; from decimal import Decimal
  sub=sum((Decimal(i['precio'])*i['cantidad'] for i in items),Decimal(0)); return Response({'usuario':r.user.pk,'items':items,'subtotal':sub,'impuestos':sub*Decimal('.18'),'total':sub*Decimal('1.18'),'total_con_descuento':sub*Decimal('1.18'),'cantidad_items':sum(i['cantidad'] for i in items)})
 def change(self,r,add=False):
  try: p=Producto.objects.get(pk=r.data.get('producto')); n=int(r.data.get('cantidad',1))
  except (Producto.DoesNotExist,ValueError,TypeError): raise ValidationError('Producto o cantidad inválida')
  c=self.cart(); i=c.items.filter(producto=p).first(); n=n+(i.cantidad if i and add else 0)
  if n<1 or n>p.stock: raise ValidationError('Cantidad fuera de stock')
  Item.objects.update_or_create(carrito=c,producto=p,defaults={'cantidad':n}); return self.list(r)
 @action(detail=False,methods=['post'])
 def agregar(self,r): return self.change(r,True)
 @action(detail=False,methods=['post'])
 def actualizar(self,r): return self.change(r)
 @action(detail=False,methods=['post'])
 def eliminar(self,r): self.cart().items.filter(producto_id=r.data.get('producto')).delete(); return self.list(r)
 @action(detail=False,methods=['post'])
 def vaciar(self,r): self.cart().items.all().delete(); return self.list(r)
 @action(detail=False,methods=['post'])
 def checkout(self,r): return checkout(r)
@transaction.atomic
def checkout(r):
 from decimal import Decimal
 c=Carrito.objects.get_or_create(usuario=r.user)[0]; items=list(c.items.all()); snapshot=[]; total=Decimal(0)
 if not items or not r.data.get('direccion_envio') or not r.data.get('metodo_pago'): raise ValidationError('Carrito vacío o datos de envío/pago faltantes')
 for i in items:
  p=Producto.objects.select_for_update().get(pk=i.producto_id)
  if p.stock<i.cantidad: raise ValidationError('Stock insuficiente')
  price=p.precio*(100-p.descuento)/100; total+=price*i.cantidad; snapshot.append({'producto':p.pk,'vendedor':p.vendedor_id,'nombre':p.nombre,'cantidad':i.cantidad,'precio':str(price)}); p.stock-=i.cantidad; p.save(update_fields=['stock'])
 o=Orden.objects.create(usuario=r.user,items=snapshot,total=total*Decimal('1.18'),direccion_envio=r.data['direccion_envio'],metodo_pago=r.data['metodo_pago']); c.items.all().delete(); return Response(OrdenSerializer(o).data,status=201)
class OrdenPagination(LimitOffsetPagination): default_limit=50
class OrdenView(viewsets.ModelViewSet):
 serializer_class=OrdenSerializer; permission_classes=[permissions.IsAuthenticated]; pagination_class=OrdenPagination; http_method_names=['get','post','patch','head','options']
 def get_queryset(self):
  u=self.request.user; q=Orden.objects.all().order_by('-id'); return q if u.is_staff else q.filter(pk__in=[o.pk for o in q if o.usuario_id==u.pk or any(i.get('vendedor')==u.pk for i in o.items)])
 def create(self,r,*a,**kw): return checkout(r)
 def partial_update(self,r,*a,**kw):
  o=self.get_object(); u=r.user
  if not u.is_staff and not all(i.get('vendedor')==u.pk for i in o.items): raise PermissionDenied()
  new=r.data.get('estado'); allowed={'pendiente':'pagada','pagada':'enviada','enviada':'entregada'}
  if allowed.get(o.estado)!=new: raise ValidationError('Transición inválida')
  o.estado=new
  if new=='enviada': o.numero_seguimiento=f'TM-{o.pk:08d}'
  o.save(); return Response(OrdenSerializer(o).data)
 @action(detail=True,methods=['post'])
 @transaction.atomic
 def cancelar(self,r,pk=None):
  o=self.get_object()
  if o.usuario!=r.user and not r.user.is_staff: raise PermissionDenied()
  if o.estado!='pendiente': raise ValidationError('Solo órdenes pendientes')
  for i in o.items: Producto.objects.filter(pk=i['producto']).update(stock=m.F('stock')+i['cantidad'])
  o.estado='cancelada'; o.save(); return Response(OrdenSerializer(o).data)
 @action(detail=False,url_path='mis-ordenes')
 def mis_ordenes(self,r): return Response(OrdenSerializer(Orden.objects.filter(usuario=r.user),many=True).data)
class ResenaView(viewsets.ModelViewSet):
 queryset=Resena.objects.all().order_by('id'); serializer_class=ResenaSerializer; http_method_names=['get','post','delete','head','options']
 def perform_create(self,s): s.save(usuario=self.request.user)
 def perform_destroy(self,o):
  if o.usuario!=self.request.user and not self.request.user.is_staff: raise PermissionDenied()
  o.delete()
