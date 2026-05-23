# ============================================================
#  diagnostico/models.py
#  APPSPEC — Modelos Django para persistir avaliacoes
#  Tecnologia: Django ORM + SQLite (ensinado na disciplina)
#  Contrato: SPEC-07 6.1
# ============================================================

# ================================================================
# MODELO DE DADOS — Formulário de Prontuário em Branco
# Técnico: Este arquivo cria a "planta baixa" do banco de dados. 
# Quando você escreve uma classe aqui, o Django entende que você quer 
# criar uma tabela nova no banco de dados para guardar informações.
# Clínico: É como o formulário de papel timbrado de um prontuário:
# define exatamente quais campos (nome, data, sintomas) devem ser preenchidos.
# ================================================================

from django.db import models
# ↑ Importa o motor de banco de dados do Django (ORM)
# ↑ ORM = Object-Relational Mapper (mapeia objetos Python para tabelas SQL)


class Avaliacao(models.Model):
    # ↑ Técnico: Ao dizer "models.Model", o Django sabe que isso vai virar uma tabela e até cria um ID numérico automático para cada paciente.
    """
    Registra cada avaliacao clinica realizada.
    Tecnologia: Django ORM + SQLite — ensinado na disciplina.
    """
    # ------------------------------------------------------------
    # Dados clínicos de entrada (Sinais e Sintomas)
    # ------------------------------------------------------------
    dor_migratoria         = models.BooleanField(default=False)
    # ↑ Técnico: BooleanField cria uma coluna no banco que só aceita Verdadeiro ou Falso. Se ninguém preencher, ele começa como Falso (default=False).
    # ↑ Clínico: Representa se a dor migrou para a fossa ilíaca direita (FID).

    anorexia               = models.BooleanField(default=False)
    # ↑ Perda de apetite

    nauseas_vomitos        = models.BooleanField(default=False)
    # ↑ Presença de náuseas ou episódios de vômito

    dor_fid                = models.BooleanField(default=False)
    # ↑ Dor localizada na Fossa Ilíaca Direita

    descompressao_dolorosa = models.BooleanField(default=False)
    # ↑ Dor ao soltar rapidamente a compressão no abdome (Sinal de Blumberg)

    temperatura            = models.FloatField()
    # ↑ FloatField = Campo de número com casas decimais (ex: 37.5)

    leucocitos             = models.IntegerField()
    # ↑ IntegerField = Campo de número inteiro (ex: 12000)
    # ↑ Representa a contagem de glóbulos brancos no sangue

    neutrofilia            = models.BooleanField(default=False)
    # ↑ Aumento de neutrófilos no hemograma

    # ------------------------------------------------------------
    # Resultados calculados — Pontuação de Alvarado
    # ------------------------------------------------------------
    score_alvarado         = models.IntegerField()
    # ↑ Soma total dos pontos (0 a 10)

    classificacao_alvarado = models.CharField(max_length=20)
    # ↑ CharField = Texto curto (Baixo, Médio ou Alto risco)

    # ------------------------------------------------------------
    # Resultados de Inteligência Artificial — KNN
    # ------------------------------------------------------------
    predicao_knn           = models.IntegerField(null=True, blank=True)
    # ↑ 0 para Controle, 1 para Apendicite (conforme o dataset)

    probabilidade_knn      = models.FloatField(null=True, blank=True)
    # ↑ Probabilidade matemática (0.0 a 1.0) calculada pelo vizinho mais próximo

    confianca_knn          = models.CharField(max_length=20, blank=True, default='')
    # ↑ Tradução da probabilidade em texto didático

    # ------------------------------------------------------------
    # Resultados de Inteligência Artificial — SVM
    # ------------------------------------------------------------
    predicao_svm           = models.IntegerField(null=True, blank=True)
    probabilidade_svm      = models.FloatField(null=True, blank=True)
    confianca_svm          = models.CharField(max_length=50, blank=True, default='')

    # ------------------------------------------------------------
    # Metadados do Registro
    # ------------------------------------------------------------
    criado_em              = models.DateTimeField(auto_now_add=True)
    # ↑ auto_now_add=True = Salva a data e hora atual automaticamente no momento da criação

    class Meta:
        # ↑ Configurações extras da tabela
        verbose_name = "Avaliação Clínica"
        verbose_name_plural = "Avaliações Clínicas"
        ordering = ["-criado_em"] # ← Ordena da mais recente para a mais antiga

    def __str__(self):
        # ↑ Define como o objeto é exibido como texto (ex: no Admin)
        return (
            f"Avaliação #{self.pk} — "
            f"Alvarado: {self.score_alvarado} | "
            f"KNN: {self.predicao_knn}"
        )

