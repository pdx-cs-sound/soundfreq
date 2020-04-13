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

nopt, bopt = signal.kaiserord(-20, 10 / nfreq)
def kaiser_coeffs(n, beta=0.5):
    return signal.firwin(n, 0.01, window=('kaiser', beta), scale=True)

# https://plotly.com/python/v3/fft-filters/
def win_sinc_coeffs(n, beta=0.5):
    xs = np.arange(n)
    sinc = np.sinc(2 * 0.01 * (xs - (n - 1)) / 2)
    window = signal.windows.kaiser(n, beta)
    sw = sinc * window
    return sw / np.sum(sw)

filters = (
    ("avg 2", avg_coeffs(2)),
    ("avg 3", avg_coeffs(3)),
    ("kaiser 3 (0.5)", kaiser_coeffs(3)),
    ("avg 9", avg_coeffs(9)),
    ("kaiser 9 (0.5)", kaiser_coeffs(9)),
    (f"avg {nopt}", avg_coeffs(nopt)),
    (f"kaiser {nopt} (bopt)", kaiser_coeffs(nopt, beta=bopt)),
    (f"win sinc {nopt} (bopt)", win_sinc_coeffs(nopt, beta=bopt)),
)


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
scale = db_scale
fo = 0

def plot_sweep():
    coeffs = filters[fo][1]
    myfs, sweep = signal.freqz(coeffs, worN=fsamples)
    xs = myfs * nfreq / np.pi
    ys = scale(np.absolute(sweep))
    fplot.clear()
    fplot.plot(xs, ys)

def plot_chirp():
    coeffs = filters[fo][1]
    ts = np.linspace(0, 1, sfreq)
    mychirp  = signal.chirp(ts, 0, 1, nfreq)
    filtered = signal.convolve(mychirp, coeffs, mode='same')
    ys = scale(filtered)
    fplot.clear()
    fplot.plot(ts, ys)

plot_mode = "freq"
def plot_cur():
    if plot_mode == "freq":
        plot_sweep()
    elif plot_mode == "chirp":
        plot_chirp()
    else:
        assert False

plot_cur()

scale_mode = "dB"
def change_scale():
    global scale_mode, scale_button, scale, canvas
    if scale_mode == "dB":
        scale_mode = "linear"
        scale = linear_scale
    elif scale_mode == "linear":
        scale_mode = "dB"
        scale = db_scale
    else:
        assert False
    plot_cur()
    canvas.draw()
    scale_button.configure(text=scale_mode)

def change_plot():
    global plot_mode, plot_button, canvas
    if plot_mode == "freq":
        plot_mode = "chirp"
    elif plot_mode == "chirp":
        plot_mode = "freq"
    else:
        assert False
    plot_cur()
    canvas.draw()
    plot_button.configure(text=plot_mode)

filter_order = filters[0][0]
def change_order(dirn):
    global filter_order, order, fo, canvas
    nfilters = len(filters)
    assert fo < nfilters
    fo = (fo + nfilters + dirn) % nfilters
    filter_order = filters[fo][0]
    plot_cur()
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
scale_button = tkinter.Button(
    master=window,
    text=scale_mode,
    command=change_scale,
)
scale_button.pack(in_=controls, side=LEFT)
plot_button = tkinter.Button(
    master=window,
    text=plot_mode,
    command=change_plot,
)
plot_button.pack(in_=controls, side=LEFT)
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
