import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','settings')
import django
django.setup()
from api.models import *
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from datetime import timedelta
admin,_=User.objects.get_or_create(username='admin',defaults={'is_staff':True,'is_superuser':True}); admin.set_password('DemoAdmin2026!'); admin.save()
users=[]
for i in range(1,21):
 u,_=User.objects.get_or_create(username=f'usuario{i}'); u.set_password('DemoUsuario2026!'); u.save(); Token.objects.get_or_create(user=u); users.append(u)
g,_=Group.objects.get_or_create(name='vendedor'); users[0].groups.add(g)
for i in range(100):
 c,_=Categoria.objects.get_or_create(nombre=['laptops','accesorios','smartphones','componentes'][i%4]); p,_=Producto.objects.get_or_create(sku=f'TM{i:04}',defaults=dict(nombre=f'{c.nombre.title()} modelo {i+1}',marca=['Dell','Lenovo','Samsung','Asus'][i%4],categoria=c,vendedor=users[0],precio=100+i*25,stock=20))
for i in range(50):
 ps=list(Producto.objects.order_by('id')[i*2:i*2+2]); u=users[1+i%19]; items=[dict(producto=p.pk,vendedor=p.vendedor_id,nombre=p.nombre,cantidad=1,precio=str(p.precio)) for p in ps]; o,_=Orden.objects.get_or_create(usuario=u,numero_seguimiento=f'DEMO{i}',defaults=dict(items=items,direccion_envio='Huancayo',metodo_pago='simulado',estado='entregada',total=sum(p.precio for p in ps)))
 for p in ps: Resena.objects.get_or_create(usuario=u,producto=p,defaults=dict(calificacion=4+i%2,titulo='Compra satisfactoria',comentario='Producto conforme'))

print("Datos de prueba listos")
