
"""Scirpt to try STUFF."""


from FDpy import Fd_problem
from FDpy.expressions import Number, Symbol

n1 = Number(3)
n2 = Number(0)
print(n1/n2)
methods = ["cen", "for"]
time = "imp"
equation = ((0, 0, 0, 1), (0, 0, 1))
dx = 0.1
dt = 0.1
A = Fd_problem((0, 10), (0, 1), ((0, 1), 0), (1), equation, dx, dt, time, methods)
print(A)
u = A.forward_in_time(verbose=True)
