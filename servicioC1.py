
import numpy as np
import simpy as sp
import math
import random
import matplotlib.pyplot as plt

TOTAL_CLIENTES = 50
LAMB1 = 3 #CADA LAMB1,2, U1,2 MINUTOS LLEGA/ATIENDE A UN PAQUETE
LAMB2 = 1
U1 = 10
U2 = 1
IMP = 1000
colaC1 = 0
SIZECOLA = 10
colaC2 = 0
SEMILLA = 30
NSERVIDORES = 10
t_sistema = 0
T_SIM = 200
numRecursos = np.zeros(int(T_SIM*(1/LAMB1)*5))
tiempoRecursos = np.zeros(int(T_SIM*(1/LAMB1)*5))
indexRecursos = 0

def sourceC1(env, totalClientes, tiempoArribo, servidores):
    #for i in range(totalClientes):
    i=0
    while(True):
        i+=1
        R = random.random()
        t_arribo = -tiempoArribo * math.log(R)
        yield env.timeout(t_arribo)
        env.process(serviceC1(env, "PaqueteC1 %d" % i, servidores, 1, U1))


def serviceC1(env, name, servidor, prio, tiempoServicio):
    global colaC1
    global colaC2
    global SIZECOLA
    global t_sistema
    global indexRecursos

    t_arribo = env.now
    print("------> El paquete %s ha llegado en el minuto %.2f" % (name, t_arribo))
    servidoresDisponibles = servidor.capacity - servidor.count
    print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)
    if colaC1 >= SIZECOLA:
        print("xxxxxxxxxx El paquete %s no entro en la cola C1 en el minuto %.2f" % (name, env.now))
    else:
        colaC1 += 1
        # --------------------datos estadisticos antes-----------------------------------------------------#
        numRecursos[indexRecursos] = servidor.count
        tiempoRecursos[indexRecursos] = env.now
        indexRecursos += 1
        # ------------------------------------------------------------------------------------------------#
        with servidor.request(priority=prio) as req:
            R = random.random()
            t_impaciencia = -IMP*math.log(R)
            results = yield req | env.timeout(t_impaciencia)
            t_espera = env.now - t_arribo
            if req in results:
                # --------------------datos estadisticos despues-----------------------------------------------------#
                numRecursos[indexRecursos] = servidor.count
                tiempoRecursos[indexRecursos] = env.now
                indexRecursos += 1
                # ------------------------------------------------------------------------------------------------#
                print("****** El paquete %s tiene ancho de banda asignado despues de %.2f minutos" % (name, t_espera))
                colaC1 -=1
                print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)
                R = random.random()
                t_servicio = -tiempoServicio*math.log(R)
                yield env.timeout(t_servicio)
                t_salida = env.now
                print("<------- El paquete %s deja el recurso en el minuto %.2f" % (name, t_salida))

            else:
                t_salida = env.now
                print("<<######## El paquete %s se canso y se fue en el minuto %.2f" % (name, t_salida))
                colaC1 -= 1
                print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)

            t_sistema += (t_salida - t_arribo)


print("*************SIMULACION****************")

random.seed(SEMILLA)
env = sp.Environment()
servidores = sp.PriorityResource(env, NSERVIDORES)
env.process(sourceC1(env, TOTAL_CLIENTES, LAMB1, servidores))
env.run(until=T_SIM)

print("***************fin simulacion***************************")
#tiempoPromedio = t_sistema / TOTAL_CLIENTES
#print("Tiempo promedio de un cliente en el sistema: %d" % tiempoPromedio)

for i in range(tiempoRecursos.size):
    if tiempoRecursos[i] <= 0:
        cut = i
        break
print(tiempoRecursos);
plt.plot(tiempoRecursos[:cut-1], numRecursos[:cut-1])
plt.show()

