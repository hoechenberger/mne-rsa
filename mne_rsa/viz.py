from functools import partial
import matplotlib.pyplot as plt
from mne.viz.topo import _iter_topography
import numpy as np
from scipy.spatial import distance


def plot_dsms(dsms, names=None, items=None, n_rows=1, cmap='viridis',
              title=None):
    """Plot one or more DSMs

    Parameters
    ----------
    dsms : ndarray | list of ndarray
        The DSM or list of DSMs to plot. The DSMs can either be two-dimensional
        (n_items x n_iterms) matrices or be in condensed form.
    names : str | list of str | None
        For each given DSM, a name to show above it. Defaults to no names.
    items : list of str | None
        The each item (row/col) in the DSM, a string description. This will be
        displayed along the axes. Defaults to None which means the items will
        be numbered.
    n_rows : int
        Number of rows to use when plotting multiple DSMs at once. Defaults to
        1.
    cmap : str
        Matplotlib colormap to use. See
        https://matplotlib.org/gallery/color/colormap_reference.html
        for all possibilities. Defaults to 'viridis'.
    title : str | None
        Title for the entire figure. Defaults to no title.

    Returns
    -------
    fig : matplotlib figure
        The figure produced by matplotlib
    """
    if not isinstance(dsms, list):
        dsms = [dsms]

    if isinstance(names, str):
        names = [names]
    if names is not None and len(names) != len(dsms):
        raise ValueError(f'Number of given names ({len(names)}) does not '
                         f'match the number of DSMs ({len(dsms)})')

    n_cols = int(np.ceil(len(dsms) / n_rows))
    fig = plt.figure(figsize=(2 * n_cols, 2 * n_rows))

    ax = fig.subplots(n_rows, n_cols, sharex=True, sharey=True, squeeze=False)
    for row in range(n_rows):
        for col in range(n_cols):
            i = row * n_cols + col % n_cols
            if i < len(dsms):
                dsm = dsms[i]
                if dsm.ndim == 1:
                    dsm = distance.squareform(dsm)
                elif dsm.ndim > 2:
                    raise ValueError(f'Invalid shape {dsm.shape} for DSM')
                im = ax[row, col].imshow(dsm, cmap=cmap)

                if names is not None:
                    name = names[i]
                    ax[row, col].set_title(name)
            else:
                ax[row, col].set_visible(False)

    plt.colorbar(im, ax=ax)
    if title is not None:
        plt.suptitle(title)
    return fig


def _click_func(ax, ch_idx, dsms, cmap):
    """ Function used to plot a single DSM interactively.

    Parameters
    ----------
    ax: matplotlib.Axes.axes
        Axes.axes object on which a new single DSM is plotted.
    ch_idx: int
        Index of a channel.
    dsms: ndarray, shape (n_sensors, n_dsm_datapoint)
        DSMs of MEG recordings; there's one DSM for each sensor.
    cmap: str
        Colormap used for plotting DSMs.
        Check matplotlib.pyplot.imshow for details.
    """
    dsm = dsms[ch_idx]
    dsm = distance.squareform(dsm)
    ax.imshow(dsm, cmap=cmap)


def _plot_dsms_topo(dsms, info, layout=None, fig=None, title=None,
                    axis_facecolor='w', axis_spinecolor='w',
                    fig_facecolor='w', figsize=(6.4, 4.8), cmap='viridis',
                    show=False):
    """ Plot DSMs on 2D MEG topography.

    Parameters
    ----------
    dsms: ndarray, shape (n_sensors, n_dsm_datapoint)
        DSMs of MEG recordings; there's one DSM for each sensor.
    info: mne.io.meas_info.Info
        Info object that contains meta data of MEG recordings.
    layout: mne.channels.layout.Layout, optional
        Layout objects containing sensor layout info.
        The default, layout=None, will figure out layout based on info.
    fig: matplotlib.pyplot.Figure | None, optional
        Figure object on which DSMs on 2D MEG topography are plotted.
        The default, fig=None, creates a new Figure object.
    title: str, optional
        Title of the plot; used only when fig=None.
        The default, title=None, put no title in the figure.
    axis_facecolor: str, optional
        Face color of the each DSM. Defaults to 'w', white.
    axis_spinecolor: str, optional
        Spine color of each DSM. Defaults to 'w', white.
    fig_facecolor: str, optional
        Face color of the entire topography. Defaults to 'w', white.
    figsize: tuple of float, optional
        Figure size. The first element specify width and the second height.
        Defaults to (6.4, 4.8).
    cmap: str, optional
        Colormap used for plotting DSMs. Defaults to 'viridis'.
        Check matplotlib.pyplot.imshow for details.
    show: bool, optional
        Whether to display the generated figure. Defaults to False.

    Returns
    -------
    fig: matplotlib.pyplot.Figure
        Figure object in which DSMs are plotted on 2D MEG topography.
    """
    on_pick = partial(_click_func, dsms=dsms, cmap=cmap)

    if fig is None:
        fig = plt.figure(figsize=figsize)

        if title is not None:
            fig.suptitle(title, x=0.98, horizontalalignment='right')

    else:
        fig = plt.figure(fig.number)

    my_topo_plot = _iter_topography(info=info, layout=layout, on_pick=on_pick,
                                    fig=fig, axis_facecolor=axis_facecolor,
                                    axis_spinecolor=axis_spinecolor,
                                    fig_facecolor=fig_facecolor,
                                    unified=False)

    for i, (ax, _) in enumerate(my_topo_plot):
        dsms_i = dsms[i]
        dsms_i = distance.squareform(dsms_i)
        ax.imshow(dsms_i, cmap=cmap)

    if show:
        plt.gcf().show()

    return fig


def plot_dsms_topos(dsms, info, time_windows=None, layout=None, figs=None,
                    axis_facecolor='w', axis_spinecolor='w',
                    fig_facecolor='w', figsize=(6.4, 4.8), cmap='viridis',
                    show=False):
    """ Plot DSMs on 2D MEG topographies for multiple time windows

    Parameters
    ----------
    dsms: ndarray | numpy.memmap, shape (n_sensors, n_epochs, n_dsm_datapoint)
        DSMs of MEG recordings; one DSM for each sensor and time point.
    info: mne.io.meas_info.Info
        Info object that contains meta data of MEG recordings.
    time_windows: list of [int, int] | None, optional
        List of time windows for each of which
            the average DSM is calculated and plotted.
        If the default, time_windoww=None, the average of DSMs of
            all the time points is plotted.
        Start of time window is inclusive while end exclusive.
    layout: mne.channels.layout.Layout, optional
        Layout objects containing sensor layout info.
        The default, layout=None, will figure out layout based on info.
    figs: list of matplotlib.pyplot.Figure | None, optional
        Figure objects on which DSMs on 2D MEG topography are plotted.
    axis_facecolor: str, optional
        Face color of the each DSM. Defaults to 'w', white.
    axis_spinecolor: str, optional
        Spine color of each DSM. Defaults to 'w', white.
    fig_facecolor: str, optional
        Face color of the entire topography. Defaults to 'w', white.
    figsize: tuple of float, optional
        Figure size. The first element specify width and the second height.
        Defaults to (6.4, 4.8).
    cmap: str, optional
        Colormap used for plotting DSMs. Defaults to 'viridis'.
        Check matplotlib.pyplot.imshow for details.
    show: bool, optional
        Whether to display the generated figure. Defaults to False.

    Returns
    -------
    figs: list of matplotlib.pyplot.Figure
        Figure objects in each of which DSMs is plotted on 2D MEG topography
            for each time window.
    """
    if len(dsms.shape) != 3:
        raise ValueError("dsms have to be 3-dimensional ndarray or "
                         "numpy.memmap, "
                         "[n_sensors, n_epochs, n_dsm_datapoints]")
    elif time_windows is None:
        time_windows = [[0, dsms.shape[1]]]
    elif not isinstance(time_windows, list):
        raise TypeError("time has to be list of [int, int].")
    elif not all(isinstance(i, list) for i in time_windows):
        raise TypeError("time has to be list of [int, int].")
    elif figs is None:
        figs = [None]*len(time_windows)
    elif len(time_windows) != len(figs):
        raise ValueError("time_windows and figs needs to have a same length "
                         "or figs needs to be None.")

    # create plot for each time window in time_windows
    for i, time_window in enumerate(time_windows):
        dsms_cropped = dsms[:, time_window[0]:time_window[1], :]
        dsms_avg = dsms_cropped.mean(axis=1)
        # set title to time window
        title = f"From {time_window[0]} to {time_window[1]}"

        figs[i] = _plot_dsms_topo(dsms_avg, info, fig=figs[i], layout=layout,
                                  title=title, axis_facecolor=axis_facecolor,
                                  axis_spinecolor=axis_spinecolor,
                                  fig_facecolor=fig_facecolor,
                                  figsize=figsize, cmap=cmap, show=show)

    return figs
