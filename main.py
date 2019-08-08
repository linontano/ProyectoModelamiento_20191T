import random
import math
import simpy
semilla = 30
num_peluqueros = 1
tiempo_corte_min = 15
tiempo_corte_max = 30
t_llegadas = 20
tiempo_simulacion = 120
total_clientes = 5

te = 0.0
dt = 0.0
fin = 0.0

def cortar(cliente):
    global dt
    R = random.random()
    tiempo = tiempo_corte_max - tiempo_corte_min
    tiempo_corte = tiempo_corte_min + (tiempo*R) # Distribucion uniforme
    yield env.timeout(tiempo_corte)
    print("\o/ Corte LISTO a %s en %.2f minutos" %(cliente, tiempo_corte))
    dt = dt + tiempo_corte


def cliente (env, name, personal):
    global te
    global fin
    llega = env.now
    print ("---> %s llego a la peluqueria en minuto %.2f" % (name, llega))
    with personal.request() as request:
        yield request
        pasa = env.now
        espera = pasa - llega
        te = te + espera
        print ("**** %s pasa con el peluquero en minuto %.2f habiendo esperado %.2f" % (name, pasa, espera))
        yield env.process(cortar(name))
        deja = env.now
        print ("<--- %s deja peluqueria en minuto %.2f" % (name, deja))
        fin = deja


def principal (env, personal):
    llegada = 0
    i = 0
    for i in range(total_clientes):
        R = random.random()
        llegada = -t_llegadas*math.log(R)
        yield env.timeout(llegada)
        i +=1
        env.process(cliente(env, 'Cliente %d' % i, personal))


print("----------------------simulacion----------------------")
random.seed(semilla)
env = simpy.Environment()
personal = simpy.Resource(env, num_peluqueros)
env.process(principal(env, personal))
env.run()
print("\n-----------------------------------------------------")
print("\nIndicadores Obtenidos")

lpc = te / fin
print ("\nLongitud promedio de la cola: %.2f" % lpc)
tep = te / total_clientes
print ("Tiempo de espera promedio = %.2f" % tep)
upi = (dt / fin) / num_peluqueros
print ("Uso promedio de la instalacion = %.2f" % upi)
print ("\n---------------------------------------------------------------------")