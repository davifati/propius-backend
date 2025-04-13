from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from imoveis.models import Administradora, Condominio, Unidade
from imoveis.serializers import (
    AdministradoraSerializer,
    CondominioSerializer,
    UnidadeSerializer,
    AtivoImovelSerializer,
)
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from imoveis.services.imoveis import ImoveisService


@extend_schema(tags=["Imóveis"])
class ImoveisViewSet(viewsets.ViewSet):
    """
    Gerencia informações completas dos ativos imobiliários, incluindo Administradora,
    Condomínios e Unidades.
    """

    ImoveisService = ImoveisService()

    def _validate_and_save_data(self, serializer_class, data_list):
        """
        Helper method to validate and save data using provided serializer
        """
        objects = []
        for item_data in data_list:
            serializer = serializer_class(data=item_data)
            if not serializer.is_valid():
                return None, serializer.errors
            objects.append(serializer.save())
        return objects, None

    @extend_schema(
        description="Retorna informações detalhadas de todos os ativos imobiliários, incluindo administradoras, condomínios e unidades",
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Número da página a ser retornada (começa em 1)",
                default=1,
                examples=[
                    OpenApiExample("Página 1", value=1),
                    OpenApiExample("Página 2", value=2),
                ],
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Número de itens por página",
                default=10,
                examples=[
                    OpenApiExample("10 itens", value=10),
                    OpenApiExample("20 itens", value=20),
                    OpenApiExample("50 itens", value=50),
                ],
            ),
        ],
        responses={200: AtivoImovelSerializer},
    )
    @action(detail=False, methods=["get"], url_path="all-info")
    def info_ativos_imoveis(self, request) -> Response:
        """
        Retorna informações detalhadas de todos os ativos imobiliários, incluindo
        administradoras, condomínios e unidades.

        Parâmetros de paginação:
        - page: Número da página (começa em 1)
        - page_size: Número de itens por página

        Exemplo de URL:
        /api/imoveis/ativos-imobiliarios/info/?page=1&page_size=20
        """
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        response_data = self.ImoveisService.build_imoveis_info_paginated(
            page=page, page_size=page_size
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="info")
    def flat_info_ativos_imoveis(self, request) -> Response:
        """
        Retorna informações achatadas de todos os ativos imobiliários, incluindo
        administradoras, condomínios e unidades.
        """
        response_data = self.ImoveisService.build_flat_imoveis_data()
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="cadastro")
    def register_ativos(self, request):
        """
        Cadastra informações completas dos Imoveis: Administradoras, Condomínios e Unidades
        """
        data = request.data

        # Process each data type using helper method
        administradoras, errors = self._validate_and_save_data(
            AdministradoraSerializer, data.get("administradoras", [])
        )
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        condominios, errors = self._validate_and_save_data(
            CondominioSerializer, data.get("condominios", [])
        )
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        unidades, errors = self._validate_and_save_data(
            UnidadeSerializer, data.get("unidades", [])
        )
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare response data
        response_data = {
            "administradoras": AdministradoraSerializer(
                administradoras, many=True
            ).data,
            "condominios": CondominioSerializer(condominios, many=True).data,
            "unidades": UnidadeSerializer(unidades, many=True).data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
