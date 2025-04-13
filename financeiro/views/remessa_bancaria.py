from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter

from financeiro.models import RemessaBancaria, RemessaBancariaBoleto
from financeiro.serializers.remessa_bancaria import (
    RemessaBancariaSerializer,
    RemessaBancariaCreateSerializer,
    RemessaBancariaBoletoSerializer,
)


@extend_schema(tags=["Remessa Bancária"])
class RemessaBancariaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing remessa bancária operations.

    Provides endpoints for:
    - CRUD operations on remessas
    - Processing remessas and return files
    - Managing boletos within remessas
    """

    queryset = RemessaBancaria.objects.all()
    serializer_class = RemessaBancariaSerializer
    filterset_fields = ["administradora", "condominio", "status"]
    search_fields = ["condominio__nome", "administradora__nome"]
    ordering_fields = ["data_envio", "data_processamento", "status"]
    ordering = ["-data_envio"]

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == "create":
            return RemessaBancariaCreateSerializer
        return RemessaBancariaSerializer

    @extend_schema(
        summary="Process remessa",
        description="Process the remessa bancária and generate the remessa file.",
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID of the remessa to process",
            ),
        ],
    )
    @action(detail=True, methods=["post"])
    def processar_remessa(self, request, pk=None):
        """Process the remessa bancária and generate the remessa file."""
        remessa = self.get_object()

        if remessa.status != RemessaBancaria.STATUS_PENDENTE:
            return Response(
                {"error": "Apenas remessas pendentes podem ser processadas"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                # TODO: Implement the actual remessa file generation logic here
                # This is where you'll integrate with your bank's API or file generation service

                # Update remessa status
                remessa.status = RemessaBancaria.STATUS_PROCESSADA
                remessa.data_processamento = timezone.now()
                remessa.save()

                # Update boletos status
                RemessaBancariaBoleto.objects.filter(remessa=remessa).update(
                    processado=True, data_processamento=timezone.now()
                )

                return Response(
                    RemessaBancariaSerializer(remessa).data, status=status.HTTP_200_OK
                )

        except Exception as e:
            remessa.status = RemessaBancaria.STATUS_ERRO
            remessa.mensagem_erro = str(e)
            remessa.save()

            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Process return file",
        description="Process the return file from the bank and update boleto statuses.",
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID of the remessa to process return file",
            ),
        ],
    )
    @action(detail=True, methods=["post"])
    def processar_retorno(self, request, pk=None):
        """Process the return file from the bank and update boleto statuses."""
        remessa = self.get_object()

        if remessa.status != RemessaBancaria.STATUS_PROCESSADA:
            return Response(
                {"error": "Apenas remessas processadas podem ter retorno processado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                # TODO: Implement the actual return file processing logic here
                # This is where you'll integrate with your bank's API or file processing service

                # Update remessa status
                remessa.status = RemessaBancaria.STATUS_CONCLUIDA
                remessa.save()

                # Update boletos based on return file information
                # This is a placeholder - implement according to your bank's return file format
                RemessaBancariaBoleto.objects.filter(remessa=remessa).update(
                    processado=True, data_processamento=timezone.now()
                )

                return Response(
                    RemessaBancariaSerializer(remessa).data, status=status.HTTP_200_OK
                )

        except Exception as e:
            remessa.status = RemessaBancaria.STATUS_ERRO
            remessa.mensagem_erro = str(e)
            remessa.save()

            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="List remessa boletos",
        description="List all boletos associated with a remessa.",
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID of the remessa to list boletos",
            ),
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Filter boletos by status",
            ),
        ],
    )
    @action(detail=True, methods=["get"])
    def boletos(self, request, pk=None):
        """List all boletos associated with a remessa."""
        remessa = self.get_object()
        status_filter = request.query_params.get("status")

        boletos = RemessaBancariaBoleto.objects.filter(remessa=remessa)
        if status_filter:
            boletos = boletos.filter(status=status_filter)

        serializer = RemessaBancariaBoletoSerializer(boletos, many=True)
        return Response(serializer.data)
