from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFT, RealAmplitudes
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, Session
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit_ibm_runtime import EstimatorV2 as Estimator
import matplotlib.pyplot as plt
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
from qiskit.primitives import StatevectorSampler
from qiskit.circuit.library import efficient_su2
import numpy as np

service = QiskitRuntimeService("ibm_quantum", "8f3ca9ff5ac49fe1593b4ce6ac5f65d3c2a131e1ec9de531add647404b4ea0acdeee03a6000cffdb26ed6f8fcf52c128257340232a306e1d2faae421d15e1974")
n = 1
E = 2**n
num_qubits = 2*n + 2

def collision(result):
    l = list(result)
    for i in range(n, 1, -1):
        if l[i] != l[i+n+1]:
            return False
    return l[1] != l[n+2]

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
    #cr = ClassicalRegister(2*n + 2)
    #qc.add_register(cr)
    qc.h(0)
    qc.h(n+1)
    qc = preparation_etats(qc, psi[0], psi[1])
    qc.append(QFT(n), range(1, n+1))
    qc.append(QFT(n), range(n+2, 2*n+2))
    qc.cx(0,n+1)
    qc.h(0)
    #qc.measure(range(2*n+2), cr[0:2*n+2])
    return qc

t = 3 # Nombre d'essais
r = 1 # Nombre de répétitions

tries = 0
successes = 0

#psi = RealAmplitudes(n, reps=3, entanglement='full')

backend = service.least_busy(operational=True, simulator=False)
pm = generate_preset_pass_manager(backend=backend, target=backend.target, optimization_level=1)

#psi_isa_circuit = pm.run(psi)

with Session(backend=backend) as session:
    # Submit a request to the Sampler primitive within the session.
    sampler = Sampler(mode=session)
    #sampler = Sampler(mode=backend)
    #sampler = StatevectorSampler()
    for _ in range(r):
        s = randint(1, E-1)
        for i in range(t):
            x1 = randint(0, E-1)
            psi1 = generer_entrees(x1, s, E)
            x2 = randint(0, E-1)
            psi2 = generer_entrees(x2, s, E)

            qc = generer_circuit((psi1, psi2), E)
            qc.measure_all()
            print(qc)
            print("---"*30)
            circuit = efficient_su2(127, entanglement="linear")
            circuit.measure_all()
            param_values = np.random.rand(circuit.num_parameters)

            isa_circuit = pm.run(circuit)
            job = sampler.run([(isa_circuit, param_values)])


            result = job.result()[0].data.meas #.get_counts(qc)
            if job.done():
                print(job.metrics())
            print(result)
            break
        
            if collision(qubit) and qubit[len(qubit)//2] == '1':
                #print(qubit[0]) # 0 => pair, 1 => impair
                #print(f"Trouvé en {i+1} essais")
                if int(qubit[0]) == s%2:
                    successes += 1
                qc.reset(range(2*n+2))
                break
            else:
                qc.reset(range(2*n+2))
        
            tries += 1
        
        """if not collision(qubit):
            if randint(0, 1) == s%2:
                successes += 1"""
    

print(f"Accuracy : {successes/r*100}%")
print(f"Nombre moyen d'essais : {tries/r}")