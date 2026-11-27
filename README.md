# Quarto Plotly Interactive Plot Template

A Quarto HTML example for Plotly charts with any number of slider-controlled
parameters, multiple series, optional secondary y-axis, fixed axis ranges, and
configurable legends.

## Files

- `plot.qmd` contains graph-specific functions, sliders, and display options.
- `interactive_plot.py` contains the reusable Python plotting helper.
- `plotly_slider.html` contains the Plotly.js slider bridge and slider-label CSS.
- `_quarto.yml` makes Python imports resolve relative to this directory.

## Setup and render

Install Quarto and Python, then install the Python dependencies:

```shell
python -m pip install -r requirements.txt
quarto render plot.qmd
```

Run the render command from this directory.

## Defining plots

Pass each series in `plots`. Every series function receives `x` and all slider
parameters as keyword arguments:

```python
plots=[
    {"func": first_series, "name": "First"},
    {"func": second_series, "name": "Second", "yaxis": "y2"},
]
```

Use `x_range`, `y_range`, and `y2_range` for fixed ranges. `legend` accepts
Plotly legend layout options, and `show_slider_tick_labels=False` hides only the
labels below sliders while preserving the selected-value display.
