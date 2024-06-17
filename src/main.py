import queue
import random
from collections import deque

random.seed()
QUANTUM = 3
c_quantum = 0

def gerar_id():
    palavra = ""
    for _ in range(10):
        numeroAleatorio = random.randint(0, 1000)
        letrasMaiusculas = random.randint(97, 122)
        letrasMinusculas = random.randint(65, 90)
        
        if(numeroAleatorio % 2 == 0):
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

# [faz_algo for i in fila] <-- assim

class Despachante(Escalonador): # Curto Prazo
    def __init__(self, id):
        super(Despachante, self).__init__(id)  # Herdando do escalonador        

    # adiciona o processo a uma cpu
    def Despacho(self, memoria_ram, cpu):  # Seleciona processo para receber o estado de Executando
        if (cpu.executando == False):
            for fila in memoria_ram.filas: #começa sempre na primeira
                if not fila.empty():  # Verifica se a fila não está vazia
                    processo = fila.get()  # Pega o primeiro processo da fila
                    cpu.adicionar_processo(processo)#
                    processo.pcb.estado = 'Executando'
                    print(f'Processo de id: {processo.pcb.id} movido de Pronto para {processo.pcb.estado}\n')
                    #  1    2   3   4
                    # [14, 18, 22, 44]
                       
                    break
        
        if (cpu.processo): 
            estado = cpu.executar_processo()
            
            # print({cpu.processo.})

            if (estado == "QuantumMax"): #Time Slice
                cpu.processo.pcb.prioridade += 1
                if(cpu.processo.pcb.prioridade == 5):#Volta para a primeira fila caso chegue na última e precise voltar a executar
                    cpu.processo.pcb.prioridade = 1     
                cpu.processo.pcb.estado = 'Pronto'
                memoria_ram.adicionar_processo_pronto(cpu.processo)
                cpu.limpaCPU()

            if (estado == 'TerminouFase1'):
                cpu.processo.pcb.prioridade = 1
                memoria_ram.bloqueia_processo(cpu.processo)
                cpu.limpaCPU()

            if (estado == 'TerminouFase2'):
                memoria_ram.remove_processo(cpu.processo)
                cpu.limpaCPU()

            if (estado == "Executando"): #Continua exec
                print(f'Processo {cpu.processo.pcb.id} ainda executando. Etapa: {cpu.processo.etapa}')

            
    # executar processos dentro da cpu
        # situacao_atual = cpu.executar_processo(processo)
        # if (situacao_atual == "Acabou o processo"): # Processo.estado = "Executando" -> "Finalizado"
        #     ...
        # elif (situacao_atual == "Quantum finalizou"): # Dá um time-slacing e vai pra próxima fila ("Executando" -> "Pronto")
        #     ...

class MedioPrazo(Escalonador): # Medio Prazo
    def __init__(self, id):
        super(MedioPrazo, self).__init__(id)  # Herdando do escalonador

    # Memória RAM --> Memória Secundária.
    def swap_out(self, processo, ram, secundaria):  # Chama remover processo
        if (processo.pcb.estado == "Pronto"):
            secundaria[processo.disco].adicionar_processo_pronto_suspenso(processo)  # Pronto-suspenso
            processo.pcb.estado = 'Pronto-Suspenso'
            # printa que passa de pronto -> pronto-suspenso
            print(f'Processo de id: {processo.pcb.id} movido Pronto para Pronto-Suspenso\n')
            processo.pcb.prioridade = 1
        else:  # estado == Bloqueado
            secundaria[processo.disco].adicionar_processo_bloqueado_suspenso
            processo.pcb.estado = 'Bloqueado-Suspenso'
            print(f'Processo {processo.pcb.id} Bloqueado --> Bloqueado-Suspenso\n')
            processo.pcb.prioridade = 1

    # É preciso tirar o processo da lista de processos que estão na Memória Sececundária e jogá-lo pra lista da RAM
    # TODO: Fazer ser retornado um booleano para verificar se é possível
    def swap_in(self, processo, ram, secundaria) -> bool:  # Memória Secundária --> Memoria_RAM
        flag = True#Essa flag é de controle para o sucesso, pq pode ter limite na Memória, assim ele continua no 
        if (processo.pcb.estado == "Pronto-Suspenso"):
            processo.pcb.estado = "Pronto"
            processo.pcb.prioridade = 1
            flag = ram.adicionar_processo_pronto(processo)
            if(flag == False): # Checar a flag antes de remover da Mem. Sec.
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
        # Define a prioridade do processo, caso sofra time-slice p += 1, e sempre começa com 1 (fila de maior prioridade)
        
        # TODO: Guardar quanto tempo o processo gasta em cada fase
        # Quando acabar o tempo total em CPU, o processo terminou (só atualizar o tempo para o fim do processo quando ele estiver em CPU)
        self.etapa = 0
        self.pcb = PCB(gerar_id())

    # def enviar_memoria_primaria(self):
       # ...

class MemoriaRam:
    capacidade = 34359738368  # 32Gbytes == 32768 Mbytes
    memoria = [] # 2048Mb cada partição(particionamento fixo) ou seja terá 16 elementos
    
    espaco_livre = capacidade  # Começa com 32Gbytes livres
    # Instanciando as quatro filas de processos prontos para serem executados
    filas = [queue.Queue() for _ in range(4)] #filas de prontos
    bloqueados = []
    escalona = MedioPrazo('medio_prazo_id')

    def adicionar_processo_pronto(self, processo: Processo) -> bool:
        #if (self.espaco_livre - processo.tamanho) < 0:  # Caso não haja espaço na memória primária
            # Coloquei isso, caso implementemos uma função para colocar como pronto_suspenso e uma como bloqueado_suspenso
            #return self.escalonador_medio_prazo.swap_out(processo)
        
        if(len(self.memoria) == 16): 
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


        print(f'---------- Memória RAM ----------')
        for index, fila in enumerate(self.filas):
            print(f'Fila de Prontos {index + 1}')
            temp_list = list(fila.queue)
            for processo in temp_list:
                print(f'ID: {processo.pcb.id}, Prioridade: {processo.pcb.prioridade}, Estado: {processo.pcb.estado}')
        print()
        return True
    
        
    def bloqueia_processo(self, processo: Processo):
        if(len(self.memoria) < 16):
                self.bloqueados.append(processo)
                processo.pcb.estado = "Bloqueado"
                print(f'Processo de id: {processo.pcb.id} movido de Executando para {processo.pcb.estado}\n')
                print('Fila de Bloqueado:', self.bloqueados)
        else:
            self.escalona.swap_out(processo)
            print("Memória Cheia")
            
                

    def remove_processo(self, processo: Processo):
        self.memoria.remove(processo)
        print(f'Processo de id: {processo.pcb.id} terminou a execução\n')


    def processa_bloqueados(self):
        for processo in self.bloqueados:
            processo.ioEtapa += 1
            print(f'Processo {processo.pcb.id} está na fila de bloqueados')
            print(processo.ioEtapa)
            print(processo.io)
            print('--')
            if (processo.ioEtapa == processo.io):
                processo.ioEtapa = 0
                self.bloqueados.remove(processo)
                processo.pcb.estado = "Pronto"
                self.adicionar_processo_pronto(processo)
                

class MemoriaSecundaria:
    def __init__(self, identificador):
        self.id = identificador
        self.fila_suspensos = [] # Filas com processos pronto-suspensos
        self.bloqueados = [] # Fila com processos bloqueados (suspensos)

    def adicionar_processo_pronto_suspenso(self, processo: Processo):
        self.fila_suspensos.append(processo)

    def adicionar_processo_bloqueado_suspenso(self, processo: Processo):
        self.bloqueados.append(processo)
    # Aqui como não tem uma capacidade, basta tirar daqui o processo
    def remover_processo_pronto_suspenso(self, processo: Processo):
        self.fila_suspensos.remove(processo)

    def remover_processo_bloqueado_suspenso(self, processo: Processo):
        self.bloqueados.remove(processo)

class CPU: 
    #Política Feedback:
    #-Quantum == 3;
    #-Se um processo sofreu interrupção ele voltará para a 1 fila de processos prontos após o término da operação de E/S;
    #-Se um processo sofreu fatia de tempo ele irá para a próxima fila de prontos, caso alcance a última irá retornar para a primeira;
    def __init__(self, identificador):
        self.id = identificador #Identificador do número da  (processo.pcb.prioridade)
        self.clock = 0 #Contador de unidades de tempo de execução do processo atual
        self.processo = None
        self.executando = False

    def limpaCPU(self):
        self.clock = 0
        self.processo = None
        self.executando = False
    
    def adicionar_processo(self, processo: Processo):
        self.limpaCPU()
        self.processo = processo
                                                    # [p1,p2,p3]
    def executar_processo(self):# [ 1,2,4  ]   #chamar o despachante p/ exec
        self.executando = True

        if (self.processo.etapa == self.processo.f1): 
            return 'TerminouFase1'
        
        if (self.processo.etapa == (self.processo.f2 + self.processo.f1 + self.processo.io)):
            return 'TerminouFase2'
            
        if (self.clock == QUANTUM):
            print(f'Processo {self.processo.pcb.id} sofreu um Time-slicing\n')
            return 'QuantumMax'

        self.clock += 1
        self.processo.etapa += 1

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
    cpu1 = CPU('cpu1')
    cpu2 = CPU('cpu2')
    cpu3 = CPU('cpu3')
    cpu4 = CPU('cpu4')

    processos = deque()
    cont_n_arqs = 0
    # Leitura do arquivo com cada um dos processos
    with open('input.txt', 'r') as arquivo:
        for linha in arquivo:
            processo_linha = [x.strip() for x in linha.split(',')]
            processo = Processo(int(processo_linha[0]), int(processo_linha[1]), int(processo_linha[2]),  # e.g. 12,4,5,6,800,2
                                int(processo_linha[3]), int(processo_linha[4]), (processo_linha[5]))
            id = processo_linha[5]

            processo.pcb.estado = "Pronto-Suspenso"
            print(f'Processo de id: {processo.pcb.id} movido de Novo para {
                  processo.pcb.estado}\n')
            processos.append(processo)
            secundaria[id].adicionar_processo_pronto_suspenso(processo)#Está depois do print de troca mas da no mesmo
            cont_n_arqs +=1

    despachante = Despachante('teste')
    medioPrazo = MedioPrazo('medio_prazo_id')#Só iniciou ele
    despachangeAtivo = False

    processos_list = list(processos)  # Converte a fila em uma lista para iteração


    while True:#Ajeitar p/ o "clock"
        clock = input("")
        if clock == "":
            c_quantum += 1
            print('Quantum', c_quantum)
        else:
            print("Valor inválido")
            break

            #A cada clock, tenta alocar um processo inicial da memória secundária para a memória RAM. Se não conseguir, esse processo vai para o fim da fila.
        for processo in processos:
            if processo.chegada == c_quantum:
                sucesso = medioPrazo.swap_in(processo, ram, secundaria[processo.disco])
                if not sucesso:
                    # Se o swap_in falhar, coloca o processo de volta ao final da fila
                    processos.append(processo)
        
        despachante.Despacho(ram, cpu1)

        ram.processa_bloqueados()

if __name__ == '__main__':
    Computador()
