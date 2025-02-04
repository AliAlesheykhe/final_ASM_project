# ballmotion.pyx
from libc.stdlib cimport malloc, free
import numpy as np
cimport numpy as np
cimport cython

# Shared library imports
cdef extern from "libballmotion.so":
    void move_parabolic(double* x, double* y, double* vel_x, double* vel_y, double* gravity)
    void move_sinusoidal(double* x, double* y, double* vel_x, double* w, double* amp)
    void move_angled(double* x, double* y, double* vel_x, double* angle)

# Define the move_ball_path function
def move_ball_path(np.ndarray[double, ndim=1] pos, double vel_x, double vel_y, double gravity, double w, double angle, str path):
    cdef double x = pos[0]
    cdef double y = pos[1]
    cdef double amp = 20.0
    
    if path == 'straight':
        x += vel_x
    elif path == 'angled':
        move_angled(&x, &y, &vel_x, &angle)
    elif path == 'parabolic':
        move_parabolic(&x, &y, &vel_x, &vel_y, &gravity)
    elif path == 'sinusoidal':
        move_sinusoidal(&x, &y, &vel_x, &w, &amp)

    pos[0] = x
    pos[1] = y
    return pos, vel_x, vel_y
