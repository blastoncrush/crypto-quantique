from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator
 
# Crée un nouveau circuit avec deux qubits
qc = QuantumCircuit(2)
 
# Ajoute une porte Hadamard au qubit 0
qc.h(0)
 
# Effectue une porte X (not) sur le qubit 1, contrôlée par le qubit 0
qc.cx(0, 1)
 
# Return a drawing of the circuit using MatPlotLib ("mpl").
# These guides are written by using Jupyter notebooks, which
# display the output of the last line of each cell.
# If you're running this in a script, use `print(qc.draw())` to
# print a text drawing.
qc.draw("mpl")