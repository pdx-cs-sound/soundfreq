from tkinter import *
from scipy import fftpack
import math, numpy, struct, sys, wave
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

window = Tk()
window.title("soundfreq")
window.protocol("WM_DELETE_WINDOW", window.quit)

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

info, samples = read_wave(sys.argv[1])

size = 4096
samples = samples[:size]
for i in range(size):
    samples[i] *= math.sin(math.pi * i / (size - 1))

myfft = fftpack.fft(samples)
assert len(myfft) == size

# https://matplotlib.org/3.2.1/gallery/user_interfaces/
#   embedding_in_tk_sgskip.html
fig = plt.figure(figsize=(12, 8), dpi=100)
fplot = fig.add_subplot(1, 1, 1)
xs = [info.framerate * x / size for x in range(size // 2)]
ys = [20 * math.log10(abs(myfft[i] * 2 / size)) for i in range(size // 2)]
fplot.plot(xs, ys)

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

window.mainloop()
exit(0)
