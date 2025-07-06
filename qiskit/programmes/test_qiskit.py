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

def test():
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure_all()
    return qc

def test2(nbr):
    simulator = Aer.get_backend('qasm_simulator')
    nbr1 = 0
    nbr2 = 0
    for i in range(nbr):
        qc = test()
        transpiled_qc = transpile(qc, simulator)
        job = simulator.run(transpiled_qc)
        result = job.result()
        counts = result.get_counts(transpiled_qc)
        print(counts)
        qubit = list(counts.keys())[0]
        if qubit[0] == '0':
            nbr1 += 1
        else:
            nbr2 += 1
    print(f"Nombre de 0 : {nbr1}, Nombre de 1 : {nbr2}")