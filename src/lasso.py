import streamlit as st
import plotly.express as px


def plotly_lasso(mat, height):
    fig = px.imshow(mat, color_continuous_scale='gray')
    fig.update_layout(width=height, height=height)
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False, scaleanchor="x", scaleratio=1)
    
    return fig