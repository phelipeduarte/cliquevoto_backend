from rest_framework import serializers
from .models import Eleitor, Evento

class InscricaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eleitor
        fields = ['evento', 'nome', 'cpf', 'email', 'whatsapp']

    def validate_cpf(self, value):
        # Remove pontos e traços para salvar apenas números no banco
        import re
        return re.sub(r'\D', '', value)

class EventoPublicoSerializer(serializers.ModelSerializer):
    """Dados que o Votante vê antes de se cadastrar (Logo, Edital, Status)"""
    organizacao_nome = serializers.ReadOnlyField(source='organizacao.nome')
    organizacao_logo = serializers.ReadOnlyField(source='organizacao.logo_url')

    class Meta:
        model = Evento
        fields = [
            'id', 'titulo', 'mensagem_boas_vindas', 'resumo_evento', 
            'link_edital', 'organizacao_nome', 'organizacao_logo', 'status_evento'
        ]