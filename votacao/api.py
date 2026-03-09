from typing import List
from ninja import NinjaAPI, Schema
from django.shortcuts import get_object_or_404
from .models import Evento, Enquete, Opcao, Eleitor, Voto
from django.db.models import Count
from django.db import transaction

api = NinjaAPI(title="CliqueVoto API")

# ==========================================
# SCHEMAS DE VALIDAÇÃO
# ==========================================
class VotoIndividual(Schema):
    enquete_id: int
    opcao_id: int

class VotoLoteSchema(Schema):
    evento_id: str
    cpf_eleitor: str
    votos: List[VotoIndividual]

# ==========================================
# ENDPOINTS
# ==========================================

@api.get("/eleicoes/ativas")
def listar_eleicoes_ativas(request):
    """
    Lista eventos ativos. Ajustado para refletir o novo Model com a mensagem de credenciamento.
    """
    eventos = Evento.objects.filter(is_ativo=True).select_related('organizacao')
    return [
        {
            "id": str(e.id), 
            "titulo": e.titulo, 
            "slug_convocacao": e.slug_convocacao, 
            "organizacao_nome": e.organizacao.nome,
            "logo_url": e.organizacao.logo_url,
            "mostrar_fotos": e.mostrar_fotos,
            "mensagem_boas_vindas": e.mensagem_boas_vindas,
            
            # --- NOVO CAMPO EXPOSTO AQUI ---
            "mensagem_credenciamento": e.mensagem_credenciamento, 
            
            "resumo_evento": e.resumo_evento,
            "link_edital": e.link_edital, 
            "status_evento": e.status_evento 
        } 
        for e in eventos
    ]

@api.get("/eleicoes/{evento_id}/enquetes")
def listar_enquetes(request, evento_id: str):
    enquetes = Enquete.objects.filter(evento_id=evento_id).prefetch_related('opcoes')
    return [
        {
            "id": eq.id, 
            "titulo": eq.titulo, 
            "tipo_enquete": eq.tipo_enquete,
            "status": eq.status,
            "opcoes": [
                {
                    "id": o.id, 
                    "nome": o.nome, 
                    "numero": o.numero,
                    "foto_url": o.foto_url
                } for o in eq.opcoes.all()
            ]
        } 
        for eq in enquetes
    ]

@api.post("/votar")
def registrar_votos(request, payload: VotoLoteSchema):
    # Ajuste: CPF agora pode ter status diferente de 'aprovado'
    eleitor = Eleitor.objects.filter(
        evento_id=payload.evento_id, 
        cpf=payload.cpf_eleitor,
        status='aprovado' # Apenas quem foi aprovado pelo gestor vota
    ).first()

    if not eleitor:
        return api.create_response(request, {"erro": "CPF não autorizado ou pendente de aprovação."}, status=403)

    if eleitor.token_utilizado:
        return api.create_response(request, {"erro": "Votos já registrados para este CPF."}, status=400)

    with transaction.atomic():
        for voto in payload.votos:
            # Auditamos o voto salvando o hash ou ID do eleitor se necessário
            Voto.objects.create(
                enquete_id=voto.enquete_id, 
                opcao_id=voto.opcao_id,
                eleitor_hash=str(eleitor.id) # Usando o ID como hash inicial
            )
        
        eleitor.token_utilizado = True
        eleitor.save()

    return {"sucesso": True, "mensagem": "Votos computados com sucesso!"}

@api.get("/eleicoes/{evento_id}/resultados")
def ver_resultados(request, evento_id: str):
    # Mantemos a lógica de agregação, mas garantimos que as relações estão ok
    enquetes = Enquete.objects.filter(evento_id=evento_id).prefetch_related('opcoes')
    resultados_enquetes = []
    
    for eq in enquetes:
        # Contagem baseada na relação inversa 'votos' definida no related_name
        total_enquete = Voto.objects.filter(enquete_id=eq.id).count()
        opcoes_data = []
        
        # O Django Ninja usa a relação reversa para o annotate
        opcoes_com_votos = eq.opcoes.annotate(total_votos=Count('voto')).order_by('-total_votos')
        
        for o in opcoes_com_votos:
            opcoes_data.append({
                "nome": o.nome,
                "votos": o.total_votos,
                "porcentagem": round((o.total_votos / total_enquete * 100), 2) if total_enquete > 0 else 0,
                "foto_url": o.foto_url
            })
        
        resultados_enquetes.append({
            "enquete_id": eq.id,
            "titulo": eq.titulo,
            "total_votos": total_enquete,
            "ranking": opcoes_data
        })

    return {
        "resultados_por_enquete": resultados_enquetes
    }