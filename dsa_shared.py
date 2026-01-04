import ctypes, os
from ctypes import c_void_p, c_char_p, c_size_t, c_int, c_double, POINTER, byref, create_string_buffer

_lib_path_candidates = [
    os.path.join(os.getcwd(), "libstudentdsa.so"),
    os.path.join(os.getcwd(), "studentdsa.dll"),
    os.path.join(os.getcwd(), "studentdsa.so"),
]

_lib_path = None
for p in _lib_path_candidates:
    if os.path.exists(p):
        _lib_path = p
        break

if not _lib_path:
    _lib_path = "libstudentdsa.so" if os.name != "nt" else "studentdsa.dll"

if os.name == "nt":
    _lib = ctypes.WinDLL(_lib_path)
else:
    _lib = ctypes.CDLL(_lib_path)

_lib.load_from_string.argtypes = [c_char_p]
_lib.load_from_string.restype = c_void_p
_lib.free_handle.argtypes = [c_void_p]
_lib.free_handle.restype = None
_lib.sort_by_roll.argtypes = [c_void_p]; _lib.sort_by_roll.restype = c_int
_lib.sort_by_name.argtypes = [c_void_p]; _lib.sort_by_name.restype = c_int
_lib.search_roll.argtypes = [c_void_p, c_int, c_char_p, c_size_t]; _lib.search_roll.restype = c_int
_lib.stats.argtypes = [c_void_p, POINTER(c_int), POINTER(c_double), POINTER(c_int), POINTER(c_int)]; _lib.stats.restype = c_int
_lib.export_to_string.argtypes = [c_void_p, POINTER(c_char_p), POINTER(c_size_t)]; _lib.export_to_string.restype = c_int
_lib.free_string.argtypes = [c_char_p]; _lib.free_string.restype = None
_lib.export_to_file.argtypes = [c_void_p, c_char_p]; _lib.export_to_file.restype = c_int

class DSALibError(Exception):
    pass

class DSALib:
    def __init__(self):
        self.lib = _lib
        self.handle = None

    def load_from_string(self, s: str):
        if isinstance(s, str):
            b = s.encode('utf-8')
        else:
            b = s
        h = self.lib.load_from_string(c_char_p(b))
        if not h:
            raise DSALibError("Failed to load data into DSA library")
        self.handle = c_void_p(h)

    def free(self):
        if self.handle:
            self.lib.free_handle(self.handle)
            self.handle = None

    def sort_by_roll(self):
        if not self.handle: raise DSALibError("No handle")
        return self.lib.sort_by_roll(self.handle)

    def sort_by_name(self):
        if not self.handle: raise DSALibError("No handle")
        return self.lib.sort_by_name(self.handle)

    def search_roll(self, key: int):
        if not self.handle: raise DSALibError("No handle")
        bufsize = 512
        buf = create_string_buffer(bufsize)
        r = self.lib.search_roll(self.handle, int(key), buf, bufsize)
        if r == 0:
            return buf.value.decode('utf-8')
        elif r == 1:
            return None
        else:
            raise DSALibError("search_roll failed")

    def stats(self):
        if not self.handle: raise DSALibError("No handle")
        count = c_int(); avg = c_double(); mn = c_int(); mx = c_int()
        rc = self.lib.stats(self.handle, byref(count), byref(avg), byref(mn), byref(mx))
        if rc != 0:
            raise DSALibError("stats failed")
        return {"count": count.value, "avg": float(avg.value), "min": mn.value, "max": mx.value}

    def export_to_string(self):
        if not self.handle: raise DSALibError("No handle")
        outbuf = c_char_p(); outlen = c_size_t()
        rc = self.lib.export_to_string(self.handle, byref(outbuf), byref(outlen))
        if rc != 0:
            raise DSALibError("export_to_string failed")
        data = ctypes.string_at(outbuf, outlen.value)
        self.lib.free_string(outbuf)
        return data.decode('utf-8')
