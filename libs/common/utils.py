import time


class TimeIt:
    """
    Class to measure run-time of a function or computation...
    """
    def __init__(self, name: str = None):
        self._name = name if name is not None else "Func"

    def __enter__(self):
        self._start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end = time.time()
        dur = (self._end - self._start) * 1000
        print(f"{self._name}: {dur:.02f}ms")
