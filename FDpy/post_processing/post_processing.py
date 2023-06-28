"""Module to animate the solution in a GIF."""

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from functools import partial
import numpy as np
import pathlib
from IPython.display import display, clear_output


ROOT_DIRECTORY = pathlib.Path(__file__).resolve().parent.parent.parent / "sample_code"
mpl.rcParams["animation.ffmpeg_path"] = ROOT_DIRECTORY


def transfrom_to_mat(exact, domain, dx, interval, dt):
    """Transform the given exact solution into a matrix."""
    x_vec = np.arange(domain[0], domain[1] + dx, dx)
    t_vec = np.arange(interval[0], interval[1] + dt, dt)
    if callable(exact):
        exact = np.vectorize(exact)
        return exact(x_vec[:, None], t_vec[None, :])
    else:
        try:
            return np.reshape(np.array(exact), (len(x_vec), len(t_vec)))
        except ValueError:
            raise ValueError(
                f"Wrong shape of exact solution. Specify either a function or an array of size {len(x_vec)*len(t_vec)}."
            )


def start_animation(
    domain,
    time_interval,
    dx,
    dt,
    u_mat,
    exact,
    boundary,
    bc_map,
    reduce_frame,
    interval,
    xlabel,
    ylabel,
    label,
    exact_label,
    xlim,
    ylim,
    fps,
    save,
    filename,
    error,
    anim,
    jup,
):
    """Run the animation using function "animate" and allow suer to specify some parameters."""

    def animate(
        i,
        domain,
        dx,
        dt,
        boundary,
        u_mat,
        reduce_frame=1,
        exact_mat=None,
        line2=None,
        line3=None,
        line4=None,
        bc_map=None,
        u_with_bc=[],
        bc=False,
    ):
        x0 = domain[0]
        xf = domain[1]
        x_vec = np.arange(x0, xf + dx, dx)
        u_vec = u_mat[int(i * reduce_frame)]
        bc_map = np.array(bc_map)
        p = sum(bc_map >= 0)
        n = sum(bc_map < 0)
        left_entries = np.zeros(p)
        right_entries = np.zeros(n)
        for count, elem in enumerate(boundary):
            dummy = elem[0]
            if bc_map[count] < 0:
                for counter, idx in enumerate(elem[1:]):
                    dummy += idx * u_vec[-(counter + 1)]
                right_entries[bc_map[count]] = dummy
            else:
                for counter, idx in enumerate(elem[1:]):
                    dummy += idx * u_vec[counter]
                left_entries[bc_map[count]] = dummy
        u_vec = np.insert(u_vec, 0, left_entries)
        u_vec = np.insert(u_vec, len(u_vec), right_entries)
        u_with_bc.append(u_vec)
        if line2 is not None:
            line2.set_xdata(x_vec)
            line2.set_ydata(u_vec)
        if line3 is not None:
            exact_vec = exact_mat[:, i * reduce_frame]
            line3.set_xdata(x_vec)
            line3.set_ydata(exact_vec)
        if line4 is not None:
            line4.set_text(f"t={np.around((i+1)*dt, decimals=1)}s")
        if jup:
            clear_output(wait=True)
            display(fig)
            clear_output(wait=True)
        if bc:
            return u_with_bc
        return (x_vec, u_vec)

    if anim:
        fig, ax = plt.subplots()
        if exact is not None:
            exact_mat = transfrom_to_mat(exact, domain, dx, time_interval, dt)
            u_min = min(np.min(u_mat), np.min(exact_mat))
            u_max = max(np.max(u_mat), np.max(exact_mat))
            line3 = ax.plot(0.0, 0.0, label=exact_label)[0]
        else:
            exact_mat = None
            u_min = np.min(np.array(u_mat))
            u_max = np.max(np.array(u_mat))
            line3 = None
        line2 = ax.plot(0.0, 0.0, label=label)[0]
        line4 = ax.text(
            domain[1] * (1 - np.sign(domain[1]) * 0.5), u_min * (1 + np.sign(u_min) * 0.1), f"t={0}s", fontsize=20
        )
        ax.set(
            xlim=[domain[0] - dx, domain[1] + dx] if xlim is None else xlim,
            ylim=[u_min * (1 - np.sign(u_min) * 0.1), u_max * (1 + np.sign(u_max) * 0.1)] if ylim is None else ylim,
            xlabel=xlabel,
            ylabel=ylabel,
        )
        ax.legend()
        frames = int(len(u_mat) / reduce_frame) - 1
        print("Creating animation...")
        anim = animation.FuncAnimation(
            fig,
            partial(
                animate,
                domain=domain,
                dx=dx,
                dt=dt,
                boundary=boundary,
                u_mat=u_mat,
                reduce_frame=reduce_frame,
                exact_mat=exact_mat,
                line2=line2,
                line3=line3,
                line4=line4,
                bc_map=bc_map,
            ),
            frames=frames,
            interval=interval,
        )

        if save:
            if filename is None:
                filename = "GIF_FDpyn.gif"
            elif not isinstance(filename, str):
                raise ValueError("Filename should be a string.")
            print("Saving GIF, close animation to continue...")
            # writervid = animation.FFMpegWriter(fps=fps)
            anim.save(ROOT_DIRECTORY / filename)
        if not jup:
            plt.show()

    if exact is not None and error:
        if not anim:
            exact_mat = transfrom_to_mat(exact, domain, dx, time_interval, dt)
        u_with_bc = []
        for count, _ in enumerate(np.arange(time_interval[0], time_interval[1] + dt, dt)):
            u_with_bc = animate(
                count,
                domain=domain,
                dx=dx,
                dt=dt,
                boundary=boundary,
                u_mat=u_mat,
                reduce_frame=reduce_frame,
                exact_mat=exact_mat,
                bc_map=bc_map,
                u_with_bc=u_with_bc,
                bc=True,
            )
        return np.linalg.norm(u_with_bc - np.transpose(exact_mat))
    else:
        return None
