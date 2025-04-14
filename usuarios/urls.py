from django.urls import path
from . import views

urlpatterns = [
    path("empresas/cadastradas/", views.listar_empresas, name="listar_empresas"),
    path("usuario/cadastro/", views.cadastrar_usuario, name="cadastrar_usuario"),
    path("login/", views.login_entrar, name="login_entrar"),
]
