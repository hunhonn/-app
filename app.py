import streamlit as st
import plotly.graph_objects as go 
from streamlit_option_menu import option_menu
import datetime
import database as db
import pandas as pd
import statsmodels.api as sm

currency= ["SEK","SGD"]
page_title= "SGD to SEK Currency Tracker"
page_icon= ":money_with_wings:"
layout="centered"

st.set_page_config(page_title=page_title,page_icon=page_icon,layout=layout)
st.title(page_title+ " " +page_icon)

#hide streamlit styling
hide_st_style="""
            <style>
            #MainMenu {visibility: hidden};
            footer {visibility: hidden}
            header {visibility: hidden}
            </style>
            """
st.markdown(hide_st_style,unsafe_allow_html=True)          


#database interface
items=db.fetch_all()
time_values=[item['time'] for item in items]
time_values_sgt=[times + 28800 for times in time_values]
rate_values=[item['rate']for item in items]

formatted_times = [datetime.datetime.fromtimestamp(epoch).strftime('%H:%M %d/%m/%y') for epoch in time_values_sgt]
rate_diff = [items[i + 1]['rate'] - items[i]['rate'] for i in range(len(items) - 1)]

#dataframe for prediction
data=pd.read_csv("https://raw.githubusercontent.com/hunhonn/-app/main/SGD_SEK%20Historical%20Data.csv")
historical_rate=data['Price'].values.tolist()
new_rate=rate_values[13:]
total_rates=pd.DataFrame({'Rate':historical_rate+new_rate})

#ML
p,d,q=(0,1,0)
model = sm.tsa.SARIMAX(total_rates, order=(p, d, q), 
                seasonal_order=(p, d, q, 52))
fitted=model.fit()
predictions=fitted.predict(len(total_rates),len(total_rates)+60)

#Navigation
selected=option_menu(
    menu_title= None,
    options=["Graph","Table"],
    icons=["bar-chart-fill","file-spreadsheet-fill"],
    orientation="horizontal"
)

if selected=="Graph":
    st.header("Graph Visualization")
    
    col1, col2= st.columns(2)
    col1.metric("Latest rate",f"{round(items[-1]['rate'],3)}")
    #utc_time=datetime.datetime.utcfromtimestamp(items[-1]['time']).strftime('%H:%M %d/%m/%y')
    utc_time=formatted_times[-1]
    col2.metric("Time",f"{utc_time}")

    #creating chart
    
    ####for prediction line graph####

    fig=go.Figure(data=go.Waterfall(
    y=rate_diff,
    measure=rate_diff,
    x=formatted_times,base=rate_values[0]
    ))
    fig.update_layout(title="$Rate vs Time")
    
    fig3=go.Figure()
    fig3.add_trace(go.Scatter(
        x=total_rates.index,
        y=total_rates['Rate'],
        mode='lines',
        name='Training Data',
        line=dict(color='blue')
    ))
    fig3.add_trace(go.Scatter(
    x=predictions.index,
    y=predictions,
    mode='lines',
    name='Predictions',
    line=dict(color='green')
    ))
    fig3.update_layout(
    title="SEK Rate - SARIMA Prediction",
    xaxis_title="Date",
    yaxis_title="Price",
    legend_title="Data",
    )
    fig3.update_layout(plot_bgcolor='white')

    st.plotly_chart(fig,use_container_width=True)
    st.plotly_chart(fig3,use_container_width=True)

elif selected=="Table":
    st.header("SGD to SEK Dataset")
    #table
    rate_diff.insert(0,"-")
    percent_diff=[round(((rate_values[i+1]/rate_values[i])*100)-100,2) for i in range(len(rate_values)-1)]
    percent_diff.insert(0,"-")
    fig1=go.Figure(data=go.Table(header=dict(values=['timestamp','SGD to SEK rate','Δrate','Δrate,%']),
                                 cells=dict(values=[formatted_times,rate_values,rate_diff,percent_diff])))
    st.plotly_chart(fig1,use_container_width=True)