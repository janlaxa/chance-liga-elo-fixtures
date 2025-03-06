import plotly.graph_objects as go
import plotly.express as px
import datetime as dt
import pandas as pd
from modules.encode_image import encode_image
from data.raw.club_mapping import club_mapping

def get_elo_fixtures_bar_chart(filtered_fixtures):

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

        fig_elo_diff.add_annotation(
            x=row.event_timestamp,
            y=y_annotation,
            text=f"{club_mapping[row.opponent_id]["scoreboard"]}",
            showarrow=False,
            font=dict(size=12, color="black")
        )
        
        fig_elo_diff.add_layout_image(
            dict(
            source=encode_image(club_mapping[row.opponent_id]["club_logo"]),
            x=int(row.event_timestamp),  # Convert datetime to Unix timestamp
            y=y_image,  # Adjust y position as needed
            xref="x",
            yref="y",
            sizex=1740873600.0,  # Adjust size as needed
            sizey=300,
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
        #title="Future Fixtures - ELO",
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
