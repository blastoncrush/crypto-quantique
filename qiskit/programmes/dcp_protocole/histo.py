import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import os

# Données initiales
A = [0.8, 0.892, 0.877, 0.883, 0.8810000000000001, 0.8770000000000002, 0.8780000000000001,
     0.8789999999999999, 0.9120000000000004, 0.8960000000000001, 0.8840000000000002, 0.8900000000000001,
     0.872, 0.8760000000000002, 0.88, 0.8680000000000002, 0.872, 0.887, 0.8760000000000001,
     0.8850000000000001, 0.8030000000000002, 0.867, 0.8830000000000001, 0.8750000000000001,
     0.8820000000000001, 0.8700000000000001, 0.887, 0.8760000000000001, 0.8850000000000001,
     0.879, 0.8909999999999999, 0.88, 0.8030000000000002, 0.8630000000000004, 0.843,
     0.8680000000000002, 0.8760000000000002, 0.8570000000000002, 0.8510000000000002, 0.86,
     0.887, 0.8760000000000001, 0.8850000000000001, 0.879, 0.8909999999999999, 0.88,
     0.903, 0.8860000000000001, 0.8930000000000001, 0.892, 0.884, 0.8860000000000002,0.8570000000000002,0.8550000000000001,0.8560000000000001,0.8689999999999999,0.8680000000000002,0.853,0.8770000000000002,0.8520000000000002]

# Étapes de discrétisation
min_val, max_val = np.min(A), np.max(A)
step = 0.005  # largeur des cases
bins = np.arange(min_val, max_val + step, step)
hist, edges = np.histogram(A, bins=bins)

# Moyenne des voisines pour les bins à 0
hist_smoothed = hist.astype(float)
for i in range(1, len(hist) - 1):
    if hist[i] == 0:
        hist_smoothed[i] = (hist[i - 1] + hist[i + 1]) / 2

if hist[0] == 0:
    hist_smoothed[0] = hist[1]
if hist[-1] == 0:
    hist_smoothed[-1] = hist[-2]

# 🔁 NOUVEAU : lissage par influence des voisins
# Noyau de pondération (influence locale)
kernel = np.array([0.33, 0.34, 0.33])
probs_local = np.convolve(hist_smoothed, kernel, mode='same')

# Normaliser en probabilités
probs = probs_local / np.sum(probs_local)

# Fonction de tirage aléatoire
def tirage_pondere(n=1):
    indices = np.random.choice(len(probs), size=n, p=probs)
    tirages = []
    for idx in indices:
        val = np.random.uniform(edges[idx], edges[idx + 1])
        tirages.append(val)
    return np.array(tirages)

# Exemple : tirer 10 000 valeurs
tirages = tirage_pondere(10000)

# Affichage
min_val, max_val = np.min(tirages), np.max(tirages)
step = 0.005
bins = np.arange(min_val, max_val + step, step)

plt.hist(tirages, bins=bins,density=True,edgecolor='black',color='magenta',alpha=0.4)
kde = gaussian_kde(tirages)
x = np.linspace(0.7, 1.0, 2000)
plt.plot(x, kde(x), color='blue', linewidth=3, label='Simulateur Quantique')
plt.xlim(0.3, 1.0)

# Paramètres de la distribution
mu = 0.5       # moyenne (centre)
sigma = np.std(tirages)-0.01   # écart-type
n = 1000    # nombre de tirages

# Tirage des valeurs selon une distribution normale
valeurs = np.random.normal(loc=mu, scale=sigma, size=n)
kde = gaussian_kde(valeurs)
x = np.linspace(0.3, 0.6, 2000)
plt.plot(x, kde(x), color='red', linewidth=3, label='Ordinateur classique')

# Histogramme des valeurs tirées
plt.hist(valeurs, bins=50, density=True,edgecolor='black', color='steelblue')




plt.xlabel("Probabilités de Succès")
plt.ylabel("Nombre d'apparitions")
plt.title("Comparaison Classique et Simulateur Quantique(avec bruit)")

plt.legend()
plt.show()