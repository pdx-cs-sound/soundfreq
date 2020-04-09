from tkinter import *
from scipy import fftpack
import math, numpy, struct, sys, wave
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import *

def read_wave(filename):
    w = wave.open(filename, 'rb')
    info = w.getparams()
    raw_samples = w.readframes(info.nframes)
    assert info.nchannels == 1
    sizes = {1: 'B', 2: 'h', 4: 'i'}
    samples = struct.unpack(
        f"<{info.nframes}{sizes[info.sampwidth]}",
        raw_samples,
    )
    float_samples = [s / (1 << (8 * info.sampwidth)) for s in samples]
    w.close()
    return (info, float_samples)

window = Tk()
window.title("soundfreq")
window.protocol("WM_DELETE_WINDOW", window.quit)

info, samples = read_wave(sys.argv[1])

size = 4096
samples = samples[:size]
for i in range(size):
    samples[i] *= math.sin(math.pi * i / (size - 1))

myfft = fftpack.fft(samples)
assert len(myfft) == size

def linear_scale(y):
    return y

def db_scale(y):
    return 20 * math.log10(y)


# https://matplotlib.org/3.2.1/gallery/user_interfaces/
#   embedding_in_tk_sgskip.html
fig = plt.figure(figsize=(12, 8), dpi=100)
fplot = fig.add_subplot(1, 1, 1)
xs = [info.framerate * x / size for x in range(size // 2)]
scale = db_scale
def plot_ys():
    ys = [scale(abs(myfft[i] * 2 / size)) for i in range(size // 2)]    
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
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

window.mainloop()
exit(0)
