import numpy as np
import simpy as sp
import math
total_clientes=100
colaC1 = 0;
colaC2 = 0;

def servicioC2(env, name, servidor,wait,prio):
    global colaC2
    global colaC1
    yield env.timeout(wait)
    t_arribo = env.now
    maxCola = 3

    print("%s llego a la peluqueria en el minuto %.2f"%(name, t_arribo))
    colaC2 += 1

    if colaC2 > maxCola:
        print("+++++++ %s no entro en la cola C2 en el minuto %.2f" % (name, env.now))
        colaC2 -= 1
        print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)
    else:
        with servidor.request(priority=prio) as request:
            print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)
            yield request
            t_servicio = np.random.exponential(1 / 2) * 10
            print("******* %s es atendido en el minuto %.2f" % (name, env.now))
            colaC2 -= 1
            print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)
            yield env.timeout(t_servicio)
            print("------- %s se va en el minuto %.2f" % (name, env.now))


def servicioC1(env, name, servidor,wait,prio):
    global colaC1
    global colaC2
    yield env.timeout(wait)
    t_arribo = env.now
    t_impaciencia= np.random.exponential(1/3)*10

    print("%s llego a la peluqueria en el minuto %.2f"%(name, t_arribo))
    print("%s puede esperar hasta el minuto %.2f" % (name, t_impaciencia + t_arribo))
    with servidor.request(priority=prio) as request:
        colaC1 += 1
        print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)
        yield request | env.timeout(t_impaciencia)
        if not request.triggered:
            print("###### %s se canso y se fue en el minuto %.2f" % (name, env.now))
            colaC1 -= 1
            print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)
        else:
            t_servicio = np.random.exponential(1 / 2) * 10
            print("****** %s es atendido en el minuto %.2f" % (name, env.now))
            colaC1 -= 1
            print("QC2: ", colaC2, "QC1: ", colaC1, "servDisponibles: ", servidor.capacity - servidor.count)
            yield env.timeout(t_servicio)
            print("------- %s se va en el minuto %.2f" % (name, env.now))

def principal (env, servidor):
    for i in range(total_clientes):
        llegadac1 = np.random.exponential(1)*5
        llegadac2 = np.random.exponential(1)*4
        i +=1
        env.process(servicioC1(env, 'ClienteC1 %d' % i, servidor, wait=llegadac1, prio=1))
        env.process(servicioC2(env, 'ClienteC2 %d' % i, servidor, wait=llegadac2, prio=0))

print("*************SIMULACION****************")
env = sp.Environment()
servidores = sp.PriorityResource(env, 20)
#env.process(principal(env, servidores))
for i in range(total_clientes):
    llegadac1 = np.random.exponential(1) * 5
    llegadac2 = np.random.exponential(1) * 4
    i += 1
    env.process(servicioC1(env, 'ClienteC1 %d' % i, servidores, wait=llegadac1, prio=1))
    env.process(servicioC2(env, 'ClienteC2 %d' % i, servidores, wait=llegadac2, prio=0))
env.run()
print("***************fin simulacion***************************")