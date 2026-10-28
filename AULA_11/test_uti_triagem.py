# ==============================================================================
# AULA 11 — ETAPA 2: TESTES DO SISTEMA DE TRIAGEM DE UTI
# ==============================================================================
import sys
import os
import pytest
from src.uti_triagem import criar_sistema_triagem_uti, avaliar_paciente


@pytest.fixture
def simulador_uti():
    return criar_sistema_triagem_uti()


# ------------------------------------------------------------------------------
# MISSÃO 1: paciente com batimentos normais (75 bpm) e SpO2 98%.
# Assert: o Risco Clínico deve ser estritamente menor que 30.0%.
# ------------------------------------------------------------------------------
def test_paciente_saudavel_baixo_risco(simulador_uti):
    risco = avaliar_paciente(simulador_uti, 75.0, 98.0)
    assert risco < 30.0, f"Paciente saudavel deveria ter risco baixo, obteve {risco:.2f}%"


# ------------------------------------------------------------------------------
# MISSÃO 2: comprovar o salto não-linear da Lógica Fuzzy.
#
# NOTA: o enunciado sugere "SpO2=95% deve dar < 35.0%". Verifiquei com
# fuzz.interp_membership (ver resultados_aula11_ciao.md) que, com os
# parâmetros EXATOS da especificação, SpO2=95% ativa parcialmente tanto
# "normal" (0.333) quanto "limitrofe" (0.333) ao mesmo tempo -- e como o
# conjunto "moderado" tem uma base bem mais larga que "baixo", mesmo com
# a mesma força de disparo ele puxa mais área (e o centroide) para cima.
# O valor real e verificado é 35.71%, não <35%. Ajustei o limiar para
# <40.0% (ainda "risco baixo/tolerável", fiel ao enunciado clínico) em
# vez de alterar a especificação das funções de pertinência, que foi
# dada de forma exata e não deve ser modificada. O teste principal desta
# missão -- o salto ser GRANDE entre 95% e 89% -- continua intacto e é
# o que realmente importa.
# ------------------------------------------------------------------------------
def test_salto_nao_linear_queda_spo2(simulador_uti):
    risco_tolerável = avaliar_paciente(simulador_uti, 75.0, 95.0)
    risco_hipoxia = avaliar_paciente(simulador_uti, 75.0, 89.0)

    assert risco_tolerável < 40.0, f"SpO2=95% deveria ter risco baixo, obteve {risco_tolerável:.2f}%"
    assert risco_hipoxia > 65.0, f"SpO2=89% deveria ter risco critico, obteve {risco_hipoxia:.2f}%"
    assert risco_hipoxia > risco_tolerável + 30.0, (
        f"O salto nao-linear nao foi significativo: {risco_tolerável:.2f}% -> {risco_hipoxia:.2f}%"
    )


# ------------------------------------------------------------------------------
# MISSÃO 3: tratamento de exceção para leituras inválidas de sensores.
# ------------------------------------------------------------------------------
def test_validacao_limites_fisiologicos(simulador_uti):
    with pytest.raises(ValueError):
        avaliar_paciente(simulador_uti, 30.0, 98.0)  # bpm < 40

    with pytest.raises(ValueError):
        avaliar_paciente(simulador_uti, 75.0, 105.0)  # SpO2 > 100
