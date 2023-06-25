import matplotlib

matplotlib.use("TkAgg", force=True)
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from functools import partial
import numpy as np
import pathlib

ROOT_DIRECTORY = pathlib.Path(__file__).resolve().parent.parent.parent / "sample_code"


def start_animation(domain, dx, u_mat, boundary):
    def animate(i, domain, dx, boundary, u_mat, ax, line2):
        x0 = domain[0]
        xf = domain[1]
        x_vec = np.arange(x0, xf + dx, dx)
        u_vec = u_mat[i]
        begin = boundary[0]
        at_0 = begin[0]
        for idx in range(len(begin) - 1):
            at_0 += begin[idx + 1] * u_vec[idx + 1]
        ending = boundary[1]
        at_M = ending[0]
        for idx in range(len(ending) - 1):
            at_M += ending[idx + 1] * u_vec[-(idx + 1)]
        u_vec = np.insert(u_vec, 0, at_0)
        u_vec = np.insert(u_vec, len(u_vec), at_M)
        line2.set_xdata(x_vec)
        line2.set_ydata(u_vec)
        return (x_vec, u_vec)

    fig, ax = plt.subplots()
    line2 = ax.plot(0.0, 0.0, label="u")[0]
    ax.set(
        xlim=[domain[0], domain[1] + dx],
        ylim=[np.min(u_mat)-2, np.max(u_mat)+2],
        xlabel="X",
        ylabel="U",
    )
    ax.legend()

    anim = animation.FuncAnimation(
        fig,
        partial(animate, domain=domain, dx=dx, boundary=boundary, u_mat=u_mat, ax=ax, line2=line2),
        frames=len(u_mat),
        interval=800,
    )
    writergif = animation.PillowWriter(fps=500)
    anim.save(ROOT_DIRECTORY / "file.gif", writer=writergif)
    plt.show()
