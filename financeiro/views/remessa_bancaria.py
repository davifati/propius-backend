# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from monitoramento.models.boleto import Boleto
from financeiro.serializers.remessa_bancaria import BoletoRemessaSerializer
from imoveis.models.unidade import Unidade
from drf_spectacular.utils import extend_schema

from financeiro.models.remessa_bancaria import RemessasBancaria

# boleto → unidade (via pasta) → condominio → administradora → nome


@extend_schema(
    tags=["Remessa Bancária"],
    summary="Retorna os boletos para a remessa bancária",
    description="Retorna os boletos para a remessa bancária",
)
class BoletosRemessaView(APIView):
    def get(self, request):
        condominio = request.GET.get("condominio")
        boletos = Boleto.objects.all()

        if condominio and condominio.lower() != "todos":
            # filtra pelas pastas das unidades do condomínio
            pastas = Unidade.objects.filter(condominio__nome=condominio).values_list(
                "pasta", flat=True
            )
            boletos = boletos.filter(pasta__in=pastas)

        serializer = BoletoRemessaSerializer(boletos, many=True)
        return Response(serializer.data)


# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.core.files.base import ContentFile
from datetime import datetime


@extend_schema(
    tags=["Remessa Bancária"],
)
class RemessaBancariaViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def gerar(self, request):
        try:
            # Validação dos dados recebidos
            unidades = request.data.get("unidades", [])
            mes = request.data.get("mes")

            if not unidades or not mes:
                return Response(
                    {"erro": "Unidades e mês são obrigatórios"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Geração do arquivo CNAB
            linhas_cnab = []
            for i, unidade in enumerate(unidades, 1):
                linha = (
                    f"Linha {i} - {unidade['administradora']} | "
                    f"{unidade['condominio']} | Unidade {unidade['unidade']} | "
                    f"Bloco {unidade['bloco']} | {unidade['nome']} | "
                    f"Valor: {unidade['valor']} | Vencimento: {unidade['data_vencimento']}"
                )
                linhas_cnab.append(linha)

            # Criação do arquivo
            conteudo = "\n".join(linhas_cnab)
            nome_arquivo = (
                f"remessa_{mes}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            arquivo = ContentFile(conteudo.encode("utf-8"))

            # Salvar no banco de dados
            remessa = RemessasBancaria.objects.create(
                mes=mes,
                conteudo=conteudo,
                arquivo=arquivo,
                quantidade_unidades=len(unidades),
            )

            return Response(
                {
                    "mensagem": "Remessa gerada com sucesso",
                    "quantidade_unidades": len(unidades),
                    "mes_referencia": mes,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"erro": "Erro ao gerar remessa", "detalhes": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
