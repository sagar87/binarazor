import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from bokeh.models import WheelZoomTool
from bokeh.plotting import figure

from config import App


def bokeh_scatter(df, image=None):
    if image is not None:
        df = df[df.is_positive]
    boolean_array = df.is_positive.values.astype(int)
    color_array = np.array(["lightgrey", "red"])[boolean_array].tolist()
    size_array = np.array([st.session_state.dotsize_neg, st.session_state.dotsize_pos])[
        boolean_array
    ].tolist()

    p = figure(match_aspect=True, sizing_mode="stretch_both")

    if image is not None:
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

    if image is not None:
        p.circle(
            df["X"],
            df["Y"],
            radius=size_array,
            fill_color=color_array,
            fill_alpha=0.1,
            line_color="red",
        )
    else:
        p.circle(
            df["X"],
            df["Y"],
            radius=size_array,
            fill_color=color_array,
            fill_alpha=1.0,
            line_color=None,
        )

    p.axis.visible = False
    return p


def plotly_scatter_gl(df):
    if st.session_state.postive_cells:
        df = df[df.is_positive]
        layout = go.Layout(
            # xaxis=dict(title="X Axis"),
            # yaxis=dict(title="Y Axis"),
            scene=dict(aspectmode="data"),
            height=st.session_state.plot_height
            # aspectmode='equal',  # Set aspect ratio to be equal
            # aspectratio=dict(x=1, y=1)  # Set the aspect ratio to 1:1
        )

        # print(boolean_array)
        fig = go.Figure(
            data=go.Scattergl(
                x=df["X"],
                y=df["Y"],
                mode="markers",
                marker=dict(
                    size=st.session_state.dotsize_pos, color="red", line_width=0
                ),
            ),
            layout=layout,
        )

        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
            # autorange="reversed",
        )

    else:
        boolean_array = df.is_positive.values.astype(int)
        color_array = np.array(["lightgrey", "red"])[boolean_array].tolist()
        size_array = np.array(
            [st.session_state.dotsize_neg, st.session_state.dotsize_pos]
        )[boolean_array].tolist()
        # Create the layout for the plot
        layout = go.Layout(
            # xaxis=dict(title="X Axis"),
            # yaxis=dict(title="Y Axis"),
            scene=dict(aspectmode="data"),
            # height=st.session_state.plot_height
            # aspectmode='equal',  # Set aspect ratio to be equal
            # aspectratio=dict(x=1, y=1)  # Set the aspect ratio to 1:1
        )

        # print(boolean_array)
        fig = go.Figure(
            data=go.Scattergl(
                x=df["X"],
                y=df["Y"],
                mode="markers",
                marker=dict(size=size_array, color=color_array, line_width=0),
            ),
            # layout=layout,
        )

        fig.update_yaxes(
            scaleanchor="x",
            scaleratio=1,
            # autorange="reversed",
        )

    return fig


def plotly_scatter_marker_gl(df):
    boolean_array = df.is_positive.values.astype(int)
    color_array = np.array(["lightgrey", "red"])[boolean_array.astype(int)].tolist()
    # Create the layout for the plot
    layout = go.Layout(
        xaxis=dict(title=st.session_state.secondary_channel),
        yaxis=dict(title=st.session_state.primary_channel),
        scene=dict(aspectmode="data"),
        # height=500
        # aspectmode='equal',  # Set aspect ratio to be equal
        # aspectratio=dict(x=1, y=1)  # Set the aspect ratio to 1:1
    )

    # print(boolean_array)
    fig = go.Figure(
        data=go.Scattergl(
            x=df[st.session_state.secondary_channel],
            y=df[st.session_state.primary_channel],
            mode="markers",
            marker=dict(size=5, color=color_array, line_width=0),
        ),
        layout=layout,
    )

    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )

    return fig


def plot_hist(df):
    boolean_array = df.is_positive.values.astype(int)
    fig = px.histogram(
        df,
        x=st.session_state.primary_channel,
        color=boolean_array,
        color_discrete_map={True: "red", False: "lightgrey"},
    )  #
    return fig


def plot_ecdf(img):
    fig = px.ecdf(img.reshape(-1)[img.reshape(-1) < 50])
    return fig


def strip_plot(df):
    fig = px.histogram(
        df,
        x="percentage_positive",
        color="is_positive",
        color_discrete_map={True: "red", False: "lightgrey"},
    )  #
    return fig
