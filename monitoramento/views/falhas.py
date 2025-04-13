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
                if not boletos_vencidos and datetime.now().day % 2 == 0:
                    falhas.append(
                        {
                            "data": datetime.now().strftime("%Y-%m-%d"),
                            "motivo": "Erro de autenticação no portal",
                        }
                    )

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


@extend_schema(tags=["Monitoramento de Falhas"], summary="Falhas de captura de boletos")
class FailsExtractionTrackerAPIView(APIView):
    def get(self, request):
        # Mock de dados simulando administradoras e boletos
        administradoras_mock = [
            {
                "nome": "Administradora Central",
                "boletos": [
                    {
                        "criado_em": "2025-04-01",
                        "status": "vencido",
                        "link_pdf": "link1.pdf",
                    },
                    {"criado_em": "2025-04-02", "status": "pago", "link_pdf": None},
                    {"criado_em": "2025-04-03", "status": "vencido", "link_pdf": None},
                    {
                        "criado_em": "2025-04-04",
                        "status": "pago",
                        "link_pdf": "link2.pdf",
                    },
                ],
            },
            {
                "nome": "Administradora Sul",
                "boletos": [
                    {"criado_em": "2025-04-01", "status": "pago", "link_pdf": None},
                    {
                        "criado_em": "2025-04-02",
                        "status": "pago",
                        "link_pdf": "link3.pdf",
                    },
                ],
            },
        ]

        resultado = []

        for adm in administradoras_mock:
            boletos = adm["boletos"]
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

            # Simular falha genérica quando não houver boletos falhos
            if not boletos_falhos and datetime.now().day % 3 == 0:
                dados_falhas.append(
                    {
                        "data": datetime.now().strftime("%Y-%m-%d"),
                        "motivo": "Erro de conexão com a API",
                    }
                )

            resultado.append(
                {
                    "nome": adm["nome"],
                    "totalExtracoes": total_extracoes,
                    "falhas": falhas,
                    "taxaFalha": round(taxa_falha, 2),
                    "dadosFalhas": dados_falhas,
                }
            )

        return Response(resultado, status=200)


from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Monitoramento de Falhas"],
    summary="Estatísticas mensais de falhas de captura de boletos",
)
class MonthlyStatsView(APIView):
    def get(self, request):
        # Dados mockados de exemplo (estatísticas por mês)
        data = [
            {"date": "01/2024", "Success": 980, "Errors": 12},
            {"date": "02/2024", "Success": 1023, "Errors": 18},
            {"date": "03/2024", "Success": 1105, "Errors": 22},
            {"date": "04/2024", "Success": 1150, "Errors": 19},
            {"date": "05/2024", "Success": 1078, "Errors": 25},
            {"date": "06/2024", "Success": 1034, "Errors": 27},
            {"date": "07/2024", "Success": 995, "Errors": 30},
            {"date": "08/2024", "Success": 1001, "Errors": 21},
            {"date": "09/2024", "Success": 1120, "Errors": 17},
            {"date": "10/2024", "Success": 1202, "Errors": 23},
            {"date": "11/2024", "Success": 1255, "Errors": 29},
            {"date": "12/2024", "Success": 1300, "Errors": 33},
        ]

        return Response(data, status=200)


@extend_schema(tags=["Monitoramento de Falhas"], summary="Falhas de captura de boletos")
class FalhasBotsImobiliariaView_DB(APIView):
    def get(self, request, *args, **kwargs):
        administradoras = Administradora.objects.all()
        resultado = []

        for administradora in administradoras:
            unidades = Unidade.objects.filter(condominio__administradora=administradora)

            falhas = []
            for unidade in unidades:
                boletos_vencidos = Boleto.objects.filter(
                    unidade=unidade, status="vencido"
                )

                for boleto in boletos_vencidos:
                    falhas.append(
                        {
                            "data": boleto.criado_em.strftime("%Y-%m-%d"),
                            "motivo": "Boleto vencido sem pagamento",
                        }
                    )

                # Simulação de erro de autenticação ou processamento
                if not boletos_vencidos and now().day % 2 == 0:
                    falhas.append(
                        {
                            "data": now().strftime("%Y-%m-%d"),
                            "motivo": "Erro de autenticação no portal",
                        }
                    )

            if falhas:
                resultado.append(
                    {
                        "nome": administradora.nome,
                        "site": administradora.site or "N/A",
                        "unidade": (
                            unidade.condominio.nome if unidades.exists() else "N/A"
                        ),
                        "dadosFalhas": falhas,
                    }
                )

        return Response(resultado)


@extend_schema(tags=["Monitoramento de Falhas"], summary="Falhas de captura de boletos")
class FailsExtractionTrackerAPIView_DB(APIView):
    def get(self, request):
        administradoras = Administradora.objects.all()
        resultado = []

        for administradora in administradoras:
            boletos = Boleto.objects.filter(
                unidade__condominio__administradora=administradora
            )

            total_extracoes = boletos.count()
            falhas = (
                boletos.filter(status="vencido").count()
                + boletos.filter(link_pdf__isnull=True).count()
            )
            taxa_falha = (falhas / total_extracoes * 100) if total_extracoes > 0 else 0

            dados_falhas = []
            boletos_falhos = boletos.filter(status="vencido")[:3]

            for boleto in boletos_falhos:
                motivo = "Boleto vencido sem pagamento"
                if boleto.link_pdf is None:
                    motivo = "Erro na geração do PDF"

                dados_falhas.append(
                    {"data": boleto.criado_em.strftime("%Y-%m-%d"), "motivo": motivo}
                )

            if not boletos_falhos and now().day % 3 == 0:
                dados_falhas.append(
                    {
                        "data": now().strftime("%Y-%m-%d"),
                        "motivo": "Erro de conexão com a API",
                    }
                )

            resultado.append(
                {
                    "nome": administradora.nome,
                    "totalExtracoes": total_extracoes,
                    "falhas": falhas,
                    "taxaFalha": round(taxa_falha, 2),
                    "dadosFalhas": dados_falhas,
                }
            )

        return Response(resultado, status=200)


@extend_schema(
    tags=["Monitoramento de Falhas"],
    summary="Estatísticas mensais de falhas de captura de boletos",
)
class MonthlyStatsView_DB(APIView):
    def get(self, request):
        example_graph = False  # TODO: DELETE ME
        if not example_graph:
            stats = (
                Boleto.objects.annotate(month=TruncMonth("criado_em"))
                .values("month")
                .annotate(
                    Success=Count("id", filter=Q(status__in=["pago", "a vencer"])),
                    Errors=Count("id", filter=Q(status__in=["vencido", "cancelado"])),
                )
                .order_by("month")
            )

            data = [
                {
                    "date": item["month"].strftime("%m/%Y"),
                    "Success": item["Success"],
                    "Errors": item["Errors"],
                }
                for item in stats
            ]
        else:
            data = [
                {"date": "01/2023", "Success": 1040, "Errors": 10},
                {"date": "02/2023", "Success": 1200, "Errors": 15},
                {"date": "03/2023", "Success": 1130, "Errors": 20},
                {"date": "04/2023", "Success": 1050, "Errors": 18},
                {"date": "05/2023", "Success": 920, "Errors": 22},
                {"date": "06/2023", "Success": 870, "Errors": 25},
                {"date": "07/2023", "Success": 790, "Errors": 30},
                {"date": "08/2023", "Success": 910, "Errors": 28},
                {"date": "09/2023", "Success": 951, "Errors": 35},
                {"date": "10/2023", "Success": 1232, "Errors": 40},
                {"date": "11/2023", "Success": 1230, "Errors": 45},
                {"date": "12/2023", "Success": 1289, "Errors": 50},
            ]

        return Response(data, status=200)
