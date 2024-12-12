import math

class Tarefa:
    def __init__(self, nome, periodo, deadline, tempo_computacao):
        self.nome = nome
        self.periodo = periodo
        self.deadline = deadline
        self.tempo_computacao = tempo_computacao
        self.prioridade = None  # Usado por DM ou RM

def calcular_mmc(a, b):
    return abs(a * b) // math.gcd(a, b)

def calcular_mmc_lista(numeros):
    mmc_atual = numeros[0]
    for n in numeros[1:]:
        mmc_atual = calcular_mmc(mmc_atual, n)
    return mmc_atual
