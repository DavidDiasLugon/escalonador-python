import queue
import random
from collections import deque

random.seed()
QUANTUM = 3
cQuantum = 0

def gerar_id():
    palavra = ""
    for _ in range(10):
        numAleatorio = random.randint(0, 1000)
        letrasMaiusculas = random.randint(97, 122)
        letrasMinusculas = random.randint(65, 90)
        if (numAleatorio % 2 == 0):
            j = chr(letrasMinusculas)
        else:
            j = chr(letrasMaiusculas)
        palavra += j
    return palavra

class PCB:
    def __init__(self, id):
        self.estado = "Novo"
        self.id = id
        self.prioridade = 1

class Escalonador:
    def __init__(self, id):
        self.id = id

class Despachante(Escalonador):  # Curto Prazo
    def __init__(self, id):
        super(Despachante, self).__init__(id)  # Herdando do escalonador

    # Adiciona o processo a uma cpu
    # Seleciona processo para receber o estado de Executando
    def Despacho(self, ram, cpu, secundaria):
        if (cpu.executando == False):
            for fila in ram.filas:  # Começa sempre na primeira
                if not fila.empty():  # Verifica se a fila não está vazia
                    processo = fila.get()  # Pega o primeiro processo da fila
                    cpu.adicionar_processo(processo)
                    processo.pcb.estado = 'Executando'
                    print(f'Processo de id: {processo.pcb.id} movido de Pronto para {processo.pcb.estado}\n')
                    break

        if (cpu.processo):
            estado = cpu.executar_processo()

            if (estado == "QuantumMax"):  # Time Slice
                cpu.processo.pcb.prioridade += 1
                # Volta para a primeira fila caso chegue na última e precise voltar a executar
                if (cpu.processo.pcb.prioridade == 5):
                    cpu.processo.pcb.prioridade = 1
                cpu.processo.pcb.estado = 'Pronto'
                ram.adicionar_processo_pronto(cpu.processo)
                cpu.limpa_cpu()

            if (estado == 'TerminouFase1'):
                cpu.processo.pcb.prioridade = 1
                id = cpu.processo.disco
                ram.bloqueia_processo(cpu.processo, ram, secundaria[id])
                cpu.limpa_cpu()

            if (estado == 'TerminouFase2'):
                ram.remove_processo(cpu.processo)
                cpu.limpa_cpu()

            if (estado == "Executando"):  # Continua exec
                print(f'{cpu.id} - Processo {cpu.processo.pcb.id} ainda executando. Etapa: {cpu.processo.etapa}')

class MedioPrazo(Escalonador):  # Médio Prazo
    def __init__(self, id):
        super(MedioPrazo, self).__init__(id)  # Herdando do escalonador

    # Memória RAM --> Memória Secundária
    def swap_out(self, processo, ram, secundaria):  # Chama remover processo
        if (processo.pcb.estado == "Pronto"):
            secundaria[processo.disco].adicionar_processo_pronto_suspenso(
                processo)  # Pronto-suspenso
            processo.pcb.estado = 'Pronto-Suspenso'
            ram.memoria.remove(processo)
            # Printa que passa de pronto -> pronto-suspenso
            print(f'Processo de id: {processo.pcb.id} movido Pronto para Pronto-Suspenso\n')
            processo.pcb.prioridade = 1
        else:  # Estado == Bloqueado
            secundaria.adicionar_processo_bloqueado_suspenso(processo)
            processo.pcb.estado = 'Bloqueado-Suspenso'
            ram.bloqueados.remove(processo)
            print(f'Processo {processo.pcb.id} Bloqueado --> Bloqueado-Suspenso\n')
            processo.pcb.prioridade = 1

    # Memória Secundaria --> Memória RAM
    def swap_in(self, processo, ram, secundaria):
        flag = True  # Essa flag é de controle para o sucesso, pq pode ter limite na Memória, assim ele continua no
        if (processo.pcb.estado == "Pronto-Suspenso"):
            processo.pcb.estado = "Pronto"
            processo.pcb.prioridade = 1
            flag = ram.adicionar_processo_pronto(processo)
            if (flag == False):  # Checar a flag antes de remover da Mem. Sec.
                return flag
            secundaria.remover_processo_pronto_suspenso(processo)
            print(f'Processo de id: {processo.pcb.id} movido de Pronto-Suspenso para {processo.pcb.estado}\n')
            return flag
        else:  # bloqueado-suspenso - > bloqueado
            # func pra passar de bloqueadosusp -> bloqueado
            print(f'Processo {processo.pcb.id} Bloqueado-Suspenso --> Bloqueado\n')
            
class Processo:
    def __init__(self, c, fase1, entradaSaida, fase2, tamanho, disco):
        self.chegada = c
        self.f1 = fase1
        self.io = entradaSaida
        self.ioEtapa = 0
        self.f2 = fase2
        self.tamanho = (tamanho * 1048576)  # Em Mbytes
        self.disco = disco
        self.etapa = 0
        self.pcb = PCB(gerar_id())

class MemoriaRam:
    capacidade = 34359738368  # 32Gbytes == 32768 Mbytes
    memoria = [] # 2048Mb cada partição(particionamento fixo) ou seja terá 16 elementos

    espacoLivre = capacidade  # Começa com 32Gbytes livres
    # Instanciando as quatro filas de processos prontos para serem executados
    filas = [queue.Queue() for _ in range(4)]  # Filas de prontos
    bloqueados = []
    escalona = MedioPrazo('medio_prazo_id')

    def adicionar_processo_pronto(self, processo: Processo) -> bool:
        if (len(self.memoria) == 16):
            print("Memória Cheia")
            return False

        if (processo.pcb.prioridade == 1):
            self.memoria.append(processo)
            self.filas[0].put(processo)
        elif (processo.pcb.prioridade == 2):
            self.memoria.append(processo)
            self.filas[1].put(processo)
        elif (processo.pcb.prioridade == 3):
            self.memoria.append(processo)
            self.filas[2].put(processo)
        elif (processo.pcb.prioridade == 4):
            self.memoria.append(processo)
            self.filas[3].put(processo)

        print(f'---------------- Memória RAM ------------------')
        for index, fila in enumerate(self.filas):
            print(f'Fila de Prontos {index + 1}')
            temp_list = list(fila.queue)
            for processo in temp_list:
                print(f'ID: {processo.pcb.id}, Prioridade: {processo.pcb.prioridade}, Estado: {processo.pcb.estado}')
        print('-----------------------------------------------')
        print()
        return True

    def bloqueia_processo(self, processo: Processo, ram, secundaria):
        if (len(self.memoria) < 16):
            self.bloqueados.append(processo)
            processo.pcb.estado = "Bloqueado"
            self.memoria.remove(processo)
            print(f'Processo de id: {processo.pcb.id} movido de Executando para {processo.pcb.estado}\n')
            print('Fila de Bloqueado:', self.bloqueados)
        else:
            self.escalona.swap_out(processo, ram, secundaria)
            print("Memória Cheia")

    def remove_processo(self, processo: Processo):
        self.memoria.remove(processo)
        print(f'Processo de id: {processo.pcb.id} terminou a execução\n')

    def processa_bloqueados(self):
        for processo in self.bloqueados:
            processo.ioEtapa += 1
            processo.etapa += 1
            print(f'Processo {processo.pcb.id} está na fila de bloqueados')
            print(processo.ioEtapa)
            print(processo.io)
            print('---')
            if (processo.ioEtapa == processo.io):
                processo.ioEtapa = 0
                self.bloqueados.remove(processo)
                processo.pcb.estado = "Pronto"
                self.adicionar_processo_pronto(processo)

class MemoriaSecundaria:
    def __init__(self, identificador):
        self.id = identificador
        self.fila_suspensos = []  # Filas com processos pronto-suspensos
        self.bloqueados = []  # Fila com processos bloqueados (suspensos)

    def adicionar_processo_pronto_suspenso(self, processo: Processo):
        self.fila_suspensos.append(processo)

    def adicionar_processo_bloqueado_suspenso(self, processo: Processo):
        self.bloqueados.append(processo)

    def remover_processo_pronto_suspenso(self, processo: Processo):
        self.fila_suspensos.remove(processo)

    def remover_processo_bloqueado_suspenso(self, processo: Processo):
        self.bloqueados.remove(processo)

class CPU:
    # Política Feedback:
    # - Quantum == 3;
    # - Se um processo sofreu interrupção ele voltará para a 1 fila de processos prontos após o término da operação de E/S;
    # - Se um processo sofreu fatia de tempo ele irá para a próxima fila de prontos, caso alcance a última irá retornar para a primeira;
    def __init__(self, identificador):
        self.id = identificador # Identificador do número da  (processo.pcb.prioridade)
        self.clock = 0  # Contador de unidades de tempo de execução do processo atual
        self.processo = None
        self.executando = False

    def limpa_cpu(self):
        self.clock = 0
        self.processo = None
        self.executando = False

    def adicionar_processo(self, processo: Processo):
        self.limpa_cpu()
        self.processo = processo

    def executar_processo(self):
        self.executando = True

        if self.processo is None:
            return ''

        if (self.processo.etapa == self.processo.f1):
            return 'TerminouFase1'

        if (self.processo.etapa == (self.processo.f2 + self.processo.f1 + self.processo.io)):
            return 'TerminouFase2'

        if (self.clock == QUANTUM):
            print(f'Processo {self.processo.pcb.id} sofreu um Time-slicing\n')
            return 'QuantumMax'
        self.processo.etapa += 1
        self.clock += 1
        return 'Executando'

class Computador:
    # Inicialização da memória principal
    ram = MemoriaRam()
    # Inicialização dos discos
    secundaria1 = MemoriaSecundaria('secundaria1')
    secundaria2 = MemoriaSecundaria('secundaria2')
    secundaria3 = MemoriaSecundaria('secundaria3')
    secundaria4 = MemoriaSecundaria('secundaria4')

    secundaria = {
        '1': secundaria1,
        '2': secundaria2,
        '3': secundaria3,
        '4': secundaria4
    }
    # Inicialização dos processadores
    cpu1 = CPU('CPU 1')
    cpu2 = CPU('CPU 2')
    cpu3 = CPU('CPU 3')
    cpu4 = CPU('CPU 4')

    processos = deque()
    cont_n_arqs = 0

    # Leitura do arquivo com cada um dos processos
    with open('input.txt', 'r') as arquivo:
        for linha in arquivo:
            processoLinha = [x.strip() for x in linha.split(',')]
            processo = Processo(int(processoLinha[0]), int(processoLinha[1]), int(processoLinha[2]),  # e.g. 12,4,5,6,800,2
                                int(processoLinha[3]), int(processoLinha[4]), (processoLinha[5]))
            id = processoLinha[5]

            processo.pcb.estado = "Pronto-Suspenso"
            print(f'Processo de id: {processo.pcb.id} movido de Novo para {processo.pcb.estado}\n')
            processos.append(processo)
            secundaria[id].adicionar_processo_pronto_suspenso(processo)
            cont_n_arqs += 1

    despachante = Despachante('curtoPrazoId')
    medioPrazo = MedioPrazo('medioPrazoId')
    despachangeAtivo = False

    # Converte a fila em uma lista para iteração
    processos_list = list(processos)

    while True:  # Ajeitar p/ o "clock"
        clock = input("")
        if clock == "":
            cQuantum += 1
            print('Quantum', cQuantum)
        else:
            print("Valor inválido")
            break

        # A cada clock, tenta alocar um processo inicial da memória secundária para a memória RAM. Se não conseguir, esse processo vai para o fim da fila.
        for processo in processos:
            if processo.chegada == cQuantum:
                sucesso = medioPrazo.swap_in(
                    processo, ram, secundaria[processo.disco])
                if not sucesso:
                    # Se o swap_in falhar, coloca o processo de volta ao final da fila
                    processos.append(processo)
        despachante.Despacho(ram, cpu1, secundaria)
        despachante.Despacho(ram, cpu2, secundaria)
        despachante.Despacho(ram, cpu3, secundaria)
        despachante.Despacho(ram, cpu4, secundaria)
        ram.processa_bloqueados()

if __name__ == '__main__':
    Computador()
