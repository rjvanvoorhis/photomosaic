cpdef int get_n(int x, int y):
    cdef int d
    d = x if x > y else y
    return 1 << int.bit_length(d -1)

cpdef int xy2d (int n, int x, int y):
    cdef int d=0
    cdef s = n//2
    cdef (int, int) x_y
    while s > 0:
        rx = (x & s) > 0
        ry = (y & s) > 0
        d += s * s *((3 * rx) ^ ry)
        x_y = rot(s, x, y, rx, ry)
        x = x_y[0]
        y = x_y[1]
        s = s//2
    return d

cpdef (int, int) rot(int n, int x, int y, int rx, int ry):
    cdef int z, m
    if ry == 0:
        if rx == 1:
            x = n - 1 - x
            y = n - 1 - y
        z = x
        m = y
        x = m
        y = z
    return (x,y)

cpdef (int, int) d2xy(int n, int d):
    cdef int t = d
    cdef int x = 0
    cdef int y = 0
    cdef int s = 1
    cdef (int, int) x_y
    cdef int rx
    cdef int ry
    while s < n:
        rx = 1 & (t//2)
        ry = 1 & (t ^ rx)
        x_y = rot(s, x, y, rx, ry)
        x = x_y[0]
        y = x_y[1]
        x += s * rx
        y += s * ry
        t = t//4
        s *= 2
    return x_y