import os
import django
from django.utils import timezone
from datetime import timedelta

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from votacao.models import Organizacao, TipoEvento, Evento, Enquete, Eleitor, Opcao

def popular_banco():
    print("🚀 Iniciando carga de teste do CliqueVoto...")

    # 1. Criar Organização (O Cliente)
    org, _ = Organizacao.objects.get_or_create(
        nome="Condomínio Madri III",
        defaults={
            'logo_url': "https://cdn-icons-png.flaticon.com/512/609/609803.png",
            'cnpj': "12.345.678/0001-90"
        }
    )

    # 2. Criar Tipo de Evento (A Regra)
    tipo, _ = TipoEvento.objects.get_or_create(
        nome="Assembleia Geral Ordinária",
        defaults={
            'exige_aprovacao_cadastro': True,
            'voto_com_peso': True
        }
    )

    # 3. Criar Evento (O Show com as novas funcionalidades)
    # Aqui usamos o status 'inscricoes_abertas' para testar o seu novo rito
    evento, created = Evento.objects.get_or_create(
        slug_convocacao="madri-2026",
        defaults={
            'titulo': "Assembleia Geral 2026 - Madri III",
            'organizacao': org,
            'tipo': tipo,
            'status_evento': 'inscricoes_abertas', # <-- Habilita o botão de cadastro no front
            'mensagem_boas_vindas': "Sejam bem-vindos à Assembleia Geral do Condomínio Madri III. Sua participação é fundamental!",
            'resumo_evento': "Pauta principal: Aprovação de contas e Eleição de Síndico.",
            'link_edital': "https://www.google.com.br",
            'data_inicio': timezone.now() + timedelta(hours=2), # Começa em 2h
            'data_fim': timezone.now() + timedelta(days=1),
            'is_ativo': True,
            'mostrar_fotos': True
        }
    )

    # 4. Criar Pautas (Enquetes)
    # Pauta 1: Aprovação (O Signal vai criar Sim/Não/Abster automaticamente)
    Enquete.objects.get_or_create(
        evento=evento,
        titulo="Aprovação das contas do exercício 2025",
        defaults={'tipo_enquete': "aprovacao", 'status': "aguardando"}
    )

    # Pauta 2: Eleição (Manual)
    pauta2, _ = Enquete.objects.get_or_create(
        evento=evento,
        titulo="Eleição de Novo Síndico (Gestão 2026-2027)",
        defaults={'tipo_enquete': "candidatos", 'status': "aguardando"}
    )
    
    if not Opcao.objects.filter(enquete=pauta2).exists():
        Opcao.objects.create(enquete=pauta2, nome="Phelipe (Chapa 01)", numero=10)
        Opcao.objects.create(enquete=pauta2, nome="João (Chapa 02)", numero=20)

    # 5. Criar Votantes em diferentes estágios (Para testar o seu Rito)
    
    # 5.1 Você (Já aprovado para testar o acesso)
    Eleitor.objects.get_or_create(
        evento=evento,
        cpf="12345678901",
        defaults={
            'nome': "Phelipe Especialista (Aprovado)",
            'email': "phelipe@teste.com",
            'whatsapp': "41999999999",
            'status': 'aprovado',
            'peso_voto': 1.0000
        }
    )

    # 5.2 Um votante pendente (Para testar a lista de aprovação no Admin)
    Eleitor.objects.get_or_create(
        evento=evento,
        cpf="98765432100",
        defaults={
            'nome': "Candidato a Votante",
            'email': "pendente@teste.com",
            'whatsapp': "41888888888",
            'status': 'pendente'
        }
    )

    print("✅ Banco populado com sucesso!")
    print(f"🔗 Link de Inscrição: http://localhost:5174/inscricao/madri-2026")
    print(f"🔗 API Info: http://127.0.0.1:8000/api/evento/info/madri-2026/")

if __name__ == "__main__":
    popular_banco()