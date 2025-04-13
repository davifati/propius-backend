from django.urls import path, include
from rest_framework.routers import DefaultRouter
from financeiro.views.historico import HistoricoValorBoletoAcumuladoAPIView
from financeiro.views import MesAnteriorKPIAPIView
from financeiro.views.ranking import FinanceiroRankingBoletosAPIView
from financeiro.views.remessa_bancaria import (
    RemessaBancariaViewSet,
)

router = DefaultRouter()
router.register(r"", RemessaBancariaViewSet, basename="remessa-bancaria")

urlpatterns = [
    path("boletos/ranking/", FinanceiroRankingBoletosAPIView.as_view()),
    path("kpi/mensal-retroativo/", MesAnteriorKPIAPIView.as_view()),
    path("boletos/volume/historico/", HistoricoValorBoletoAcumuladoAPIView.as_view()),
    path("boletos/remessas-bancarias/", include(router.urls)),
]
