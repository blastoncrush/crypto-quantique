from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit.circuit.library import QFT
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit_aer import Aer
from random import randint
import math

n = 2
E = 2**n

def collision(result):
    l = list(result)
    m = len(l)//2
    for i in range(m-1, m-n, -1):
        if l[i] != l[i+m]:
            return False
    return True

def preparation_etats(qc, q1, q2): # chaque qubit est un tuple de deux listes de 0 ou 1, tel que q = |0>|q1[0]> + |1>|q1[1]> 
    n = len(q1[0])
    for i in range(n):
        if (q1[0][i], q1[1][i]) == (1, 1):
            qc.x(i+1)
        elif (q1[0][i], q1[1][i]) == (0, 1):
            qc.cx(0, i+1)
        elif (q1[0][i], q1[1][i]) == (1, 0):
            qc.x(i+1)
            qc.cx(0, i+1)
    
    m = n + 1
    for i in range(n):
        if (q2[0][i], q2[1][i]) == (1, 1):
            qc.x(i+1+m)
        elif (q2[0][i], q2[1][i]) == (0, 1):
            qc.cx(m, i+1+m)
        elif (q2[0][i], q2[1][i]) == (1, 0):
            qc.x(i+1+m)
            qc.cx(m, i+1+m)
    
    return qc

def int_to_bin(x, n):
    res = [int(c) for c in list(str(bin(x)[2:]))]
    if len(res) < n:
        res = [0] * (n - len(res)) + res
    return res

def generer_entrees(x, s, E):
    res = (int_to_bin(x, n), int_to_bin((x+s)%E, n))
    return res

def generer_circuit(psi, E):
    qc = QuantumCircuit(2*n + 2)
    cr = ClassicalRegister(2*n + 2)
    qc.add_register(cr)
    qc.h(0)
    qc.h(n+1)
    qc = preparation_etats(qc, psi[0], psi[1])
    qc.append(QFT(n), range(1, n+1))
    qc.append(QFT(n), range(n+2, 2*n+2))
    qc.cx(0,n+1)
    qc.h(0)
    qc.measure(range(2*n+2), cr[0:2*n+2])
    return qc


# Création du simulateur
simulator = Aer.get_backend('qasm_simulator')

# Transpiler le circuit pour décomposer les instructions non supportées (ex: QFT)
nbr_shot = 1

t = 1000 # Nombre d'essais
r = 10 # Nombre de répétitions

tries = 0
successes = 0

for _ in range(r):
    s = randint(1, E-1)
    for i in range(t):
        x1 = randint(0, E-1)
        psi1 = generer_entrees(x1, s, E)
        x2 = randint(0, E-1)
        psi2 = generer_entrees(x2, s, E)

        qc = generer_circuit((psi1, psi2), E)
        transpiled_qc = transpile(qc, simulator)

        # Exécuter le circuit avec le circuit transpilé
        job = simulator.run(transpiled_qc, shots=nbr_shot)
        result = job.result()

        counts = result.get_counts(transpiled_qc)
        qubit = list(counts.keys())[0]
        if collision(qubit) and qubit[len(qubit)//2] == '1':
            #print(qubit[0]) # 0 => pair, 1 => impair
            #print(f"Trouvé en {i+1} essais")
            if int(qubit[0]) == s%2:
                successes += 1
            break
        else:
            qc.reset(range(2*n+2))
        
        tries += 1

        #fig = plot_histogram(counts)
        #fig.savefig("histogram.png")

qc.draw("mpl")
print(qubit)
plt.show()
print(f"Accuracy : {successes/r*100}%")
print(f"Nombre moyen d'essais : {tries/r}")

