from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator
import matplotlib.pyplot as plt

qc = QuantumCircuit(8)
cr = ClassicalRegister(8)
qc.add_register(cr)

qc.h(0)
qc.x(2)
qc.h(4)
qc.x(6)
qc.x(7)
qc.cx(0,1)
qc.cx(0,2)
qc.cx(0,3)
qc.cx(4,5)
qc.cx(4,7)
qc.append(QFT(3), [1, 2, 3])
qc.measure(range(1,4), cr[1:4])
qc.append(QFT(3), [5, 6, 7])
qc.measure(range(5,8), cr[5:8])
qc.cx(0,4)
qc.measure(4, cr[4])
qc.h(0)
qc.measure(0, cr[0])

qc.draw("mpl")
plt.savefig("dcp_protocol.png")

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
from qiskit.quantum_info import Statevector
import numpy as np
##
# --- Setup() ---
def setup():
    # Pour simplification : retourne un paramètre public fictif
    mpk = {"A": "random_matrix", "t": "trapdoor_function"}
    sk = {"k": "trapdoor"}  # k est une NTCF
    return mpk, sk

# --- KeyGen(mpk) ---
def keygen(mpk):
    # 3 registres : pour b, x, et la fonction f_b,k(x)
    b_reg = QuantumRegister(1, name='b')
    x_reg = QuantumRegister(1, name='x')
    fx_reg = QuantumRegister(1, name='fx')
    qc = QuantumCircuit(b_reg, x_reg, fx_reg)

    # Superposition sur b et x
    qc.h(b_reg)
    qc.h(x_reg)

    # Exemple : fonction f_b,k(x) simulée par un CNOT
    qc.cx(x_reg, fx_reg)

    # Mesure de fx (simulate function output observation)
    qc.measure_all()

    # Simule et retourne l'état après la mesure
    backend = Aer.get_backend('aer_simulator')
    result = execute(qc, backend, shots=1024).result()
    counts = result.get_counts()
    
    return qc, counts

# --- Affichage de la clé publique ---
def display_keygen_result():
    mpk, sk = setup()
    qc, counts = keygen(mpk)
    print("Counts après génération de la griffe :")
    print(counts)
    qc.draw('mpl').show()

display_keygen_result()
