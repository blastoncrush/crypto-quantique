from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import QFT
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, Session
from qiskit_ibm_runtime import SamplerV2 as Sampler
from random import randint
import numpy as np
from qiskit_aer import Aer
import matplotlib.pyplot as plt

simulator = Aer.get_backend('qasm_simulator')
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()
qc = transpile(qc, simulator)
job = simulator.run(qc)
result = job.result()
counts = result.get_counts(qc)
print(counts)
qc.draw("mpl")
plt.show()