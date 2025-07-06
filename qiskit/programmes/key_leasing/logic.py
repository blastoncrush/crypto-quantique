def lxor(qc, a, b, c):
    qc.cx(a, b)
    qc.cx(a, c)
    return qc

def land(qc, a, b, c):
    qc.ccx(a, b, c)
    return qc

def lor(qc, a, b, c):
    qc.x([0,1])
    qc.ccx(0,1,2)
    qc.x(2)
    qc.x([0,1])
    return qc

def int_to_bin(x, n):
    res = str(bin(x)[2:])
    if len(res) < n:
        res = '0' * (n - len(res)) + res
    return res