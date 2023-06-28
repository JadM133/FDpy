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
dx = 0.01
dt = 0.1
x = Symbol("x")
ic = -1 * x * (x - 1) * 4
domain=(0, 10)
A = Fd_problem((0, 10), (0, 1), ((0, 0, 1), (0, 0, -1)), dx=0.01, dt=0.1, method=["bac", "for"])


def init_func(x):
    return np.exp(-(x-3)**2)
x_vec = np.arange(domain[0], domain[1], dx)
print(len(x_vec))
func = np.vectorize(init_func)
A.info(acc_x=1, acc_t=1)
A.add(boundary=[(0, 1)], initial=[(0, 1)], bc_map=[0])
solution_A = A.forward_in_time(acc_x=1, acc_t=1)
er = A.post_process(solution_A, error=True, save=True, reduce_frame=1)
print(er)
