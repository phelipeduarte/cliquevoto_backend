from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# ==========================================
# 1. MOTOR DE REGRAS E ORGANIZAÇÃO
# ==========================================

class TipoEvento(models.Model):
    nome = models.CharField(max_length=100, unique=True, help_text="Ex: Assembleia Condominial, Eleição Sindical")
    descricao = models.TextField(blank=True, null=True)
    exige_aprovacao_cadastro = models.BooleanField(default=True)
    voto_com_peso = models.BooleanField(default=False, help_text="Habilita contagem por fração ideal/cotas")
    permite_procuracao = models.BooleanField(default=False)

    def __str__(self):
        return self.nome

class Organizacao(models.Model):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    logo_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Logo do Cliente (URL)")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Organização"
        verbose_name_plural = "Organizações"

    def __str__(self):
        return self.nome

# ==========================================
# 2. O EVENTO E SUAS PAUTAS
# ==========================================

class Evento(models.Model):
    STATUS_EVENTO = [
        ('configuracao', 'Em Configuração (Inscrições Fechadas)'),
        ('inscricoes_abertas', 'Inscrições Abertas'),
        ('em_andamento', 'Evento Iniciado (Sala Liberada)'),
        ('finalizado', 'Finalizado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizacao = models.ForeignKey(Organizacao, on_delete=models.CASCADE, related_name='eventos')
    tipo = models.ForeignKey(TipoEvento, on_delete=models.RESTRICT, null=True, blank=True)
    
    titulo = models.CharField(max_length=255)
    slug_convocacao = models.SlugField(max_length=255, unique=True, blank=True, null=True, help_text="URL amigável para o edital")
    
    status_evento = models.CharField(max_length=20, choices=STATUS_EVENTO, default='configuracao')
    
    mensagem_boas_vindas = models.TextField(blank=True, null=True, help_text="Ex: Sejam bem-vindos a Assembleia Geral do Condomínio Madri III")
    
    # --- NOVO CAMPO ADICIONADO ---
    mensagem_credenciamento = models.CharField(
        max_length=255,
        default="Esta assembleia está na fase de credenciamento e envio de documentos.",
        help_text="Aviso exibido no painel inicial durante a fase de inscrições."
    )
    
    resumo_evento = models.TextField(blank=True, null=True, help_text="Breve descrição do que será tratado")
    link_edital = models.URLField(max_length=500, blank=True, null=True, help_text="Link para visualização dos termos/edital")
    
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    is_ativo = models.BooleanField(default=True)
    mostrar_fotos = models.BooleanField(default=True, verbose_name="Mostrar fotos na urna?")

    def __str__(self):
        return f"{self.titulo} ({self.get_status_evento_display()})"

class Enquete(models.Model):
    TIPO_CHOICES = [
        ('candidatos', 'Eleição de Candidatos/Chapas'),
        ('aprovacao', 'Aprovação (Sim / Não / Abster)'),
    ]
    
    STATUS_CHOICES = [
        ('aguardando', 'Aguardando'),
        ('em_votacao', 'Em Votação'),
        ('encerrada', 'Encerrada'),
    ]
    
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='enquetes')
    titulo = models.CharField(max_length=255, help_text="Ex: Aprovação de Contas 2025")
    tipo_enquete = models.CharField(max_length=20, choices=TIPO_CHOICES, default='candidatos')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aguardando')

    def __str__(self):
        return f"{self.titulo} ({self.get_status_display()})"

class Opcao(models.Model):
    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name='opcoes', null=True)
    nome = models.CharField(max_length=255)
    numero = models.IntegerField(blank=True, null=True)
    foto_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Foto (URL)")

    class Meta:
        verbose_name = "Opção"
        verbose_name_plural = "Opções"

    def __str__(self):
        return f"{self.nome} - {self.enquete.titulo if self.enquete else ''}"

# ==========================================
# 3. CREDENCIAMENTO E VOTAÇÃO
# ==========================================

class Eleitor(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente de Aprovação'),
        ('aprovado', 'Aprovado (Acesso Liberado)'),
        ('rejeitado', 'Rejeitado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='eleitores')
    
    # Dados do Rito de Cadastro
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14) 
    email = models.EmailField(null=True, blank=True) 
    whatsapp = models.CharField(max_length=20, null=True, blank=True) 
    
    # Controle de Fração Ideal
    peso_voto = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    
    # Status e Segurança
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    motivo_rejeicao = models.TextField(blank=True, null=True, help_text="Explicar por que não foi aprovado")
    
    token_acesso = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True) 
    data_aprovacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('evento', 'cpf')
        verbose_name = "Eleitor / Votante"
        verbose_name_plural = "Eleitores / Votantes"

    def __str__(self):
        return f"{self.nome} ({self.cpf}) - {self.get_status_display()}"

class Voto(models.Model):
    enquete = models.ForeignKey(Enquete, on_delete=models.CASCADE, related_name='votos')
    opcao = models.ForeignKey(Opcao, on_delete=models.CASCADE)
    eleitor_hash = models.CharField(max_length=255, help_text="Hash anônimo do eleitor para auditoria")
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voto computado em {self.enquete.titulo}"

# ==========================================
# 4. GATILHOS AUTOMÁTICOS (SIGNALS)
# ==========================================
@receiver(post_save, sender=Enquete)
def criar_opcoes_automaticas(sender, instance, created, **kwargs):
    if created and instance.tipo_enquete == 'aprovacao':
        Opcao.objects.create(enquete=instance, nome='Sim', numero=1)
        Opcao.objects.create(enquete=instance, nome='Não', numero=2)
        Opcao.objects.create(enquete=instance, nome='Abster-se', numero=3)