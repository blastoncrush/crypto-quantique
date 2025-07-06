from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, Session
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit.quantum_info import SparsePauliOp


service = QiskitRuntimeService("ibm_quantum", "8f3ca9ff5ac49fe1593b4ce6ac5f65d3c2a131e1ec9de531add647404b4ea0acdeee03a6000cffdb26ed6f8fcf52c128257340232a306e1d2faae421d15e1974")
backend = service.least_busy(operational=True, simulator=False)
pm = generate_preset_pass_manager(backend=backend, target=backend.target, optimization_level=1)

with Session(backend=backend) as session:
    sampler = Sampler(mode=session)
    #sampler = Sampler(mode=backend)
    observables_labels = ["IZ", "IX", "ZI", "XI", "ZZ", "XX"]
    observables = [SparsePauliOp(label) for label in observables_labels]
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    print(qc)
    print("---"*30)

    isa_circuit = pm.run(qc)
    isa_circuit.draw("mpl", idle_wires=False)
    #print(qc.num_parameters)
    print(isa_circuit.count_ops())
    job = sampler.run([(isa_circuit, []), (isa_circuit, []), (isa_circuit, [])])
    print(f">>> Job ID: {job.job_id()}")
    print(f">>> Job Status: {job.status()}")


    result = job.result()[0].data.meas.get_bitstrings() #.get_counts(qc)
    if job.done():
        print(job.metrics())
    print(result)