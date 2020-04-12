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

def avg(xs, n):
    avg = xs[:-n]
    for i in range(1, n):
        avg += xs[i:-n+i]
    np.append(avg, [0] * n)
    return avg / n

def windowed(xs, n):
    taps = signal.firwin(n, 0.1, window='hanning')
    return signal.convolve(xs, taps, mode='same')

nsamples = 48000
step = 100
fsamples = nsamples / step

filter_orders = [
    "avg 2",
    "avg 3",
    "window 3",
    "avg 9",
    "window 9",
    "2× avg 3",
]

myfs = np.linspace(1, nsamples / 2, num=fsamples, endpoint=False)
sin_t = np.linspace(0, nsamples, num=nsamples)
sweeps = [[] for _ in range(len(filter_orders))]
for f in myfs:
    sine = np.sin(2 * math.pi * f * sin_t)
    sweeps[0].append(max(avg(sine, 2)))
    sweeps[1].append(max(avg(sine, 3)))
    sweeps[2].append(max(windowed(sine, 3)))
    sweeps[3].append(max(avg(sine, 9)))
    sweeps[4].append(max(windowed(sine, 9)))
    sweeps[5].append(max(avg(avg(sine, 3), 3)))

size = len(myfs)

def linear_scale(ys):
    return ys

def db_scale(ys):
    return 20 * np.log10(ys)

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

filter_order = filter_orders[0]
def change_order():
    global filter_order, obutton, fo, canvas
    assert fo < len(filter_orders)
    fo = (fo + 1) % len(filter_orders)
    filter_order = filter_orders[fo]
    plot_ys()
    canvas.draw()
    obutton.configure(text=filter_order)

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
toolbar = NavigationToolbar2Tk(canvas, window)
toolbar.update()
button = tkinter.Button(
    master=window,
    text=ampl_mode,
    command=change_mode,
)
button.pack(side=BOTTOM)
obutton = tkinter.Button(
    master=window,
    text=filter_order,
    command=change_order,
)
obutton.pack(side=LEFT)
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

window.mainloop()
exit(0)
