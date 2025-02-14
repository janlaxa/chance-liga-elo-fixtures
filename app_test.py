#!/usr/bin/env python
# coding: utf-8

# In[31]:


import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import StringIO


# In[ ]:


# Page config
st.set_page_config(page_title="Czech Football Clubs ELO", layout="wide")


# In[32]:


czech_clubs = [
    'SlaviaPraha',
    'SpartaPraha',
    'ViktoriaPlzen',
    'BanikOstrava',
    'Jablonec',
    'HradecKralove',
    'SlovanLiberec',
    'SigmaOlomouc',
    'Slovacko',
    'CeskeBudejovice',
    'Teplice',
    'BohemiansPraha',
    'Karvina',
    'Dukla',
    'Pardubice',
    'MladaBoleslav'
]


# In[33]:


def get_elo_data(club):
    try:
        """Fetch ELO data from the API"""
        response = requests.get(f'http://api.clubelo.com/{club}')
        df = pd.read_csv(StringIO(response.text))
        latest_elo = df.iloc[-1]['Elo']
        latest_date = df.iloc[-1]['From']
        return latest_elo, latest_date, df
    except:
        return None, None, None


# In[34]:


# Create a list to store club data
clubs_data = []

# Fetch data for each club
for club in czech_clubs:
    elo, date, club_elo_df = get_elo_data(club)
    if elo is not None:
        # Format club name for display (remove camel case)
        display_name = ''.join([' ' + c if c.isupper() else c for c in club]).strip()
        clubs_data.append({
            'Club': display_name,
            'ELO Rating': round(elo),
            'Last Updated': date
        })


# In[35]:


# Convert to DataFrame and sort by ELO
clubs_df = pd.DataFrame(clubs_data)
clubs_df = clubs_df.sort_values('ELO Rating', ascending=False)


# In[36]:


# App title
st.title("Czech Football Clubs ELO Ratings")

# Display stats
st.subheader("Current ELO Ratings")
st.dataframe(
    clubs_df,
    hide_index=True,
    column_config={
        'ELO Rating': st.column_config.NumberColumn(format="%d"),
        'Last Updated': st.column_config.DateColumn('Last Updated')
    }
)

# Calculate and display some statistics
st.subheader("League Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Highest ELO", f"{clubs_df['ELO Rating'].max()}")
    st.caption(f"({clubs_df.iloc[0]['Club']})")
    
with col2:
    st.metric("Average ELO", f"{round(clubs_df['ELO Rating'].mean())}")
    
with col3:
    st.metric("Lowest ELO", f"{clubs_df['ELO Rating'].min()}")
    st.caption(f"({clubs_df.iloc[-1]['Club']})")

# Create a bar chart
st.subheader("ELO Ratings Comparison")
chart_data = clubs_df.set_index('Club')
st.bar_chart(chart_data['ELO Rating'])


# In[ ]:




