from ctypes import c_int32, c_uint32

I32_MAX = 2147483647
I32_MIN = -2147483648

class CompatPrng:
    __slots__ = ('seed_array', 'inext', 'inextp')

    def __init__(self, seed: int):
        self.seed_array = [0] * 56

        if seed == I32_MIN:
            subtraction = I32_MAX
        else:
            subtraction = abs(seed)

        mj = 161803398 - subtraction
        self.seed_array[55] = mj
        mk = 1
        ii = 0

        for _ in range(1, 55):
            ii += 21
            if ii >= 55:
                ii -= 55

            self.seed_array[ii] = mk
            mk = mj -mk
            if mk < 0:
                mk += I32_MAX

            mj = self.seed_array[ii]

        for _ in range(1, 5):
            for i in range(1, 56):
                n = i + 30
                if n >= 55:
                    n -= 55

                self.seed_array[i] = self._wrapping_sub_i32(self.seed_array[i], self.seed_array[1 + n])
                if self.seed_array[i] < 0:
                    self.seed_array[i] += I32_MAX

        self.inext = 0
        self. inextp = 21

    def sample(self) -> float:
        return float(self.internal_sample()) * (1.0 / float(I32_MAX))

    def internal_sample(self) -> int:
        loc_inext = self.inext
        loc_inext += 1
        if loc_inext >= 56:
            loc_inext = 1

        loc_inextp = self.inextp
        loc_inextp += 1
        if loc_inextp >= 56:
            loc_inextp = 1

        ret_val = self.seed_array[loc_inext] - self.seed_array[loc_inextp]

        if ret_val == I32_MAX:
            ret_val -= 1

        if ret_val < 0:
            ret_val += I32_MAX

        self.seed_array[loc_inext] = ret_val
        self.inext = loc_inext
        self.inextp = loc_inextp

        return ret_val

    @staticmethod
    def _wrapping_sub_i32(a: int, b: int) -> int:
        res = a - b
        return c_int32(res).value

class CSharpRandom:
    __slots__ = ('prng',)

    def __init__(self, seed: int):
        self.prng = CompatPrng(seed)

    def next(self) -> int:
        return self.prng.internal_sample()

    def next_max(self, max_val: int) -> int:
        return int(self.prng.sample() * float(max_val))


INT_MASK = 0x7FFFFFFF
INT_TO_REAL = 1.0 / (float(I32_MAX) + 1.0)

class OsuRandom:
    __slots__ = ('x', 'y', 'z', 'w', 'bit_buf', 'bit_idx')

    def __init__(self, seed: int):
        self.x = c_uint32(seed).value
        self.y = 842502087
        self.z = 3579807591
        self.w = 273326509
        self.bit_buf = 0
        self.bit_idx = 32

    def gen_unsigned(self) -> int:
        t = self.x ^ c_uint32(self.x << 11).value
        self.x = self.y
        self.y = self.z
        self.z = self.w

        w_shifted = self.w >> 19
        t_shifted = t >> 8
        self.w = self.w ^ w_shifted ^ t ^ t_shifted

        return self.w

    def next_int(self) -> int:
        return INT_MASK & self.gen_unsigned()

    def next_double(self) -> float:
        return INT_TO_REAL * float(self.next_int())

    def next_int_range(self, min_val: int, max_val: int) -> int:
        return int(float(min_val) + self.next_double() * float(max_val - min_val))

    def next_double_range(self, min_val: float, max_val: float) -> int:
        return int(min_val + self.next_double() * (max_val - min_val))

    def next_bool(self) -> bool:
        if self.bit_idx == 32:
            self.bit_buf = self.gen_unsigned()
            self.bit_idx = 1
        else:
            self.bit_idx += 1
            self.bit_buf >>= 1

        return (self.bit_buf & 1) == 1
