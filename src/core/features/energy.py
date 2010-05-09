import numpy as np

def energy_sequence(framed):
    def frame_energy(frame):
        return np.square(frame).sum()
    nframes, framesize = framed.shape
    output = np.ndarray(nframes)
    for i, frame in enumerate(framed):
        output[i] = frame_energy(frame)
    return output


