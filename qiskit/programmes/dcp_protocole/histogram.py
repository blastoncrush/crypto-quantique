from dcp_protocole_runtime import dcp
from qiskit_ibm_runtime import QiskitRuntimeService
import os

path = os.path.join(os.path.abspath(__file__))
path = str(path)
path = path[:len(path) - 2] + "txt"
    
#def clean_jobs():
#    service = QiskitRuntimeService("ibm_quantum", "c8ca78f4949bd2869f3d7e8702c2cf5d86a4ce0a7b6e2de90b7579d635fd8ec19a16bc80fe510086caa914199181981b55ceedf6d2e039c6ad4c82f3ca7a897e")
#    for id in [job.job_id() for job in service.jobs()]:
#        service.delete_job(id)





accuracy = dcp(t=10, r=10)
print(f"Essai {1} : {accuracy*100}%")
with open(path, "a") as f:
    f.write(str(accuracy) + "\n")