import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.cm as cm

from escalonadores import construir_intervalos
from tarefas import calcular_mmc_lista

def plotar_simulacao(tarefas, linha_do_tempo, instancias, tipo_analise="edf"):
    intervalos = construir_intervalos(linha_do_tempo)
    
    # Conta o número de tarefas + 1 (para a CPU)
    Numero_tarefas = len(tarefas) + 1
    
    # Cria a lista de tarefas invertida e adiciona a CPU no topo
    task_names = [t.nome for t in tarefas]
    task_names.reverse()  
    nomes_tarefas = ["CPU"] + task_names

    # Calcula o hiper-período
    periodos = [t.periodo for t in tarefas]
    hiper_periodo = calcular_mmc_lista(periodos)

    tempos_liberacao = {t.nome: [] for t in tarefas}
    instancias_map = {}
    for instancia in instancias:
        tempos_liberacao[instancia['nome_tarefa']].append(instancia['tempo_liberacao'])
        instancias_map[(instancia['nome_tarefa'], instancia['execucao_id'])] = instancia

    U = None
    limite = None
    escalonavel = True
    # Cálculo da taxa de utilização U = sum(Ci/Ti)
    U = sum(t.tempo_computacao / t.periodo for t in tarefas)
    n = len(tarefas)
    limite = n * (2**(1/n) - 1)

    fig = plt.Figure(figsize=(12, 8))

    is_rm = (tipo_analise.lower() == 'rm')
    if tipo_analise.lower() != 'rm':
        # Subplots com sharex para sincronizar zoom/pan
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
    else:
        # Apenas um subplot se for RM
        ax4 = fig.add_subplot(1, 1,1)

    if tipo_analise.lower() == "edf":
        titulo_gantt = "Escalonamento EDF (Gantt Chart)"
    elif tipo_analise.lower() == "dm":
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

    cores = {}
    cmap = cm.get_cmap("tab10")
    for i, nome in enumerate(nomes_tarefas):
        cores[nome] = cmap(i)

    cpu_y = nomes_tarefas.index("CPU")

    intervalos_por_instancia = {}
    for intervalo in intervalos:
        instancia = intervalo[0]
        inicio = intervalo[1]
        fim = intervalo[2]
        chave = (instancia['nome_tarefa'], instancia['execucao_id'])
        if chave not in intervalos_por_instancia:
            intervalos_por_instancia[chave] = []
        intervalos_por_instancia[chave].append((inicio, fim))

    # Plotar intervalos, prioridades, etc.
    for intervalo in intervalos:
        instancia = intervalo[0]
        inicio = intervalo[1]
        fim = intervalo[2]
        nome_tarefa = instancia['nome_tarefa']
        execucao_id = instancia['execucao_id']
        prioridade = instancia.get('prioridade', None) 

        # Barra na CPU
        ax4.barh(cpu_y, fim - inicio, left=inicio, height=0.8, color=cores.get(nome_tarefa, 'gray'), edgecolor='black')
        ax4.text((inicio + fim) / 2, cpu_y, str(execucao_id), ha='center', va='center', color='white', fontsize=8)

        if nome_tarefa in nomes_tarefas and nome_tarefa != "CPU":
            y = nomes_tarefas.index(nome_tarefa)
            ax4.barh(y, fim - inicio, left=inicio, height=0.8, color=cores.get(nome_tarefa, 'gray'), edgecolor='black', alpha=0.7)
            ax4.text((inicio + fim) / 2, y, str(execucao_id), ha='center', va='center', color='white', fontsize=8)

            if prioridade is not None:
                prioridade = Numero_tarefas - int(prioridade)
                ax4.text((inicio + fim) / 2, y + 0.4, f"P{prioridade}", ha='center', va='bottom', color='black', fontsize=8)

    # Preempções, intervalos ociosos entre intervalos da mesma tarefa e hachura entre ativação e primeira execução
    for chave, lista_int in intervalos_por_instancia.items():
        lista_int.sort(key=lambda x: x[0])
        nome_tarefa, execucao_id = chave
        instancia = instancias_map[chave]
        deadline = instancia['deadline_absoluto']
        release_time = instancia['tempo_liberacao']

        y = nomes_tarefas.index(nome_tarefa) if nome_tarefa in nomes_tarefas else None

        if y is not None and len(lista_int) > 0:
            # Hachurar entre ativação e primeira execução, se houver gap
            ini_first = lista_int[0][0]
            if release_time < ini_first:
                ax4.add_patch(
                    patches.Rectangle((release_time, y - 0.4),
                                      ini_first - release_time,
                                      0.8,
                                      facecolor='gray',
                                      alpha=0.3,
                                      hatch='\\',
                                      edgecolor='black')
                )

            # Verificar interrupções
            for i, (ini, fim) in enumerate(lista_int):
                if i < len(lista_int) - 1:
                    # Interrompido
                    ax4.plot(fim, y, marker='s', markerfacecolor='blue', markeredgecolor='black', ms=8)
                    ini_next = lista_int[i+1][0]

                    # Área hachurada representando o intervalo ocioso
                    ax4.add_patch(
                        patches.Rectangle((fim, y - 0.4),
                                          ini_next - fim,
                                          0.8,
                                          facecolor='y',
                                          alpha=0.3,
                                          hatch='/',
                                          edgecolor='black')
                    )
                else:
                    # Último intervalo: verificar conclusão e deadline
                    if instancia['tempo_restante'] == 0 and tipo_analise != 'rm':
                        if fim <= deadline:
                            ax4.plot(fim, y, marker='$\u2713$', markerfacecolor='green', markeredgecolor='green', ms=8)
                        else:
                            ax4.plot(fim, y, marker='X', markerfacecolor='red', markeredgecolor='black', ms=8)
                            escalonavel=False
                    else:
                        if fim > deadline and tipo_analise != 'rm':
                            ax4.plot(fim, y, marker='X', markerfacecolor='red', markeredgecolor='black', ms=8)
                            escalonavel=False

    # Criar patches para a legenda
    patch_hachura = patches.Rectangle((0, 0), 1, 1, facecolor='gray', alpha=0.3, hatch='\\', edgecolor='black')
    patch_interrompido = patches.Rectangle((0, 0), 1, 1, facecolor='y', alpha=0.3, hatch='//', edgecolor='black')

    ax4.legend([patch_hachura, patch_interrompido],
               ['Intervalo ocioso', 'Intervalo Interrompido'],
               loc='lower right', fontsize=9)

    # Se for RM, mostrar resultados U, limite e se é escalonável
    if is_rm and U is not None and limite is not None:
        escalonavel = U <= limite
        texto_escalonabilidade = f"Escalonabilidade RM:\nU = {U:.3f}, Limite = {limite:.3f}\n"
        texto_escalonabilidade += "Escalonável" if escalonavel else "Não escalonável"
        color =  "black" if escalonavel else "red"
        fig.text(0.9, 0.9, texto_escalonabilidade, ha='center', va='top', fontsize=12, color='white', bbox=dict(facecolor=color, alpha=0.5))
    else:
        texto_escalonabilidade = f"Escalonabilidade {tipo_analise}:\nU = {U:.3f}\n"
        texto_escalonabilidade += "Escalonável" if escalonavel else "Não escalonável"
        color =  "black" if escalonavel else "red"
        fig.text(0.9, 0.9, texto_escalonabilidade, ha='center', va='top', fontsize=12, color='white', bbox=dict(facecolor=color, alpha=0.5))

    fig.tight_layout()
    return fig
