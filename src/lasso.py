import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def plotly_lasso(mat, height):
    fig = px.imshow(mat, color_continuous_scale='gray')
    fig.update_layout(width=height, height=height)
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False, scaleanchor="x", scaleratio=1)
    # config = {'scrollZoom': True}
    # fig.show(config=config)
    return fig



def plotly_polygons(mat, height, pts):
    
    # fig = go.Figure()
    
    fig = px.imshow(mat, color_continuous_scale='gray')
    
    fig.update_layout(width=height, height=height)
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False, scaleanchor="x", scaleratio=1)
    
    
    for r in pts:
        x = [ item[0] for item in r['cells'] ] + [ r['cells'][0][0] ]
        y = [ item[1] for item in r['cells'] ] + [ r['cells'][0][1] ]
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode='lines',
                name=r['status']
            )
        )
    return fig
        