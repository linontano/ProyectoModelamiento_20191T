import numpy as np
import simpy as sp
import math
import random
import matplotlib.pyplot as plt
from matplotlib import rc
import seaborn as sns
import pandas as pd
import statsmodels.api as sm
import statsmodels.stats.diagnostic as smd
import statsmodels.graphics.tsaplots as smp



SEMILLA = 30
TOTAL_CLIENTES = 5000
#CADA LAMB1,2, U1,2 MINUTOS LLEGA/ATIENDE A UN PAQUETE
LAMB = np.array([1, 0.27])
U = np.array([1, 2])
IMP = 5
SIZECOLA = 20
NSERVIDORES = 10
T_SIM = 250
colaC1 = 0
colaC2 = 0
t_sistema = 0
numRejected = 0 #numero de rechazos, sea por impaciencia o max Cola
numServed = 0
L = 50
ALPHA = 0.9326
W = 700
CARGA = "Alta"

numRecursos = np.zeros(TOTAL_CLIENTES*10)
tiempoRecursos = np.zeros(TOTAL_CLIENTES*10) #int(T_SIM*(1/LAMB1)
indexRecursos = 0

#Genera los paquetes de clase 1, llamando al servicio de ese tipo.
def sourceC1(env, totalClientes, tiempoArribo, servidores):
    for i in range(totalClientes):
        R = random.random()
        t_arribo = -tiempoArribo * math.log(R)
        yield env.timeout(t_arribo)
        env.process(serviceC1(env, "PaqueteC1 %d" % (i+1), servidores, 1, U[0]))

#Genera los paquetes de clase 2, llamando al servicio de ese tipo.
def sourceC2(env, totalClientes, tiempoArribo, servidores):
    for i in range(totalClientes):
        R = random.random()
        t_arribo = -tiempoArribo * math.log(R)
        yield env.timeout(t_arribo)
        env.process(serviceC2(env, "PaqueteC2 %d" % (i+1), servidores, 0, U[1]))

#Realiza el servicio de atencion cuando llega un paquete tipo 1, presenta impaciencia y menor prioridad
def serviceC1(env, name, servidor, prio, tiempoServicio):
    global colaC1
    global colaC2
    global SIZECOLA
    global t_sistema
    global indexRecursos
    global numRejected
    global numServed

    t_arribo = env.now
    print("------> El paquete %s ha llegado en el minuto %.2f" % (name, t_arribo))
    colaC1 += 1
    servidoresDisponibles = servidor.capacity - servidor.count
    if colaC1 > SIZECOLA:
        print("xxxxxxxxxx El paquete %s no entro en la cola C1 en el minuto %.2f" % (name, env.now))
        colaC1 -= 1
        print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)
        numRejected += 1
    else:
        print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)
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
                colaC1 -= 1
                R = random.random()
                t_servicio = -tiempoServicio*math.log(R)
                servidoresDisponibles = servidor.capacity - servidor.count
                print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)
                yield env.timeout(t_servicio)
                t_salida = env.now
                print("<------- El paquete %s deja el recurso en el minuto %.2f" % (name, t_salida))
                numServed += 1

            else:
                t_salida = env.now
                print("<<######## El paquete %s se canso y se fue en el minuto %.2f, despues de %.2f minutos" % (name, t_salida, t_salida - t_arribo))
                colaC1 -= 1
                numRejected += 1

            t_sistema += (t_salida - t_arribo)
        # --------------------datos estadisticos despues-----------------------------------------------------#
        numRecursos[indexRecursos] = servidor.count
        tiempoRecursos[indexRecursos] = t_salida
        indexRecursos += 1
        # ------------------------------------------------------------------------------------------------#
        servidoresDisponibles = servidor.capacity - servidor.count
        print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)

#Realiza el servicio de atencion cuando llega un paquete tipo 2, tiene mayor prioridad
def serviceC2(env, name, servidor, prio, tiempoServicio):
    global colaC1
    global colaC2
    global SIZECOLA
    global t_sistema
    global indexRecursos
    global numRejected
    global numServed

    t_arribo = env.now
    print("------> El paquete %s ha llegado en el minuto %.2f" % (name, t_arribo))
    servidoresDisponibles = servidor.capacity - servidor.count
    colaC2 += 1
    if colaC2 > SIZECOLA:
        print("xxxxxxxxxx El paquete %s no entro en la cola C2 en el minuto %.2f" % (name, env.now))
        numRejected += 1
        colaC2 -= 1
        print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)
    else:
        print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)
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
            servidoresDisponibles = servidor.capacity - servidor.count
            print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)
            R = random.random()
            t_servicio = -tiempoServicio*math.log(R)
            yield env.timeout(t_servicio)
            t_salida = env.now
            print("<------- El paquete %s deja el recurso en el minuto %.2f" % (name, t_salida))
            numServed += 1

            t_sistema += (t_salida - t_arribo)
        # --------------------datos estadisticos despues-----------------------------------------------------#
        numRecursos[indexRecursos] = servidor.count
        tiempoRecursos[indexRecursos] = t_salida
        indexRecursos += 1
        # ------------------------------------------------------------------------------------------------#
        servidoresDisponibles = servidor.capacity - servidor.count
        print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidoresDisponibles)

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

print("*************SIMULACION****************")

random.seed(SEMILLA)
env = sp.Environment()
servidores = sp.PriorityResource(env, NSERVIDORES)
env.process(sourceC1(env, TOTAL_CLIENTES, LAMB[0], servidores))
env.process(sourceC2(env, TOTAL_CLIENTES, LAMB[1], servidores))
env.run(until=T_SIM)

print("***************fin simulacion***************************")
tiempoPromedio = t_sistema / TOTAL_CLIENTES
print("Tiempo promedio de un cliente en el sistema: %d" % tiempoPromedio)
cut = 0

print(tiempoRecursos[:indexRecursos-1])
npromedio = np.sum(numRecursos[:indexRecursos-1])/(indexRecursos-1)
movil = mediaMovil(W, numRecursos, indexRecursos)

boolArr1 =(tiempoRecursos >= L - 1)
boolArr2 = (tiempoRecursos <L)
boolArr = boolArr1*boolArr2
ind = 0
while ind < TOTAL_CLIENTES*2:
    if boolArr[ind]:
        break
    ind += 1
print(ind)
npromedio = np.sum(numRecursos[ind:indexRecursos-1])/(indexRecursos-ind)
sumaRecursos = np.sum(numRecursos)
print("Valor01: %d \t Valor02: %d" % (sumaRecursos, numServed))
print("Rechazos: %d " % numRejected)
Aoff = U[0]/LAMB[0] + U[1]/LAMB[1]
Acar = Aoff*(1-numRejected/numServed)
print(Aoff)
print("Average: %.2f \t Theorical: %.2f" % (Acar, Aoff))
outY = numRecursos[ind:indexRecursos]
outX = tiempoRecursos[ind:indexRecursos]
shiftY = ALPHA*(outY-Acar)+Acar
zt = outY - shiftY
#zt = outY[1:] - 0.728*outY[:len(outY)-1]

# GRAFICAS ####################################################################################
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
smp.plot_pacf(outY, lags=50)
plt.figure()
plt.subplots_adjust(hspace=0.5)
plt.subplot(411)
plt.ylim(0,10)
plt.title(r"\textbf{Carga %s}" % CARGA)
plt.ylabel("No. Recursos")
plt.grid(True)
plt.plot(tiempoRecursos[:indexRecursos], numRecursos[:indexRecursos], label='Serie Temporal')
plt.plot(tiempoRecursos[:indexRecursos], np.ones(indexRecursos)*npromedio, 'g--')
plt.plot(tiempoRecursos[:movil.size], movil, 'r', label='Media Movil')
plt.legend(loc=1)
plt.subplot(412)
plt.ylim(0,10)
plt.title(r"\textbf{Carga %s}" % CARGA)
plt.plot(tiempoRecursos[ind: indexRecursos], numRecursos[ind: indexRecursos], 'y', label='Serie Temporal')
plt.plot(tiempoRecursos[ind:indexRecursos], np.ones(indexRecursos-ind)*Aoff, 'g', label='Promedio')
plt.plot(tiempoRecursos[ind:indexRecursos], np.ones(indexRecursos-ind)*Acar, 'r--', label='Con Rechazo')
plt.ylabel("No. Recursos")
plt.legend(loc=1)
plt.grid(True)
plt.subplot(413)
plt.ylim(0,10)
plt.title(r"\textbf{Carga %s}" % CARGA)
plt.grid(True)
plt.plot(outX, outY,  'g', label='Serie Temporal')
plt.plot(outX[1:], shiftY[1:], 'r', label= 'Estimacion AR')
plt.ylabel("No. Recursos")
plt.legend(loc=1)
plt.subplot(414)
plt.title(r"\textbf{Carga %s}" % CARGA)
plt.ylim(1.5,-1.5)
plt.scatter(outX, zt)
plt.grid(True)

plt.show()

#res = pd.DataFrame(data=np.column_stack((outX, outY)), columns=['Time']+['Servers'])
#df = sns.pairplot(res)
#plt.show()
#print(res.head())
#print(res.describe())
