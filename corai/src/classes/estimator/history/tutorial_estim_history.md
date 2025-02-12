# Estim_history

An estimator object which stores the history of a training. The history contains a column for the epoch and columns for
the metric values, which are chosen at creation.

The library integrates the estimator in the pipeline such that one only needs to initialise it and start the training.

## 1. Initialisation

In order to initialise an `Estim_history` one will need three things:

- a `list` of metric names, these will be used for the column names in the `dataframe` contained in the `estimator`,
- a flag indicating whether validation will be used, if validation is present a second column will be added for each
  metric to store the result for validation,
- a `dictionary` of hyper-parameters (optional), it is a dictionary containing the parameters that will change during
  different trainings and which will be compared for performance at the end. For more details on hyper-parameters check
  out:
  [`corai/src/classes/estimator/hyper_parameters/Tutorial_estim_hyperparameter.md`](https://github.com/Code-Cornelius/CorAI/blob/master/corai/src/classes/estimator/hyper_parameters/tutorial_estim_hyperparameter.md)

```python
estimator_history = corai.Estim_history(metric_names, validation, hyper_params)
```

### 1.1 Initialise directly using the data

When the data is available, one can create the `Estim_history` directly:

```python
df = pd.DataFrame(self.history)
df['fold'] = 0  # estimators require a fold column.

hyper_params = Estim_history.serialize_hyper_parameters(self.hyper_params)  # put the parameters in correct form
# we rename the columns so they suit the standard of estimators.
metric_names, columns, validation = Estim_history.deconstruct_column_names(df.columns)
df.columns = columns
estimator = Estim_history(df=df, metric_names=metric_names, validation=validation, hyper_params=hyper_params)

# assumes one fold case
estimator.list_best_epoch.append(best_epoch)
estimator.list_train_times.append(train_time)

estimator.best_fold = 0
```

## 2. Handling data

### 2.1. Adding data

Once the estimator is initialised we can add data using the append method. The general append method for estimators was
overriden to accept information about a complete training or a fold in the case of a k-fold training. The following
parameters will be necessary:

- the history. It is a `dictionary` of the collected data. One of the entries should have the name `epoch`
  and it should be an array containing the epoch number. The rest of the entries in the dictionary should have each of
  the column names as keys, and the results stored in arrays of values. All the arrays should have the same length,
  equal to the maximum number of epochs.

- the best epoch of the fold. It is an `int` representing the epoch number with the best performance.
- the `fold_time`, this is an `int` representing the training time in seconds.
- optionally, one can pass the `period_kept_data` argument. This is also an `int` and it dictates which rows to keep.
  For example, if `period_kept_data` is 5 then only the rows 0...5...10...15... will be kept.

finally, one needs to update the `best_fold`:

```python
estimator.best_fold = 0
```

```python
estimator_history.append(history, fold_best_epoch, fold_time, period_kept_data)
```

### 2.2. Retrieving data

The library offers multiple methods of retrieving data from the `estim_history`.

- Retrieve the values of a column. The function will return a numpy array.

```python
values = estimator_history.get_values_col(column)
```

- Retrieve the values of a fold from a column. Same as above for one fold.

```python
values = estimator_history.get_values_fold_col(fold, column)
```

- Retrieve a specific value. Same as above for one fold, at one epoch.

```python
values = estimator_history.get_values_fold_epoch_col(fold, epoch, column)
```

## 3. Saving and loading

There are two possible ways of storing an estimator to file: `csv` and `json`. The main difference between the two is
that the `csv` will only store the values from the dataframe while the `json` will also store metadata.

### 3.1. Saving

- Saving to `csv`. This method only requires the path where the file will be stored.

```python
estimator_history.to_csv(path)
```

- Saving to `json`. Additional to the path, this method takes a flat idication whether or not compression should be
  applied. It is important to always use the same flag for storing and loading an estimator.

```python
estimator_history.to_json(self, path, compress)
```

### 3.2. Loading

- Loading from `csv`. Similarly to saving, loading from `csv` only requires the path.

```python
corai.Estim_history.from_csv(path)
```

- Loading from `json`. Similarly to saving, loading from `json` requires the path and the compression flag.

```python
corai.Estim_history.from_csv(path, compressed)
```

## 4. Plotting

For more details of the general architecture of the plotters read: `corai_estimator/how_to_use_estimators_and_plotters.md`.

It is possible to show the history of the training in a very convenient way. Two methods are available.

1. Plot an axis for each fold, a line type per type of loss,
2. one axis on one plot, with two y-axis for two different metrics, and all the folds plot together.

On all the plots, there is a black dash line at the point when the early-stopper stopped the training.

### 4.1. Relplot
Relplots are used for showing evolution of a feature with respect to another as a time-series.

`Relplot_history` is initialised with the data used for plotting.

```python
history_plot = corai.Relplot_history(estimator_history)
```

One can plot the history of training along some metrics with:

```python
history_plot.lineplot(log_axis_for_loss)
```

![alt text](Tutorial_estim_history_sin_lineplot.png?raw=true "Title")

It is also possible to draw all the information on one plot, though one must choose to plot only with respect to two
metrics.
*Generated by running `corai/tests/examples_of_tasks/copy_of_test_examples/regression_sinus.py`
with 4 folds*.

```python
history_plot.draw_two_metrics_same_plot(key_for_second_axis_plot,
                                        log_axis_for_loss,
                                        log_axis_for_second_axis)
```

![alt text](Tutorial_estim_history_sin_two_metrics_same_plot.png?raw=true "Title")

*Generated by running [`corai/tests/examples_of_tasks/copy_of_test_examples/regression_sinus.py`](https://github.com/Code-Cornelius/CorAI/blob/master/corai/tests/examples_of_tasks/copy_of_test_examples/regression_sinus.py)
with 4 folds*.


