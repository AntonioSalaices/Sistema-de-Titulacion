from django.conf.urls import url
from . import views
from views import index,vista_login,vista_registrar,vista_logout,GraficaView, vista_registraregre,  contacto_mail, registrarminuta, get_data, CharData, report, vista_lista_minutas, EgresadoViewSet
urlpatterns = [
    url(r'^$', index, name="index" ),
    url(r'^login/', vista_login, name="login" ),
    url(r'^usuarios/registrar',vista_registrar , name="registrar" ),
    url(r'^usuarios/egresados', vista_registraregre , name="egresados" ),
    url(r'^usuarios/listado', EgresadoViewSet , name="busqueda" ),
    url(r'^usuarios/data', GraficaView.as_view() , name="grafica" ),
    url(r'^usuarios/reporte', views.report, name='report'),
    url(r'^usuarios/graficas', CharData.as_view()),
    url(r'^usuarios/convocar', contacto_mail , name="convocar" ),
    url(r'^usuarios/minuta', registrarminuta , name="minuta" ),
    url(r'^usuarios/lista_minutas', vista_lista_minutas , name="listaminutas" ),
    url(r'^logout/',vista_logout,name='logout'),
]
