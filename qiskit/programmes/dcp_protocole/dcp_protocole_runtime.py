from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, Session, SamplerV2 as Sampler
from random import randint

# --- Paramètres de l'expérience ---
n = 1                 # Nombre de bits
E = 2**n              # Taille de l'espace
num_qubits = 2*n + 2  # Nombre total de qubits

# --- Authentification via token ---
service = QiskitRuntimeService(
    "ibm_quantum",
    "1f842c78d2123827361250b682c808394af9139f5dbe2181d1b92810d37e016ed82458bf43377c99d7e7832b396409c918e485ee1788cad85fc4d19863d10f8b"  # <-- Remplace ceci par ton token IBM Quantum
)

# --- Fonctions utilitaires ---
def int_to_bin(x, n):
    res = [int(c) for c in list(str(bin(x)[2:]))]
    return [0] * (n - len(res)) + res

def generer_entrees(x, s, E):
    return (int_to_bin(x, n), int_to_bin((x + s) % E, n))

def collision(result):
    l = list(result)
    for i in range(n-1):
        if l[i] != l[i + n + 1]:
            return False
    return l[n - 1] != l[2 * n]

def preparation_etats(qc, q1, q2):
    for i in range(n):
        if (q1[0][i], q1[1][i]) == (1, 1):
            qc.x(i + 1)
        elif (q1[0][i], q1[1][i]) == (0, 1):
            qc.cx(0, i + 1)
        elif (q1[0][i], q1[1][i]) == (1, 0):
            qc.x(i + 1)
            qc.cx(0, i + 1)

    m = n + 1
    for i in range(n):
        if (q2[0][i], q2[1][i]) == (1, 1):
            qc.x(i + 1 + m)
        elif (q2[0][i], q2[1][i]) == (0, 1):
            qc.cx(m, i + 1 + m)
        elif (q2[0][i], q2[1][i]) == (1, 0):
            qc.x(i + 1 + m)
            qc.cx(m, i + 1 + m)
    return qc

def generer_circuit(psi):
    qc = QuantumCircuit(2*n + 2)
    qc.h(0)
    qc.h(n + 1)
    qc = preparation_etats(qc, psi[0], psi[1])
    qc.append(QFT(n), range(1, n + 1))
    qc.append(QFT(n), range(n + 2, 2*n + 2))
    qc.cx(0, n + 1)
    qc.h(0)
    qc.measure_all()
    return qc

# --- Fonction principale (exécution sur ordinateur quantique) ---
def dcp(t, r):
    backend = service.least_busy(operational=True, simulator=False)
    pm = generate_preset_pass_manager(backend=backend, target=backend.target, optimization_level=1)

    tries = 0
    successes = 0

    with Session(backend=backend) as session:
        sampler = Sampler(mode=session)

        for k in range(r):
            s = randint(0, E - 1)
            circuits = []

            for i in range(t):
                x1 = randint(0, E - 1)
                psi1 = generer_entrees(x1, s, E)
                x2 = randint(0, E - 1)
                psi2 = generer_entrees(x2, s, E)

                qc = generer_circuit((psi1, psi2))
                transpiled_qc = pm.run(qc)
                circuits.append((transpiled_qc, []))

            job = sampler.run(circuits, shots=1)
            results = [res.data.meas.get_bitstrings()[0] for res in job.result()]

            for qubit in results:
                if collision(qubit) and qubit[n] == '1':
                    if int(qubit[2*n + 1]) == s % 2:
                        successes += 1
                    break
                tries += 1

    return successes / r


