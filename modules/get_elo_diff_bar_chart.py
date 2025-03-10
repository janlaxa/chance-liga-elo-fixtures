import plotly.graph_objects as go
import plotly.express as px
import datetime as dt
from modules.encode_image import encode_image
from data.raw.club_mapping import club_mapping

def get_elo_diff_bar_chart(filtered_fixtures):
    
    fig_elo_diff = go.Figure()
    club_color = club_mapping[filtered_fixtures["club_id"].max()]["color"]
    # Add bars for ELO difference
    fig_elo_diff.add_trace(go.Bar(
        x=filtered_fixtures["event_timestamp"],  # Convert datetime to timestamp
        y=filtered_fixtures["elo_diff"],
        text=filtered_fixtures["elo_diff"].astype(str),  # Display ELO diff inside the bar
        marker_color=filtered_fixtures["elo_diff"].apply(lambda x: club_color if x >= 0 else "lightgrey"),
        name="ELO Difference"
    ))

    # Add Opponent ELO as annotations above the bars
    for row in filtered_fixtures.itertuples():
        y_annotation = row.elo_diff - 40 if row.elo_diff <= 0 else row.elo_diff + 40
        y_image = row.elo_diff - 150 if row.elo_diff <= 0 else row.elo_diff + 150
        home_away = 'H' if filtered_fixtures["club_id"].iloc[0] == row.home_team_id else 'A'
        fig_elo_diff.add_annotation(
            x=row.event_timestamp,
            y=y_annotation,
            text=f"{club_mapping[row.opponent_id]["scoreboard"]} ({home_away})",
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
            sizey=120,
            xanchor="center",
            yanchor="middle",
            layer="above"
            )
        )

    # Update layout
    fig_elo_diff.update_traces(textposition="inside")
    fig_elo_diff.update_layout(
        title="Meziklubový ELO rozdíl",
        #xaxis_title="Fixture Date",
        #yaxis_title="Elo Difference",
        xaxis=dict(
            tickmode="array",
            tickvals=filtered_fixtures["event_timestamp"],  # Use timestamps
            ticktext=filtered_fixtures["event_date"].dt.strftime("%Y-%m-%d"),  # Display readable dates
            type="linear"  # Ensure it's treated as a continuous scale
        ),
        yaxis=dict(
            range=[-650,650]#[filtered_fixtures["elo_diff"].min() - 200, filtered_fixtures["elo_diff"].max() + 200]
        )
    )
    return fig_elo_diff