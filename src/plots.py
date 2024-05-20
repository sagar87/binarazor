import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from bokeh.plotting import figure, show


def bokeh_scatter(df):
    N = 4000
    x = np.random.random(size=N) * 100
    y = np.random.random(size=N) * 100
    boolean_array = df.is_positive.values.astype(int)
    color_array = np.array(["lightgrey", "red"])[boolean_array].tolist()
    size_array = np.array([st.session_state.dotsize_neg, st.session_state.dotsize_pos])[
        boolean_array
    ].tolist()

    radii = np.random.random(size=N) * 1.5
    colors = np.array(
        [(r, g, 150) for r, g in zip(50 + 2 * x, 30 + 2 * y)], dtype="uint8"
    )

    TOOLS = "hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,examine,help"

    p = figure()

    p.circle(
        df["X"],
        df["Y"],
        radius=size_array,
        fill_color=color_array,
        fill_alpha=1.0,
        line_color=None,
    )
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
    # df = pd.DataFrame(results)
    boolean_array = df.is_positive.values.astype(int)
    color_array = np.array(["lightgrey", "red"])[boolean_array.astype(int)].tolist()

    # fig = px.strip(df, x="is_positive", y="percentage_positive", color='is_positive',
    #    color_discrete_sequence=['lightgrey', 'red'])

    fig = px.histogram(
        df,
        x="percentage_positive",
        color="is_positive",
        color_discrete_map={True: "red", False: "lightgrey"},
    )  #
    return fig
