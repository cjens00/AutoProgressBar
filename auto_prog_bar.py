import itertools
import math
import timeit
from itertools import repeat
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
            "NoProgressIndicator": "-"
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
            raise TypeError("Argument 'callables' is not a callable type or iterable of.")

    def start(self):
        # maximum progress value
        is_complete_number = 100

        # width of progress bar
        bar_length = get_terminal_size().columns // 4

        # value representing one bar of progress
        increment = is_complete_number // bar_length

        # repeat is not what i want, finite generator at least worked
        # TODO: check itertools.cycle()
        gen_progress = (
            (len(self.results) / len(self.callables)) *
            is_complete_number
            for infinite in repeat(None)
        )
        gen_bars_complete = (
            self.styles["ProgressIndicator"] *
            (int(next(gen_progress)) // increment)
            for infinite in repeat(None)
        )
        gen_bars_incomplete = (
            self.styles["NoProgressIndicator"] *
            (bar_length - int(next(gen_progress)) // increment)
            for infinite in repeat(None)
        )
        print(f"{self.title}")
        for call in self.callables:
            self.results.append(call())
            [
                print(expr, end="") for expr in
                [
                    f"\r",
                    self.styles["LeftCap"],
                    next(gen_bars_complete),
                    next(gen_bars_incomplete),
                    self.styles["RightCap"],
                    f" {next(gen_progress):2.2f}%"
                ]
            ]
            stdout.flush()
        print("\n", end="")
        return self

    def result(self):
        return self.results


if __name__ == "__main__":
    imports = "\n".join([
                          "import itertools",
                          "import math",
                          "import timeit",
                          "from itertools import repeat",
                          "from functools import partial",
                          "from typing import Union, TypeVar",
                          "from sys import stdout",
                          "from shutil import get_terminal_size",
                          "from auto_prog_bar import ProgressBar"
                      ])

    bar_partial_time = timeit.timeit(
        "ProgressBar([partial(sum, range(1_001)) for i in range(200_000)],"
        "\"sum([0, 1,000]) x 200,000:\").start()",
        number=10,
        setup=imports
    )
    print(bar_partial_time)

    bar_lambda_time = timeit.timeit(
        "ProgressBar([lambda: sum(range(1_001)) for i in range(200_000)],"
        "\"sum([0, 1,000]) x 200,000:\").start()",
        number=10,
        setup=imports
    )
    print(bar_lambda_time)
