from django.urls import include, path
from rest_framework.routers import DefaultRouter
from imoveis.views.imoveis import ImoveisViewSet
from imoveis.views.administradora import AdministradoraViewSet
from imoveis.views.condominio import CondominioViewSet
from imoveis.views.unidade import UnidadeViewSet


router = DefaultRouter()

router.register(
    r"administradoras", AdministradoraViewSet, basename="ativos-administradoras"
)
router.register(r"condominios", CondominioViewSet, basename="ativos-condominios")
router.register(r"unidades", UnidadeViewSet, basename="ativos-unidades")
router.register(r"ativos-imobiliarios", ImoveisViewSet, basename="ativos-locaticios")


urlpatterns = [
    path("imoveis/", include(router.urls)),
]
