import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import numpy as np

st.set_page_config(layout='wide')
st.title('Regional Overview')
st.divider()

df_in = pd.read_csv("https://raw.githubusercontent.com/UCL-ShippingGroup/shipping-explorer/main/datasets/inventories_total.csv")
df_reg = pd.read_csv("https://raw.githubusercontent.com/UCL-ShippingGroup/shipping-explorer/main/datasets/country_status_labels_v3.csv")

df = df_in.merge(
    df_reg[["iso_3", "region_wb", "status"]],
    left_on="alpha-3",
    right_on="iso_3",
    how="left"
)

# Remove the duplicate ISO-3 column from df_reg
df = df.drop(columns="iso_3")

# ---------------------------------------------------------
# Indicator control
# ---------------------------------------------------------

metric = st.segmented_control(
    "Metric",
    options=[
        "GHG emissions (t CO2e)",
        "Energy Demand (TJ)"
    ],
    default="GHG emissions (t CO2e)",
    key="region_metric"
)

if metric == "GHG emissions (t CO2e)":
    total_col = "co2e_t"
    voyage_col = "co2e_t_voy"
    port_col = "co2e_t_stop"
    value_title = "GHG emissions (t CO2e)"

else:
    total_col = "ene_tj"
    voyage_col = "ene_tj_voy"
    port_col = "ene_tj_stop"
    value_title = "Energy Demand (TJ)"


# ---------------------------------------------------------
# Keep international arrivals/departures
# ---------------------------------------------------------

plot_df = df[
    df["Inventory"].isin([
        "Int. Arr. Inventory",
        "Int. Dep. Inventory"
    ])
].copy()


# ---------------------------------------------------------
# Function to create chart
# ---------------------------------------------------------

def create_group_chart(data, group_col):

    # -----------------------------------------------------
    # Aggregate country data
    # -----------------------------------------------------

    grouped = (
        data
        .dropna(subset=[group_col])
        .groupby(
            [group_col, "Inventory"],
            as_index=False
        )[
            [total_col, voyage_col, port_col]
        ]
        .sum()
    )

    # -----------------------------------------------------
    # Calculate percentages
    # -----------------------------------------------------

    grouped["Voyage %"] = (
        grouped[voyage_col]
        / grouped[total_col]
        * 100
    )

    grouped["Port %"] = (
        grouped[port_col]
        / grouped[total_col]
        * 100
    )

    arrivals = grouped[
        grouped["Inventory"] == "Int. Arr. Inventory"
    ].copy()

    departures = grouped[
        grouped["Inventory"] == "Int. Dep. Inventory"
    ].copy()

    fig = go.Figure()


    # =====================================================
    # ARRIVALS
    # =====================================================

    # In Port - darker blue
    fig.add_trace(
        go.Bar(
            y=arrivals[group_col],
            x=arrivals[port_col],

            name="Arrivals — In Port",

            orientation="h",
            offsetgroup="arrivals",
            legendgroup="arrivals",

            marker_color="#1565C0",

            customdata=arrivals[
                ["Port %", total_col]
            ],

            hovertemplate=(
                "<b>%{y}</b><br>"
                "International Arrivals<br>"
                "In Port<br><br>"
                f"{value_title}: %{{x:,.2f}}<br>"
                "Percentage: %{customdata[0]:.1f}%<br>"
                f"Total: %{{customdata[1]:,.2f}}"
                "<extra></extra>"
            )
        )
    )

    # In Voyage - lighter blue
    fig.add_trace(
        go.Bar(
            y=arrivals[group_col],
            x=arrivals[voyage_col],

            name="Arrivals — In Voyage",

            orientation="h",
            offsetgroup="arrivals",
            legendgroup="arrivals",

            marker_color="#90CAF9",

            customdata=arrivals[
                ["Voyage %", total_col]
            ],

            hovertemplate=(
                "<b>%{y}</b><br>"
                "International Arrivals<br>"
                "In Voyage<br><br>"
                f"{value_title}: %{{x:,.2f}}<br>"
                "Percentage: %{customdata[0]:.1f}%<br>"
                f"Total: %{{customdata[1]:,.2f}}"
                "<extra></extra>"
            )
        )
    )


    # =====================================================
    # DEPARTURES
    # =====================================================

    # In Port - darker red
    fig.add_trace(
        go.Bar(
            y=departures[group_col],
            x=departures[port_col],

            name="Departures — In Port",

            orientation="h",
            offsetgroup="departures",
            legendgroup="departures",

            marker_color="#C62828",

            customdata=departures[
                ["Port %", total_col]
            ],

            hovertemplate=(
                "<b>%{y}</b><br>"
                "International Departures<br>"
                "In Port<br><br>"
                f"{value_title}: %{{x:,.2f}}<br>"
                "Percentage: %{customdata[0]:.1f}%<br>"
                f"Total: %{{customdata[1]:,.2f}}"
                "<extra></extra>"
            )
        )
    )

    # In Voyage - lighter red
    fig.add_trace(
        go.Bar(
            y=departures[group_col],
            x=departures[voyage_col],

            name="Departures — In Voyage",

            orientation="h",
            offsetgroup="departures",
            legendgroup="departures",

            marker_color="#EF9A9A",

            customdata=departures[
                ["Voyage %", total_col]
            ],

            hovertemplate=(
                "<b>%{y}</b><br>"
                "International Departures<br>"
                "In Voyage<br><br>"
                f"{value_title}: %{{x:,.2f}}<br>"
                "Percentage: %{customdata[0]:.1f}%<br>"
                f"Total: %{{customdata[1]:,.2f}}"
                "<extra></extra>"
            )
        )
    )


    # -----------------------------------------------------
    # Layout
    # -----------------------------------------------------

    fig.update_layout(

        barmode="stack",

        xaxis=dict(
            title=value_title,
            tickformat=",.2s"
        ),

        yaxis=dict(
            title=None
        ),

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,

            entrywidth=180,
            entrywidthmode="pixels"
        ),

        margin=dict(
            l=20,
            r=20,
            t=20,
            b=120
        ),

        hovermode="closest"
    )

    return fig

col1, col2 = st.columns(2)

with col1:
    st.subheader("By region")

    fig_region = create_group_chart(
        plot_df,
        "region_wb"
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )


with col2:
    st.subheader("By development status")

    fig_status = create_group_chart(
        plot_df,
        "status"
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True
    )
