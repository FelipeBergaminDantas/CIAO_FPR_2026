# ==============================================================================
# AULA 11 — ETAPA 2: SISTEMA DE TRIAGEM MÉDICA DE UTI
# Motor de inferência fuzzy para classificação de risco clínico, explorando
# saltos não-lineares (trapézios de saturação) para sinais vitais críticos.
# ==============================================================================
import sys
import os
import numpy as np
import skfuzzy as fuzzy
from skfuzzy import control as ctrl


def criar_sistema_triagem_uti():
    """
    1. Cria os antecedentes (freq_cardiaca: 40-160, spo2: 70-100) e o
       consequente (risco: 0-100).
    2. Configura o método de defuzzificação para 'centroid'.
    3. Mapeia as funções de pertinência (trimf e trapmf) conforme a
       especificação clínica.
    4. Cria as 5 regras de inferência clínicas.
    5. Retorna o ControlSystemSimulation compilado.
    """
    freq_cardiaca = ctrl.Antecedent(np.arange(40, 161, 1), "freq_cardiaca")
    spo2 = ctrl.Antecedent(np.arange(70, 101, 1), "spo2")
    risco = ctrl.Consequent(np.arange(0, 101, 1), "risco", defuzzify_method="centroid")

    # Frequência Cardíaca (bpm)
    freq_cardiaca["bradicardia"] = fuzzy.trimf(freq_cardiaca.universe, [40, 40, 60])
    freq_cardiaca["normal"] = fuzzy.trimf(freq_cardiaca.universe, [50, 75, 100])
    freq_cardiaca["taquicardia"] = fuzzy.trapmf(freq_cardiaca.universe, [90, 110, 160, 160])

    # Saturação de Oxigênio (%)
    spo2["critica"] = fuzzy.trapmf(spo2.universe, [70, 70, 88, 91])
    spo2["limitrofe"] = fuzzy.trimf(spo2.universe, [89, 93, 96])
    spo2["normal"] = fuzzy.trapmf(spo2.universe, [94, 97, 100, 100])

    # Risco Clínico (%)
    risco["baixo"] = fuzzy.trimf(risco.universe, [0, 0, 35])
    risco["moderado"] = fuzzy.trimf(risco.universe, [25, 50, 75])
    risco["critico"] = fuzzy.trapmf(risco.universe, [65, 85, 100, 100])

    # Tabela de Regras Clínicas
    r1 = ctrl.Rule(spo2["critica"], risco["critico"])  # Regra de Ouro/Saturação
    r2 = ctrl.Rule(freq_cardiaca["bradicardia"] & spo2["limitrofe"], risco["critico"])
    r3 = ctrl.Rule(freq_cardiaca["taquicardia"] & spo2["limitrofe"], risco["critico"])
    r4 = ctrl.Rule(freq_cardiaca["normal"] & spo2["limitrofe"], risco["moderado"])
    r5 = ctrl.Rule(freq_cardiaca["normal"] & spo2["normal"], risco["baixo"])

    sistema_controle = ctrl.ControlSystem([r1, r2, r3, r4, r5])
    return ctrl.ControlSystemSimulation(sistema_controle)


def avaliar_paciente(simulador, bpm, spo2_val):
    """
    1. Valida se bpm está em [40, 160]. Caso contrário, lança ValueError.
    2. Valida se spo2_val está em [70, 100]. Caso contrário, lança ValueError.
    3. Injeta as entradas no simulador e executa o compute().
    4. Retorna a saída 'risco'.
    """
    if not (40 <= bpm <= 160):
        raise ValueError(f"Frequencia cardiaca fora da escala [40, 160]: {bpm}")
    if not (70 <= spo2_val <= 100):
        raise ValueError(f"SpO2 fora da escala [70, 100]: {spo2_val}")

    simulador.input["freq_cardiaca"] = bpm
    simulador.input["spo2"] = spo2_val
    simulador.compute()
    return simulador.output["risco"]


if __name__ == "__main__":
    # Teste rápido manual em tela
    sim = criar_sistema_triagem_uti()
    print("Sistema de UTI instanciado com sucesso!")

    casos = [
        ("Paciente saudavel", 75, 98),
        ("Queda tolerável de SpO2", 75, 95),
        ("Hipoxia aguda (salto nao-linear)", 75, 89),
    ]
    for nome, bpm, spo2_val in casos:
        risco_calc = avaliar_paciente(sim, bpm, spo2_val)
        print(f"[{nome}] FC={bpm} bpm, SpO2={spo2_val}% -> Risco = {risco_calc:.2f}%")
