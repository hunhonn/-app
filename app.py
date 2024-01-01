import streamlit as st
import plotly.graph_objects as go 
from streamlit_option_menu import option_menu
import datetime
import database as db

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
rate_values=[item['rate']for item in items]
sgt_offset=datetime.timedelta(hours=8)

formatted_times = [datetime.datetime.fromtimestamp(epoch).strftime('%H:%M %d/%m/%y') for epoch in time_values]
rate_diff = [items[i + 1]['rate'] - items[i]['rate'] for i in range(len(items) - 1)]

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
    #TODO add timezone
    utc_time=datetime.datetime.utcfromtimestamp(items[-1]['time']).strftime('%H:%M %d/%m/%y')
    col2.metric("Time",f"{utc_time+sgt_offset}")

    #creating chart
    
    ####for line graph####
    #fig=go.Figure(data=go.Scatter(x=formatted_times,y=rate_values,mode='lines+markers',name='$Rate vs Time'))
    #fig.update_layout(title='Rate vs Time',xaxis_title='datetime',yaxis_title='$Rate',margin=dict(l=0,r=0,t=5,b=5))

    fig=go.Figure(data=go.Waterfall(
    y=rate_diff,
    measure=rate_diff,
    x=formatted_times,base=rate_values[0]
    ))
    fig.update_layout(title="$Rate vs Time")
    
    st.plotly_chart(fig,use_container_width=True)

elif selected=="Table":
    st.header("dataframe")
    #table 
    rate_diff.insert(0,"-")
    fig1=go.Figure(data=go.Table(header=dict(values=['timestamp','SGD to SEK rate','Δrate']),
                                 cells=dict(values=[formatted_times,rate_values,rate_diff])))
    st.plotly_chart(fig1,use_container_width=True)