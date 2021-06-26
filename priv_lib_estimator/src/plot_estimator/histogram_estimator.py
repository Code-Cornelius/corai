# normal libraries
from abc import abstractmethod
import seaborn as sns

# my libraries
from priv_lib_plot import APlot
from priv_lib_util.tools import function_str
from priv_lib_util.tools.src.function_dict import filter
import priv_lib_util
from priv_lib_estimator.src.plot_estimator.plot_estimator import Plot_estimator


# errors:


# other files

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class Histogram_estimator(Plot_estimator):
    """
    Abstract class

    Redefine:
        get_dict_fig
        get_dict_plot_param
    """


    def __init__(self, estimator, separators=None, *args, **kwargs):
        super().__init__(estimator, separators, *args, **kwargs)


    # section ######################################################################
    #  #############################################################################
    # plot


    @abstractmethod
    def get_dict_fig(self, separators, key):
        """

        Args:
            separators:
            key:

        Returns:

        Examples:
            title = self.generate_title(parameters=separators, parameters_value=key,
                                        before_text="Histogram")
            fig_dict = {'title': title,
                        'xlabel': "x",
                        'ylabel': "y"}
            return fig_dict

        """
        pass

    def hist(self, column_name_draw, separators_plot=None, separators_filter=None,
             palette='PuOr', hue=None, bins=20,
             binrange=None, stat='count', multiple="stack", kde=True, path_save_plot=None):
        """
        Semantics:
            histogram plot.

        Args:
            column_name_draw:
            separators_plot:
            separators_filter:
            palette:
            hue:
            bins:
            binrange (pair): borns of the ax.
            stat: Aggregate statistic to compute in each bin.
                'count' shows the number of observations.
                'frequency' shows the number of observations divided by the bin width.
                'density' normalizes counts so that the area of the histogram is 1.
                'probability' normalizes counts so that the sum of the bar heights is 1.
            multiple: Approach to resolving multiple elements when semantic mapping creates subsets.
                {“layer”, “dodge”, “stack”, “fill”}
            kde (bool): If True, compute a kernel density estimate to smooth the distribution and show on the plot as (one or more) line(s). Only relevant with univariate data.
            path_save_plot:

        Returns:

        """
        # super call for gathering all separators together and having the group by done.
        separators, global_dict, keys = super().draw(separators_plot=separators_plot)
        keys = filter(separators, keys, separators_filter)
        plots = []
        for key in keys:
            data = global_dict.get_group(key)
            plot = APlot()
            plots.append(plot)
            sns.histplot(x=column_name_draw, bins=bins,
                         hue=hue, multiple=multiple, binrange=binrange,
                         legend='full', kde=kde,
                         palette=palette, data=data, ax=plot._axs[0], stat=stat)
            fig_dict = self.get_dict_fig(separators, key)
            plot.set_dict_ax(0, fig_dict)

            if path_save_plot is not None:
                name_file = ''.join([function_str.tuple_to_str(key, ''), 'evol_estimation'])
                plot.save_plot(name_save_file=name_file)
        return plots
