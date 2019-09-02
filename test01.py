import numpy as np
import simpy as sp
import math
import random
import matplotlib.pyplot as plt

total_clientes = 100
lamb1 = 1
lamb2 = 1
u1 = 1
u2 = 1
imp = 1
colaC1 = 0
SIZECOLA = 10
colaC2 = 0
semilla = 30
nservidores = 50
d1 = 1
d2 = 2 * d1
tiempoSim = 50
tiempoSistema = 0

numRecursos = np.zeros(total_clientes*5)
tiempoRecursos = np.zeros(total_clientes*5)
indexRecursos = 0




def servicioC2(env, name, servidor, wait, prio):
    global colaC2
    global colaC1
    global SIZECOLA
    global u2
    global d2
    global indexRecursos
    yield env.timeout(wait)
    t_arribo = env.now

    print("%s llego a la peluqueria en el minuto %.2f" % (name, t_arribo))
    colaC2 += d2

    if colaC2 > sizeCola:
        print("+++++++ %s no entro en la cola C2 en el minuto %.2f" % (name, env.now))
        colaC2 -= d2
        print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)
    else:
        with servidor.request(priority=prio) as request:
            R = random.random()
            print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)

            yield request
            # --------------------datos estadisticos ---------------------------------------------------------#
            numRecursos[indexRecursos] = servidor.count
            tiempoRecursos[indexRecursos] = env.now
            indexRecursos += 1
            # ------------------------------------------------------------------------------------------------#

            t_servicio = -u2 * math.log(R)
            print("******* %s es atendido en el minuto %.2f" % (name, env.now))
            colaC2 -= d2
            print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)

            yield env.timeout(t_servicio)
            print("------- %s se va en el minuto %.2f" % (name, env.now))


def servicioC1(env, name, servidor, wait, prio):
    global colaC1
    global colaC2
    global SIZECOLA
    global u1
    global imp
    global d1
    global indexRecursos
    global tiempoSistema
    global number

    yield env.timeout(wait)
    number += 1
    t_arribo = env.now
    R = random.random()
    t_impaciencia = -imp * math.log(R)

    print("%s %d llego a la peluqueria en el minuto %.2f" % (name, number, t_arribo))
    colaC1 += d1
    print("%s %d puede esperar hasta el minuto %.2f" % (name, number, t_impaciencia + t_arribo))
    if colaC2 > sizeCola:
        print("+++++++ %s %d no entro en la cola C2 en el minuto %.2f" % (name, number, env.now))
        colaC2 -= d1
        print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)
    else:
        # --------------------datos estadisticos antes-----------------------------------------------------#
        numRecursos[indexRecursos] = servidor.count
        tiempoRecursos[indexRecursos] = env.now
        indexRecursos += 1
        # ------------------------------------------------------------------------------------------------#
        with servidor.request(priority=prio) as request:
            colaC1 += d1
            print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)
            yield request | env.timeout(t_impaciencia)

            if not request.triggered:
                print("###### %s %d se canso y se fue en el minuto %.2f" % (name, number, env.now))
                colaC1 -= d1
                print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)
                # --------------------datos estadisticos antes-----------------------------------------------------#
                numRecursos[indexRecursos] = servidor.count
                tiempoRecursos[indexRecursos] = env.now
                indexRecursos += 1
                # ------------------------------------------------------------------------------------------------#
                tiempoSistema += (env.now - t_arribo)
            else:
                # --------------------datos estadisticos ---------------------------------------------------------#
                numRecursos[indexRecursos] = servidor.count
                tiempoRecursos[indexRecursos] = env.now
                indexRecursos += 1
                # ------------------------------------------------------------------------------------------------#
                t_servicio = -u1 * math.log(R)
                print("****** %s %d es atendido en el minuto %.2f" % (name, number, env.now))
                colaC1 -= d1
                print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)
                yield env.timeout(t_servicio)
                print("------- %s %d se va en el minuto %.2f" % (name, number, env.now))
                tiempoSistema += (env.now - t_arribo)


def principal(env, servidor):
    number = 0
    for i in range(total_clientes):
        R = random.random()
        llegadac1 = -lamb1 * math.log(R)
        llegadac2 = -lamb2 * math.log(R)

        env.process(servicioC1(env, 'ClienteC1', servidor, wait=llegadac1, prio=1))
        #env.process(servicioC2(env, 'ClienteC2 %d' % i, servidor, wait=llegadac2, prio=0))


print("*************SIMULACION****************")
random.seed(semilla)
env = sp.Environment()
servidores = sp.PriorityResource(env, nservidores)
env.process(principal(env, servidores))



# for i in range(total_clientes):
#     R = random.random()
#     llegadac1 = -lamb1 * math.log(R)
#     #llegadac2 = -lamb2 * math.log(R)
#     i += 1
#     env.process(servicioC1(env, 'Coneximport numpy as np
import random as r
import simpy as sp
import math
r.seed(30)


def servicioC2F(env, name, servidor, wait):

    with servidor.request() as request:
        yield request
        print("servDisponibles: ", servidor.capacity - servidor.count)
        print("******* %s es atendido en el minuto %.2f" % (name, env.now))

        yield env.timeout(wait)
        print("------- %s se va en el minuto %.2f" % (name, env.now))
    print("servDisponibles: ", servidor.capacity - servidor.count)

def servicioC2(env, name, servidor, wait):
    yield env.timeout(wait)
    t_arribo = env.now

    print("%s llego a la peluqueria en el minuto %.2f" % (name, t_arribo))



    with servidor.request() as request:
        while (servidor.capacity - servidor.count) < 2:
            # next = env.peek()
            # if next != sp.core.Infinity:
            print("/////////%s CAPACIDAD NO SUFICIENTE, SE ENCOLA. %2.f" % (name, env.now))
            env.step(False)

        yield request
        t_servicio = -3 * math.log(R)

        yield(env.process(servicioC2F(env, name, servidor, wait=t_servicio)))
        print("CONFIRMADO------- %s se fue en el minuto %.2f" % (name, env.now))
    print("servDisponibles: ", servidor.import numpy as np
import random as r
import simpy as sp
import math
r.seed(30)


def servicioC2F(env, name, servidor, wait):

    with servidor.request() as request:
        yield request
        print("servDisponibles: ", servidor.capacity - servidor.count)
        print("******* %s es atendido en el minuto %.2f" % (name, env.now))

        yield env.timeout(wait)
        print("------- %s se va en el minuto %.2f" % (name, env.now))
    print("servDisponibles: ", servidor.capacity - servidor.count)

def servicioC2(env, name, servidor, wait):
    yield env.timeout(wait)
    t_arribo = env.now

    print("%s llego a la peluqueria en el minuto %.2f" % (name, t_arribo))



    with servidor.request() as request:
        while (servidor.capacity - servidor.count) < 2:
            # next = env.peek()
            # if next != sp.core.Infinity:
            print("/////////%s CAPACIDAD NO SUFICIENTE, SE ENCOLA. %2.f" % (name, env.now))
            env.step(False)

        yield request
        t_servicio = -3 * math.log(R)

        yield(env.process(servicioC2F(env, name, servidor, wait=t_servicio)))
        print("CONFIRMADO------- %s se fue en el minuto %.2f" % (name, env.now))
    print("servDisponibles: ", servidor.capacity - servidor.count)

R = r.random()
env = sp.Environment()
servidores = sp.PriorityResource(env, 5)
for i in range(5):
    R = r.random()
    llegadac1 = -2 * math.log(R)
    i += 1
    env.process(servicioC2(env, 'ConexionC1 %d' % i, servidores, wait=llegadac1))

env.run()
capacity - servidor.count()

R = r.random()
env = sp.Environment()
servidores = sp.PriorityResource(env, 5)
for i in range(5):
    R = r.random()
    llegadac1 = -2 * math.log(R)
    i += 1
    env.process(servicioC2(env, 'ConexionC1 %d' % i, servidores, wait=llegadac1))

env.run()
ionC1 %d' % i, servidores, wait=llegadac1, prio=1))
#     #env.process(servicioC2(env, 'ConexionC2 %d' % i, servidores, wait=llegadac2, prio=0))
env.run()
print("***************fin simulacion***************************")
tiempoPromedio = tiempoSistema/total_clientes
print("Tiempo promedio de un cliente en el sistema: %d" %tiempoPromedio)

for i in range(tiempoRecursos.size):
    if tiempoRecursos[i] <= 0:
        cut = i
        break

plt.plot(tiempoRecursos[:cut-1], numRecursos[:cut-1])
plt.show()

