import collections

from pytorch_lightning.loggers import LightningLoggerBase
from pytorch_lightning.loggers.base import rank_zero_experiment
from pytorch_lightning.utilities import rank_zero_only


class History_dict(LightningLoggerBase):
    def __init__(self, aplot=None):
        super().__init__()

        self.history = collections.defaultdict(list)
        # The defaultdict will create an entry with an empty list if they key is missing when trying to access

        self.aplot = aplot # plot only when it is given.

    @property
    def name(self):
        return "Logger_custom_plot"

    @property
    def version(self):
        return "1.0"

    @property
    @rank_zero_experiment
    def experiment(self):
        # Return the experiment object associated with this logger.
        pass

    @rank_zero_only
    def log_metrics(self, metrics, step):
        # metrics is a dictionary of metric names and values

        # fetch all metrics
        for metric_name, metric_value in metrics.items():
            if metric_name != 'epoch':
                self.history[metric_name].append(metric_value)
            else:  # case epoch. We want to avoid adding multiple times the same. It happens for multiple losses.
                if (not len(self.history['epoch']) or  # len == 0:
                        not self.history['epoch'][
                                -1] == metric_value):  # the last values of epochs is not the one we are currently trying to add.
                    self.history['epoch'].append(metric_value)
                else:
                    pass

        self.plot_history_prediction()
        return

    def fetch_score(self, keys):
        # string or list of strings
        if isinstance(keys, str):
            return self.history[keys]
        else:
            return [self.history[key] for key in keys]

    def log_hyperparams(self, params):
        pass

    def plot_history_prediction(self):
        # TODO CHOICE SCORE TO PLOT
        # losses
        epochs_loss, loss_train, loss_val = self.fetch_score(['epoch', 'train_loss', 'val_loss'])
        if len(epochs_loss) == len(loss_train) == len(loss_val) and self.aplot is not None:
            # plot the prediction:
            self.aplot._axs[0].clear()

            # plot losses
            if len(epochs_loss) > 1: # make the test so it does not plot in the case of empty loss.
                self.aplot.uni_plot(0, epochs_loss, loss_train,
                                    dict_plot_param={'color': 'blue', 'linestyle': '-', 'linewidth': 2.5,
                                                     'markersize': 0.,
                                                     'label': 'Training Loss'},
                                    dict_ax={'title': "History Training", 'xlabel': 'Epochs', 'ylabel': 'Loss',
                                             'yscale': 'log'})
                self.aplot.uni_plot(0, epochs_loss, loss_val,  # logging after the call: we miss one value
                                    dict_plot_param={'color': 'orange', 'linestyle': '-', 'linewidth': 2.5,
                                                     'markersize': 0.,
                                                     'label': 'Validation Loss'},
                                    dict_ax={'title': "History Training", 'xlabel': 'Epochs', 'ylabel': 'Loss',
                                             'yscale': 'log'})
            self.aplot.show_legend()
            self.aplot.show_and_continue()


######### the plotting would for now look like:

"""
loss = loggers[1].history['train_loss']
loss_epochs = loggers[1].history['epoch']
aplot = corai_plot.APlot(how=(1, 1))
aplot.uni_plot(0, loss_epochs, loss,
               dict_plot_param={'color': None, 'linestyle': '-', 'linewidth': 2.5, 'markersize': 0.,
                                'label': 'Training Loss'},
               dict_ax={'title': "History Training", 'xlabel': 'Epochs', 'ylabel': 'Loss', 'yscale': 'log'})
aplot.show_legend()"""