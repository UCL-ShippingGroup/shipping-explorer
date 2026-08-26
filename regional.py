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

    # -----------------------------------------------------
    # Sort groups by combined arrivals + departures total
    # -----------------------------------------------------

    group_order = (
        grouped
        .groupby(group_col)[total_col]
        .sum()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    arrivals = grouped[
        grouped["Inventory"] == "Int. Arr. Inventory"
    ].copy()

    departures = grouped[
        grouped["Inventory"] == "Int. Dep. Inventory"
    ].copy()


    # -----------------------------------------------------
    # Hover labels depending on metric
    # -----------------------------------------------------

    if metric == "GHG emissions (t CO2e)":
        voyage_hover_label = "In Voyage (t CO2e)"
        port_hover_label = "In Port (t CO2e)"
        total_hover_label = "Total (t CO2e)"

    else:
        voyage_hover_label = "In Voyage (TJ)"
        port_hover_label = "In Port (TJ)"
        total_hover_label = "Total (TJ)"


    fig = go.Figure()


    # =====================================================
    # ARRIVALS
    # =====================================================

    # In Voyage FIRST - lighter blue
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
                "International Arrivals<br><br>"
                f"{voyage_hover_label}: %{{x:,.2f}}<br>"
                "Percentage: %{customdata[0]:.1f}%<br>"
                f"{total_hover_label}: %{{customdata[1]:,.2f}}"
                "<extra></extra>"
            )
        )
    )

    # In Port SECOND - darker blue
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
                "International Arrivals<br><br>"
                f"{port_hover_label}: %{{x:,.2f}}<br>"
                "Percentage: %{customdata[0]:.1f}%<br>"
                f"{total_hover_label}: %{{customdata[1]:,.2f}}"
                "<extra></extra>"
            )
        )
    )


    # =====================================================
    # DEPARTURES
    # =====================================================

    # In Voyage FIRST - lighter red
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
                "International Departures<br><br>"
                f"{voyage_hover_label}: %{{x:,.2f}}<br>"
                "Percentage: %{customdata[0]:.1f}%<br>"
                f"{total_hover_label}: %{{customdata[1]:,.2f}}"
                "<extra></extra>"
            )
        )
    )

    # In Port SECOND - darker red
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
                "International Departures<br><br>"
                f"{port_hover_label}: %{{x:,.2f}}<br>"
                "Percentage: %{customdata[0]:.1f}%<br>"
                f"{total_hover_label}: %{{customdata[1]:,.2f}}"
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
            title=None,
            categoryorder="array",
            categoryarray=group_order,

            # Horizontal Plotly bars put the first category
            # at the bottom, so reverse to put largest on top
            autorange="reversed"
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

st.subheader(
    "A Closer Look at {0} in the Regional Context".format(
        st.session_state.iso_country),
    divider = 'grey')

# ---------------------------------------------------------
# Selected country and its region
# ---------------------------------------------------------

selected_iso3 = st.session_state.get("iso_3", None)

selected_region = (
    df.loc[
        df["alpha-3"] == selected_iso3,
        "region_wb"
    ]
    .dropna()
    .iloc[0]
)


# ---------------------------------------------------------
# Filter to countries in selected country's region
# ---------------------------------------------------------

country_region_df = df[
    (df["region_wb"] == selected_region)
    & (
        df["Inventory"].isin([
            "Int. Arr. Inventory",
            "Int. Dep. Inventory"
        ])
    )
].copy()


# ---------------------------------------------------------
# Calculate each country's % in port
# ---------------------------------------------------------

country_region_df["Port %"] = (
    country_region_df[port_col]
    / country_region_df[total_col]
    * 100
)


# ---------------------------------------------------------
# Split arrivals and departures
# ---------------------------------------------------------

arrivals = country_region_df[
    country_region_df["Inventory"] == "Int. Arr. Inventory"
].copy()

departures = country_region_df[
    country_region_df["Inventory"] == "Int. Dep. Inventory"
].copy()


# ---------------------------------------------------------
# Colours
# ---------------------------------------------------------

arrivals["Colour"] = arrivals["alpha-3"].apply(
    lambda x: "#1565C0" if x == selected_iso3 else "#90CAF9"
)

departures["Colour"] = departures["alpha-3"].apply(
    lambda x: "#C62828" if x == selected_iso3 else "#EF9A9A"
)


# ---------------------------------------------------------
# Hover labels
# ---------------------------------------------------------

if metric == "GHG emissions (t CO2e)":
    port_hover_label = "In Port (t CO2e)"
    total_hover_label = "Total (t CO2e)"

else:
    port_hover_label = "In Port (TJ)"
    total_hover_label = "Total (TJ)"

country_order = (
    country_region_df
    .groupby("alpha-3")["Port %"]
    .mean()
    .sort_values(ascending=True)
    .index
    .tolist()
)

# ---------------------------------------------------------
# Create figure
# ---------------------------------------------------------

fig_country_region = go.Figure()


# International Arrivals
fig_country_region.add_trace(
    go.Bar(
        x=arrivals["alpha-3"],
        y=arrivals["Port %"],

        name="International Arrivals",

        marker_color=arrivals["Colour"],

        customdata=arrivals[
            [port_col, total_col]
        ],

        hovertemplate=(
            "<b>%{x}</b><br>"
            "International Arrivals<br><br>"
            "In Port: %{y:.1f}%<br>"
            f"{port_hover_label}: %{{customdata[0]:,.2f}}<br>"
            f"{total_hover_label}: %{{customdata[1]:,.2f}}"
            "<extra></extra>"
        )
    )
)


# International Departures
fig_country_region.add_trace(
    go.Bar(
        x=departures["alpha-3"],
        y=departures["Port %"],

        name="International Departures",

        marker_color=departures["Colour"],

        customdata=departures[
            [port_col, total_col]
        ],

        hovertemplate=(
            "<b>%{x}</b><br>"
            "International Departures<br><br>"
            "In Port: %{y:.1f}%<br>"
            f"{port_hover_label}: %{{customdata[0]:,.2f}}<br>"
            f"{total_hover_label}: %{{customdata[1]:,.2f}}"
            "<extra></extra>"
        )
    )
)


# ---------------------------------------------------------
# Layout
# ---------------------------------------------------------

fig_country_region.update_layout(

    barmode="group",

    xaxis=dict(
    title=None,
    categoryorder="array",
    categoryarray=country_order
    ),

    yaxis=dict(
        title="In Port (%)",
        ticksuffix="%",
        range=[0, 100]
    ),

    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.20,
        xanchor="center",
        x=0.5
    ),

    margin=dict(
        l=20,
        r=20,
        t=40,
        b=100
    ),

    hovermode="closest"
)


st.markdown(#### f"Percentage of Emissions/Energy Demand in Port for each Country in {selected_region}")

st.plotly_chart(
    fig_country_region,
    use_container_width=True
)
