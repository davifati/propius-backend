from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.db.models import Q

from monitoramento.models.boleto import Boleto
from imoveis.models.unidade import Unidade
from imoveis.models.administradora import Administradora
from monitoramento.serializers.imobiliaria import ImobiliariaSerializer
from drf_spectacular.utils import extend_schema
from datetime import datetime
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter


class CustomPagination(PageNumberPagination):
    page_size = 10  # Valor padrão
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(
    tags=["Monitoramento de Falhas"],
    summary="Falhas de captura de boletos",
    parameters=[
        OpenApiParameter(
            name="page", description="Número da página", required=False, type=int
        ),
        OpenApiParameter(
            name="page_size",
            description="Quantidade de itens por página",
            required=False,
            type=int,
        ),
    ],
)
class FailsExtractionTrackerAPIView(APIView):
    def get(self, request):
        resultado = []
        administradoras = Administradora.objects.all()

        for adm in administradoras:
            unidades_ids = Unidade.objects.filter(
                condominio__administradora=adm
            ).values_list("id", flat=True)

            boletos_qs = Boleto.objects.filter(pasta__in=unidades_ids)

            boletos = [
                {
                    "criado_em": b.criado_em.strftime("%Y-%m-%d"),
                    "status": b.status,
                    "link_pdf": b.link_pdf,
                }
                for b in boletos_qs
            ]

            total_extracoes = len(boletos)
            falhas = sum(
                1 for b in boletos if b["status"] == "vencido" or b["link_pdf"] is None
            )
            taxa_falha = (falhas / total_extracoes * 100) if total_extracoes > 0 else 0

            dados_falhas = []
            boletos_falhos = [b for b in boletos if b["status"] == "vencido"][:3]

            for boleto in boletos_falhos:
                motivo = "Boleto vencido sem pagamento"
                if boleto["link_pdf"] is None:
                    motivo = "Erro na geração do PDF"
                dados_falhas.append({"data": boleto["criado_em"], "motivo": motivo})

            if not boletos_falhos and timezone.now().day % 3 == 0:
                dados_falhas.append(
                    {
                        "data": timezone.now().strftime("%Y-%m-%d"),
                        "motivo": "Erro de conexão com a API",
                    }
                )

            resultado.append(
                {
                    "nome": adm.nome.upper(),
                    "totalExtracoes": total_extracoes,
                    "falhas": falhas,
                    "taxaFalha": round(taxa_falha, 2),
                    "dadosFalhas": dados_falhas,
                }
            )

        # Paginar resultado manualmente
        paginator = CustomPagination()
        paginated_result = paginator.paginate_queryset(resultado, request)

        return paginator.get_paginated_response(paginated_result)


@extend_schema(tags=["Monitoramento de Falhas"], summary="Falhas de captura de boletos")
class FalhasBotsImobiliariaView(APIView):
    def get(self, request, *args, **kwargs):
        # Mock de dados de administradoras
        administradoras_mock = [
            {
                "nome": "Administradora Alpha",
                "site": "https://alpha-adm.com",
                "unidades": [
                    {
                        "condominio": "Condomínio Sol Nascente",
                        "boletos": [
                            {"criado_em": "2025-04-01", "status": "vencido"},
                            {"criado_em": "2025-04-03", "status": "vencido"},
                        ],
                    },
                    {"condominio": "Condomínio Lua Nova", "boletos": []},
                ],
            },
            {
                "nome": "Administradora Beta",
                "site": None,
                "unidades": [{"condominio": "Condomínio Estrela Guia", "boletos": []}],
            },
        ]

        resultado = []

        for adm in administradoras_mock:
            falhas = []

            for unidade in adm["unidades"]:
                boletos_vencidos = [
                    b for b in unidade["boletos"] if b["status"] == "vencido"
                ]

                for boleto in boletos_vencidos:
                    falhas.append(
                        {
                            "data": boleto["criado_em"],
                            "motivo": "Boleto vencido sem pagamento",
                        }
                    )

                # Simulação de erro de autenticação
                # if not boletos_vencidos and datetime.now().day % 2 == 0:
                #    falhas.append(
                #        {
                #            "data": datetime.now().strftime("%Y-%m-%d"),
                #            "motivo": "Erro de autenticação no portal",
                #        }
                #    )

            if falhas:
                resultado.append(
                    {
                        "nome": adm["nome"],
                        "site": adm["site"] or "N/A",
                        "unidade": (
                            adm["unidades"][0]["condominio"]
                            if adm["unidades"]
                            else "N/A"
                        ),
                        "dadosFalhas": falhas,
                    }
                )

        return Response(resultado)


@extend_schema(
    tags=["Monitoramento de Falhas"],
    summary="Estatísticas mensais de falhas de captura de boletos",
)
class MonthlyStatsView(APIView):
    def get(self, request):
        # Exclui boletos sem data de criação ou com data inválida
        boletos_por_mes = (
            Boleto.objects.exclude(criado_em__isnull=True)
            .filter(criado_em__gte="2000-01-01")  # Filtrando datas inválidas
            .annotate(month=TruncMonth("criado_em"))
            .values("month")
            .annotate(
                total=Count("id"),
                errors=Count(
                    "id", filter=Q(link_pdf__isnull=True) | Q(status="vencido")
                ),
            )
            .order_by("month")
        )

        resultado = []
        for item in boletos_por_mes:
            date_obj = item["month"]

            if date_obj:
                date_str = date_obj.strftime("%m/%Y")
            else:
                print("date_obj is None")
                continue  # Ignora boletos com data inválida

            total = item["total"]
            errors = item["errors"]
            success = total - errors

            resultado.append(
                {
                    "date": date_str,
                    "Success": success,
                    "Errors": errors,
                }
            )

        return Response(resultado, status=200)
