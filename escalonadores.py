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
