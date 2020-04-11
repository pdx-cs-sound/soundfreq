from tkinter import *
from scipy import fftpack
import math, numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import *

window = Tk()
window.title("filtersweep")
window.protocol("WM_DELETE_WINDOW", window.quit)

def filter(xs):
    yield 0
    for i in range(1, len(xs)):
        yield 0.5 * (xs[i-1] + xs[i])

nsamples = 48000
step = 200

sweeps = [[], []]
myfs = []
for f in range(1, nsamples // 2, step):
    myfs.append(f)
    samples = [math.sin(2 * math.pi * i * f / nsamples)
               for i in range(nsamples)]
    peak1 = max(filter(samples))
    sweeps[0].append(peak1)
    peak2 = max(filter(list(filter(samples))))
    sweeps[1].append(peak2)

size = len(myfs)

def linear_scale(y):
    return y

def db_scale(y):
    return 20 * math.log10(y)

# https://matplotlib.org/3.2.1/gallery/user_interfaces/
#   embedding_in_tk_sgskip.html
fig = plt.figure(figsize=(12, 8), dpi=100)
fplot = fig.add_subplot(1, 1, 1)
xs = myfs
scale = db_scale
fo = 0
def plot_ys():
    ys = [scale(sweeps[fo][i]) for i in range(size)]
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

filter_order = "order 1"
def change_order():
    global filter_order, obutton, fo, canvas
    if fo == 0:
        filter_order = "order 2"
        fo = 1
    elif fo == 1:
        filter_order = "order 1"
        fo = 0
    else:
        assert False
    plot_ys()
    canvas.draw()
    obutton.configure(text=filter_order)

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
toolbar = NavigationToolbar2Tk(canvas, window)
toolbar.update()
button = Button(
    master=window,
    text=ampl_mode,
    command=change_mode,
)
button.pack(side=BOTTOM)
obutton = Button(
    master=window,
    text=filter_order,
    command=change_order,
)
obutton.pack(side=LEFT)
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

window.mainloop()
exit(0)
