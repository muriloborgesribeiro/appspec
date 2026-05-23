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
