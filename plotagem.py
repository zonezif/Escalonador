import matplotlib.pyplot as plt
from escalonadores import construir_intervalos
from tarefas import calcular_mmc_lista

def plotar_simulacao(tarefas, linha_do_tempo, instancias, tipo_analise="edf"):
    intervalos = construir_intervalos(linha_do_tempo)
    Numero_tarefas = len(tarefas) + 1
    task_names = [t.nome for t in tarefas]
    task_names.reverse()  # inverte a lista de tarefas
    nomes_tarefas = ["CPU"] + task_names

    periodos = [t.periodo for t in tarefas]
    hiper_periodo = calcular_mmc_lista(periodos)

    tempos_liberacao = {t.nome: [] for t in tarefas}
    instancias_map = {}
    for instancia in instancias:
        tempos_liberacao[instancia['nome_tarefa']].append(instancia['tempo_liberacao'])
        instancias_map[(instancia['nome_tarefa'], instancia['execucao_id'])] = instancia

    fig = plt.Figure(figsize=(12, 8))

    # Compartilhar o eixo x para sincronizar zoom/pan
    ax2 = fig.add_subplot(2, 1, 1)
    ax4 = fig.add_subplot(2, 1, 2, sharex=ax2)

    ax2.set_title("Ativações (▶ = liberação) | Deadlines (contagem regressiva)")
    ax2.set_xlim(0, hiper_periodo)
    ax2.set_ylim(-1, len(nomes_tarefas))
    ax2.set_yticks(range(len(nomes_tarefas)))
    ax2.set_yticklabels(nomes_tarefas)
    ax2.set_xlabel("Tempo (ms)")
    ax2.set_xticks(range(0, hiper_periodo + 1))
    ax2.grid(True, axis='x', linestyle=':', alpha=0.7)

    # Marcar liberações no subplot superior
    for i, nome in enumerate(nomes_tarefas):
        if nome != "CPU":
            for tempo in tempos_liberacao.get(nome, []):
                ax2.plot(tempo, i, marker='>', color='black')

    # Contagem regressiva de deadlines no subplot superior
    for i, nome in enumerate(nomes_tarefas):
        if nome != "CPU":
            t_inst = [j for j in instancias if j['nome_tarefa'] == nome]
            for instancia in t_inst:
                for tempo in range(instancia['tempo_liberacao'], instancia['deadline_absoluto']):
                    restante = instancia['deadline_absoluto'] - tempo
                    ax2.text(tempo + 0.5, i, str(restante), ha='center', va='center', fontsize=7)

    if tipo_analise == "edf":
        titulo_gantt = "Escalonamento EDF (Gantt Chart)"
    elif tipo_analise == "dm":
        titulo_gantt = "Escalonamento DM (Gantt Chart)"
    else:
        titulo_gantt = "Escalonamento RM (Gantt Chart)"

    ax4.set_title(titulo_gantt + "\n(✓ = prazo cumprido, X = prazo perdido, □ = interrompido)")
    ax4.set_xlim(0, hiper_periodo)
    ax4.set_ylim(-1, len(nomes_tarefas))
    ax4.set_yticks(range(len(nomes_tarefas)))
    ax4.set_yticklabels(nomes_tarefas)
    ax4.set_xlabel("Tempo (ms)")
    ax4.set_xticks(range(0, hiper_periodo + 1))
    ax4.grid(True, axis='x', linestyle=':', alpha=0.7)

    # Marcar liberações no subplot inferior
    for i, nome in enumerate(nomes_tarefas):
        if nome != "CPU":
            for tempo in tempos_liberacao.get(nome, []):
                ax4.plot(tempo, i, marker='>', color='black')

    import matplotlib.cm as cm
    cmap = cm.get_cmap("tab10")
    cores = {}
    for i, nome in enumerate(nomes_tarefas):
        cores[nome] = cmap(i)

    cpu_y = nomes_tarefas.index("CPU")

    intervalos_por_instancia = {}
    for intervalo in intervalos:
        instancia, inicio, fim = intervalo
        chave = (instancia['nome_tarefa'], instancia['execucao_id'])
        if chave not in intervalos_por_instancia:
            intervalos_por_instancia[chave] = []
        intervalos_por_instancia[chave].append((inicio, fim))

    # Plotar intervalos, prioridades, preempções e deadlines
    for intervalo in intervalos:
        instancia = intervalo[0]
        inicio = intervalo[1]
        fim = intervalo[2]
        nome_tarefa = instancia['nome_tarefa']
        execucao_id = instancia['execucao_id']
        prioridade = instancia.get('prioridade', None)  # caso não exista prioridade, retorna None

        # Barra na CPU
        ax4.barh(cpu_y, fim - inicio, left=inicio, height=0.8, color=cores.get(nome_tarefa, 'gray'), edgecolor='black')
        ax4.text((inicio + fim) / 2, cpu_y, str(execucao_id), ha='center', va='center', color='white', fontsize=8)

        if nome_tarefa in nomes_tarefas and nome_tarefa != "CPU":
            y = nomes_tarefas.index(nome_tarefa)
            ax4.barh(y, fim - inicio, left=inicio, height=0.8, color=cores.get(nome_tarefa, 'gray'), edgecolor='black', alpha=0.7)
            ax4.text((inicio + fim) / 2, y, str(execucao_id), ha='center', va='center', color='white', fontsize=8)

            # Se prioridade estiver definida, mostra acima da barra
            if prioridade is not None:
                prioridade = Numero_tarefas - int(prioridade)
                ax4.text((inicio + fim) / 2, y + 0.4, f"P{prioridade}", ha='center', va='bottom', color='black', fontsize=8)

    # Preempções e deadlines (última etapa)
    for chave, lista_int in intervalos_por_instancia.items():
        lista_int.sort(key=lambda x: x[0])
        nome_tarefa, execucao_id = chave
        instancia = instancias_map[chave]
        deadline = instancia['deadline_absoluto']
        y = nomes_tarefas.index(nome_tarefa) if nome_tarefa in nomes_tarefas else None

        if y is not None:
            for i, (ini, fim) in enumerate(lista_int):
                if i < len(lista_int) - 1:
                    # Interrompido
                    ax4.plot(fim, y, marker='s', markerfacecolor='blue', markeredgecolor='black', ms=8)
                else:
                    # Verificar conclusão e deadline
                    if instancia['tempo_restante'] == 0:
                        if fim <= deadline:
                            # Deadline cumprido
                            ax4.plot(fim, y, marker='$\u2713$', markerfacecolor='green', markeredgecolor='green', ms=8)
                        else:
                            # Deadline perdido
                            ax4.plot(fim, y, marker='X', markerfacecolor='red', markeredgecolor='black', ms=8)
                    else:
                        if fim > deadline:
                            ax4.plot(fim, y, marker='X', markerfacecolor='red', markeredgecolor='black', ms=8)

    fig.tight_layout()
    return fig
