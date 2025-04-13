from django.urls import path, include
from rest_framework.routers import DefaultRouter
from monitoramento.views.boleto import BoletoViewSet
from monitoramento.views.cronograma_execucao import (
    CronogramaExecucaoBotsView,
    HistoricalExtractionCalendarView,
    HistoricalExtractionCalendarView_2,
)
from monitoramento.views.falhas import (
    FalhasBotsImobiliariaView,
    FailsExtractionTrackerAPIView,
    MonthlyStatsView,
)
from monitoramento.views.admin_graph import admin_grafico_boletos

router = DefaultRouter()
router.register(r"boletos", BoletoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "falhas/imobiliaria/",
        FalhasBotsImobiliariaView.as_view(),
        name="falhas-imobiliaria",
    ),
    path(
        "falhas/extracao/",
        FailsExtractionTrackerAPIView.as_view(),
        name="falhas-extracao",
    ),
    path(
        "estatisticas/mensais/", MonthlyStatsView.as_view(), name="estatisticas-mensais"
    ),
    path(
        "historico/extracao/",
        HistoricalExtractionCalendarView.as_view(),
        name="historico-extracao",
    ),
    path(
        "historico-extracao-2-not-used/",
        HistoricalExtractionCalendarView_2.as_view(),
        name="historico-extracao-2",
    ),
    path(
        "cronograma/execucao/",
        CronogramaExecucaoBotsView.as_view(),
        name="cronograma-execucao",
    ),
    path("admin/grafico-boletos/", admin_grafico_boletos, name="admin_grafico_boletos"),
]
