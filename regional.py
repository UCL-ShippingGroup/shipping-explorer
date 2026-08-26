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


st.markdown(f"#### Percentage of Emissions/Energy Demand in Port for each Country in {selected_region}")

st.plotly_chart(
    fig_country_region,
    use_container_width=True
)


# =========================================================
# METRIC CONTROL
# =========================================================

metric = st.segmented_control(
    "Metric",
    options=[
        "GHG emissions (t CO2e)",
        "Energy Demand (TJ)"
    ],
    default="GHG emissions (t CO2e)",
    key="region_swarm_metric"
)


# ---------------------------------------------------------
# Select relevant columns
# ---------------------------------------------------------

if metric == "GHG emissions (t CO2e)":

    total_col = "co2e_t"
    port_col = "co2e_t_stop"

    port_hover_label = "In Port (t CO2e)"
    total_hover_label = "Total (t CO2e)"

else:

    total_col = "ene_tj"
    port_col = "ene_tj_stop"

    port_hover_label = "In Port (TJ)"
    total_hover_label = "Total (TJ)"


# =========================================================
# SELECTED COUNTRY
# =========================================================

selected_iso3 = st.session_state.get(
    "iso_3",
    None
)


# =========================================================
# PREPARE DATA
# =========================================================

swarm_df = df[
    df["Inventory"].isin([
        "Int. Arr. Inventory",
        "Int. Dep. Inventory"
    ])
].copy()


# Remove rows with missing regions / invalid values
swarm_df = swarm_df[
    swarm_df["region_wb"].notna()
    & swarm_df[total_col].notna()
    & (swarm_df[total_col] > 0)
    & swarm_df[port_col].notna()
].copy()


# ---------------------------------------------------------
# Calculate each country's percentage in port
# ---------------------------------------------------------

swarm_df["Port %"] = (
    swarm_df[port_col]
    / swarm_df[total_col]
    * 100
)


# =========================================================
# FUNCTION TO CREATE SWARM + BOX PLOT
# =========================================================

def create_region_swarm(data, inventory_name):

    # -----------------------------------------------------
    # Filter to arrivals or departures
    # -----------------------------------------------------

    panel_data = data[
        data["Inventory"] == inventory_name
    ].copy()


    # -----------------------------------------------------
    # Order regions by median Port %
    # -----------------------------------------------------

    region_order = (
        panel_data
        .groupby("region_wb")["Port %"]
        .median()
        .sort_values(ascending=True)
        .index
        .tolist()
    )


    # -----------------------------------------------------
    # Numeric x positions for regions
    # -----------------------------------------------------

    region_positions = {
        region: i
        for i, region in enumerate(region_order)
    }

    panel_data["x_base"] = (
        panel_data["region_wb"]
        .map(region_positions)
    )


    # -----------------------------------------------------
    # Reproducible jitter
    # -----------------------------------------------------

    rng = np.random.default_rng(42)

    panel_data["x_jitter"] = (
        panel_data["x_base"]
        + rng.uniform(
            -0.18,
            0.18,
            size=len(panel_data)
        )
    )


    # =====================================================
    # CREATE FIGURE
    # =====================================================

    fig = go.Figure()


    # =====================================================
    # BOX PLOTS
    # =====================================================

    for region in region_order:

        region_data = panel_data[
            panel_data["region_wb"] == region
        ].copy()

        values = region_data["Port %"].dropna()

        if values.empty:
            continue


        # -------------------------------------------------
        # Box statistics
        # -------------------------------------------------

        mean_value = values.mean()
        median_value = values.median()
        q1_value = values.quantile(0.25)
        q3_value = values.quantile(0.75)
        min_value = values.min()
        max_value = values.max()
        n_countries = len(values)

        x_position = region_positions[region]


        # -------------------------------------------------
        # Custom data for box hover
        # -------------------------------------------------

        box_customdata = np.column_stack([
            np.repeat(region, len(region_data)),
            np.repeat(n_countries, len(region_data)),
            np.repeat(mean_value, len(region_data)),
            np.repeat(median_value, len(region_data)),
            np.repeat(q1_value, len(region_data)),
            np.repeat(q3_value, len(region_data)),
            np.repeat(min_value, len(region_data)),
            np.repeat(max_value, len(region_data))
        ])


        # -------------------------------------------------
        # Box plot
        # -------------------------------------------------

        fig.add_trace(
            go.Box(

                x=[x_position] * len(region_data),

                y=region_data["Port %"],

                width=0.42,

                boxpoints=False,

                # Mean is drawn manually below
                boxmean=False,

                line=dict(
                    color="#707070",
                    width=1.5
                ),

                fillcolor="rgba(160,160,160,0.15)",

                showlegend=False,

                name=region,

                customdata=box_customdata,

                hovertemplate=(
                    "<b>%{customdata[0]}</b>"
                    "<br><br>"
                    "Countries: %{customdata[1]}"
                    "<br>"
                    "Mean: %{customdata[2]:.1f}%"
                    "<br>"
                    "Median: %{customdata[3]:.1f}%"
                    "<br>"
                    "Q1: %{customdata[4]:.1f}%"
                    "<br>"
                    "Q3: %{customdata[5]:.1f}%"
                    "<br>"
                    "Minimum: %{customdata[6]:.1f}%"
                    "<br>"
                    "Maximum: %{customdata[7]:.1f}%"
                    "<extra></extra>"
                )
            )
        )


        # -------------------------------------------------
        # Mean dotted line
        # No separate hover
        # -------------------------------------------------

        fig.add_trace(
            go.Scatter(

                x=[
                    x_position - 0.21,
                    x_position + 0.21
                ],

                y=[
                    mean_value,
                    mean_value
                ],

                mode="lines",

                line=dict(
                    color="#404040",
                    width=2,
                    dash="dot"
                ),

                showlegend=False,

                hoverdistance=5
            )
        )


    # =====================================================
    # NORMAL COUNTRIES
    # =====================================================

    normal = panel_data[
        panel_data["alpha-3"] != selected_iso3
    ].copy()


    fig.add_trace(
        go.Scatter(

            x=normal["x_jitter"],

            y=normal["Port %"],

            mode="markers",

            name="Countries",

            marker=dict(
                color="#1565C0",
                size=7,
                opacity=0.70
            ),

            customdata=normal[
                [
                    "alpha-3",
                    "region_wb",
                    port_col,
                    total_col
                ]
            ],

            hovertemplate=(
                "<b>%{customdata[0]}</b>"
                "<br>"
                "%{customdata[1]}"
                "<br><br>"
                "In Port: %{y:.1f}%"
                "<br>"
                f"{port_hover_label}: "
                "%{customdata[2]:,.2f}"
                "<br>"
                f"{total_hover_label}: "
                "%{customdata[3]:,.2f}"
                "<extra></extra>"
            )
        )
    )


    # =====================================================
    # SELECTED COUNTRY
    # =====================================================

    selected = panel_data[
        panel_data["alpha-3"] == selected_iso3
    ].copy()


    if not selected.empty:

        fig.add_trace(
            go.Scatter(

                x=selected["x_jitter"],

                y=selected["Port %"],

                mode="markers",

                name="Selected country",

                marker=dict(
                    color="#FFD600",
                    size=13,
                    opacity=1,

                    line=dict(
                        color="#333333",
                        width=1.5
                    )
                ),

                customdata=selected[
                    [
                        "alpha-3",
                        "region_wb",
                        port_col,
                        total_col
                    ]
                ],

                hovertemplate=(
                    "<b>%{customdata[0]}</b>"
                    "<br>"
                    "%{customdata[1]}"
                    "<br><br>"
                    "In Port: %{y:.1f}%"
                    "<br>"
                    f"{port_hover_label}: "
                    "%{customdata[2]:,.2f}"
                    "<br>"
                    f"{total_hover_label}: "
                    "%{customdata[3]:,.2f}"
                    "<extra></extra>"
                )
            )
        )


    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(

        height=550,

        xaxis=dict(
            title=None,

            tickmode="array",

            tickvals=list(
                region_positions.values()
            ),

            ticktext=list(
                region_positions.keys()
            ),

            range=[
                -0.5,
                len(region_order) - 0.5
            ]
        ),

        yaxis=dict(
            title="In Port (%)",
            ticksuffix="%",
            range=[0, 100]
        ),

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5
        ),

        margin=dict(
            l=50,
            r=20,
            t=20,
            b=120
        ),

        hoverdistance=5
    )


    return fig


# =========================================================
# INTERNATIONAL ARRIVALS
# =========================================================

st.subheader("International arrivals")

fig_arrivals = create_region_swarm(
    swarm_df,
    "Int. Arr. Inventory"
)

st.plotly_chart(
    fig_arrivals,
    use_container_width=True
)


# =========================================================
# INTERNATIONAL DEPARTURES
# =========================================================

st.subheader("International departures")

fig_departures = create_region_swarm(
    swarm_df,
    "Int. Dep. Inventory"
)

st.plotly_chart(
    fig_departures,
    use_container_width=True
)
