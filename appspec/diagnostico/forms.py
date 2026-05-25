# ============================================================
#  diagnostico/forms.py
#  APPSPEC -- Formulario de dados clinicos
#  Tecnologia: Django Forms (ensinado na disciplina)
#  Contrato: SPEC-07 6.2
#  Anti-alucinacao #8: validacao estrita de entrada
# ============================================================

from django import forms


class DadosClinicosForm(forms.Form):
    """
    Formulario clinico com validacao de range.
    Tecnologia: Django Forms — ensinado na disciplina.
    Mecanismo anti-alucinacao #8: validacao estrita de entrada.
    """

    # --- Sintomas (Alvarado) ---
    dor_migratoria = forms.BooleanField(
        required=False,
        label="Dor migratória para FID",
        help_text="Dor que migrou do periumbilical para a fossa ilíaca direita",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    anorexia = forms.BooleanField(
        required=False,
        label="Anorexia (perda de apetite)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    nauseas_vomitos = forms.BooleanField(
        required=False,
        label="Náuseas ou vômitos",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    # --- Sinais (Alvarado) ---
    dor_fid = forms.BooleanField(
        required=False,
        label="Dor à palpação em FID (2 pontos)",
        help_text="Dor no ponto de McBurney",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    descompressao_dolorosa = forms.BooleanField(
        required=False,
        label="Descompressão dolorosa (sinal de Blumberg)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    temperatura = forms.FloatField(
        label="Temperatura (°C)",
        min_value=35.0,
        max_value=42.0,
        help_text="Faixa fisiológica: 35.0 – 42.0 °C",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': '36.5',
        }),
    )

    # --- Laboratorial (Alvarado) ---
    leucocitos = forms.IntegerField(
        label="Leucócitos (/mm³)",
        min_value=1000,
        max_value=50000,
        help_text="Faixa fisiológica: 1.000 – 50.000 /mm³",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '8000',
        }),
    )
    neutrofilia = forms.BooleanField(
        required=False,
        label="Neutrofilia (desvio à esquerda no leucograma)",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )


class HistoricoFilterForm(forms.Form):
    """Formulário de filtros para a página de histórico.

    Campos opcionais, todos em GET. Usamos tipos compatíveis com
    inputs HTML nativos (datetime-local, number, select) para evitar
    dependências externas.
    """
    start_datetime = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control form-control-sm'}),
        label='Data/Hora início',
    )
    end_datetime = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control form-control-sm'}),
        label='Data/Hora fim',
    )

    alvarado_min = forms.IntegerField(required=False, min_value=0, max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'min'}),
        label='Alvarado mínimo')
    alvarado_max = forms.IntegerField(required=False, min_value=0, max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'max'}),
        label='Alvarado máximo')

    CLASS_CHOICES = [('', '— Qualquer —'), ('alto', 'Alto'), ('moderado', 'Moderado'), ('baixo', 'Baixo')]
    classificacao = forms.ChoiceField(required=False, choices=CLASS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}), label='Classificação Alvarado')

    KNN_CHOICES = [('', '— Qualquer —'), ('1', 'Apendicite'), ('0', 'Sem')]
    knn = forms.ChoiceField(required=False, choices=KNN_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}), label='Predição KNN')

    CONFIANCA_CHOICES = [('', '— Qualquer —'), ('Alta', 'Alta'), ('Média', 'Média'), ('Baixa', 'Baixa')]
    confianca = forms.ChoiceField(required=False, choices=CONFIANCA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}), label='Confiança (texto)')

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_datetime')
        end = cleaned.get('end_datetime')
        if start and end and start > end:
            raise forms.ValidationError('Data/Hora início não pode ser maior que Data/Hora fim.')
        amin = cleaned.get('alvarado_min')
        amax = cleaned.get('alvarado_max')
        if amin is not None and amax is not None and amin > amax:
            raise forms.ValidationError('Alvarado mínimo não pode ser maior que máximo.')
        return cleaned
