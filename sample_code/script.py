from FDpy import Fd_problem
import sympy


x = sympy.symbols("x")
expr = 2 * x + 4 + 6 * x
print(expr)
methods = [("for", "cen"), ("for", "for")]
time = "imp"
equation = ((0, 0, 0, 1), (0, 0, 1))
dx = 0.1
dt = 0.1
A = Fd_problem((0, 1), (0, 10), (0, 1), (2, 2), equation, dx, dt, time, methods)
print(A)
u = A.forward_in_time()
