from typing import List, Dict, Any, Optional
from django.db.models import Q

from financeiro.models.remessa_bancaria import RemessaBancaria, RemessaBancariaBoleto
from imoveis.models.administradora import Administradora
from imoveis.models.condominio import Condominio
from imoveis.models.unidade import Unidade


class RemessaService:
    """Service for managing remessa bancaria operations."""

    @staticmethod
    def criar_remessa(
        administradora_id: int, condominio_id: int, boletos_ids: List[int]
    ) -> RemessaBancaria:
        """
        Create a new remessa bancaria with selected boletos.

        Args:
            administradora_id: ID of the administradora
            condominio_id: ID of the condominio
            boletos_ids: List of boleto IDs to include

        Returns:
            RemessaBancaria: The created remessa instance
        """
        # Validate inputs
        administradora = Administradora.objects.get(id=administradora_id)
        condominio = Condominio.objects.get(id=condominio_id)

        # Create remessa
        remessa = RemessaBancaria.objects.create(
            administradora=administradora, condominio=condominio
        )

        # Add boletos
        for boleto_id in boletos_ids:
            boleto = RemessaBancariaBoleto.objects.get(id=boleto_id)
            boleto.remessa = remessa
            boleto.status = "PENDENTE"
            boleto.save()

        # Update totals
        remessa.atualizar_totais()
        return remessa

    @staticmethod
    def processar_remessa(remessa_id: int) -> Dict[str, Any]:
        """
        Process a remessa bancaria and generate the file.

        Args:
            remessa_id: ID of the remessa to process

        Returns:
            Dict[str, Any]: Processing result with status and message
        """
        try:
            remessa = RemessaBancaria.objects.get(id=remessa_id)

            # Here you would implement the actual remessa file generation
            # This is a placeholder for the actual implementation
            remessa.status = "PROCESSADA"
            remessa.save()

            return {
                "status": "success",
                "message": "Remessa processada com sucesso",
                "remessa_id": remessa_id,
            }
        except Exception as e:
            remessa.status = "ERRO"
            remessa.observacao = str(e)
            remessa.save()

            return {"status": "error", "message": str(e), "remessa_id": remessa_id}

    @staticmethod
    def listar_remessas(
        administradora_id: Optional[int] = None,
        condominio_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List remessas with optional filters.

        Args:
            administradora_id: Optional filter by administradora
            condominio_id: Optional filter by condominio
            status: Optional filter by status

        Returns:
            List[Dict[str, Any]]: List of remessas with their details
        """
        query = Q()

        if administradora_id:
            query &= Q(administradora_id=administradora_id)
        if condominio_id:
            query &= Q(condominio_id=condominio_id)
        if status:
            query &= Q(status=status)

        remessas = RemessaBancaria.objects.filter(query)

        return [
            {
                "id": remessa.id,
                "administradora": remessa.administradora.nome,
                "condominio": remessa.condominio.nome,
                "data_geracao": remessa.data_geracao,
                "status": remessa.status,
                "valor_total": float(remessa.valor_total),
                "quantidade_boletos": remessa.quantidade_boletos,
            }
            for remessa in remessas
        ]

    @staticmethod
    def listar_boletos_remessa(
        remessa_id: int, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List boletos in a remessa with optional status filter.

        Args:
            remessa_id: ID of the remessa
            status: Optional filter by status

        Returns:
            List[Dict[str, Any]]: List of boletos with their details
        """
        query = Q(remessa_id=remessa_id)
        if status:
            query &= Q(status=status)

        boletos = RemessaBancariaBoleto.objects.filter(query)

        return [
            {
                "id": boleto.id,
                "unidade": str(boleto.unidade),
                "numero_documento": boleto.numero_documento,
                "valor": float(boleto.valor),
                "data_vencimento": boleto.data_vencimento,
                "status": boleto.status,
                "linha_digitavel": boleto.linha_digitavel,
                "codigo_barras": boleto.codigo_barras,
            }
            for boleto in boletos
        ]
