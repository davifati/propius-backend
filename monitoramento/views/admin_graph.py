from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


@staff_member_required
def admin_grafico_boletos(request):
    # Dados mockados
    dados = [
        {"usuario": "João", "quantidade": 15},
        {"usuario": "Maria", "quantidade": 23},
        {"usuario": "Carlos", "quantidade": 8},
        {"usuario": "Ana", "quantidade": 12},
    ]

    labels = [item["usuario"] for item in dados]
    values = [item["quantidade"] for item in dados]

    return render(
        request,
        "admin/grafico_boletos.html",
        {"labels": labels, "values": values, "title": "Boletos por Usuário"},
    )

