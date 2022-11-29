import math
from functools import partial
from typing import Union, TypeVar
from sys import stdout
from shutil import get_terminal_size

Callable = TypeVar("Callable")
Callables = TypeVar("Callables")


class ProgressBar:
    def __init__(self, callables: Union[Callable, Callables], title: str = None):
        self.title = "" if title is None else title
        self.styles = {
            "LeftCap": "[",
            "RightCap": "]",
            "ProgressIndicator": "=",
            "NoProgressIndicator": "-",
        }
        self.callables: Callables = callables
        self.results: list[any] = []
        self._valid_()

    def _valid_(self):
        if hasattr(self.callables, "__iter__") and len(self.callables) > 0:
            if callable(self.callables[0]):
                return True
        elif callable(self.callables):
            return True
        else:
            raise TypeError("Argument 'callable' is not a callable type or iterable of.")

    def start(self):
        maximum_percent_value = 100
        bar_length = get_terminal_size().columns // 4
        increment = maximum_percent_value // bar_length

        g_range_max = 1_000_000
        gen_progress = (
            (len(self.results) / len(self.callables)) *
            maximum_percent_value for inf in range(g_range_max)
        )
        gen_bars_complete = (
            self.styles["ProgressIndicator"] *
            (int(next(gen_progress)) // increment) for inf in range(g_range_max)
        )
        gen_bars_incomplete = (
            self.styles["NoProgressIndicator"] *
            (bar_length - int(next(gen_progress)) // increment) for inf in range(g_range_max)
        )
        print(f"{self.title}")
        for call in self.callables:
            self.results.append(call())
            [
                print(expr, end="") for expr in
                [
                    f"\r", self.styles["LeftCap"],
                    next(gen_bars_complete),
                    next(gen_bars_incomplete),
                    self.styles["RightCap"], f" {next(gen_progress):2.2f}%"
                ]
            ]
            stdout.flush()
        print("\n", end="")
        return self.results


if __name__ == "__main__":
    bar_partial = ProgressBar([partial(math.comb, 10_000_000, 34) for i in range(200_000)],
                              "math.comb(10_000_000, 34) x 100:").start()

    bar_lambda = ProgressBar([lambda: math.comb(10_000_000, 34) for i in range(200_000)],
                             "math.comb(10_000_000, 34) x 100:").start()
