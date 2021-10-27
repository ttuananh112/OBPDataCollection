import numpy as np


def vector3d_to_numpy(v):
    if v is None:
        return np.array([None, None, None])
    return np.array([v.x, v.y, v.z])
