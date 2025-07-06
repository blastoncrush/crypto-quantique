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

class QuantumKeyLeasing:
    def __init__(self, n, m, q):
        """
        Initialize the quantum key leasing system without security parameter.
        
        Args:
            security_param: Security parameter lambda
        """
        self.api_key = "8f3ca9ff5ac49fe1593b4ce6ac5f65d3c2a131e1ec9de531add647404b4ea0acdeee03a6000cffdb26ed6f8fcf52c128257340232a306e1d2faae421d15e1974"
        self.noise_bound = 1
        self.service = QiskitRuntimeService("ibm_quantum", self.api_key)
        self.n = n
        self.m = m
        self.q = q

    def fprime(self, k, b):
        """
        NTCF 
        b ∈ {0, 1}
        """
        #e = np.random.randint(-self.noise_bound, self.noise_bound + 1, size=self.n)  # bruit
        A, t = k # t = As + e0
        e = 0
        return lambda x: (A * x + e + b * t)%self.q # si A est une matrice, remplacer * par @

    def qc_keyleasing(self, table):
        """
        Génère le circuit quantique pour la clé de leasing.
        Attention : le code suppose que q = 2 et que x est de dimension 1.
        """
        qc = QuantumCircuit(1 + 2 * int(np.log2(self.q)) * self.n, 1 + 2 * int(np.log2(self.q)) * self.n)

        qc.h(0)

        for i in range(1, int(np.log2(self.q)) + 1): # prendre la partie entiere si q n'est pas une puissance de 2
            qc.h(i)
        
        for input, output in table.items():
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
        return qc


    def keygen(self, mpk):
        #backend = self.service.least_busy(operational=True, simulator=False)
        #pm = generate_preset_pass_manager(backend=backend, target=backend.target, optimization_level=1)
        k = mpk
    
        """
        with Session(backend=backend) as session:
            sampler = Sampler(mode=session)
            
            fprimes = sum(flat([[b*x*self.fprime(k, b)(x) for b in [0,1]] for x in range(self.q)]))
            qc = self.qc_keyleasing(fprimes)
            isa_circuit = pm.run(qc)
                
            job = sampler.run([(isa_circuit, [])], shots=1)
            results = [elem.data.meas.get_bitstrings()[0] for elem in job.result()]
        """
        
        simulator = Aer.get_backend('qasm_simulator')
        fprimes = [[self.fprime(k, b)(x) for x in range(self.q)] for b in [0,1]]
        table = {'0' + int_to_bin(i, int(np.log2(self.q))):int_to_bin(fprimes[0][i], int(np.log2(self.q))) for i in range(len(fprimes[0]))} #self.n => log2(q)
        table.update({'1' + int_to_bin(i, int(np.log2(self.q))):int_to_bin(fprimes[1][i], int(np.log2(self.q))) for i in range(len(fprimes[1]))})
        # table = {'00': '0', '01': '10', '010': '0', '011': '10', '10': '1', '11': '11', '110': '1', '111': '11'}
        print(table)
        
        qc = self.qc_keyleasing(table)
        print(qc)
        qc = transpile(qc, simulator)
        job = simulator.run(qc)
        result = job.result()
        counts = result.get_counts(qc)
        print(counts)
        #qc.draw("mpl")
        #plt.show()