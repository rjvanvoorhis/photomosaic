import cython
import numpy as np


@cython.boundscheck(False)
cpdef int[:] get_order(int[:,:] arr, int[:] out):
    cdef size_t i
    I = arr.shape[0]
    for i in range(I):
        out[i] = get_sort_idx(arr[i])
    return out


@cython.boundscheck(False)
cpdef int diff2d(int[:, :] arr, int[:, :] arr2) nogil:
    cdef size_t i, j, k
    cdef int total = 0
    cdef int dx
    I = arr.shape[0]
    J = arr.shape[1]
    for i in range(I):
        for j in range(J):
            dx = arr[i, j] - arr2[i,j]
            total += dx * dx
    return total

@cython.boundscheck(False)
cpdef int diff3d(int[:, :, :] arr, int[:, :, :] arr2) nogil:
    cdef size_t i, j,
    cdef int total = 0
    cdef int dx, dy, dz
    I = arr.shape[0]
    J = arr.shape[1]
    for i in range(I):
        for j in range(J):
            dx = arr[i, j, 0] - arr2[i,j,0]
            dy = arr[i, j, 1] - arr2[i,j,1]
            dz = arr[i, j, 2] - arr2[i,j,2]
            total += dx * dx
            total += dy * dy
            total += dz * dz
    return total

@cython.boundscheck(False)
cpdef int get_sort_idx(int[:] arr) nogil:
    cdef size_t i
    cdef int idx = 0
    cdef int min_val = arr[0]
    I = arr.shape[0]
    for i in range(I):
        if arr[i] < min_val:
            min_val = arr[i]
            idx = i
    return idx


@cython.boundscheck(False)
cpdef int[:, :] diff2dlist(int[:, :, :] img_tiles, int[:, :, :] sample_tiles, int[:, :] out):
    cdef size_t i, j
    I = img_tiles.shape[0]
    J = sample_tiles.shape[0]
    for i in range(I):
        for j in range(J):
            out[i, j] = diff2d(sample_tiles[j], img_tiles[i])
    return out

@cython.boundscheck(False)
cpdef int[:, :] diff3dlist(int[:, :, :, :] img_tiles, int[:, :, :, :] sample_tiles, int[:, :] out):
    cdef size_t i, j
    I = img_tiles.shape[0]
    J = sample_tiles.shape[0]
    for i in range(I):
        for j in range(J):
            out[i, j] = diff3d(sample_tiles[j], img_tiles[i])
    return out
