"""
Adapted functions from the librosa.core.spectrum module.

This module includes selected functions extracted from the librosa library,
specifically from the librosa.core.spectrum module. The adapted functions
are provided here for convenience without the need for the entire librosa
library as a dependency.

Selected Functions:
- amplitude_to_db
- db_to_amplitude
- db_to_power
- pcen

Original Source:
https://github.com/librosa/librosa

Original License (ISC License):
## ISC License

Copyright (c) 2013--2023, librosa development team.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""
from typing import Optional

import numpy as np
import scipy.signal


def amplitude_to_db(
    spec: np.ndarray,
    ref: float = 1.0,
    amin: float = 1e-5,
    top_db: Optional[float] = 80.0,
) -> np.ndarray:
    """Convert an amplitude spectrogram to dB-scaled spectrogram.

    Parameters
    ----------
    spec : np.ndarray
        Input amplitude data
    ref : float > 0.0
        Reference power: output will be relative to `ref` (default: 1.0 for
        amplitude and power spectra)



    Notes
    -----
    Adapted from librosa 0.10.1. See
    https://librosa.org/doc/main/generated/librosa.amplitude_to_db.html
    """
    power = np.square(np.abs(spec))
    log_spec = 10.0 * np.log10(np.maximum(amin**2, power))
    log_spec -= 10.0 * np.log10(np.maximum(amin, np.abs(ref) ** 2))

    if top_db is not None:
        if top_db < 0:
            raise ValueError("top_db must be non-negative")
        log_spec = np.maximum(log_spec, log_spec.max() - top_db)

    return log_spec


def db_to_power(value: float) -> float:
    return np.power(10.0, value * 0.1)


def db_to_amplitude(value: float) -> float:
    return db_to_power(value) ** 0.5


def pcen_core(
    S: np.ndarray,
    *,
    sr: float = 22050,
    hop_length: int = 512,
    gain: float = 0.98,
    bias: float = 2,
    power: float = 0.5,
    time_constant: float = 0.400,
    eps: float = 1e-6,
    b: Optional[float] = None,
    max_size: int = 1,
    ref: Optional[np.ndarray] = None,
    axis: int = -1,
    max_axis: Optional[int] = None,
    zi: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Per-channel energy normalization (PCEN)

    Notes
    -----
    This is a direct port of librosa 0.10.1's implementation of PCEN. See
    https://librosa.org/doc/main/generated/librosa.pcen.html
    """
    if power < 0:
        raise ValueError(f"power={power} must be nonnegative")

    if gain < 0:
        raise ValueError(f"gain={gain} must be non-negative")

    if bias < 0:
        raise ValueError(f"bias={bias} must be non-negative")

    if eps <= 0:
        raise ValueError(f"eps={eps} must be strictly positive")

    if time_constant <= 0:
        raise ValueError(
            f"time_constant={time_constant} must be strictly positive"
        )

    if b is None:
        t_frames = time_constant * sr / float(hop_length)
        # By default, this solves the equation for b:
        #   b**2  + (1 - b) / t_frames  - 2 = 0
        # which approximates the full-width half-max of the
        # squared frequency response of the IIR low-pass filter

        b = (np.sqrt(1 + 4 * t_frames**2) - 1) / (2 * t_frames**2)

        # NOTE: This assertion is to trick the type checker into thinking
        # that b is not None. It is not actually necessary.
        assert b is not None

    if not 0 <= b <= 1:
        raise ValueError(f"b={b} must be between 0 and 1")

    S = np.abs(S)

    if ref is None:
        if max_size == 1:
            ref = S
        elif S.ndim == 1:
            raise ValueError(
                "Max-filtering cannot be applied to 1-dimensional input"
            )
        else:
            if max_axis is None:
                if S.ndim != 2:
                    raise ValueError(
                        f"Max-filtering a {S.ndim:d}-dimensional spectrogram "
                        "requires you to specify max_axis"
                    )
                # if axis = 0, max_axis=1
                # if axis = +- 1, max_axis = 0
                max_axis = np.mod(1 - axis, 2)

            ref = scipy.ndimage.maximum_filter1d(S, max_size, axis=max_axis)

        # NOTE: Type checker trick
        assert ref is not None

    if zi is None:
        # Make sure zi matches dimension to input
        shape = tuple([1] * ref.ndim)
        zi = np.empty(shape)
        zi[:] = scipy.signal.lfilter_zi([b], [1, b - 1])[:]

    # Temporal integration
    S_smooth: np.ndarray
    S_smooth, _ = scipy.signal.lfilter([b], [1, b - 1], ref, zi=zi, axis=axis)

    # Adaptive gain control
    # Working in log-space gives us some stability, and a slight speedup
    smooth = np.exp(-gain * (np.log(eps) + np.log1p(S_smooth / eps)))

    # Dynamic range compression
    S_out: np.ndarray
    if power == 0:
        S_out = np.log1p(S * smooth)
    elif bias == 0:
        S_out = np.exp(power * (np.log(S) + np.log(smooth)))
    else:
        S_out = (bias**power) * np.expm1(power * np.log1p(S * smooth / bias))

    return S_out
