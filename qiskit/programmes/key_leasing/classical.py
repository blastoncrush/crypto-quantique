import numpy as np
import keyleasing

# ===============================
# PARAMÈTRES
# ===============================
n = 1         # taille des vecteurs secrets (réduite pour clarté)
q = 2        # petit modulus puissance de premier
Bx = q
Bs = 3 * q      # BX/BS need to be superpolynomial in lambda
m = 1           # nombre d'échantillons
noise_bound = 1  # bruit simple (bruit = ±1, ±2)

# ===============================
# OUTILS DE BASE
# ===============================
def flat(xss):
    """
    Aplatit une liste de listes en une seule liste.
    """
    flat_list = [
    x
    for xs in xss
    for x in xs
]
    return flat_list

def add_noise(v, bound=noise_bound):
    """Ajoute un bruit discret borné à un vecteur."""
    noise = np.random.randint(-bound, bound + 1, size=v.shape)
    return (v + noise) % q

def gentrap(n, m, q):
    """
    Génère une matrice aléatoire A de taille m x n dans Zq et une trapdoor td associée.
    """
    """
    Ap = np.random.randint(0, q, size=(m, n-1))  # matrice publique
    t = np.random.randint(0, 2, size=n-1)  # trapdoor
    # A = [Ap || -Ap @ t] où t = (t, 1)T
    A = np.hstack([Ap, -Ap @ t[:, np.newaxis]])
    """

    A = 2
    td = None
    return (A, td)

# ===============================
# CORE SUBROUTINES
# ===============================
def setup(security_param=128):
    """Génère les clés publiques et secrètes du système"""
    A, td = gentrap(n, m, q)          # matrice publique
    s = np.random.randint(0, Bs)              # secret
    e = np.random.randint(-noise_bound, noise_bound + 1)  # bruit
    t = (A * s + e) % q
    mpk = (A, t)                                         # NTCF pair = clé publique
    sk = td
    return (mpk, sk)                                   # (mpk, sk)

def encrypt(pk, message_bit):
    """
    Chiffre un bit (0 ou 1) avec la clé publique.
    
    Args:
        mpk (dict): Clé publique contenant la matrice A et le vecteur t.
        message_bit (int): Bit à chiffrer (0 ou 1) = message μ ∈ {0, 1}
    
    Returns:
        tuple: Chiffrement sous forme de trois éléments (ct1, ct2, ct3).
    """
    k, y = pk
    A, t = k

    r_t = np.random.randint(0, q, size=m)  # r ∈ {0,1}^m, r_t est le transposé (vecteur ligne)

    e_prime = np.random.randint(-noise_bound, noise_bound + 1)  # e' ← D_Zq,Bp'

    ct1 = (r_t @ A) % q  # ct1 = rᵗ * A mod q
    ct2 = (r_t @ t) % q  # ct2 = rᵗ * t mod q
    ct3 = (r_t @ y + e_prime + message_bit * (q // 2 + 1)) % q  # ct3 = rᵗ * y + e' + ⌊q/2⌋ * b mod q

    ct = (ct1, ct2, ct3)
    return ct


# ===============================
# DÉMO COMPLÈTE
# ===============================
if __name__ == "__main__":
    quantum_machine = keyleasing.QuantumKeyLeasing(n, m, q)
    mpk, sk = setup()
    quantum_machine.keygen(mpk)