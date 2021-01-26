# normal libraries
from abc import abstractmethod

import numpy as np  # maths library and arrays
# my libraries
from priv_lib_estimator.src.estimator.estimator import Estimator
from priv_lib_estimator.src.plot_estimator.plot_estimator import Plot_estimator

from priv_lib_plot import APlot


# errors:


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class Statistic_plot_estimator(Plot_estimator):
    def __init__(self, estimator, separators=None, *args, **kwargs):
        super().__init__(estimator, separators, *args, **kwargs)

    # section ######################################################################
    #  #############################################################################
    # data

    @abstractmethod
    def rescale_time_plot(self, rescale_factor, times):
        """
        In order to plot not wrt time but wrt to a rescale factor.

        Args:
            rescale_factor:
            times:

        Returns:

        """
        pass

    @abstractmethod
    def rescale_sum(self, my_sum, times):
        """Rescale the data, for instance the MSE. The method is useful bc I can rescale with attributes. Abstract method allows me to use specific scaling factor.
        I use it in order to normalize the sums.

        Args:
            my_sum:
            times:

        Returns:

        """
        pass

    # section ######################################################################
    #  #############################################################################
    # plot

    @abstractmethod
    def get_dict_fig(self, convergence_in):
        # convergence_in is simply a check parameter. It discriminates the dict_fig.
        pass

    def draw(self, mini_T, times, name_column_evolution, computation_function,
             class_for_hist=None, separators=None, *args, **kwargs):
        """

        Args:
            mini_T:
            times:
            name_column_evolution: following which data should I compute the statistics
            computation_function: which function giving the statistics.

            class_for_hist: Draw the statistics + the histogram for last value.
            For that I need to pass which hist class.

            separators:
            *args:
            **kwargs:

        Returns:

        """
        separators, global_dict, keys = super().draw(separators=separators)

        comp_sum = np.zeros(self.estimator.DF[name_column_evolution].nunique())
        for key in keys:
            data = global_dict.get_group(key)
            estimator = Estimator(data.copy())

            self.test_true_value(
                data)  # test if there is only one true value i  the given sliced data.
            # It could lead to potential big errors.
            estimator.apply_function_upon_data_store_it("value", computation_function, "computation",
                                                        true_parameter=estimator.DF["true value"].mean())

            comp_sum += estimator.DF.groupby([name_column_evolution])["computation"].sum()  # .values

        TIMES_plot = self.rescale_time_plot(mini_T, times)
        comp_sum = self.rescale_sum(comp_sum, times).values

        plot = APlot()
        plot.uni_plot(0, TIMES_plot, comp_sum, dict_plot_param={"linewidth": 2})
        fig_dict = self.get_dict_fig(convergence_in="MSE")
        plot.set_dict_ax(nb_ax=0, dict_ax=fig_dict, bis=False)
        plot.save_plot(name_save_file=''.join([computation_function.__name__, '_comput']))

        if class_for_hist is not None:
            # I create a histogram:
            # first, find the DF with only the last estimation, which should always be the max value of column_evolution.
            max_value_evol = self.estimator.DF[name_column_evolution].max()

            hist_DF = self.estimator.__class__(
                self.estimator.DF[self.estimator.DF[name_column_evolution]
                                  == max_value_evol].copy())  # copy() for independence

            my_hist = class_for_hist(hist_DF, *args, **kwargs)
            my_hist.draw()
        return
