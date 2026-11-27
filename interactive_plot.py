from itertools import product

import numpy as np
import plotly.graph_objects as go


def interactive_plot(
    plots,
    x,
    sliders,
    title="Interactive Plot",
    x_label="x",
    y_label="y",
    *,
    x_range=None,
    y_range=None,
    y2_label=None,
    y2_range=None,
    show_legend=True,
    legend=None,
    show_slider_tick_labels=True,
):
    """Build a Plotly line chart from multiple slider-driven series."""
    if not sliders:
        raise ValueError("Provide at least one slider.")
    if legend is not None and not isinstance(legend, dict):
        raise TypeError("legend must be a Plotly layout options dictionary.")
    if callable(plots):
        plots = [{"func": plots}]
    elif not isinstance(plots, (list, tuple)):
        raise TypeError("plots must be a list or tuple of plot definitions.")
    if not plots:
        raise ValueError("Provide at least one plot.")
    if not isinstance(show_legend, bool):
        raise TypeError("show_legend must be a boolean.")
    if not isinstance(show_slider_tick_labels, bool):
        raise TypeError("show_slider_tick_labels must be a boolean.")

    plot_specs = []
    for index, plot_spec in enumerate(plots, start=1):
        if not isinstance(plot_spec, dict):
            raise TypeError("Each plot must be a dictionary.")
        plot_func = plot_spec.get("func")
        if not callable(plot_func):
            raise TypeError("Each plot must have a callable func.")
        yaxis = plot_spec.get("yaxis", "y")
        if yaxis not in ("y", "y2"):
            raise ValueError("Plot yaxis must be 'y' or 'y2'.")
        name = plot_spec.get("name")
        plot_specs.append(
            {
                "func": plot_func,
                "name": str(name) if name is not None else f"Series {index}",
                "yaxis": yaxis,
            }
        )

    slider_names = list(sliders)
    slider_values = []
    initial_indices = []
    labels = []
    units = []
    for name, spec in sliders.items():
        minimum = float(spec["min"])
        maximum = float(spec["max"])
        step = float(spec["step"])
        initial = float(spec["value"])
        if step <= 0 or maximum < minimum:
            raise ValueError(f"Invalid slider range for {name!r}.")

        values = np.arange(minimum, maximum + step / 2, step)
        if values.size == 0 or initial < minimum or initial > maximum:
            raise ValueError(f"Invalid initial value for slider {name!r}.")
        initial_index = int(round((initial - minimum) / step))
        if initial_index >= values.size or not np.isclose(
            values[initial_index], initial
        ):
            raise ValueError(
                f"Initial value for slider {name!r} must align with its step."
            )

        slider_values.append(values.tolist())
        initial_indices.append(initial_index)
        labels.append(str(spec.get("label", name)))
        units.append(str(spec.get("unit", "")))

    x_values = np.asarray(x)
    if x_values.ndim != 1:
        raise ValueError("x must be one-dimensional.")

    def validate_axis_range(value, name):
        if value is None:
            return None
        try:
            limits = np.asarray(value, dtype=float)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{name} must contain two finite numbers.") from error
        if (
            limits.shape != (2,)
            or not np.all(np.isfinite(limits))
            or limits[0] >= limits[1]
        ):
            raise ValueError(f"{name} must contain two increasing finite numbers.")
        return limits.tolist()

    x_range = validate_axis_range(x_range, "x_range")
    y_range = validate_axis_range(y_range, "y_range")
    y2_range = validate_axis_range(y2_range, "y2_range")

    def evaluate(plot_func, parameter_values):
        parameters = dict(zip(slider_names, parameter_values))
        y_values = np.asarray(plot_func(x_values, **parameters))
        if y_values.ndim != 1 or len(y_values) != len(x_values):
            raise ValueError("The plotting function must return one y value per x.")
        return y_values.tolist()

    curves = [
        [
            evaluate(plot_spec["func"], combination)
            for plot_spec in plot_specs
        ]
        for combination in product(*slider_values)
    ]
    curve_index = 0
    for index, value_index in enumerate(initial_indices):
        curve_index = curve_index * len(slider_values[index]) + value_index

    slider_names_in_plot = [
        f"interactive-parameter-{index}"
        for index in range(len(slider_names))
    ]
    slider_specs = [
        dict(
            name=slider_names_in_plot[index],
            active=initial_indices[index],
            currentvalue={"prefix": f"{labels[index]}: ", "suffix": f" {units[index]}"},
            pad={"t": 35},
            x=0,
            y=(-0.32 if show_slider_tick_labels else -0.18) * index,
            len=1,
            ticklen=0,
            minorticklen=0,
            steps=[
                dict(
                    label=f"{value:g}",
                    value=str(value_index),
                    method="skip",
                    args=[],
                )
                for value_index, value in enumerate(values)
            ],
        )
        for index, values in enumerate(slider_values)
    ]

    traces = [
        go.Scatter(
            x=x_values.tolist(),
            y=curves[curve_index][index],
            mode="lines",
            name=plot_spec["name"],
            yaxis=plot_spec["yaxis"],
            showlegend=show_legend,
        )
        for index, plot_spec in enumerate(plot_specs)
    ]
    x_axis = dict(
        showgrid=True,
        zeroline=True,
        gridcolor="lightgray",
        zerolinecolor="lightgray",
        zerolinewidth=0.5,
    )
    y_axis = dict(
        showgrid=True,
        zeroline=True,
        gridcolor="lightgray",
        zerolinecolor="lightgray",
        zerolinewidth=0.5,
    )
    if x_range is not None:
        x_axis.update(range=x_range, autorange=False)
    if y_range is not None:
        y_axis.update(range=y_range, autorange=False)

    layout = dict(
        title=title,
        showlegend=show_legend,
        xaxis_title=x_label,
        yaxis_title=y_label,
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=80,
            r=30,
            t=60,
            b=100 + 50 * len(slider_specs),
        ),
        sliders=slider_specs,
        xaxis=x_axis,
        yaxis=y_axis,
        meta={
            "interactive_plot": {
                "curves": curves,
                "initial_indices": initial_indices,
                "value_counts": [len(values) for values in slider_values],
                "slider_names": slider_names_in_plot,
                "trace_indices": list(range(len(plot_specs))),
                "show_slider_tick_labels": show_slider_tick_labels,
            }
        },
    )
    if legend is not None:
        layout["legend"] = dict(legend) | {"bordercolor": "lightgray", "borderwidth": 1}
    if (
        any(plot_spec["yaxis"] == "y2" for plot_spec in plot_specs)
        or y2_label is not None
        or y2_range is not None
    ):
        y2_axis = dict(
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
        )
        if y2_label is not None:
            y2_axis["title"] = y2_label
        if y2_range is not None:
            y2_axis.update(range=y2_range, autorange=False)
        layout["yaxis2"] = y2_axis

    fig = go.Figure(data=traces)
    fig.update_layout(**layout)
    return fig
