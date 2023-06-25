
"""Scirpt to try STUFF."""


from FDpy import Fd_problem
from FDpy.expressions import Number, Symbol
import numpy as np

n1 = Number(3)
n2 = Number(0)
methods = ["cen", "for"]
time = "imp"
equation = ((0, 0, 0, 1), (0, 0, 0, 1))
dx = 0.1
dt = 0.1
x = Symbol('x')
ic = -1*x*(x-10)*4
A = Fd_problem((0, 1), (0, 1), (0, 0), (2*x-1, (0, 2)), ((0, 0, 0, 1), (0, 0, 0, 1)), dx=0.2, dt=0.2)
print(A)
solution = A.forward_in_time(verbose=True)
