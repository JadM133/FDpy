"""Scirpt to try STUFF."""


from FDpy import Fd_problem
from FDpy.expressions import Number, Symbol
import math
import numpy as np

def expr(x, t):
    try:
        return math.erf(x/(2*t**0.5))
    except (ZeroDivisionError):
        return 1


n1 = Number(3)
n2 = Number(0)
methods = ["bac", "for"]
time = "imp"
equation = ((0, 0, 1), (0, 0, 1))
dx = 0.1
dt = 0.1
x = Symbol("x")
ic = -1 * x * (x - 1) * 4
A = Fd_problem((0, 10), (0, 1), ((0, 0, 0, 1), (0, 0, 1)), dx=0.02, dt=0.1, method=["cen", "for"])
B = Fd_problem((0, 10), (0, 1), ((0, 0, 0, 1), (0, 0, 1)), dx=0.02, dt=0.1, method=["cen", "for"])
# A.info()
A.add(boundary=[0, (0, 1)], initial=1, bc_map=[0, -1])
B.add(boundary=[0, (0, 1)], initial=1, bc_map=[-1, 0])
solution_A = A.forward_in_time()
solution_B = B.forward_in_time()

er = A.post_process(solution_A, exact=expr, error=True, save=True, anim=False)
print(er)
