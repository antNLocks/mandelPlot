import numpy as np
from PIL import Image
from numba import jit, njit, prange
from numba_progress import ProgressBar


@jit(nopython=True)
def _julia(z0, c, max_iter=50):
    z = z0
    for i in range(max_iter):
        z = z**2 + c
        if abs(z) > 2:
            return i
    return -1

def is_in_julia(z0, c, max_iter=50):
    """
    Tests if a number is likely to be in the Julia set.
    The function :math:`f_c(z) = z^2 + c` is iterated from :math:`z = z0` and if after *max_iter* iterations the magnitude is less than 2, *z0* is likely to be in the Julia set.

    Parameters
    ----------
    z0 : complex
        The number to test
    c : complex
        The complex value defining this Julia set
    max_iter : int, optional
        The maximum number of iteration of the Julia sequence to test (default is 50)

    Returns
    -------
    bool
        True if *z0* is likely to be in the Julia set defined by *c*, False if it is definitely not in the set.
    
    Examples
    --------
    >>> Julia.is_in_julia(1j,0.5+0.01j)
    False
    >>> Julia.is_in_julia(0, 1j)
    True
    >>> Julia.is_in_julia(0, 0.251)
    True
    >>> Julia.is_in_julia(0,0.251, max_iter=100)
    False
    """
    return _julia(z0, c, max_iter) < 0

@jit(nopython=True)
def _color(i, max_iter, color_values):
    """Assigns a triplet of RGB values to an integer *i*, representing the iteration at witch the Julia series diverges past a magnitude of 2."""
    if i < 0:
        return (0,0,0) # The point is IN the set, so we color it black
    else:
        return (color_values[i], color_values[i], 255)

@njit(nogil=True, parallel=True)
def _juliaColorArray(c, zmin, dx, dy, max_iter, width_pixel_number, height_pixel_number, progress_proxy, color_values):
    """Creates the array that will be used to generate the image of the set"""
    a = np.empty((height_pixel_number,width_pixel_number,3))
    jdy = 1j*dy
    zMinRealMaxImag = zmin + (height_pixel_number-1)*jdy
    for k in prange(width_pixel_number):
        for l in prange(height_pixel_number):
            a[l,k] = _color(_julia(zMinRealMaxImag + k*dx - l*jdy, c, max_iter), max_iter, color_values)
        progress_proxy.update(1)
    return a

def plot_julia(c=-0.8 + 0.156j, zmin=-2-1j, zmax=2+1j, width_pixel_number=2000, max_iter=50, fig_path="./julia_graph.png"):
    """
    Creates an image of the graph of the Julia set, then export to a specific path.

    A progress bar has been added so that you are able to follow the advancement of the function.

    Parameters
    ----------
    c : complex, optional
        Complex value defining this Julia set (default is an example value of -0.8 + 0.156i)
    zmin : complex, optional
        Complex coordinates of the bottom-left corner of the image (default is -2-1i)
    zmin : complex, optional
        Complex coordinates of the top-right corner of the image (default is 2+1i)
    width_pixel_number : int, optional
        The number of pixels of the width of the image (default is 2000). Image ratio is not fixed and depends on the values of zmin and zmax.
    max_iter : int, optional
        The maximum number of iteration of the Julia sequence to test (default is 50). 
        For more details, go to the documentation of the function *is_in_Julia*.
    fig_path : str, optional
        Path of the image file created (default is './Julia_graph.png') 

    Returns
    -------
    None

    """
    height_pixel_number = int((zmax.imag - zmin.imag) / (zmax.real - zmin.real) * width_pixel_number)
    dx = (zmax - zmin).real / width_pixel_number
    dy = (zmax - zmin).imag / height_pixel_number

    color_values = np.array(range(0,max_iter))
    color_values = 255 + np.floor(np.log(color_values/max_iter + 0.004) * 255/np.log(255))
    color_values = color_values.astype(np.uint8)

    with ProgressBar(total=width_pixel_number) as progress:
        juliaColorArray = _juliaColorArray(c, zmin, dx, dy, max_iter, width_pixel_number, height_pixel_number, progress, color_values).astype(np.uint8)

    im = Image.fromarray(juliaColorArray)
    im.save(fig_path)