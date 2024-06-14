from bokeh.models import WheelZoomTool
from bokeh.plotting import figure


def bokeh_scatter(df, image, height, dotsize_pos, dotsize_neg, positive, downsample):
    p = figure(match_aspect=True, sizing_mode="stretch_both")

    p.image(
        image=[image[::-1, :]],
        x=[0],
        y=[0],
        dw=[downsample * image.shape[1]],
        dh=[downsample * image.shape[0]],
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
    p.plot_height = height
    p.axis.visible = False
    return p
