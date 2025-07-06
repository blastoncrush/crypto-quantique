from qiskit import QuantumCircuit, ClassicalRegister, transpile
from qiskit.circuit.library import QFT, RealAmplitudes
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram
from qiskit_aer import Aer
from random import randint
import math
from qiskit_ibm_runtime import QiskitRuntimeService, Session

n = 6
E = 2**n
num_qubits = 2*n + 4

def get_n():
    return n

def collision(result):
    l = list(result)
    for i in range(0, n-1):
        if l[i] != l[i+n+1]:
            return False
    return l[n] != l[2*n+2]

def generer_circuit(qc):
    qc.h(0)
    qc.h(n+2)
    qc.append(QFT(n), range(1, n+1))
    qc.append(QFT(n), range(n+3, 2*n+3))
    qc.cx(0,n+2)
    qc.h(0)
    qc.measure_all()
    return qc

def dcp(qc,t,r):
    # Création du simulateur
    simulator = Aer.get_backend('qasm_simulator')

    tries = 0
    successes = 0

    for _ in range(r):
        #print(f"Essai {_+1}/{r}")
        s = randint(0, E-1)
        for i in range(t):
            qc = generer_circuit(qc)
            transpiled_qc = transpile(qc, simulator)

            # Exécuter le circuit avec le circuit transpilé
            job = simulator.run(transpiled_qc)
            result = job.result()

            counts = result.get_counts(transpiled_qc)
            qubit = list(counts.keys())[0]
            if collision(qubit) and qubit[len(qubit)//2-1] == '1':
                #print(qubit[0]) # 0 => pair, 1 => impair
                #print(f"Trouvé en {i+1} essais")
                if int(qubit[0]) == s%2:
                    #print(x1, x2, s)
                    successes += 1
                    #qc.draw("mpl")
                    #plt.show()
                qc.reset(range(num_qubits))
                break
            else:
                qc.reset(range(num_qubits))
        
            tries += 1

            #fig = plot_histogram(counts)
            #fig.savefig("histogram.png")
        if not collision(qubit):
            if randint(0, 1) == s%2:
                successes += 1
                #print(f"Accuracy : {successes/r*100}%")
                #print(f"Nombre moyen d'essais : {tries/r}")
        
    return successes/r


