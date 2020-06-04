#  Copyright (c) 2020. BooleanTRN
#  Author: Rohit Suratekar
#
#  This file is part of BooleanTRN project.
#
# Main file which will deal with all functions available in this library.

from BooleanTRN.analysis import run
import timeit

time = timeit.timeit('run()',
                     'from __main__ import run',
                     number=1)

print(f"Total time: {time:.3} seconds")
