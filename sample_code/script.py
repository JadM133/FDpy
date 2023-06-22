from FDpy import Fd_problem
from trying import totalfunc


expr = 2
print(expr)
methods = [("for", "cen"), ("for", "for")]
time = "imp"
equation = ((0, 0, 0, 1), (0, 0, 1))
dx = 0.1
dt = 0.1
A = Fd_problem((0, 10), (0, 1), ((0, 1), (0), (1, 2), equation, dx, dt, time, methods)
print(A)
u = A.forward_in_time()
