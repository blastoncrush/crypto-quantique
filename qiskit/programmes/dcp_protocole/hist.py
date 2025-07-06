import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
import test_dcp_protocole_simu as dcpsim
import dcp_protocole_runtime as runn
import os


A = []
B = []
for i in range(1):
    A.append(dcpsim.dcp(1000, 1))
    print(A)

"""
plt.hist(A, bins=10, edgecolor='black')
plt.xlim(0.0, 1.0)

kde = gaussian_kde(A)
x = np.linspace(0, 1.0, 200)
if len(moyenne) > 0:
    moyenne = moyenne[0]
"""
        
moyenne = np.mean(A)
print(moyenne)
B.append(float(moyenne))
print(B)

data_file = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"), f"moyenne{n}-{t}.txt")
access_mode = 'a' if os.path.exists(data_file) else 'w'
with open(data_file, access_mode) as f:
    f.write(f"{moyenne}\n")
    
"""
plt.plot(x, kde(x), color='red', linewidth=2, label='Lissage KDE')

plt.legend()
plt.show()
"""