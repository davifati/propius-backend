from django.db.models import Sum
from typing import List, Dict, Any
from imoveis.models.administradora import Administradora


class RankingService:
    """Service for handling ranking calculations."""

    @staticmethod
    def get_ranking_administradoras() -> List[Dict[str, Any]]:
        """
        Get ranking of administradoras by total boleto value.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing administradora name and total value
        """
        ranking_boletos = (
            Administradora.objects.annotate(
                valor_total=Sum("condominios__unidades__boletos__valor")
            )
            .filter(valor_total__gt=0)
            .order_by("-valor_total")
            .values("nome", "valor_total")
        )

        return [
            {
                "administradora": item["nome"],
                "valor": float(item["valor_total"]),
                "posicao": idx + 1,
            }
            for idx, item in enumerate(ranking_boletos)
        ]
