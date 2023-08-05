#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 18 16:44:50 2023

@author: sohrab-salehin
"""
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# Importing files

# Link of importing tables:
    # For funnel raw data: https://metabase.pinsvc.net/question/6715-steps-number-of-session-per-city-raw-data 
    # For city sessions: https://metabase.pinsvc.net/question/6468-city-number-of-session



funnel_raw_data = pd.read_csv("funnel_raw.csv") # Should be imported everytime for updating
funnel_raw_data["date_hour"] = pd.to_datetime(funnel_raw_data["date_hour"])
funnel_raw_data["date"] = funnel_raw_data["date_hour"].dt.strftime("%Y-%m-%d")
funnel_raw_data = funnel_raw_data.drop("date_hour", axis=1)

city_ids = pd.read_csv("hotel_id_and_names.csv")
city_name_fa_en = pd.read_csv("city_name_fa_en.csv").dropna()
city_name_fa_en.rename(columns={"City Name Fa": "city_name_fa"}, inplace=True)
city_sessions = pd.read_csv("top_sessions_cities.csv").rename(  # should be imported everytime for updating
    columns={"city_ids": "city_id"}
)

# Creating tables we need for the dashboard

top_ten = city_sessions[:10]    # top ten searched cities

# creaging a table for having cities with their IDs
# bacuase funnel raw data is according to city IDs not name of cities

cities = pd.merge(left=city_ids,
                  right=city_name_fa_en,
                  on="city_name_fa",
                  how="inner")      
                                    
cities = cities[["city_id", "City Name En"]].drop_duplicates(subset=["City Name En"])
cities = cities.merge(right=city_sessions, on="city_id", how="inner").sort_values(
    by="Number_of_session", ascending=False
)
city_ids = cities.set_index("city_id")["City Name En"].to_dict()


# Distinguishig each channel type in funnel raw data

index = funnel_raw_data[
    funnel_raw_data["channel"].str.contains("jek", case=False)
].index
funnel_raw_data.loc[index, "channel_type"] = "jek"
index = funnel_raw_data[
    funnel_raw_data["channel"].str.contains("web", case=False)
].index
funnel_raw_data.loc[index, "channel_type"] = "web"
index = funnel_raw_data[
    funnel_raw_data["channel"].str.contains("asan", case=False)
].index
funnel_raw_data.loc[index, "channel_type"] = "AP"


# Funnel Dahsboard

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Hotel Funnel by City Dashboard"),
    html.Label("Select City:"),
    dcc.Dropdown(
        id="city-dropdown",
        options=[{"label": city_ids[city_id], "value": city_id} for city_id in city_ids],
        value=list(city_ids.keys())[0],
        style= {'width' : '500px'}
    ),
    html.Div([
        dcc.Graph(id='jek-sales_graph', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='web-sales_graph', style={'width': '50%', 'float': 'right'})
    ]),
    
    html.Div([
        dcc.Graph(id='jek-search_graph', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='web-search_graph', style={'width': '50%', 'float': 'right'})
    ]),
    html.Div([
        dcc.Graph(id='jek-stp1_graph', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='web-stp1_graph', style={'width': '50%', 'float': 'right'})
    ]),
    html.Div([
        dcc.Graph(id='jek-stp2_graph', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='web-stp2_graph', style={'width': '50%', 'float': 'right'})
    ]),
    html.Div([
        dcc.Graph(id='jek-stp3_graph', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='web-stp3_graph', style={'width': '50%', 'float': 'right'})
    ]),
    html.Div([
        dcc.Graph(id='jek-stp4_graph', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='web-stp4_graph', style={'width': '50%', 'float': 'right'})
    ]),
    html.Div([
        dcc.Graph(id='jek-stp5_graph', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='web-stp5_graph', style={'width': '50%', 'float': 'right'})
    ])
])

@app.callback(
    [
     Output("jek-sales_graph", "figure"),
     Output("web-sales_graph", "figure"),
     Output("jek-search_graph", "figure"),
     Output("web-search_graph", "figure"),
     Output("jek-stp1_graph", "figure"),
     Output("web-stp1_graph", "figure"),
     Output("jek-stp2_graph", "figure"),
     Output("web-stp2_graph", "figure"),
     Output("jek-stp3_graph", "figure"),
     Output("web-stp3_graph", "figure"),
     Output("jek-stp4_graph", "figure"),
     Output("web-stp4_graph", "figure"),
     Output("jek-stp5_graph", "figure"),
     Output("web-stp5_graph", "figure"),
    ], 
    [Input("city-dropdown", "value")]
)

def update_graph(city_id):
    funnel = funnel_raw_data[funnel_raw_data["city_id"] == city_id]
    
    fig_jek_sales = sales_chart(funnel, 'jek', 'Jek Sales')
    fig_web_sales = sales_chart(funnel, 'web', 'Web Sales')
    fig_jek_search = search_chart(funnel, 'jek', 'Jek Search')
    fig_web_search = search_chart(funnel, 'web', 'Web Search')
    fig_jek_stp1 = draft_visit_chart(funnel, "jek", "JEK Draft to Visit Stage")
    fig_web_stp1 = draft_visit_chart(funnel, "web", "Web Draft to Visit Stage")
    fig_jek_stp2 = confirm_draft_chart(funnel, "jek", "JEK Confirm to Draft Stage")
    fig_web_stp2 = confirm_draft_chart(funnel, "web", "Web Confirm to Draft Stage")
    fig_jek_stp3 = prepayement_confirm_chart(funnel, "jek", "JEK Prepay to Conf Stage")
    fig_web_stp3 = prepayement_confirm_chart(funnel, "web", "Web Prepay to Conf Stage")
    fig_jek_stp4 = booked_prepay_chart(funnel, "jek", "JEK Booked to Prepay Stage")
    fig_web_stp4 = booked_prepay_chart(funnel, "web", "Web Booked to Prepay Stage")
    fig_jek_stp5 = fulfilled_booked_chart(funnel, "jek", "JEK Fulfilled to Booked Stage")
    fig_web_stp5 = fulfilled_booked_chart(funnel, "web", "Web Fulfilled to Booked Stage")
    
    figs= [
        fig_jek_sales,
        fig_web_sales,
        fig_jek_search,
        fig_web_search,
        fig_jek_stp1,
        fig_web_stp1,
        fig_jek_stp2,
        fig_web_stp2,
        fig_jek_stp3,
        fig_web_stp3,
        fig_jek_stp4,
        fig_web_stp4,
        fig_jek_stp5,
        fig_web_stp5
        ]
    return figs

def sales_chart(funnel, channel_type, title):
    fulfilled= (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "fulfilled")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    fig= go.Figure()
    fig.add_trace(go.Scatter(
        x= fulfilled.index,
        y= fulfilled.values,
        name= 'Orders'
        )
    )
    moving_avg = fulfilled.rolling(window=7).mean()
    fig.add_trace(
        go.Scatter(x=moving_avg.index, y=moving_avg.values, name="Moving Average - 7 Days")
    )
    fig.update_layout(title= title)
    return fig

def search_chart(funnel, channel_type, title):
    search= (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "hotel_or_city_page")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    fig= go.Figure()
    fig.add_trace(go.Scatter(
        x= search.index,
        y= search.values,
        name= 'Sessions'
        )
    )
    moving_avg = search.rolling(window=7).mean()
    fig.add_trace(
        go.Scatter(x=moving_avg.index, y=moving_avg.values, name="Moving Average - 7 Days")
    )
    fig.update_layout(title= title)
    return fig

def draft_visit_chart(funnel, channel_type, title):
    stp1 = (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "hotel_or_city_page")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    stp2 = (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "draft_page")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    draft_to_visit = stp2 / stp1
    fig= go.Figure()
    fig.add_trace(go.Scatter(
        x= draft_to_visit.index,
        y= draft_to_visit.values,
        name= 'Ratio'
        )
    )
    moving_avg = draft_to_visit.rolling(window=7).mean()
    fig.add_trace(
        go.Scatter(x=moving_avg.index, y=moving_avg.values, name="Moving Average - 7 Days")
    )
    fig.update_layout(title= title)
    return fig

def confirm_draft_chart(funnel, channel_type, title):
    stp2 = (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "draft_page")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    stp3 = (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "confirm_info_success")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    confirm_to_draft = stp3 / stp2
    fig= go.Figure()
    fig.add_trace(go.Scatter(
        x= confirm_to_draft.index,
        y= confirm_to_draft.values,
        name= 'Ratio'
        )
    )
    moving_avg = confirm_to_draft.rolling(window=7).mean()
    fig.add_trace(
        go.Scatter(x=moving_avg.index, y=moving_avg.values, name="Moving Average - 7 Days")
    )
    fig.update_layout(title= title)
    return fig

def prepayement_confirm_chart(funnel, channel_type, title):
    stp3 = (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "confirm_info_success")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    stp4 = (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "pre_payment_stage")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    prepay_to_confirm = stp4 / stp3
    fig= go.Figure()
    fig.add_trace(go.Scatter(
        x= prepay_to_confirm.index,
        y= prepay_to_confirm.values,
        name= 'Ratio'
        )
    )
    moving_avg = prepay_to_confirm.rolling(window=7).mean()
    fig.add_trace(
        go.Scatter(x=moving_avg.index, y=moving_avg.values, name="Moving Average - 7 Days")
    )
    fig.update_layout(title= title)
    return fig

def booked_prepay_chart(funnel, channel_type, title):
    stp4 = (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "pre_payment_stage")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    stp5 = (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "book_locked_successfully")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    book_to_prepay = stp5 / stp4
    fig= go.Figure()
    fig.add_trace(go.Scatter(
        x= book_to_prepay.index,
        y= book_to_prepay.values,
        name= 'Ratio'
        )
    )
    moving_avg = book_to_prepay.rolling(window=7).mean()
    fig.add_trace(
        go.Scatter(x=moving_avg.index, y=moving_avg.values, name="Moving Average - 7 Days")
    )
    fig.update_layout(title= title)
    return fig

def fulfilled_booked_chart(funnel, channel_type, title):
    stp5 = (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "book_locked_successfully")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    stp6 = (
        funnel[
            (funnel["channel_type"] == channel_type)
            & (funnel["log_type"] == "fulfilled")
        ]
        .reset_index(drop=True)
        .groupby("date")["number_of_session"]
        .sum()
    )
    fulfilled_to_book = stp6 / stp5
    fig= go.Figure()
    fig.add_trace(go.Scatter(
        x= fulfilled_to_book.index,
        y= fulfilled_to_book.values,
        name= 'Ratio'
        )
    )
    moving_avg = fulfilled_to_book.rolling(window=7).mean()
    fig.add_trace(
        go.Scatter(x=moving_avg.index, y=moving_avg.values, name="Moving Average - 7 Days")
    )
    fig.update_layout(title= title)
    return fig
if __name__ == '__main__':
    app.run_server(debug= True)