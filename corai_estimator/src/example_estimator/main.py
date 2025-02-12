# normal libraries
import time

import pandas as pd
from corai_estimator.src.example_estimator.estim_benchmark_array import Relplot_benchmark_array, \
    Estim_benchmark_array, Distplot_benchmark_array
# priv libraries
from corai_plot import APlot
from corai_util.tools.src.benchmarking import benchmark
from tqdm import tqdm


# section ######################################################################
#  #############################################################################
# helper functions


def index_access(arr):
    for i in range(len(arr)):
        arr[i] + 1
        i + 1


def double_index_access(arr):
    for i in range(len(arr)):
        arr[i] + 1
        i + 1
        arr[i] + 1


def elem_enum(arr):
    for i, elem in enumerate(arr):
        elem + 1
        i + 1


def benchmark_and_save(estim, func, method_name, number_of_reps=100, *args, **kwargs):
    time_dict = {"Method": [method_name] * number_of_reps,
                 "Array Size": [len(test_arr)] * number_of_reps,
                 "Comput. Time": []}

    for _ in range(number_of_reps):
        time = benchmark(func, number_of_rep=1, silent_benchmark=True, *args, **kwargs)
        time_dict["Comput. Time"].append(time)

    estim.append(pd.DataFrame(time_dict))


# section ######################################################################
#  #############################################################################
# Benchmarking

# prepare data
import numpy as np

TEST = False
if TEST:
    powers = np.array(range(13, 17))
else:
    powers = np.array(range(13, 21))

number_of_reps = 200
sizes = 2 ** powers

estim = Estim_benchmark_array()

for size in tqdm(sizes):
    test_arr = list(range(size))
    benchmark_and_save(estim, index_access, "index_access", arr=test_arr, number_of_reps=number_of_reps)
    benchmark_and_save(estim, elem_enum, "double_index_access", arr=test_arr, number_of_reps=number_of_reps)
    benchmark_and_save(estim, elem_enum, "elem_enum", arr=test_arr, number_of_reps=number_of_reps)

print(estim)

time.sleep(1)
plot_evol_estim = Relplot_benchmark_array(estim)

plot_evol_estim.lineplot(column_name_draw='Comput. Time', envelope_flag=True,
                         kind='line', palette='Dark2',
                         hue="Method", markers=True, style="Method",
                         dict_plot_for_main_line={})

plot_hist_estim = Distplot_benchmark_array(estim)
plot_hist_estim.hist(column_name_draw='Comput. Time', separators_plot=["Array Size"], hue='Method',
                     palette='PuOr', bins=50,  separators_filter={'Method': ['elem_enum'], 'Array Size': sizes[-2:]},
                     binrange=None, stat='count', multiple="layer", kde=True, path_save_plot=None)

APlot.show_plot()
