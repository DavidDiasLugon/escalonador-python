import queue
import random

random.seed()


def gera_id():
    palavra = ""
    for i in range(10):
        letra = random.randint(33, 127)
        j = chr(letra)
        palavra += j
    return palavra


class PCB:
    def __init__(self, id, prioridade):
        self.estado = "Novo"
        self.id = id
        self.prioridade = prioridade


class Processo:
    def __init__(self, chegada, fase1, entrada_saida, fase2, tamanho, disco):
        self.c = chegada
        self.f1 = fase1
        self.io = entrada_saida
        self.f2 = fase2
        self.tamanho = (tamanho * 1048576)  # Em Mbytes
        self.disco = disco
        # Define a prioridade do processo, caso sofra time-slice p += 1, e sempre começa com 1 (fila de maior prioridade)
        self.prioridade = 1
        # TODO: Guardar quanto tempo o processo gasta em cada fase
        # Quando acabar o tempo total em CPU, o processo terminou (só atualizar o tempo para o fim do processo quando ele estiver em CPU)
        self.etapa = 0
        self.pcb = PCB(gera_id(), self.prioridade)

    def enviar_memoria_primaria(self):
        ...


class Memoria_RAM:
    capacidade = 34359738368  # 32Gbytes
    espaco_livre = capacidade  # Começa com 32Gbytes livres
    # Instanciando as quatro filas de processos prontos para serem executados
    filas = [queue.Queue() for _ in range(4)]
    bloqueados = []

    def adicionar_processo_pronto(self, processo: Processo):
        if (self.espaco_livre - processo.tamanho) < 0:  # Caso não haja espaço na memória primária
            # Coloquei isso, caso implementemos uma função para colocar como pronto_suspenso e uma como bloqueado_suspenso
            return SwapOut(processo).pronto_suspenso
        if (processo.prioridade == 1):
            self.filas[0].put(processo)
        elif (processo.prioridade == 2):
            self.filas[1].put(processo)
        elif (processo.prioridade == 3):
            self.filas[2].put(processo)
        elif (processo.prioridade == 4):
            self.filas[3].put(processo)
        self.espaco_livre -= processo.tamanho

    def remover_processo(self, processo: Processo):
        # Como resolver isso? (Só sairá da RAM caso outro processo queirae entrar)
        if (self.espaco_livre + processo.tamanho) > self.capacidade:
            self.espaco_livre = self.capacidade
        if (processo.prioridade == 1):
            self.filas[0].pop(0)
            if (processo.pcb.estado == "Pronto"):
                # Coloquei isso, caso implementemos uma função para colocar como pronto_suspenso e uma como bloqueado_suspenso
                SwapOut(processo).pronto_suspenso
            else:  # Condição para caso esteja na fila de bloqueados
                # Coloquei isso, caso implementemos uma função para colocar como pronto_suspenso e uma como bloqueado_suspenso
                SwapOut(processo).bloqueado_suspenso
        elif (processo.prioridade == 2):
            self.filas[1].pop(0)
            if (processo.pcb.estado == "Pronto"):
                # Coloquei isso, caso implementemos uma função para colocar como pronto_suspenso e uma como bloqueado_suspenso
                SwapOut(processo).pronto_suspenso
            else:
                # Coloquei isso, caso implementemos uma função para colocar como pronto_suspenso e uma como bloqueado_suspenso
                SwapOut(processo).bloqueado_suspenso
        elif (processo.prioridade == 3):
            self.filas[2].pop(0)
            if (processo.pcb.estado == "Pronto"):
                # Coloquei isso, caso implementemos uma função para colocar como pronto_suspenso e uma como bloqueado_suspenso
                SwapOut(processo).pronto_suspenso
            else:
                # Coloquei isso, caso implementemos uma função para colocar como pronto_suspenso e uma como bloqueado_suspenso
                SwapOut(processo).bloqueado_suspenso
        elif (processo.prioridade == 4):
            self.filas[3].pop(0)
            if (processo.pcb.estado == "Pronto"):
                # Coloquei isso, caso implementemos uma função para colocar como pronto_suspenso e uma como bloqueado_suspenso
                SwapOut(processo).pronto_suspenso
            else:
                # Coloquei isso, caso implementemos uma função para colocar como pronto_suspenso e uma como bloqueado_suspenso
                SwapOut(processo).bloqueado_suspenso
        self.espaco_livre += processo.tamanho


class Memoria_secundaria:  # Discos
    fila_suspensos = []  # Filas com processos pronto-suspensos
    bloqueados = []  # Criar func de bloqueado suspenso

    def __init__(self, identificador):
        self.id = identificador
        self.armazenamento = []

    def adicionar_processo_pronto_suspenso(self, processo: Processo):
        self.fila_suspensos.append(processo)

    def adicionar_processo_bloqueado_suspenso(self, processo: Processo):
        self.bloqueados.append(processo)

    # aqui como não tem uma capacidade, basta tirar daqui o processo
    def remover_processo(self, processo: Processo):
        self.armazenamento.remove(processo)


class CPU:
    QUANTUM = 3

    def __init__(self, identificador):
        self.id = identificador
        self.clock = 0

    def executar_processo(self, processo: Processo):
        processo.momento_saida -= 1
        self.clock += 1

        # f1 = 2
        # f2 = 6
        # momento_saida 8
        #
        #

        if processo.f

        # verifica se acabou o processo
        if processo.momento_saida == 0:
            # processo.momento_saida = processo.momento_saida
            self.clock = 0
            return 'Acabou o processo'

        # verifica se atingiu o quantum
        if self.clock == self.QUANTUM:
            processo.prioridade += 1
            self.clock = 0
            print(f'Processo {processo.pcb.id} sofreu um Time-slicing\n')
            return 'Atingiu o quantum'

        return 'Está executando'


class Escalonador:
    def __init__(self, identificador):
        self.id = identificador


class Despachante(Escalonador):  # Curto Prazo
    def __init__(self, identificador):
        super(Despachante, self).__init__(
            identificador)  # Herdando do escalonador

    def Despacho(self):  # Seleciona processo para receber o estado de Executando
        situacao_atual = cpu.executar_processo(processo)
        if (situacao_atual == 'Acabou o processo'):
            ...
        elif (situacao_atual == 'Atingiu o quantum'):
            ...


class MedioPrazo(Escalonador):
    def __init__(self, identificador):
        super(MedioPrazo, self).__init__(
            identificador)  # Herdando do escalonador

    def clock(self):

        print('O primeiro quantum foi executado!\n')

    # Memória RAM --> Memória Secundária.
    def SwapOut(self, processo, ram, secundaria, id):  # Chama remover processo
        if (processo.PCB.estado == "Pronto"):
            secundaria[id].adicionar_processo(processo)  # Pronto-suspenso
            # printa que passa de pronto -> pronto-suspenso
            print(f'Processo {processo.pcb.id} Pronto --> Pronto-Suspenso\n')
        else:  # estado == Bloqueado
            print(f'Processo {
                  processo.pcb.id} Bloqueado --> Bloqueado-Suspenso\n')
            ...  # TODO: Criar função pra adicionar em Bloqueado-Suspeso

        processo.remover_processo(processo)

    # É preciso tirar o processo da lista de processos que estão na Memória Sececundária e jogá-lo pra lista da RAM
    # TODO: Fazer ser retornado um booleano para verificar se é possível
    def SwapIn(self, processo, ram, secundaria):   # Memória Secundária --> Memoria_RAM
        if (processo.PCB.estado == "Pronto-Suspenso"):
            processo.adicionar_processo_pronto(processo)
            print(f'Processo {processo.pcb.id} Pronto-Suspenso --> Pronto\n')
        else:  # bloqueado suspenso - > bloqueado
            # func pra passar de bloqueadosusp -> bloqueado
            print(f'Processo {
                  processo.pcb.id} Bloqueado-Suspenso --> Bloqueado\n')


# Mémória secundária: armazenamento ->
# Memória primária: filas (fila de prontos)   adicionar_processo(processo)
# - se retorna -1, MedioPrazo faz SwapOut


class Computador:
    # Inicialização da memória principal
    ram = Memoria_RAM()
    # Inicialização dos processadores
    cpu1 = CPU('cpu1')
    cpu2 = CPU('cpu2')
    cpu3 = CPU('cpu3')
    cpu4 = CPU('cpu4')
    # Inicialização dos discos
    secundaria1 = Memoria_secundaria('secundaria1')
    secundaria2 = Memoria_secundaria('secundaria2')
    secundaria3 = Memoria_secundaria('secundaria3')
    secundaria4 = Memoria_secundaria('secundaria4')

    secundaria = {
        '1': secundaria1,
        '2': secundaria2,
        '3': secundaria3,
        '4': secundaria4
    }

    processos = queue.Queue()

    # Leitura do arquivo com cada um dos processos
    with open('input.txt', 'r') as arquivo:
        for linha in arquivo:
            processo_linha = [x.strip() for x in linha.split(',')]

            processo = Processo(int(processo_linha[0]), int(processo_linha[1]), int(processo_linha[2]),  # e.g. 12,4,5,6,800,2
                                int(processo_linha[3]), int(processo_linha[4]), int(processo_linha[5]))
            id = processo_linha[5]

            processo.pcb.estado = "Pronto-Suspenso"
            print(f'Processo de id: {processo.pcb.id} movido de Novo para {
                  processo.pcb.estado}\n')
            processos.put(processo)
            secundaria[id].adicionar_processo(processo)

    medioPrazo = MedioPrazo('medio_prazo_id')

    while True:
        clock = input("")
        if clock == "":
            # print('1 Quantum')

            # A cada clock, tenta alocar um processo inicial da memória secundária para a memória RAM. Se não conseguir, esse processo vai para o fim da fila.
            if not processos.empty():  # Verifica se a fila não está vazia
                processo = processos.get()  # Remove e retorna o primeiro processo da fila
                sucesso = medioPrazo.SwapIn(processo, ram, secundaria)

                if not sucesso:
                    # Se o SwapIn falhar, coloca o processo de volta ao final da fila
                    processos.put(processo)

            medioPrazo.clock()

        elif clock == "-1":
            break
        else:
            print("Valor inválido")


if __name__ == '__main__':
    Computador()  # Só para testar :D
