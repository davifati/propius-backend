from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now, timedelta
from django.db.models import Max
from datetime import timedelta

from imoveis.models.administradora import Administradora
from monitoramento.models.boleto import Boleto
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Monitoramento de Cronograma de Execução"],
    summary="Mock de cronograma de execução dos bots",
)
class CronogramaExecucaoBotsView(APIView):
    def get(self, request):
        mock_data = [
            {
                "administradora": "Alpha Gestão",
                "condominio": "Alpha Gestão",
                "ultima_execucao": "2024-03-30T14:30:00",
                "proxima_execucao": "2024-03-30T14:30:00",
                "status": "Sucesso",
            },
            {
                "administradora": "Alpha Gestão 2",
                "condominio": "Alpha Gestão",
                "ultima_execucao": "2024-03-30T14:30:00",
                "proxima_execucao": "2024-03-30T14:30:00",
                "status": "Sucesso",
            },
            {
                "administradora": "Alpha Gestão 3",
                "condominio": "Alpha Gestão",
                "ultima_execucao": "2024-03-30T14:30:00",
                "proxima_execucao": "2024-03-30T14:30:00",
                "status": "Sucesso",
            },
            {
                "administradora": "Alpha Gestão 4 ",
                "condominio": "Alpha Gestão",
                "ultima_execucao": "2024-03-30T14:30:00",
                "proxima_execucao": "2024-03-30T14:30:00",
                "status": "Sucesso",
            },
        ]

        return Response(mock_data)


@extend_schema(
    tags=["Monitoramento de Cronograma de Execução"],
    summary="Cronograma de execução dos bots",
)
class CronogramaExecucaoBotsView_DB(APIView):
    def get(self, request):
        administradoras = Administradora.objects.all()
        data_execucao = "2024-03-30T14:30:00"

        resultado = []

        for administradora in administradoras:
            total_boletos = Boleto.objects.filter(
                unidade__condominio__administradora=administradora
            ).count()
            boletos_com_falha = Boleto.objects.filter(
                unidade__condominio__administradora=administradora,
                status="vencido",  # Assumindo que "vencido" representa falha
            ).count()

            estatistica_falhas = (
                f"{(boletos_com_falha / total_boletos * 100):.2f}%"
                if total_boletos > 0
                else "0%"
            )

            status_execucao = "Falha" if boletos_com_falha > 0 else "Sucesso"

            resultado.append(
                {
                    "administradora": administradora.nome,
                    "dataExecucao": data_execucao,
                    "status": status_execucao,
                    "estatisticaFalhas": estatistica_falhas,
                }
            )

        return Response(resultado)


@extend_schema(
    tags=["Monitoramento de Cronograma de Execução"],
    summary="Cronograma histórico de execução dos bots",
)
class HistoricalExtractionCalendarView(APIView):

    def get(self, request):
        data = [
            {
                "imobiliaria": "APSA",
                "ultimaExtracao": "2025-03-01",
                "proximaExtracao": "2025-03-05",
                "status": "sucesso",
            },
            {
                "imobiliaria": "ABRJ",
                "ultimaExtracao": "2025-03-01",
                "proximaExtracao": "2025-03-06",
                "status": "falha",
            },
            {
                "imobiliaria": "BCF",
                "ultimaExtracao": "2025-03-02",
                "proximaExtracao": "2025-03-07",
                "status": "sucesso",
            },
            {
                "imobiliaria": "ABRJ",
                "ultimaExtracao": "2025-03-02",
                "proximaExtracao": "2025-03-08",
                "status": "inatividade",
            },
            {
                "imobiliaria": "ADRIO",
                "ultimaExtracao": "2025-03-05",
                "proximaExtracao": "2025-03-11",
                "status": "sucesso",
            },
        ]

        return Response(data=data)


@extend_schema(tags=["trash"], summary="Cronograma histórico de execução dos bots")
class HistoricalExtractionCalendarView_2(APIView):
    def get(self, request):

        administradoras = Administradora.objects.all()
        resultado = []

        for administradora in administradoras:
            ultima_extracao = (
                Boleto.objects.filter(
                    unidade__condominio__administradora=administradora
                )
                .aggregate(ultima_extracao=Max("criado_em"))
                .get("criado_em")
            )

            if ultima_extracao:
                proxima_extracao = ultima_extracao + timedelta(days=4)
                boletos_vencidos = Boleto.objects.filter(
                    unidade__condominio__administradora=administradora,
                    status="vencido",
                ).count()

                dias_desde_ultima = (now().date() - ultima_extracao).days
                if dias_desde_ultima > 7:
                    status = "inatividade"
                elif boletos_vencidos > 0:
                    status = "falha"
                else:
                    status = "sucesso"
            else:
                ultima_extracao = "N/A"
                proxima_extracao = "N/A"
                status = "inatividade"

            resultado.append(
                {
                    "imobiliaria": administradora.nome,
                    "ultimaExtracao": (
                        ultima_extracao.strftime("%Y-%m-%d")
                        if ultima_extracao != "N/A"
                        else "N/A"
                    ),
                    "proximaExtracao": (
                        proxima_extracao.strftime("%Y-%m-%d")
                        if proxima_extracao != "N/A"
                        else "N/A"
                    ),
                    "status": status,
                }
            )

        return Response(data=resultado)
