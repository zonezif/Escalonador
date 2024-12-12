import math
import matplotlib.pyplot as plt

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

def atribuir_prioridades_dm(tarefas):
    # Deadline Monotonic: quanto menor o deadline, maior a prioridade
    tarefas_ordenadas = sorted(tarefas, key=lambda x: x.deadline)
    for i, t in enumerate(tarefas_ordenadas):
        t.prioridade = i + 1
    return tarefas

def atribuir_prioridades_rm(tarefas):
    # Rate Monotonic: quanto menor o período, maior a prioridade
    tarefas_ordenadas = sorted(tarefas, key=lambda x: x.periodo)
    for i, t in enumerate(tarefas_ordenadas):
        t.prioridade = i + 1
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
                'execucao_id': k + 1,
                'prioridade': t.prioridade if t.prioridade is not None else None
            })
            k += 1
    return instancias

def escalonamento_edf(instancias, tempo_total):
    linha_do_tempo = []
    tarefas_prontas = []

    for tempo in range(tempo_total):
        for instancia in instancias:
            if instancia['tempo_liberacao'] == tempo:
                tarefas_prontas.append(instancia)

        tarefas_prontas = [t for t in tarefas_prontas if t['tempo_restante'] > 0]

        if tarefas_prontas:
            tarefas_prontas.sort(key=lambda x: x['deadline_absoluto'])
            tarefa_em_execucao = tarefas_prontas[0]
            tarefa_em_execucao['tempo_restante'] -= 1
            linha_do_tempo.append((tempo, tarefa_em_execucao))
        else:
            linha_do_tempo.append((tempo, None))
    return linha_do_tempo

def escalonamento_dm(instancias, tempo_total):
    # Deadline Monotonic
    linha_do_tempo = []
    tarefas_prontas = []

    for tempo in range(tempo_total):
        for instancia in instancias:
            if instancia['tempo_liberacao'] == tempo:
                tarefas_prontas.append(instancia)

        tarefas_prontas = [t for t in tarefas_prontas if t['tempo_restante'] > 0]

        if tarefas_prontas:
            tarefas_prontas.sort(key=lambda x: x['prioridade'])
            tarefa_em_execucao = tarefas_prontas[0]
            tarefa_em_execucao['tempo_restante'] -= 1
            linha_do_tempo.append((tempo, tarefa_em_execucao))
        else:
            linha_do_tempo.append((tempo, None))
    return linha_do_tempo

def escalonamento_rm(instancias, tempo_total):
    # Rate Monotonic
    linha_do_tempo = []
    tarefas_prontas = []

    for tempo in range(tempo_total):
        for instancia in instancias:
            if instancia['tempo_liberacao'] == tempo:
                tarefas_prontas.append(instancia)

        tarefas_prontas = [t for t in tarefas_prontas if t['tempo_restante'] > 0]

        if tarefas_prontas:
            tarefas_prontas.sort(key=lambda x: x['prioridade'])
            tarefa_em_execucao = tarefas_prontas[0]
            tarefa_em_execucao['tempo_restante'] -= 1
            linha_do_tempo.append((tempo, tarefa_em_execucao))
        else:
            linha_do_tempo.append((tempo, None))
    return linha_do_tempo

def construir_intervalos(linha_do_tempo):
    intervalos = []
    if not linha_do_tempo:
        return intervalos
    tarefa_atual = linha_do_tempo[0][1]
    inicio = 0
    for i in range(1, len(linha_do_tempo)):
        mudou = False
        if (linha_do_tempo[i][1] is None and tarefa_atual is not None):
            mudou = True
        elif (linha_do_tempo[i][1] is not None and tarefa_atual is None):
            mudou = True
        elif (linha_do_tempo[i][1] is not None and tarefa_atual is not None and
              (linha_do_tempo[i][1]['nome_tarefa'] != tarefa_atual['nome_tarefa'] or
               linha_do_tempo[i][1]['execucao_id'] != tarefa_atual['execucao_id'])):
            mudou = True

        if mudou:
            if tarefa_atual is not None:
                intervalos.append((tarefa_atual, inicio, i))
            tarefa_atual = linha_do_tempo[i][1]
            inicio = i

    if tarefa_atual is not None:
        intervalos.append((tarefa_atual, inicio, len(linha_do_tempo)))
    return intervalos

def plotar_simulacao(tarefas, linha_do_tempo, instancias, tipo_analise="edf"):
    intervalos = construir_intervalos(linha_do_tempo)
    nomes_tarefas = ["CPU", "tarefa4", "tarefa3", "tarefa2", "tarefa1"]

    periodos = [t.periodo for t in tarefas]
    hiper_periodo = calcular_mmc_lista(periodos)

    tempos_liberacao = {t.nome: [] for t in tarefas}
    instancias_map = {}
    for instancia in instancias:
        tempos_liberacao[instancia['nome_tarefa']].append(instancia['tempo_liberacao'])
        instancias_map[(instancia['nome_tarefa'], instancia['execucao_id'])] = instancia

    fig = plt.figure(figsize=(12, 8))

    # Subplot 1: Tabela
    ax1 = fig.add_subplot(4, 1, 1)
    ax1.axis('off')
    texto_tabela = []
    cabecalhos = ["Tarefa", "T (ms)", "D (ms)", "C (ms)"]
    for t in tarefas:
        texto_tabela.append([t.nome, str(t.periodo), str(t.deadline), str(t.tempo_computacao)])
    tabela = ax1.table(cellText=texto_tabela,
                       colLabels=cabecalhos,
                       loc='center',
                       cellLoc='center')
    tabela.scale(1, 1.5)
    ax1.set_title(f"Cálculo do MMC: {hiper_periodo} ms", pad=20)

    # Subplot 2: Ativações
    ax2 = fig.add_subplot(4, 1, 2)
    ax2.set_title("Ativações (▲ = liberação)")
    ax2.set_xlim(0, hiper_periodo)
    ax2.set_ylim(-1, len(nomes_tarefas))
    ax2.set_yticks(range(len(nomes_tarefas)))
    ax2.set_yticklabels(nomes_tarefas)
    ax2.set_xlabel("Tempo (ms)")
    ax2.set_xticks(range(0, hiper_periodo + 1))
    ax2.grid(True, axis='x', linestyle=':', alpha=0.7)

    for i, nome in enumerate(nomes_tarefas):
        if nome != "CPU":
            for tempo in tempos_liberacao[nome]:
                # Marcamos o release time com um triângulo
                ax2.plot(tempo, i, marker='^', color='black')

    # Subplot 3: Deadlines
    ax3 = fig.add_subplot(4, 1, 3)
    ax3.set_title("Deadlines (contagem regressiva)")
    ax3.set_xlim(0, hiper_periodo)
    ax3.set_ylim(-1, len(nomes_tarefas))
    ax3.set_yticks(range(len(nomes_tarefas)))
    ax3.set_yticklabels(nomes_tarefas)
    ax3.set_xlabel("Tempo (ms)")
    ax3.set_xticks(range(0, hiper_periodo + 1))
    ax3.grid(True, axis='x', linestyle=':', alpha=0.7)
    # Mostrando contagem regressiva de deadlines
    for i, nome in enumerate(nomes_tarefas):
        if nome != "CPU":
            for instancia in [j for j in instancias if j['nome_tarefa'] == nome]:
                for tempo in range(instancia['tempo_liberacao'], instancia['deadline_absoluto']):
                    restante = instancia['deadline_absoluto'] - tempo
                    ax3.text(tempo + 0.5, i, str(restante), ha='center', va='center', fontsize=7)

    # Subplot 4: Gantt Chart
    if tipo_analise == "edf":
        titulo_gantt = "Escalonamento EDF (Gantt Chart)"
    elif tipo_analise == "dm":
        titulo_gantt = "Escalonamento DM (Gantt Chart)"
    else:
        titulo_gantt = "Escalonamento RM (Gantt Chart)"

    ax4 = fig.add_subplot(4, 1, 4)
    ax4.set_title(titulo_gantt + "\n(o = prazo cumprido, ● = prazo perdido, □ = interrompido)")
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

    cpu_y = nomes_tarefas.index("CPU")

    # Descobrir preempções e deadline misses
    intervalos_por_instancia = {}
    for intervalo in intervalos:
        instancia, inicio, fim = intervalo
        chave = (instancia['nome_tarefa'], instancia['execucao_id'])
        if chave not in intervalos_por_instancia:
            intervalos_por_instancia[chave] = []
        intervalos_por_instancia[chave].append((inicio, fim))

    # Plotar intervalos
    for intervalo in intervalos:
        instancia = intervalo[0]
        inicio = intervalo[1]
        fim = intervalo[2]
        nome_tarefa = instancia['nome_tarefa']
        execucao_id = instancia['execucao_id']

        # Barra na CPU
        ax4.barh(cpu_y, fim - inicio, left=inicio, height=0.8, color=cores[nome_tarefa], edgecolor='black')
        ax4.text((inicio + fim) / 2, cpu_y, str(execucao_id), ha='center', va='center', color='white', fontsize=8)

        # Barra da tarefa
        if nome_tarefa in nomes_tarefas and nome_tarefa != "CPU":
            y = nomes_tarefas.index(nome_tarefa)
            ax4.barh(y, fim - inicio, left=inicio, height=0.8, color=cores[nome_tarefa], edgecolor='black', alpha=0.7)
            ax4.text((inicio + fim) / 2, y, str(execucao_id), ha='center', va='center', color='white', fontsize=8)

    # Marcar preempções e deadlines
    for chave, lista_int in intervalos_por_instancia.items():
        lista_int.sort(key=lambda x: x[0])
        nome_tarefa, execucao_id = chave
        instancia = instancias_map[chave]
        deadline = instancia['deadline_absoluto']
        y = nomes_tarefas.index(nome_tarefa) if nome_tarefa in nomes_tarefas else None

        # Intervalos múltiplos indicam preempção nos intervalos anteriores ao último
        for i, (ini, fim) in enumerate(lista_int):
            if i < len(lista_int) - 1:
                # Preempção
                ax4.plot(fim, y, marker='s', markerfacecolor='none', markeredgecolor='black', ms=8)
            else:
                # Último intervalo: verificar completion
                if instancia['tempo_restante'] == 0:
                    # Completou
                    if fim <= deadline:
                        # Deadline met: círculo aberto
                        ax4.plot(fim, y, marker='o', markerfacecolor='none', markeredgecolor='black', ms=8)
                    else:
                        # Deadline missed: círculo preenchido
                        ax4.plot(fim, y, marker='o', markerfacecolor='black', markeredgecolor='black', ms=8)
                else:
                    # Não completou (tempo_restante > 0)
                    # Não marcamos nada, pois não completou a tempo
                    # Se quiser marcar deadline missed caso o tempo já passe do deadline:
                    if fim > deadline:
                        ax4.plot(fim, y, marker='o', markerfacecolor='black', markeredgecolor='black', ms=8)

    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Este código permite escolher entre três algoritmos de escalonamento: EDF, DM e RM.
    #
    # - EDF (Earliest Deadline First): Prioridade pela tarefa com deadline absoluto mais próximo.
    # - DM (Deadline Monotonic): Prioridade fixa pela deadline relativa (menor deadline = maior prioridade).
    # - RM (Rate Monotonic): Prioridade fixa pelo período (menor período = maior prioridade).
    #
    # Observação: Em RM, o campo deadline não influencia a prioridade, apenas o período.
    #
    # Ajuste `tipo_analise` para "edf", "dm" ou "rm" e execute.

    tipo_analise = "rm"  # altere para "edf", "dm" ou "rm"

    tarefas = [
        # Tarefa(nome, periodo, deadline, tempo_computacao)
        Tarefa("tarefa1", 20, 5, 3),
        Tarefa("tarefa2", 15, 7, 3),
        Tarefa("tarefa3", 10, 10, 4),
        Tarefa("tarefa4", 20, 20, 3)
    ]

    periodos = [t.periodo for t in tarefas]
    hiper_periodo = calcular_mmc_lista(periodos)

    # Atribuir prioridades conforme o tipo de análise
    if tipo_analise == "dm":
        atribuir_prioridades_dm(tarefas)
    elif tipo_analise == "rm":
        atribuir_prioridades_rm(tarefas)
    # Se for EDF, nenhuma prioridade fixa precisa ser atribuída

    instancias = gerar_instancias(tarefas, hiper_periodo)

    if tipo_analise == "edf":
        linha_do_tempo = escalonamento_edf(instancias, hiper_periodo)
    elif tipo_analise == "dm":
        linha_do_tempo = escalonamento_dm(instancias, hiper_periodo)
    else:
        linha_do_tempo = escalonamento_rm(instancias, hiper_periodo)

    plotar_simulacao(tarefas, linha_do_tempo, instancias, tipo_analise)
