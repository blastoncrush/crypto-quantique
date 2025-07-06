"""
import requests
import qiskit_ibm_runtime
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.transpiler import generate_preset_pass_manager
from qiskit.qasm3 import dumps
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit import transpile
 
service = QiskitRuntimeService(channel='ibm_quantum')
backend = service.backend("ibm_kyiv")
 
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
 
theta = Parameter('theta')
phi = Parameter('phi')
parameter_values = {'theta': 1.57, 'phi': 3.14}   # In case we want to pass a dictionary

qc = QuantumCircuit(2)
 
# Add parameterized gates
qc.rx(theta, 0)
qc.ry(phi, 1)
qc.cx(0, 1)
qc.measure_all()
 
# Draw the original circuit
qc.draw('mpl')
 
# Get an ISA circuit
isa_circuit = pm.run(qc)

qasm_str = dumps(isa_circuit)
print("Generated QASM 3 code:")
print(qasm_str)

url = 'https://api.quantum-computing.ibm.com/runtime/jobs'
auth_id = "Bearer 70d54fe35de0768c66a02030d3737937f626ca02d375453d43e52b0e2cdc3c9357d41912e16e30d3ba9c2603b89f47939c255d66916f0bd55af4983f5fe573a6"
backend = 'ibm_kyiv'
 
headers = {
    'Content-Type': 'application/json',
    'Authorization':auth_id
    }
 
job_input = {
    'program_id': 'sampler',
    "backend": backend,
    "hub": "hub1",
    "group": "group1",
    "project": "project1",
    "params": {
        # Choose one option: direct parameter transfer or through a dictionary
        #"pubs": [[qasm_str,[1,2],500]], # primitive unified blocs (PUBs) containing one circuit each.
        "pubs": [[qasm_str,parameter_values,500]], # primitive unified blocs (PUBs) containing one circuit each.
}}
 
response = requests.post(url, headers=headers, json=job_input)
 
if response.status_code == 200:
    job_id = response.json().get('id')
    print(f"Job created: {response.text}")
else:
    print(f"Error: {response.status_code}")

print(response.text)
"""

token = "70d54fe35de0768c66a02030d3737937f626ca02d375453d43e52b0e2cdc3c9357d41912e16e30d3ba9c2603b89f47939c255d66916f0bd55af4983f5fe573a6"

import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session

def create_bell_state():
    """Create a Bell state circuit"""
    qc = QuantumCircuit(2, 2)  # 2 qubits and 2 classical bits
    qc.h(0)        # Put qubit 0 in superposition
    qc.cx(0, 1)    # CNOT to entangle qubits
    qc.measure_all()  # Measure both qubits
    return qc


def main():
    try:
        # Initialize the service
        service = QiskitRuntimeService(channel="ibm_quantum", token=token)
        
        # Get the least busy backend
        backend = service.least_busy(simulator=False, operational=True)
        print(f"Using backend: {backend.name}")

        # Create the circuit
        qc = create_bell_state()
        print("Original circuit:")
        print(qc)
        
        # Transpile the circuit for the specific backend
        transpiled_qc = transpile(qc, backend=backend)
        print("\nTranspiled circuit:")
        print(transpiled_qc)
        
        # Create a session and run the circuit
        with Session(backend=backend) as session:
            sampler = Sampler()
            job = sampler.run([transpiled_qc], shots=10)
            result = job.result()
            
            # Access data from the BitArray format
            print("\nMeasurement results:")
            
            result = job.result()[0].data.meas.get_bitstrings() #.get_counts(qc)
            if job.done():
                print(job.metrics())
            print(result)
        
        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False
    
if __name__ == "__main__":
    main()