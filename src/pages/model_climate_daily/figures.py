import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import pandas as pd
from .options_selector import acc_vars_options, daily_vars_options
from utils.custom_logger import logging
from utils.figures_utils import add_attribution


def make_acc_figure(df, year, var, title=None):
    fig = make_subplots()

    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df["q1"],
            mode="lines",
            name="5th Percentile",
            line=dict(width=0, color="gray"),
            showlegend=False,
            hoverinfo="skip"
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df["q3"],
            mode="lines",
            name="5-95th percentiles range",
            line=dict(width=0, color="gray"),
            fillcolor="rgba(0, 0, 0, 0.1)",
            showlegend=True,
            fill="tonexty",
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=df.dummy_date,
            y=df["q2"],
            mode="lines",
            name="50th Percentile",
            line=dict(width=0.5, color="gray"),
            showlegend=True,
        ),
    )

    # Only plot the yearly accumulation where we have actual data (not NaN)
    df_with_data = df[df[f"{var}_yearly_acc"].notna()]
    fig.add_trace(
        go.Scatter(
            x=df_with_data.dummy_date,
            y=df_with_data[f"{var}_yearly_acc"],
            mode="lines",
            name=year,
            line=dict(width=3, color="black"),
            showlegend=True,
        ),
    )

    if year == pd.to_datetime("now", utc=True).year:
        try:
            fig.add_vline(
                x=pd.to_datetime("now", utc=True),
                line_width=2,
                line_dash="dash",
                line_color="rgba(1, 1, 1, 0.2)",
            )
            fig.add_annotation(
                x=pd.to_datetime("now", utc=True),
                y=0.2, text='TODAY', showarrow=False, textangle=-90,
                xref='x', yref='y domain', yanchor='bottom', xanchor='center',
                xshift=-15,  # Offset 15 pixels to the left
                font=dict(size=13, color='rgba(1, 1, 1, 0.3)'),
            )
            # Add circular marker at current time
            current_row = df[df['time'] == pd.to_datetime("now").normalize()][f"{var}_yearly_acc"]
            if not current_row.empty and not pd.isna(current_row.item()):
                current_value = current_row.item()
                fig.add_trace(
                    go.Scatter(
                        x=[pd.to_datetime("now", utc=True)],
                        y=[current_value],
                        mode='markers',
                        marker=dict(size=10, color='black'),
                        showlegend=False,
                        hoverinfo='y'
                    )
                )
            # Only add forecast range if the columns exist
            if f"{var}_min_yearly_acc" in df.columns and f"{var}_max_yearly_acc" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.dummy_date,
                        y=df[f"{var}_min_yearly_acc"],
                        mode="lines",
                        name="Forecast q15",
                        line=dict(width=0, color="red"),
                        showlegend=False,
                        hoverinfo="skip"
                    ),
                )

                fig.add_trace(
                    go.Scatter(
                        x=df.dummy_date,
                        y=df[f"{var}_max_yearly_acc"],
                        mode="lines",
                        name="Forecast q95",
                        line=dict(width=0, color="red"),
                        showlegend=False,
                        fill="tonexty",
                    ),
                )
        except Exception as e:
            logging.warning(
                f"Cannot add forecast data: {type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}"
            )

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        margin={"r": 5, "t": 50, "l": 0.1, "b": 0.1},
        barmode="stack",
        legend=dict(orientation="h"),
        yaxis=dict(showgrid=True, title=next(item["label"] for item in acc_vars_options if item["value"] == var),
                   zeroline=True, zerolinewidth=4, autorange='min'),
    )
    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14), yref='container', y=0.97))

    return add_attribution(fig)


def make_daily_figure(df, year, var, title=None):
    fig = make_subplots()

    #
    # Where the temperature crosses the climatology line, the fill areas create visual artifacts because the color transition doesn't happen exactly at the crossing point. The above and below arrays switch at the data point level, but the actual crossing between var and var_clima happens between data points, causing overlap/gaps at the transitions.
    # The fix is to interpolate the exact crossing points and insert them into the data before splitting into above/below series.
    # --- Compute exact crossing points via linear interpolation ---
    y1 = df[var].values
    y2 = df[f"{var}_clima"].values
    x = df["time"].values  # datetime64

    new_times = list(df["time"])
    new_y1 = list(y1)
    new_y2 = list(y2)

    insertions = []
    for i in range(len(y1) - 1):
        # Skip if either value is NaN
        if np.isnan(y1[i]) or np.isnan(y1[i+1]) or np.isnan(y2[i]) or np.isnan(y2[i+1]):
            continue
        # Detect sign change (crossing)
        if (y1[i] - y2[i]) * (y1[i+1] - y2[i+1]) < 0:
            # Linear interpolation to find crossing time
            denom = (y1[i] - y2[i]) - (y1[i+1] - y2[i+1])
            t_frac = (y1[i] - y2[i]) / denom  # fraction between i and i+1
            t_cross = x[i] + t_frac * (x[i+1] - x[i])
            v_cross = y2[i] + t_frac * (y2[i+1] - y2[i])  # same value for both at crossing
            insertions.append((i + 1, t_cross, v_cross))

    # Insert crossing points in reverse order to preserve indices
    for idx, t_cross, v_cross in reversed(insertions):
        new_times.insert(idx, t_cross)
        new_y1.insert(idx, v_cross)
        new_y2.insert(idx, v_cross)

    # Rebuild a working DataFrame with interpolated crossings
    dfi = pd.DataFrame({
        "time": new_times,
        var: new_y1,
        f"{var}_clima": new_y2,
    })

    # Filter out rows where the actual variable is NaN (future dates with no data)
    # Keep these for climatology but not for the fills
    dfi_valid = dfi[dfi[var].notna()].copy()

    mask = dfi_valid[var] > dfi_valid[f"{var}_clima"]
    dfi_valid["above"] = np.where(mask, dfi_valid[var], dfi_valid[f"{var}_clima"])
    dfi_valid["below"] = np.where(mask, dfi_valid[f"{var}_clima"], dfi_valid[var])

    # Map dummy_date for the clima/percentile traces (join on time)
    dummy_map = df.set_index("time")["dummy_date"]
    dfi["dummy_date"] = dfi["time"].map(dummy_map)
    # For inserted crossing rows, forward-fill dummy_date (approximate, only affects clima line)
    dfi["dummy_date"] = dfi["dummy_date"].ffill()

    color_above = "rgba(255, 76, 45, 1)"
    color_below = "rgba(99, 178, 207, 1)"
    if var in [
        "pressure_msl_mean",
        "cloud_cover_mean",
        "relative_humidity_2m_mean",
        "soil_moisture_0_to_7cm_mean",
        "soil_moisture_7_to_28cm_mean",
        "soil_moisture_28_to_100cm_mean",
    ]:
        color_above = "rgba(99, 178, 255, 1)"
        color_below = "rgba(205, 133, 63, 1)"

    # Below-average fill (use dfi_valid with only actual data, not future NaN dates)
    fig.add_trace(go.Scatter(
        x=dfi_valid["time"], y=dfi_valid[f"{var}_clima"],
        mode="lines", line=dict(width=0),
        showlegend=False, hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=dfi_valid["time"], y=dfi_valid["below"],
        fill="tonexty", name="Below Average",
        fillcolor=color_below, mode="none",
    ))

    # Above-average fill
    fig.add_trace(go.Scatter(
        x=dfi_valid["time"], y=dfi_valid[f"{var}_clima"],
        mode="lines", line=dict(width=0),
        showlegend=False, hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=dfi_valid["time"], y=dfi_valid["above"],
        fill="tonexty", name="Above average",
        fillcolor=color_above, mode="none",
    ))

    # Clima line and percentile band use original df / dummy_date
    fig.add_trace(go.Scatter(
        x=df.dummy_date, y=df[f"{var}_clima"],
        mode="lines", name="Clima",
        line=dict(width=3, color="black"), showlegend=True,
    ))
    fig.add_trace(go.Scatter(
        x=df.dummy_date, y=df["q05"],
        mode="lines", name="5th Percentile",
        line=dict(width=0, color="gray"),
        showlegend=False, hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=df.dummy_date, y=df["q95"],
        mode="lines", name="5-95th percentiles range",
        line=dict(width=0, color="gray"),
        fillcolor="rgba(0, 0, 0, 0.1)",
        showlegend=True, fill="tonexty",
    ))

    if year == pd.to_datetime("now", utc=True).year:
        current_row = df[df['time'] == pd.to_datetime("now").normalize()][var]
        if not current_row.empty and not pd.isna(current_row.item()):
            current_value = current_row.item()
            fig.add_trace(go.Scatter(
                x=[pd.to_datetime("now", utc=True)],
                y=[current_value],
                mode='markers',
                marker=dict(size=10, color='black'),
                showlegend=False, hoverinfo='y'
            ))
        fig.add_vline(
            x=pd.to_datetime("now", utc=True),
            line_width=2, line_dash="dash",
            line_color="rgba(1, 1, 1, 0.2)",
        )
        fig.add_annotation(
            x=pd.to_datetime("now", utc=True),
            y=0.2, text='TODAY', showarrow=False, textangle=-90,
            xref='x', yref='y domain', yanchor='bottom', xanchor='center',
            xshift=-15,  # Offset 15 pixels to the left
            font=dict(size=13, color='rgba(1, 1, 1, 0.3)'),
        )

    fig.update_layout(
        modebar=dict(orientation="v"),
        dragmode=False,
        margin={"r": 5, "t": 30, "l": 0.1, "b": 0.1},
        barmode="stack",
        legend=dict(orientation="h"),
        yaxis=dict(
            showgrid=True,
            title=next(item["label"] for item in daily_vars_options if item["value"] == var),
            autorange="min", zeroline=True, zerolinewidth=4
        ),
    )
    if title is not None:
        fig.update_layout(title=dict(text=title, font=dict(size=14), yref='container', y=0.97))

    return add_attribution(fig)
