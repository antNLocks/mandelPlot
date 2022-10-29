import numpy as np
from PIL import Image
from numba import jit, njit, prange
from numba_progress import ProgressBar


@jit(nopython=True)
def _mandelbrot(c, max_iter=50):
    z = 0
    for i in range(max_iter):
        z = z**2 + c
        if abs(z) > 2:
            return i
    return -1

def is_in_mandelbrot(c, max_iter=50):
    """
    Tests if a number is likely to be in the Mandelbrot set.
    The function :math:`f_c(z) = z^2 + c` is iterated from :math:`z = 0` and if, after *max_iter* iterations the magnitude is less than 2, *c* is likely to be in the Mandelbrot set.

    Parameters
    ----------
    c : complex
        The number to test
    max_iter : int, optional
        The maximum number of iteration of the Mandelbrot sequence to test (default is 50)

    Returns
    -------
    bool
        True if *c* is likely to be in the Mandelbrot set, False if it is definitely not in the set.
    
    Examples
    --------
    >>> is_in_mandelbrot(1j)
    True
    >>> is_in_mandelbrot(c=0.251)
    True
    >>> is_in_mandelbrot(c=0.251, max_iter=100)
    False
    """
    return _mandelbrot(c, max_iter) < 0

@jit(nopython=True)
def _color(i, max_iter, color_values):
    """Assigns a triplet of RGB values to an integer *i*, representing the iteration at witch the Mandelbrot series diverges past a magnitude of 2."""
    if i < 0:
        return (0,0,0) # The point is IN the set, so we color it black
    else:
        return (color_values[i], color_values[i], 255)

@njit(nogil=True, parallel=True)
def _mandelbrotColorArray(zmin, dx, dy, max_iter, width_pixel_number, height_pixel_number, progress_proxy, color_values):
    """Creates the array that will be used to generate the image of the set"""
    a = np.empty((height_pixel_number,width_pixel_number,3))
    jdy = 1j*dy
    zMinRealMaxImag = zmin + (height_pixel_number-1)*jdy
    for k in prange(width_pixel_number):
        for l in prange(height_pixel_number):
            a[l,k] = _color(_mandelbrot(zMinRealMaxImag + k*dx - l*jdy, max_iter), max_iter, color_values)
        progress_proxy.update(1)
    return a

def plot_mandelbrot(zmin=-2.1-1.25j,zmax=0.5+1.25j, width_pixel_number=2000, max_iter=50, fig_path="./mandelbrot_graph.png"):
    """
    Creates an image of the graph of the Mandelbrot set, then export to a specific path.
    If called with parameters at their default value, the generated image will be a view of the entire set.

    A progress bar has been added so that you are able to follow the advancement of the function.

    Parameters
    ----------
    zmin : complex, optional
        Complex coordinates of the bottom-left corner of the image (default is -2.1 - 1.25i)
    zmin : complex, optional
        Complex coordinates of the top-right corner of the image (default is 0.5 + 1.25i)
    width_pixel_number : int, optional
        The number of pixels of the width of the image (default is 2000). Image ratio is not fixed and depends on the values of zmin and zmax.
    max_iter : int, optional
        The maximum number of iteration of the Mandelbrot sequence to test (default is 50). 
        For more details, go to the documentation of the function *is_in_mandelbrot*.
    fig_path : str, optional
        Path of the image file created (default is './mandelbrot_graph.png') 

    Returns
    -------
    None

    """
    height_pixel_number = int((zmax.imag - zmin.imag) / (zmax.real - zmin.real) * width_pixel_number)
    dx = (zmax - zmin).real / width_pixel_number
    dy = (zmax - zmin).imag / height_pixel_number

    color_values = np.array(range(0,max_iter))
    color_values = np.floor(255 + np.log(color_values/max_iter + 0.004) * 255/np.log(255))
    color_values = color_values.astype(np.uint8)

    with ProgressBar(total=width_pixel_number) as progress:
        mandelbrotColorArray = _mandelbrotColorArray(zmin, dx, dy, max_iter, width_pixel_number, height_pixel_number, progress, color_values).astype(np.uint8)

    im = Image.fromarray(mandelbrotColorArray)
    im.save(fig_path)