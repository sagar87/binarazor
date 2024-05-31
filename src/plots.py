from bokeh.models import WheelZoomTool
from bokeh.plotting import figure

from config import App


def bokeh_scatter(df, image, dotsize_pos, dotsize_neg, positive):
    p = figure(match_aspect=True, sizing_mode="stretch_both")

    p.image(
        image=[image[::-1, :]],
        x=[0],
        y=[0],
        dw=[App.DEFAULT_SCALE * image.shape[1]],
        dh=[App.DEFAULT_SCALE * image.shape[0]],
    )
    p.x_range.range_padding = 0
    p.y_range.range_padding = 0
    p.toolbar.active_scroll = p.select_one(WheelZoomTool)

    p.circle(
        df[df.is_positive]["X"],
        df[df.is_positive]["Y"],
        radius=dotsize_pos,
        fill_color="lightgrey",
        fill_alpha=0.1,
        line_color="red",
    )
    if not positive:
        p.circle(
            df[~df.is_positive]["X"],
            df[~df.is_positive]["Y"],
            radius=dotsize_neg,
            fill_color="lightgrey",
            fill_alpha=0.1,
            line_color=None,
        )

    p.axis.visible = False
    return p
