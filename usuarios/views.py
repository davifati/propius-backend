from django.shortcuts import render
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny


EMPRESAS_MOCK = ["Propius", "AdministramosImoveis"]


@extend_schema(
    summary="Lista de empresas",
    tags=["Controle de Usuários"],
)
@api_view(["GET"])
def listar_empresas(request):
    """
    Retorna lista de empresas cadastradas no sistema, as quais já possuem automacao de captura de boletos.
    """
    return Response(EMPRESAS_MOCK, status=status.HTTP_200_OK)


@extend_schema(
    summary="Cadastro de usuario",
    tags=["Controle de Usuários"],
)
@api_view(["POST"])
def cadastrar_usuario(request):
    """
    Cadastro de um novo usuario no sistema.
    """
    data = request.data
    required_fields = ["email", "password", "empresa", "perfil"]

    # Verifica se todos os campos obrigatórios foram enviados
    if not all(field in data and data[field] for field in required_fields):
        return Response(
            {"error": "Todos os campos são obrigatórios."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Aqui você pode adicionar lógica real futuramente.
    print("Usuário cadastrado (mock):", data)

    return Response(
        {"message": "Cadastro realizado com sucesso."}, status=status.HTTP_201_CREATED
    )


@extend_schema(
    summary="Login de usuario",
    tags=["Controle de Usuários"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login_entrar(request):
    email = request.data.get("email")
    password = request.data.get("password")

    # Neste ponto, qualquer email e senha são aceitos
    if email and password:
        # Pode retornar dados mockados por enquanto
        return Response(
            {
                "message": "Login realizado com sucesso.",
                "user": {
                    "email": email,
                    "nome": "Usuário Aprovado",
                    "token": "fake-jwt-token",
                },
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"error": "Email e senha são obrigatórios."},
            status=status.HTTP_400_BAD_REQUEST,
        )
