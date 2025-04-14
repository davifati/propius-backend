from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from monitoramento.models.boleto import Boleto
from imoveis.models.unidade import Unidade


@extend_schema(
    tags=["Financeiro"],
    summary="Histórico de valores acumulados de boletos por administradora",
)
class HistoricoValorBoletoAcumuladoAPIView(APIView):
    def get(self, request, *args, **kwargs) -> Response:
        """
        Retorna o histórico mensal dos valores acumulados de boletos por administradora.
        """
        try:
            # Mapeia as unidades com suas administradoras
            unidades = Unidade.objects.select_related(
                "condominio__administradora"
            ).exclude(pasta__isnull=True)
            pasta_to_adm = {}
            for unidade in unidades:
                if unidade.pasta:
                    try:
                        pasta_int = int(unidade.pasta)
                        pasta_to_adm[pasta_int] = unidade.condominio.administradora.nome
                    except ValueError:
                        continue

            # Recupera todos os boletos com a data de vencimento
            boletos = Boleto.objects.all().values("pasta", "valor", "data_vencimento")

            # Inicializa o dicionário para armazenar o histórico
            historico = {}

            for boleto in boletos:
                pasta = boleto["pasta"]
                valor = boleto["valor"]
                data_vencimento = boleto["data_vencimento"]

                try:
                    pasta_int = int(pasta)
                    adm_nome = pasta_to_adm.get(pasta_int)

                    if adm_nome:
                        # Calcula o mês/ano
                        mes_ano = f"{data_vencimento.month:02d}/{data_vencimento.year}"

                        # Se a administradora não existir no histórico, inicializa o dicionário
                        if adm_nome not in historico:
                            historico[adm_nome] = {}

                        if mes_ano not in historico[adm_nome]:
                            historico[adm_nome][mes_ano] = 0

                        # Atualiza o valor acumulado para essa administradora e mês/ano
                        historico[adm_nome][mes_ano] += float(valor)

                except ValueError:
                    continue

            # Converte o histórico para o formato esperado pela resposta da API
            data = []
            for adm_nome, meses in historico.items():
                for mes_ano, total in meses.items():
                    data.append(
                        {
                            "date": mes_ano,
                            "name": adm_nome.upper(),  # Adicionando o nome da administradora
                            "balance": round(total, 2),
                        }
                    )

            # Ordena os dados pelo mês/ano e nome da administradora
            data.sort(key=lambda x: (x["date"], x["name"]))

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Erro ao buscar histórico de boletos", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
