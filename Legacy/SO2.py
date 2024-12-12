import math
import matplotlib.pyplot as plt

class Tarefa:
    def __init__(self, nome, periodo, deadline, tempo_computacao):
        self.nome = nome
        self.periodo = periodo
        self.deadline = deadline
        self.tempo_computacao = tempo_computacao
        # Prioridade será definida após criar todas as tarefas.

def calcular_mmc(a, b):
    return abs(a * b) // math.gcd(a, b)

def calcular_mmc_lista(numeros):
    mmc_atual = numeros[0]
    for n in numeros[1:]:
        mmc_atual = calcular_mmc(mmc_atual, n)
    return mmc_atual

def atribuir_prioridades(tarefas):
    # Quanto menor a deadline, maior a prioridade.
    # Podemos atribuir prioridade de forma que a tarefa com menor deadline receba prioridade 1,
    # a próxima prioridade 2, etc.
    tarefas_ordenadas = sorted(tarefas, key=lambda x: x.deadline)
    for i, t in enumerate(tarefas_ordenadas):
        t.prioridade = i+1  # i+1 pois prioridade 1 é a mais alta
    # O objeto tarefa agora tem um atributo prioridade.
    return tarefas

def gerar_instancias(tarefas, hiper_periodo):
    instancias = []
    for t in tarefas:
        k = 0
        while k * t.periodo < hiper_periodo:
            tempo_liberacao = k * t.periodo
            deadline_absoluto = tempo_liberacao + t.deadline
            instancias.append({
                'nome_tarefa': t.nome,
                'tempo_liberacao': tempo_liberacao,
                'deadline_absoluto': deadline_absoluto,
                'tempo_restante': t.tempo_computacao,
                'prioridade': t.prioridade
            })
            k += 1
    return instancias

def escalonamento_dm(instancias, tempo_total):
    # Deadline Monotonic: Sempre executa a tarefa com maior prioridade fixa (menor deadline relativo)
    linha_do_tempo = []
    tarefas_prontas = []

    for tempo in range(tempo_total):
        # Adicionar instâncias que chegam neste instante
        for instancia in instancias:
            if instancia['tempo_liberacao'] == tempo:
                tarefas_prontas.append(instancia)

        # Filtrar as que ainda não terminaram
        tarefas_prontas = [t for t in tarefas_prontas if t['tempo_restante'] > 0]

        # Escolher a tarefa com maior prioridade (prioridade = menor número)
        if tarefas_prontas:
            tarefas_prontas.sort(key=lambda x: x['prioridade'])  # menor prioridade numérica = mais alta
            tarefa_em_execucao = tarefas_prontas[0]
            tarefa_em_execucao['tempo_restante'] -= 1
            linha_do_tempo.append((tempo, tarefa_em_execucao['nome_tarefa']))
        else:
            # Nada pronto para executar
            linha_do_tempo.append((tempo, None))
    return linha_do_tempo

def construir_intervalos(linha_do_tempo):
    intervalos = []
    if not linha_do_tempo:
        return intervalos
    tarefa_atual = linha_do_tempo[0][1]
    inicio = 0
    for i in range(1, len(linha_do_tempo)):
        if linha_do_tempo[i][1] != tarefa_atual:
            intervalos.append((tarefa_atual, inicio, i))
            tarefa_atual = linha_do_tempo[i][1]
            inicio = i
    intervalos.append((tarefa_atual, inicio, len(linha_do_tempo)))
    intervalos = [iv for iv in intervalos if iv[0] is not None]
    return intervalos

def plotar_simulacao(tarefas, linha_do_tempo, instancias):
    intervalos = construir_intervalos(linha_do_tempo)
    # Ordem fixa desejada, por exemplo:
    nomes_tarefas = ["tarefa1", "tarefa2", "tarefa3", "tarefa4"]

    periodos = [t.periodo for t in tarefas]
    hiper_periodo = calcular_mmc_lista(periodos)

    tempos_liberacao = {t.nome: [] for t in tarefas}
    deadlines = {t.nome: [] for t in tarefas}
    for instancia in instancias:
        tempos_liberacao[instancia['nome_tarefa']].append(instancia['tempo_liberacao'])
        deadlines[instancia['nome_tarefa']].append(instancia['deadline_absoluto'])

    fig = plt.figure(figsize=(12, 8))

    # Subplot 1: Tabela de parâmetros e MMC
    ax1 = fig.add_subplot(4, 1, 1)
    ax1.axis('off')
    texto_tabela = []
    cabecalhos = ["Tarefa", "T (ms)", "D (ms)", "C (ms)", "Prioridade"]
    for t in tarefas:
        texto_tabela.append([t.nome, str(t.periodo), str(t.deadline), str(t.tempo_computacao), str(t.prioridade)])
    tabela = ax1.table(cellText=texto_tabela,
                       colLabels=cabecalhos,
                       loc='center',
                       cellLoc='center')
    tabela.scale(1, 1.5)
    ax1.set_title(f"Cálculo do MMC: {hiper_periodo} ms (Deadline Monotonic)", pad=20)

    # Subplot 2: Ativações
    ax2 = fig.add_subplot(4, 1, 2)
    ax2.set_title("Ativações (x indica o instante em que a tarefa é liberada)")
    ax2.set_xlim(0, hiper_periodo)
    ax2.set_ylim(-1, len(nomes_tarefas))
    ax2.set_yticks(range(len(nomes_tarefas)))
    ax2.set_yticklabels(nomes_tarefas)
    ax2.set_xlabel("Tempo (ms)")
    ax2.set_xticks(range(0, hiper_periodo + 1))
    ax2.grid(True, axis='x', linestyle=':', alpha=0.7)
    for i, nome in enumerate(nomes_tarefas):
        for tempo in tempos_liberacao[nome]:
            ax2.text(tempo, i, 'x', ha='center', va='center', color='red')

    # Subplot 3: Deadlines (opcional, mesmo que no EDF, apenas ilustrando deadlines)
    ax3 = fig.add_subplot(4, 1, 3)
    ax3.set_title("Deadlines (contagem regressiva para o deadline)")
    ax3.set_xlim(0, hiper_periodo)
    ax3.set_ylim(-1, len(nomes_tarefas))
    ax3.set_yticks(range(len(nomes_tarefas)))
    ax3.set_yticklabels(nomes_tarefas)
    ax3.set_xlabel("Tempo (ms)")
    ax3.set_xticks(range(0, hiper_periodo + 1))
    ax3.grid(True, axis='x', linestyle=':', alpha=0.7)
    for i, nome in enumerate(nomes_tarefas):
        for instancia in [j for j in instancias if j['nome_tarefa'] == nome]:
            for tempo in range(instancia['tempo_liberacao'], instancia['deadline_absoluto']):
                restante = instancia['deadline_absoluto'] - tempo
                ax3.text(tempo + 0.5, i, str(restante), ha='center', va='center', fontsize=7)

    # Subplot 4: Gantt Chart
    ax4 = fig.add_subplot(4, 1, 4)
    ax4.set_title("Escalonamento Deadline Monotonic (Gantt Chart)")
    ax4.set_xlim(0, hiper_periodo)
    ax4.set_ylim(-1, len(nomes_tarefas))
    ax4.set_yticks(range(len(nomes_tarefas)))
    ax4.set_yticklabels(nomes_tarefas)
    ax4.set_xlabel("Tempo (ms)")
    ax4.set_xticks(range(0, hiper_periodo + 1))
    ax4.grid(True, axis='x', linestyle=':', alpha=0.7)

    cmap = plt.get_cmap("tab10")
    cores = {}
    for i, nome in enumerate(nomes_tarefas):
        cores[nome] = cmap(i)

    for intervalo in intervalos:
        nome_tarefa, inicio, fim = intervalo
        y = nomes_tarefas.index(nome_tarefa)
        ax4.barh(y, fim - inicio, left=inicio, height=0.8, color=cores[nome_tarefa], edgecolor='black')
        # Aqui pode-se colocar o número da instância (ciclo) da tarefa se desejar.
        # Porém, o pedido original era apenas mudar a lógica de escalonamento.
        ax4.text((inicio + fim) / 2, y, nome_tarefa, ha='center', va='center', color='white', fontsize=8)

    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    tarefas = [
        Tarefa("tarefa1", 20, 5, 3),
        Tarefa("tarefa2", 15, 7, 3),
        Tarefa("tarefa3", 10, 10, 4),
        Tarefa("tarefa4", 20, 18, 2)
    ]

    # Atribuir prioridades com base no Deadline Monotonic
    tarefas = atribuir_prioridades(tarefas)

    periodos = [t.periodo for t in tarefas]
    hiper_periodo = calcular_mmc_lista(periodos)
    instancias = gerar_instancias(tarefas, hiper_periodo)

    # Agora usamos escalonamento DM, não EDF
    linha_do_tempo = escalonamento_dm(instancias, hiper_periodo)

    plotar_simulacao(tarefas, linha_do_tempo, instancias)
