import matplotlib.pyplot as plt
import matplotlib.animation as animation
from functools import partial
import numpy as np
import pathlib

ROOT_DIRECTORY = pathlib.Path(__file__).resolve().parent.parent.parent / "figures"


def animate(i, domain, dx, boundary, u_mat, ax):
    x0 = domain[0]
    xf = domain[1]
    x_vec = np.arange(x0, xf, dx)
    u_vec = [boundary[0], u_mat[i], boundary[1]]
    ax.set(xlim=[x0, xf], ylim=[np.min(u_vec), np.max(u_vec)], xlabel="Time [s]")
    plt.plot(x_vec, x_vec)


def animate_func(domain, dx, u_mat, boundary):
    fig, ax = plt.subplots()
    ax.legend()
    anim = animation.FuncAnimation(
        fig,
        partial(animate, domain=domain, dx=dx, boundary=boundary, u_mat=u_mat, ax=ax),
        interval=10,
    )
    #print(__name__)
    # print(__main__)
    #writergif = animation.PillowWriter()
    #anim.save(ROOT_DIRECTORY / "file.gif", writer=writergif)
    plt.show()
