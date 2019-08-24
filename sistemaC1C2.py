
import numpy as np
import simpy as sp
import math
import random
import matplotlib.pyplot as plt

TOTAL_CLIENTES = 10000
LAMB1 = 1 #CADA LAMB1,2, U1,2 MINUTOS LLEGA/ATIENDE A UN PAQUETE
LAMB2 = 3
U1 = 8
U2 = 5
IMP = 18
colaC1 = 0
SIZECOLA = 15
colaC2 = 0
SEMILLA = 30
NSERVIDORES = 10
t_sistema = 0
T_SIM = 500
numRecursos = np.zeros(TOTAL_CLIENTES*5)
tiempoRecursos = np.zeros(TOTAL_CLIENTES*5) #int(T_SIM*(1/LAMB1)
indexRecursos = 0


def sourceC1(env, totalClientes, tiempoArribo, servidores):
    for i in range(totalClientes):
        R = random.random()
        t_arribo = -tiempoArribo * math.log(R)
        yield env.timeout(t_arribo)
        env.process(serviceC1(env, "PaqueteC1 %d" % (i+1), servidores, 1, U1))



def sourceC2(env, totalClientes, tiempoArribo, servidores):
    for i in range(totalClientes):
        R = random.random()
        t_arribo = -tiempoArribo * math.log(R)
        yield env.timeout(t_arribo)
        env.process(serviceC2(env, "PaqueteC2 %d" % (i+1), servidores, 1, U2))

def mediaMovil (w, arreglo, size):
    mediaMovil = np.zeros(size - w)
    for i in range(size - w):
        if i <= w-1:
            suma = 0
            for s in range(-(i-1), i-1, 1):
                suma += arreglo[i+s]
            mediaMovil[i] = suma/(2*i-1)
        if i > w-1:
            suma = 0
            for s in range(-w, w, 1):
                suma += arreglo[i + s]
            mediaMovil[i] = suma/(2*w+1)

    return mediaMovil

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

            if req in results:
                # --------------------datos estadisticos despues-----------------------------------------------------#
                numRecursos[indexRecursos] = servidor.count
                tiempoRecursos[indexRecursos] = env.now
                indexRecursos += 1
                # ------------------------------------------------------------------------------------------------#
                t_espera = env.now - t_arribo
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
env.process(sourceC1(env, TOTAL_CLIENTES, LAMB1, servidores))
env.process(sourceC2(env, TOTAL_CLIENTES, LAMB2, servidores))
env.run(until=T_SIM)

print("***************fin simulacion***************************")
tiempoPromedio = t_sistema / TOTAL_CLIENTES
print("Tiempo promedio de un cliente en el sistema: %d" % tiempoPromedio)
cut = 0

print(tiempoRecursos[:indexRecursos-1])
npromedio = np.sum(numRecursos[:indexRecursos-1])/(indexRecursos-1)
movil = mediaMovil(500, numRecursos, indexRecursos)



plt.figure()

plt.subplot(311)
plt.ylabel("No. Recursos")
plt.grid(True)
plt.plot(tiempoRecursos[:indexRecursos], numRecursos[:indexRecursos], tiempoRecursos[:indexRecursos], np.ones(indexRecursos)*npromedio, 'g--')
plt.subplot(312)
plt.ylabel("Media Móvil")
plt.grid(True)
plt.plot(tiempoRecursos[:movil.size], movil, 'r')


plt.subplot(313)
boolArr1 =(tiempoRecursos >= 49)
boolArr2 = (tiempoRecursos <50)
boolArr = boolArr1*boolArr2
ind = 0
while ind < 5000:
    if boolArr[ind]:
        break
    ind += 1
print(ind)
npromedio = np.sum(numRecursos[ind:indexRecursos-1])/(indexRecursos-ind)
plt.plot(tiempoRecursos[ind: indexRecursos], numRecursos[ind: indexRecursos], 'y',tiempoRecursos[ind: indexRecursos], np.ones(indexRecursos-ind)*npromedio, 'g--')
plt.ylabel("No. Recursos")
plt.grid(True)
plt.show()

