"""
Real spectrum tranforms (DCT, DST, MDCT)
"""

__all__ = ['dct', 'idct']

import numpy as np
import _fftpack

import atexit
atexit.register(_fftpack.destroy_ddct1_cache)
atexit.register(_fftpack.destroy_ddct2_cache)
atexit.register(_fftpack.destroy_dct1_cache)
atexit.register(_fftpack.destroy_dct2_cache)

def dct(x, type=2, n=None, axis=-1, norm=None):
    """
    Return the Discrete Cosine Transform of arbitrary type sequence x.

    Parameters
    ----------
    x : array-like
        input array.
    type : {1, 2, 3}
        type of the DCT (see Notes).
    n : int, optional
        Length of the transform.
    axis : int, optional
        axis over which to compute the transform.
    norm : {None, 'ortho'}
        normalization mode (see Notes).

    Returns
    -------
    y : real ndarray

    Notes
    -----
    For a single dimension array ``x``, ``dct(x, norm='ortho')`` is equal to
    matlab ``dct(x)``.

    There are theoretically 8 types of the DCT, only the first 3 types are
    implemented in scipy. 'The' DCT generally refers to DCT type 2, and 'the'
    Inverse DCT generally refers to DCT type 3.

    type I
    ~~~~~~
    There are several definitions of the DCT-I; we use the following
    (for ``norm=None``):

    .. math::
        y_k = x_0 + (-1)^k x_{N-1} + 2\\sum_{n=1}^{N-2} x_n
        \\cos\\left({\\pi nk\\over N-1}\\right),
        \\qquad 0 \\le k < N.

    Only None is supported as normalization mode for DCT-I. Note also that the
    DCT-I is only supported for input size > 1

    type II
    ~~~~~~~
    There are several definitions of the DCT-II; we use the following
    (for ``norm=None``):

    .. math::
        y_k = 2 \\sum_{n=0}^{N-1} x_n
        \\cos\\left({\\pi(2n+1)k\\over 2N}\\right)
        \\qquad 0 \\le k < N.

    If ``norm='ortho'``, :math:`y_k` is multiplied by a scaling factor `f`:

    .. math::
        f = \\begin{cases} \\sqrt{1/(4N)}, & \\text{if $k = 0$} \\\\
    \t\t\\sqrt{1/(2N)}, & \\text{otherwise} \\end{cases}

    Which makes the corresponding matrix of coefficients orthonormal
    (`OO' = Id`).

    type III
    ~~~~~~~~

    There are several definitions, we use the following
    (for ``norm=None``):

    .. math::
        y_k = x_0 + 2 \\sum_{n=1}^{N-1} x_n
        \\cos\\left({\\pi n(2k+1) \\over 2N}\\right)
        \\qquad 0 \\le k < N,

    or, for ``norm='ortho'``:

    .. math::
        y_k = {x_0\\over\\sqrt{N}} + {1\\over\\sqrt{N}} \\sum_{n=1}^{N-1}
        x_n \\cos\\left({\\pi n(2k+1) \\over 2N}\\right)
        \\qquad 0 \\le k < N.

    The (unnormalized) DCT-III is the inverse of the (unnormalized) DCT-II, up
    to a factor `2N`. The orthonormalized DCT-III is exactly the inverse of the
    orthonormalized DCT-II.

    References
    ----------

    http://en.wikipedia.org/wiki/Discrete_cosine_transform

    'A Fast Cosine Transform in One and Two Dimensions', by J. Makhoul, `IEEE
    Transactions on acoustics, speech and signal processing` vol. 28(1),
    pp. 27-34, http://dx.doi.org/10.1109/TASSP.1980.1163351 (1980).

    """
    if type == 1 and norm is not None:
        raise NotImplementedError(
              "Orthonormalization not yet supported for DCT-I")
    return _dct(x, type, n, axis, normalize=norm)

def idct(x, type=2, n=None, axis=-1, norm=None):
    """
    Return the Inverse Discrete Cosine Transform of arbitrary type sequence x.

    Parameters
    ----------
    x : array-like
        input array.
    type : {1, 2, 3}
        type of the IDCT (see Notes).
    n : int, optional
        Length of the transform.
    axis : int, optional
        axis over which to compute the transform.
    norm : {None, 'ortho'}
        normalization mode (see Notes).

    Returns
    -------
    y : real ndarray

    Notes
    -----
    For a single dimension array x, idct(x, norm='ortho') is equal to matlab
    idct(x)

    'The' IDCT is the IDCT of type 2, which is the same as DCT of type 3.

    IDCT of type 1 is the DCT of type 1, IDCT of type 2 is the DCT of type 3,
    and IDCT of type 3 is the DCT of type 2.

    See Also
    --------
    dct
    """
    if type == 1 and norm is not None:
        raise NotImplementedError(
              "Orthonormalization not yet supported for IDCT-I")
    # Inverse/forward type table
    _TP = {1:1, 2:3, 3:2}
    return _dct(x, _TP[type], n, axis, normalize=norm)

def _dct(x, type, n=None, axis=-1, overwrite_x=0, normalize=None):
    """
    Return Discrete Cosine Transform of arbitrary type sequence x.

    Parameters
    ----------
    x : array-like
        input array.
    n : int, optional
        Length of the transform.
    axis : int, optional
        Axis along which the dct is computed. (default=-1)
    overwrite_x : bool, optional
        If True the contents of x can be destroyed. (default=False)

    Returns
    -------
    z : real ndarray

    """
    tmp = np.asarray(x)
    if not np.isrealobj(tmp):
        raise TypeError,"1st argument must be real sequence"

    if n is None:
        n = tmp.shape[axis]
    else:
        raise NotImplemented("Padding/truncating not yet implemented")

    if tmp.dtype == np.double:
        if type == 1:
            f = _fftpack.ddct1
        elif type == 2:
            f = _fftpack.ddct2
        elif type == 3:
            f = _fftpack.ddct3
        else:
            raise ValueError("Type %d not understood" % type)
    elif tmp.dtype == np.float32:
        if type == 1:
            f = _fftpack.dct1
        elif type == 2:
            f = _fftpack.dct2
        elif type == 3:
            f = _fftpack.dct3
        else:
            raise ValueError("Type %d not understood" % type)
    else:
        raise ValueError("dtype %s not supported" % tmp.dtype)

    if normalize:
        if normalize == "ortho":
            nm = 1
        else:
            raise ValueError("Unknown normalize mode %s" % normalize)
    else:
        nm = 0

    if type == 1 and n < 2:
        raise ValueError("DCT-I is not defined for size < 2")

    if axis == -1 or axis == len(tmp.shape) - 1:
        return f(tmp, n, nm, overwrite_x)
    #else:
    #    raise NotImplementedError("Axis arg not yet implemented")

    tmp = np.swapaxes(tmp, axis, -1)
    tmp = f(tmp, n, nm, overwrite_x)
    return np.swapaxes(tmp, axis, -1)
