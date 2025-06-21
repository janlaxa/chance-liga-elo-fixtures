import plotly.graph_objects as go
import plotly.express as px
import datetime as dt
import pandas as pd
import numpy as np
from modules.encode_image import encode_image
from data.raw.club_mapping import club_mapping
import os
def get_elo_fixtures_bar_chart(filtered_fixtures, PROJECT_ROOT=None):

    club_name = club_mapping[filtered_fixtures["club_id"].iloc[0]]["club_name"]
    club_color = club_mapping[filtered_fixtures["club_id"].iloc[0]]["color"]
    scoreboard = club_mapping[filtered_fixtures["club_id"].iloc[0]]["scoreboard"]
    fig_elo_diff = go.Figure()

    # Add horizontal line for the underlying club ELO
    max_club_elo = filtered_fixtures["club_elo"].max()
    fig_elo_diff.add_hline(y=max_club_elo, line=dict(color="rgba(128,128,128,0.6)", width=2, dash="dash"))

    # Add bars for ELO difference
    fig_elo_diff.add_trace(go.Bar(
        x=filtered_fixtures["event_timestamp"],  # Convert datetime to timestamp
        y=filtered_fixtures["opponent_elo"],
        text=filtered_fixtures["opponent_elo"].astype(str),  # Display ELO diff inside the bar
        marker_color=filtered_fixtures["elo_diff"].apply(lambda x: club_color if x >= 0 else "lightgrey"),
        name="ELO Difference"
    ))
    

    # Add Opponent ELO as annotations above the bars
    for row in filtered_fixtures.itertuples():
        y_annotation = row.opponent_elo + 100
        y_image = row.opponent_elo + 300
        home_away = 'H' if filtered_fixtures["club_id"].iloc[0] == row.home_team_id else 'A'
        
        fig_elo_diff.add_annotation(
            x=row.event_timestamp,
            y=y_annotation,
            text=f"{club_mapping[row.opponent_id]['scoreboard']} ({home_away})" if pd.notna(row.opponent_id) and row.opponent_id in club_mapping else f"Unknown ({home_away})",
            showarrow=False,
            font=dict(size=12, color="black")
        )

        fig_elo_diff.add_annotation(
            x=row.event_timestamp,
            y=0,
            yanchor="bottom",
            text=f"{np.round((row.home_team_p_win if home_away == 'H' else row.away_team_p_win) * 100, 2)}%",
            showarrow=False,
            font=dict(size=12, color="white" if row.elo_diff >=0 else "black")
        )
        
        if pd.notna(row.opponent_id) and row.opponent_id in club_mapping:
            fig_elo_diff.add_layout_image(
                dict(
                source=encode_image(os.path.join(PROJECT_ROOT, club_mapping[row.opponent_id]["club_logo"])),
                x=int(row.event_timestamp),  # Convert datetime to Unix timestamp
                y=y_image,  # Adjust y position as needed
                xref="x",
                yref="y",
                sizex=1740873600.0,  # Adjust size as needed
                sizey=250,
                xanchor="center",
                yanchor="middle",
                layer="above"
                )
            )

    

    # Annotate the horizontal line with club name and ELO to the right
    fig_elo_diff.add_annotation(
        x=filtered_fixtures["event_timestamp"].max(),  # Position at the latest event timestamp
        y=max_club_elo,
        text=f"{scoreboard}:{max_club_elo}",
        showarrow=False,
        font=dict(size=12, color="black"),
        xanchor="left",
        yanchor="bottom"
    )

    # Update layout
    fig_elo_diff.update_traces(textposition="inside")
    fig_elo_diff.update_layout(
        title="ELO soupeře a pravděpodobnost výhry",
        #xaxis_title="Fixture Date",
        #yaxis_title="Opponent ELO",
        xaxis=dict(
            tickmode="array",
            tickson="boundaries",
            tickvals=filtered_fixtures["event_timestamp"],  # Convert to datetime
            ticktext=filtered_fixtures["event_date"].dt.strftime("%Y-%m-%d"),  # Display readable dates
            type="linear"  # Ensure it's treated as a continuous scale
        ),
        yaxis=dict(
            range=[0, 2500]
        )
    )
    return fig_elo_diff
