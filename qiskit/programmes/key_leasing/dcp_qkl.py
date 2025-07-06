from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFT
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, Session
from qiskit_ibm_runtime import SamplerV2 as Sampler
from random import randint
import numpy as np
from qiskit_aer import Aer
import matplotlib.pyplot as plt
from logic import *
import keyleasing
import classical
from dcp import *
import os

n = get_n()         # taille des vecteurs secrets (réduite pour clarté)
E = 2**n
num_qubits = 2*n + 4
q = 2        # petit modulus puissance de premier
Bx = q
Bs = 3 * q      # BX/BS need to be superpolynomial in lambda
m = 1           # nombre d'échantillons

def generate_circuit(table1, table2):
    """
    Génère le circuit quantique pour la clé de leasing.
    Attention : le code suppose que q = 2 et que x est de dimension 1.
    """
    qc = QuantumCircuit(2 * (1 + 2 * int(np.log2(q)) * n), 2 * (1 + 2 * int(np.log2(q)) * n))

    # 1er échantillon
    qc.h(0)

    for i in range(1, int(np.log2(q)) + 1): # prendre la partie entiere si q n'est pas une puissance de 2
        qc.h(i)
    
    for input, output in table1.items():
        input = [int(x) for x in list(input)]
        output = [int(x) for x in list(output)]
        if output != [0] * len(output):
            for j in range(len(output)):
                if output[j] == 1:
                    to_invert = [k for k in range(len(input)) if input[k] == 0]
                    for i in to_invert:
                        qc.x(i)
                    # Portes ET
                    for k in range(1, len(input)):
                        qc = land(qc, 0, k, len(input) + j)
                    # On reset les entrées inversées
                    for i in to_invert:
                        qc.x(i)

    qc.measure(range(len(input), len(input) + len(output)), range(len(input), len(input) + len(output)))
    
    # 2ème échantillon
    m = len(input) + len(output)
    qc.h(m)

    for i in range(1, int(np.log2(q)) + 1): # prendre la partie entiere si q n'est pas une puissance de 2
        qc.h(m+i)
    
    for input, output in table2.items():
        input = [int(x) for x in list(input)]
        output = [int(x) for x in list(output)]
        if output != [0] * len(output):
            for j in range(len(output)):
                if output[j] == 1:
                    to_invert = [k for k in range(len(input)) if input[k] == 0]
                    for i in to_invert:
                        qc.x(m+i)
                    # Portes ET
                    for k in range(1, len(input)):
                        qc = land(qc, m, m+k, m + len(input) + j)
                    # On reset les entrées inversées
                    for i in to_invert:
                        qc.x(m + i)

    qc.measure(range(m + len(input), m + len(input) + len(output)), range(m + len(input), m + len(input) + len(output)))
    
    return qc


quantum_machine = keyleasing.QuantumKeyLeasing(n, m, q)
mpk, sk = classical.setup()
k = mpk

simulator = Aer.get_backend('qasm_simulator')

r = 1
t = 1000

tries = 0
successes = 0

for _ in range(r):
    #print(f"Essai {_+1}/{r}")
    s = randint(0, E-1)
    for i in range(t):
        fprimes = [[quantum_machine.fprime(k, b)(x) for x in range(quantum_machine.q)] for b in [0,1]]
        table1 = {'0' + int_to_bin(i, int(np.log2(quantum_machine.q))):int_to_bin(fprimes[0][i], int(np.log2(quantum_machine.q))) for i in range(len(fprimes[0]))} #n => log2(q)
        table1.update({'1' + int_to_bin(i, int(np.log2(quantum_machine.q))):int_to_bin(fprimes[1][i], int(np.log2(quantum_machine.q))) for i in range(len(fprimes[1]))})

        fprimes = [[quantum_machine.fprime(k, b)(x) for x in range(quantum_machine.q)] for b in [0,1]]
        table2 = {'0' + int_to_bin(i, int(np.log2(quantum_machine.q))):int_to_bin(fprimes[0][i], int(np.log2(quantum_machine.q))) for i in range(len(fprimes[0]))} #n => log2(q)
        table2.update({'1' + int_to_bin(i, int(np.log2(quantum_machine.q))):int_to_bin(fprimes[1][i], int(np.log2(quantum_machine.q))) for i in range(len(fprimes[1]))})

        qc = generate_circuit(table1, table2)
        qc = generer_circuit(qc)
        transpiled_qc = transpile(qc, simulator)

        # Exécuter le circuit avec le circuit transpilé
        job = simulator.run(transpiled_qc)
        result = job.result()

        counts = result.get_counts(transpiled_qc)
        qubit = list(counts.keys())[0]
        if collision(qubit) and qubit[n+1] == '1':
            #print(qubit[0]) # 0 => pair, 1 => impair
            #print(f"Trouvé en {i+1} essais")
            if int(qubit[2*n + 1]) == s%2:
                #print(x1, x2, s)
                successes += 1
                qc.draw("mpl")
                plt.show()
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

accuracy = successes/r
print(accuracy)
data_file = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"), f"moyenne{n}-{t}.txt")
access_mode = 'a' if os.path.exists(data_file) else 'w'
with open(data_file, access_mode) as f:
    f.write(f"{accuracy}\n")


