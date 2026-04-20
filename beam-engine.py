import numpy as np

def simply_supported_point_load(L, a, P, E, I, n=500):
    """
    L = beam length (m), a = load position from left (m),
    P = load (N), E = Young's modulus (Pa), I = second moment of area (m^4)
    Returns x, V (shear), M (moment), y (deflection)
    """
    x = np.linspace(0, L, n)
    b = L - a

    # Reactions
    R_A = P * b / L
    R_B = P * a / L

    # Shear force
    V = np.where(x < a, R_A, R_A - P)

    # Bending moment
    M = np.where(x <= a, R_A * x, R_A * x - P * (x - a))

    # Deflection (closed-form)
    y = np.where(
        x <= a,
        (P * b * x) / (6 * L * E * I) * (L**2 - b**2 - x**2),
        (P * a * (L - x)) / (6 * L * E * I) * (2*L*x - x**2 - a**2)
    )

    return x, V, M, y