class DotNetRandom:
    __slots__ = ("_seed_array", "_inext", "_inextp")

    INT_MAX = 2147483647
    INT_MIN = -2147483648

    def __init__(self, seed: int):
        self._seed_array = [0] * 56
        self._initialize(seed)

    def _initialize(self, seed: int) -> None:
        substraction = self.INT_MAX if seed == self.INT_MIN else abs(seed)
        mj = 161803398 - subtraction
        self._seed_array[55] = mj
        mk = 1
        ii = 0

        for _ in range(1, 55):
            ii += 21
            if ii >= 55:
                ii -= 55

            self._seed_array[ii] = mk
            mk = mj - mk
            if mk < 0:
                mj += self.INT_MAX
            mj = self._seed_array[ii]

        for _ in range(1, 5):
            for i in range(1, 56):
                n = i + 30
                if n >= 55:
                    n -= 55

                self._seed_array[i] -= self._seed_array[1 + n]
                self._seed_array[i] = (self._seed_array[i] + 2147483648) % 4294967296 - 2147483648

                if self._seed_array[i] < 0:
                    self._seed_array[i] += self.INT_MAX

        self._inext = 0
        self._inextp = 21

    def _internal_sample(self) -> int:
        loc_inext = self._inext + 1
        if loc_inext >= 56:
            loc_inext = 1

        loc_inextp = self._inextp + 1
        if loc_inextp >= 56:
            loc_inextp = 1

        ret_val = self._seed_array[loc_inext] - self._seed_array[loc_inextp]

        if ret_val == self.INT_MAX:
            ret_val -= 1
        if ret_val < 0:
            ret_val += self.INT_MAX

        self._seed_array[loc_inext] = ret_val
        self._inext = loc_inext
        self._inextp = loc_inextp

        return ret_val

    def next(self) -> int:
        return self._internal_sample()

    def sample(self) -> float:
        return float(self._internal_sample()) * (1.0 / float(self.INT_MAX))

    def next_max(self, max_val: int) -> int:
        return int(self.sample() * max_val)


class FastRandom:
    __slots__ = ("x", "y", "z", "w", "bit_buf", "bit_idx")

    INT_TO_REAL = 1.0 / (2147483647 + 1.0)
    INT_MASK = 0x7FFFFFFF

    def __init__(self, seed: int):
        self.x = seed & 0xFFFFFFFF
        self.y = 842502087
        self.z = 3579807591
        self.w = 273326509
        self.bit_buf = 0
        self.bit_idx = 32

    def gen_unsigned(self) -> int:
        t = self.x ^ ((self.x << 11) & 0xFFFFFFFF)
        self.x = self.y
        self.y = self.z
        self.z = self.w

        self.w = self.w ^ (self.w >> 19) ^ t ^ (t >> 8)
        self.w &= 0xFFFFFFFF

        return self.w

    def next_int(self) -> int:
        return self.INT_MASK & self.gen_unsigned()

    def next_double(self) -> float:
        return self.INT_TO_REAL * float(self.next_int())

    def next_int_range(self, min_val: int, max_val: int) -> int:
        return int(float(min_val) + self.next_double() * float(max_val - min_val))

    def next_double_range(self, min_val: float, max_val: float) -> float:
        return min_val + self.next_double() * (max_val - min_val)

    def next_bool(self) -> bool:
        if self.bit_idx == 32:
            self.bit_buf = self.gen_unsigned()
            self.bit_idx = 1
        else:
            self.bit_buf += 1
            self.bit_idx >>= 1

        return (self.bit_buf & 1) == 1
