from datetime import date, timedelta
from django.db.models import Sum, Count, Q
from django.utils.timezone import now
from monitoramento.models.boleto import Boleto


class KPIService:
    """Service class for handling KPI calculations and business logic."""

    @staticmethod
    def get_periodo_datas(hoje: date) -> tuple[date, date, date, date]:
        """Calculate date ranges for previous and current months."""
        if hoje.month == 1:
            primeiro_dia_mes_anterior = date(hoje.year - 1, 12, 1)
            primeiro_dia_mes_retrasado = date(hoje.year - 1, 11, 1)
        else:
            primeiro_dia_mes_anterior = date(hoje.year, hoje.month - 1, 1)
            primeiro_dia_mes_retrasado = date(hoje.year, hoje.month - 2, 1)

        ultimo_dia_mes_anterior = (
            primeiro_dia_mes_anterior.replace(day=28) + timedelta(days=4)
        ).replace(day=1) - timedelta(days=1)

        ultimo_dia_mes_retrasado = (
            primeiro_dia_mes_retrasado.replace(day=28) + timedelta(days=4)
        ).replace(day=1) - timedelta(days=1)

        return (
            primeiro_dia_mes_anterior,
            ultimo_dia_mes_anterior,
            primeiro_dia_mes_retrasado,
            ultimo_dia_mes_retrasado,
        )

    @staticmethod
    def calcular_variacao(valor_atual: float, valor_anterior: float) -> float:
        """Calculate percentage variation between two values."""
        return (
            ((valor_atual - valor_anterior) / valor_anterior * 100)
            if valor_anterior
            else 0
        )

    @staticmethod
    def get_volume_financeiro(primeiro_dia: date, ultimo_dia: date) -> float:
        """Get financial volume for a given period."""
        return (
            Boleto.objects.filter(
                criado_em__range=[primeiro_dia, ultimo_dia]
            ).aggregate(total=Sum("valor"))["total"]
            or 0
        )

    @staticmethod
    def get_capturas(primeiro_dia: date, ultimo_dia: date) -> int:
        """Get number of captured boletos for a given period."""
        return Boleto.objects.filter(
            criado_em__range=[primeiro_dia, ultimo_dia]
        ).count()

    @staticmethod
    def get_falhas(primeiro_dia: date, ultimo_dia: date) -> int:
        """Get number of failed boletos for a given period."""
        return Boleto.objects.filter(
            criado_em__range=[primeiro_dia, ultimo_dia],
            status__in=["vencido", "cancelado"],
        ).count()

    @classmethod
    def calcular_kpis(cls) -> list:
        """Calculate all KPIs for the current period."""
        hoje = now().date()
        (
            primeiro_dia_mes_anterior,
            ultimo_dia_mes_anterior,
            primeiro_dia_mes_retrasado,
            ultimo_dia_mes_retrasado,
        ) = cls.get_periodo_datas(hoje)

        # Calculate metrics
        volume_anterior = cls.get_volume_financeiro(
            primeiro_dia_mes_anterior, ultimo_dia_mes_anterior
        )
        volume_retrasado = cls.get_volume_financeiro(
            primeiro_dia_mes_retrasado, ultimo_dia_mes_retrasado
        )

        capturas_anteriores = cls.get_capturas(
            primeiro_dia_mes_anterior, ultimo_dia_mes_anterior
        )
        capturas_retrasadas = cls.get_capturas(
            primeiro_dia_mes_retrasado, ultimo_dia_mes_retrasado
        )

        falhas_anteriores = cls.get_falhas(
            primeiro_dia_mes_anterior, ultimo_dia_mes_anterior
        )
        falhas_retrasadas = cls.get_falhas(
            primeiro_dia_mes_retrasado, ultimo_dia_mes_retrasado
        )

        # Calculate variations
        variacao_volume = cls.calcular_variacao(volume_anterior, volume_retrasado)
        variacao_consistencia = cls.calcular_variacao(
            capturas_anteriores, capturas_retrasadas
        )
        variacao_falhas = cls.calcular_variacao(falhas_anteriores, falhas_retrasadas)

        return [
            {
                "status": "Volume Financeiro",
                "percentage": f"{variacao_volume:+.1f}%",
                "color": "emerald" if variacao_volume >= 0 else "red",
                "description": "Total acumulado referente ao mês anterior.",
                "valor_atual": float(volume_anterior),
                "valor_anterior": float(volume_retrasado),
            },
            {
                "status": "Consistência",
                "percentage": f"{variacao_consistencia:+.1f}%",
                "color": "emerald" if variacao_consistencia >= 0 else "red",
                "description": "Consistência de captura de dados referente ao mês anterior.",
                "valor_atual": capturas_anteriores,
                "valor_anterior": capturas_retrasadas,
            },
            {
                "status": "Falhas",
                "percentage": f"{variacao_falhas:+.1f}%",
                "color": "red" if variacao_falhas >= 0 else "emerald",
                "description": "O total de falhas na extração de boletos referente ao mês anterior.",
                "valor_atual": falhas_anteriores,
                "valor_anterior": falhas_retrasadas,
            },
        ]
