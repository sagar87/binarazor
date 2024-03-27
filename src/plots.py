import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def subsample_data():
    if st.session_state.subsample != 0:
        df = st.session_state.data.loc[
            st.session_state.data.sample(
                min(st.session_state.data.shape[0], int(st.session_state.subsample)),
                random_state=42,
            ).index
        ]
    else:
        df = st.session_state.data
    return df


def plotly_scatter_gl(boolean_array=None):
    df = subsample_data()

    if boolean_array is None:
        boolean_array = (
            df[st.session_state.primary_channel] > st.session_state.slider_value
        ).values
    color_array = np.array(["lightgrey", "red"])[boolean_array.astype(int)].tolist()
    # Create the layout for the plot
    layout = go.Layout(
        title="ScatterGL Plot",
        xaxis=dict(title="X Axis"),
        yaxis=dict(title="Y Axis"),
        scene=dict(aspectmode="data"),
        height=1500
        # aspectmode='equal',  # Set aspect ratio to be equal
        # aspectratio=dict(x=1, y=1)  # Set the aspect ratio to 1:1
    )

    # print(boolean_array)
    fig = go.Figure(
        data=go.Scattergl(
            x=df["X"],
            y=df["Y"],
            mode="markers",
            marker=dict(size=st.session_state.dotsize, color=color_array, line_width=0),
        ),
        layout=layout,
    )

    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
        autorange="reversed",
    )

    return fig


def plotly_scatter_marker_gl(boolean_array=None):
    df = subsample_data()
    
    if boolean_array is None:
        boolean_array = (
            df[st.session_state.primary_channel] > st.session_state.slider_value
        ).values
    color_array = np.array(["lightgrey", "red"])[boolean_array.astype(int)].tolist()
    # Create the layout for the plot
    layout = go.Layout(
        xaxis=dict(title=st.session_state.secondary_channel),
        yaxis=dict(title=st.session_state.primary_channel),
        scene=dict(aspectmode="data"),
        height=500
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


def plot_hist(boolean_array=None):
    df = subsample_data()
    if boolean_array is None:
        boolean_array = (
            df[st.session_state.primary_channel] > st.session_state.slider_value
        ).values
    color_array = np.array(["lightgrey", "red"])[boolean_array.astype(int)].tolist()
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