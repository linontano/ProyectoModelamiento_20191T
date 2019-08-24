
import numpy as np
import simpy as sp
import math
import random
import matplotlib.pyplot as plt

TOTAL_CLIENTES = 5000
LAMB1 = 3 #CADA LAMB1,2, U1,2 MINUTOS LLEGA/ATIENDE A UN PAQUETE
LAMB2 = 1.5
U1 = 10
U2 = 10
IMP = 1000
colaC1 = 0
SIZECOLA = 10
colaC2 = 0
SEMILLA = 30
NSERVIDORES = 10
t_sistema = 0
T_SIM = 500
numRecursos = np.zeros(TOTAL_CLIENTES*5)
tiempoRecursos = np.zeros(TOTAL_CLIENTES*5) #int(T_SIM*(1/LAMB1)
indexRecursos = 0

def sourceC2(env, totalClientes, tiempoArribo, servidores):
    for i in range(totalClientes):
    #i=0
    #while(True):
        i+=1
        R = random.random()
        t_arribo = -tiempoArribo * math.log(R)
        yield env.timeout(t_arribo)
        env.process(serviceC2(env, "PaqueteC2 %d" % i, servidores, 1, U2))


def serviceC2(env, name, servidor, prio, tiempoServicio):
    global colaC1
    global colaC2
    global SIZECOLA
    global t_sistema
    global indexRecursos

    t_arribo = env.now
    print("------> El paquete %s ha llegado en el minuto %.2f" % (name, t_arribo))
    servidoresDisponibles = servidor.capacity - servidor.count
    print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)
    if colaC2 >= SIZECOLA:
        print("xxxxxxxxxx El paquete %s no entro en la cola C1 en el minuto %.2f" % (name, env.now))
    else:
        colaC2 += 1
        # --------------------datos estadisticos antes-----------------------------------------------------#
        numRecursos[indexRecursos] = servidor.count
        tiempoRecursos[indexRecursos] = env.now
        indexRecursos += 1
        # ------------------------------------------------------------------------------------------------#
        with servidor.request(priority=prio) as req:
            yield req
            t_espera = env.now - t_arribo
            # --------------------datos estadisticos despues-----------------------------------------------------#
            numRecursos[indexRecursos] = servidor.count
            tiempoRecursos[indexRecursos] = env.now
            indexRecursos += 1
            # ------------------------------------------------------------------------------------------------#
            print("****** El paquete %s tiene ancho de banda asignado despues de %.2f minutos" % (name, t_espera))
            colaC2 -=1
            print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)
            R = random.random()
            t_servicio = -tiempoServicio*math.log(R)
            yield env.timeout(t_servicio)
            t_salida = env.now
            print("<------- El paquete %s deja el recurso en el minuto %.2f" % (name, t_salida))
            t_sistema += (t_salida - t_arribo)


print("*************SIMULACION****************")

random.seed(SEMILLA)
env = sp.Environment()
servidores = sp.PriorityResource(env, NSERVIDORES)
env.process(sourceC2(env, TOTAL_CLIENTES, LAMB2, servidores))
env.run(until=T_SIM)

print("***************fin simulacion***************************")
tiempoPromedio = t_sistema / TOTAL_CLIENTES
print("Tiempo promedio de un cliente en el sistema: %d" % tiempoPromedio)

for i in range(tiempoRecursos.size):
    if tiempoRecursos[i] <= 0:
        cut = i
        break
print(tiempoRecursos[:indexRecursos-1]);
plt.plot(tiempoRecursos[:cut-1], numRecursos[:cut-1])
plt.show()

