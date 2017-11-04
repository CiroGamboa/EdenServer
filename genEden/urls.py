from django.conf.urls import url
from genEden import views


urlpatterns = [

	#url(r'^registrarUsuario/$',views.registrar_usuario), #POST
	url(r'^registrarUsuario/(?P<passw>.*)/(?P<nombre>.*)/(?P<email>.*)/$',views.registrar_usuario),
	url(r'^loginUsuario/(?P<email>.*)/(?P<passw>.*)/$',views.login_usuario),
	url(r'^getMaceta/(?P<idUsuario>.*)/$',views.get_maceta), # URL temporal, poco eficiente
	#url(r'^registrarMaceta/$',views.registrar_maceta),
	url(r'^registrarMaceta/(?P<idUsuario>.*)/$',views.registrar_maceta),
	url(r'^getVariables/(?P<pkUsuario>[0-9]+)/(?P<pkMaceta>[0-9]+)/$',views.get_variables),
	url(r'^regarMaceta/(?P<pkUsuario>[0-9]+)/(?P<pkMaceta>[0-9]+)/$',views.regar_maceta),
	url(r'^agregarSemilla/(?P<pkUsuario>[0-9]+)/(?P<pkMaceta>[0-9]+)/(?P<pkPlanta>[0-9]+)/$',views.agregar_semilla),
]