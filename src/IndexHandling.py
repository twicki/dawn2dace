import sympy

def ToMemLayout(i, j, k):
    return j, k, i # Memory layout

def ToStridePolicy3D(I, J, K):
    # To memory layout
    I, J, K = ToMemLayout(I, J, K)

    # Adapt lowest order memory access
    K = 8 * sympy.ceiling(K / 8)

    # Back from memory layout
    I, J, K = ToMemLayout(I, J, K)
    I, J, K = ToMemLayout(I, J, K)
    I, J, K = ToMemLayout(I, J, K)
    I, J, K = ToMemLayout(I, J, K)
    I, J, K = ToMemLayout(I, J, K)
    return I, J, K

class Index3D:
    def __init__(self, i:int, j:int, k:int):
        self.i = i
        self.j = j
        self.k = k
