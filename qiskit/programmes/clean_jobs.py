from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService("ibm_quantum", "8f3ca9ff5ac49fe1593b4ce6ac5f65d3c2a131e1ec9de531add647404b4ea0acdeee03a6000cffdb26ed6f8fcf52c128257340232a306e1d2faae421d15e1974")
for id in [job.job_id() for job in service.jobs()]:
    service.delete_job(id)

print(service.check_pending_jobs())