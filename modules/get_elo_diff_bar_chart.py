import plotly.graph_objects as go
import plotly.express as px
import datetime as dt
from modules.encode_image import encode_image
from data.raw.club_mapping import club_mapping
import os
import pandas as pd
def get_elo_diff_bar_chart(filtered_fixtures, PROJECT_ROOT = None):
    if len(filtered_fixtures) > 10:
        subtitle = f"Zobrazeno příštích 10 utkání z {len(filtered_fixtures)}"
    else:
        subtitle = f""
    # Sort fixtures by event_date descending and take the first 10 (most recent)
    filtered_fixtures = filtered_fixtures.sort_values("event_date", ascending=False).head(10)
    # Sort back by event_date ascending for correct plotting order
    filtered_fixtures = filtered_fixtures.sort_values("event_date", ascending=True).reset_index(drop=True)
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
            text=f"{club_mapping[row.opponent_id]['scoreboard']} ({home_away})" if not pd.isna(row.opponent_id) and row.opponent_id in club_mapping else f"Unknown ({home_away})",
            showarrow=False,
            font=dict(size=12, color="black")
        )
        
        if not pd.isna(row.opponent_id) and row.opponent_id in club_mapping:
            fig_elo_diff.add_layout_image(
                dict(
                source=encode_image(os.path.join(PROJECT_ROOT, club_mapping[row.opponent_id]["club_logo"])),
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
        title={
            "text": f"Meziklubový ELO rozdíl<br><span style='font-size:12px; font-weight:normal'>{subtitle}</span>",
        },
        #xaxis_title="Fixture Date",
        #yaxis_title="Elo Difference",
        xaxis=dict(
            tickmode="array",
            tickvals=filtered_fixtures["event_timestamp"],  # Use timestamps
            ticktext=filtered_fixtures["event_date"].dt.strftime("%Y-%m-%d"),  # Display readable dates
            type="linear"  # Ensure it's treated as a continuous scale
        ),
        yaxis=dict(
            range=[-700,700]#[filtered_fixtures["elo_diff"].min() - 200, filtered_fixtures["elo_diff"].max() + 200]
        )
    )
    return fig_elo_diff