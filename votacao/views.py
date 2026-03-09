from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Evento, Eleitor
from .serializers import InscricaoSerializer, EventoPublicoSerializer
import logging

# Configura um logger simples para vermos erros no terminal
logger = logging.getLogger(__name__)

@api_view(['GET'])
def lista_eleicoes_ativas(request):
    """
    Retorna a lista de eventos ativos. 
    Se der erro 500, o print abaixo mostrará o motivo no terminal.
    """
    try:
        eventos = Evento.objects.filter(is_ativo=True).order_by('-data_inicio')
        serializer = EventoPublicoSerializer(eventos, many=True)
        return Response(serializer.data)
    except Exception as e:
        print(f"❌ ERRO CRÍTICO EM lista_eleicoes_ativas: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def detalhes_evento_publico(request, slug):
    """Retorna os dados do evento para a tela de inscrição via Slug"""
    try:
        evento = Evento.objects.get(slug_convocacao=slug, is_ativo=True)
        serializer = EventoPublicoSerializer(evento)
        return Response(serializer.data)
    except Evento.DoesNotExist:
        return Response(
            {"error": "Evento não encontrado ou link expirado."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"❌ ERRO EM detalhes_evento_publico: {e}")
        return Response({"error": "Erro interno no servidor"}, status=500)

@api_view(['POST'])
def realizar_inscricao(request):
    """Recebe o cadastro do votante e salva como Pendente"""
    serializer = InscricaoSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            evento = serializer.validated_data['evento']
            cpf = serializer.validated_data['cpf']
            
            # 1. Bloqueia se o evento não estiver em fase de inscrições
            if evento.status_evento != 'inscricoes_abertas':
                return Response(
                    {"error": "As inscrições para este evento não estão abertas no momento."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 2. Regra de Ouro: Evitar duplicidade de CPF no mesmo evento
            if Eleitor.objects.filter(evento=evento, cpf=cpf).exists():
                return Response(
                    {"error": "Este CPF já possui uma solicitação para este evento."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            serializer.save() 
            return Response(
                {"message": "Cadastro realizado com sucesso! Sua solicitação está em análise."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(f"❌ ERRO AO SALVAR INSCRIÇÃO: {e}")
            return Response({"error": "Erro ao processar inscrição"}, status=500)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)