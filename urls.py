from django.urls import path,include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView,SpectacularRedocView
from api import views
router=DefaultRouter()
router.register('productos',views.ProductoView,basename='productos')
router.register('carrito',views.CarritoView,basename='carrito')
router.register('ordenes',views.OrdenView,basename='ordenes')
router.register('reseñas',views.ResenaView,basename='reseñas')
router.register('categorias',views.CategoriaView,basename='categorias')
urlpatterns=[path('admin/',admin.site.urls),path('api/',include(router.urls)),path('api/token/',obtain_auth_token),path('api/schema/',SpectacularAPIView.as_view(),name='schema'),path('api/docs/',SpectacularSwaggerView.as_view(url_name='schema')),path('api/redoc/',SpectacularRedocView.as_view(url_name='schema'))]
from django.views.generic import TemplateView
urlpatterns += [path('',TemplateView.as_view(template_name='tienda.html'))]
