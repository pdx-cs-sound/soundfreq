import tkinter
from tkinter import *
from pylab import *
from scipy import signal
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import *

window = Tk()
window.title("filtersweep")
window.protocol("WM_DELETE_WINDOW", window.quit)

sfreq = 48000
nfreq = sfreq // 2
fsamples = nfreq // 10

def avg_coeffs(n):
    return np.array([1/n] * n)

def window_coeffs(n, beta=0.5):
    return signal.firwin(n, 0.1, window=('kaiser', beta), scale=True)

nopt, bopt = signal.kaiserord(-20, 10 / nfreq)

filters = (
    ("avg 2", avg_coeffs(2)),
    ("avg 3", avg_coeffs(3)),
    ("window 3", window_coeffs(3)),
    ("avg 9", avg_coeffs(9)),
    ("window 9", window_coeffs(9)),
    (f"avg {nopt}", avg_coeffs(nopt)),
    (f"window {nopt}", window_coeffs(nopt, beta=bopt)),
)

sweeps = []
myfs = None
for name, f in filters:
    myfs, sweep = signal.freqz(f, worN=fsamples)
    # print(name, f, sweep, np.absolute(sweep))
    sweeps.append(np.absolute(sweep))
myfs = myfs * nfreq / np.pi

size = fsamples

def linear_scale(ys):
    return ys

eps = np.finfo(float).eps
def db_scale(ys):
    return 20 * np.nan_to_num(np.log10(ys + eps))

# https://matplotlib.org/3.2.1/gallery/user_interfaces/
#   embedding_in_tk_sgskip.html
fig = plt.figure(figsize=(12, 8), dpi=100)
fplot = fig.add_subplot(1, 1, 1)
xs = myfs
scale = db_scale
fo = 0
def plot_ys():
    ys = scale(sweeps[fo])
    fplot.clear()
    fplot.plot(xs, ys)

plot_ys()

ampl_mode = "dB"
def change_mode():
    global ampl_mode, button, scale, canvas
    if ampl_mode == "dB":
        ampl_mode = "linear"
        scale = linear_scale
    elif ampl_mode == "linear":
        ampl_mode = "dB"
        scale = db_scale
    else:
        assert False
    plot_ys()
    canvas.draw()
    button.configure(text=ampl_mode)

filter_order = filters[0][0]
def change_order(dirn):
    global filter_order, order, fo, canvas
    nfilters = len(filters)
    assert fo < nfilters
    fo = (fo + nfilters + dirn) % nfilters
    filter_order = filters[fo][0]
    plot_ys()
    canvas.draw()
    order.configure(text=filter_order)

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
toolbar = NavigationToolbar2Tk(canvas, window)
toolbar.update()

controls = tkinter.Frame(master=window)
controls.pack(side=BOTTOM, fill=BOTH, expand=True)
back_button = tkinter.Button(
    master=window,
    text="←",
    command=lambda: change_order(-1),
)
back_button.pack(in_=controls, side=LEFT)
forw_button = tkinter.Button(
    master=window,
    text="→",
    command=lambda: change_order(1),
)
forw_button.pack(in_=controls, side=LEFT)
button = tkinter.Button(
    master=window,
    text=ampl_mode,
    command=change_mode,
)
button.pack(in_=controls, side=LEFT)
order = tkinter.Label(
    master=window,
    text=filter_order,
)
order.pack(in_=controls, side=RIGHT)
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

try:
    window.mainloop()
except KeyboardInterrupt:
    pass
exit(0)
