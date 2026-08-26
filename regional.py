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

    unit = "t CO2e"

else:

    total_col = "ene_tj"
    port_col = "ene_tj_stop"

    unit = "TJ"


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


# Remove rows with missing regions / invalid totals
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
    # Lowest on left -> highest on right
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
    # Numeric x positions for each region
    # -----------------------------------------------------

    region_positions = {
        region: i
        for i, region in enumerate(region_order)
    }


    # =====================================================
    # CREATE FIGURE
    # =====================================================

    fig = go.Figure()


    # =====================================================
    # LEGEND ENTRIES
    #
    # These are dummy traces so that both legend items
    # always appear regardless of which region contains
    # the selected country.
    # =====================================================

    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],

            mode="markers",

            name="Countries",

            marker=dict(
                size=7,
                color="blue",
                opacity=0.65
            ),

            showlegend=True,

            hoverinfo="skip"
        )
    )


    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],

            mode="markers",

            name="Selected country",

            marker=dict(
                size=14,
                color="yellow",

                line=dict(
                    color="black",
                    width=1.5
                )
            ),

            showlegend=True,

            hoverinfo="skip"
        )
    )


    # =====================================================
    # LOOP THROUGH REGIONS
    # =====================================================

    for region in region_order:

        subset = panel_data[
            panel_data["region_wb"] == region
        ].copy()

        position = region_positions[region]


        # -------------------------------------------------
        # Reproducible jitter
        # -------------------------------------------------

        np.random.seed(
            42 + position
        )

        jitter = np.random.uniform(
            -0.15,
            0.15,
            size=len(subset)
        )

        x_values = (
            position
            + jitter
        )


        # -------------------------------------------------
        # Mean for boxplot hover
        # -------------------------------------------------

        mean_value = (
            subset["Port %"]
            .mean()
        )


        # =================================================
        # BOX PLOT
        # =================================================

        fig.add_trace(
            go.Box(

                x=[
                    position
                ] * len(subset),

                y=subset["Port %"],

                name=region,

                boxpoints=False,

                width=0.5,

                showlegend=False,

                # Plotly displays the mean visually
                boxmean=True,

                hovertemplate=(
                    "<b>"
                    + region
                    + "</b><br>"
                    "Maximum: %{upper:.2f}%<br>"
                    "Q3 (75%): %{q3:.2f}%<br>"
                    "Median: %{median:.2f}%<br>"
                    "Mean: "
                    + f"{mean_value:.2f}%"
                    + "<br>"
                    "Q1 (25%): %{q1:.2f}%<br>"
                    "Minimum: %{lower:.2f}%<br>"
                    "Countries: "
                    + str(len(subset))
                    + "<extra></extra>"
                )
            )
        )


        # -------------------------------------------------
        # Identify selected country
        # -------------------------------------------------

        is_selected = (
            subset["alpha-3"]
            == selected_iso3
        )


        # =================================================
        # NORMAL COUNTRIES
        # =================================================

        normal = subset[
            ~is_selected
        ].copy()

        normal_x = x_values[
            ~is_selected
        ]


        if len(normal) > 0:

            customdata_normal = np.column_stack([
                normal["alpha-3"],
                normal[total_col],
                normal[port_col]
            ])


            fig.add_trace(
                go.Scatter(

                    x=normal_x,

                    y=normal["Port %"],

                    mode="markers",

                    name="Countries",

                    # Legend handled by dummy trace above
                    showlegend=False,

                    marker=dict(
                        size=7,
                        color="blue",
                        opacity=0.65
                    ),

                    customdata=customdata_normal,

                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        + region
                        + "<br><br>"
                        "In Port: %{y:.2f}%<br>"
                        "In Port ("
                        + unit
                        + "): %{customdata[2]:,.2f}<br>"
                        "Total ("
                        + unit
                        + "): %{customdata[1]:,.2f}"
                        "<extra></extra>"
                    )
                )
            )


        # =================================================
        # SELECTED COUNTRY
        # =================================================

        selected = subset[
            is_selected
        ].copy()

        selected_x = x_values[
            is_selected
        ]


        if len(selected) > 0:

            customdata_selected = np.column_stack([
                selected["alpha-3"],
                selected[total_col],
                selected[port_col]
            ])


            fig.add_trace(
                go.Scatter(

                    x=selected_x,

                    y=selected["Port %"],

                    mode="markers",

                    name="Selected country",

                    # Legend handled by dummy trace above
                    showlegend=False,

                    marker=dict(
                        size=14,
                        color="yellow",

                        line=dict(
                            color="black",
                            width=1.5
                        )
                    ),

                    customdata=customdata_selected,

                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        + region
                        + "<br><br>"
                        "In Port: %{y:.2f}%<br>"
                        "In Port ("
                        + unit
                        + "): %{customdata[2]:,.2f}<br>"
                        "Total ("
                        + unit
                        + "): %{customdata[1]:,.2f}"
                        "<extra></extra>"
                    )
                )
            )


    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(

        height=600,

        template="plotly_white",

        hovermode="closest",

        # Makes country hover much more precise
        hoverdistance=5,

        margin=dict(
            l=70,
            r=30,
            t=40,
            b=110
        ),

        xaxis=dict(

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
            ],

            title=None
        ),

        yaxis=dict(

            title="Percentage of country's total in port",

            ticksuffix="%",

            range=[
                0,
                100
            ]
        ),

        legend=dict(
            orientation="h",

            yanchor="top",
            y=-0.18,

            xanchor="center",
            x=0.5
        )
    )


    return fig


# =========================================================
# INTERNATIONAL ARRIVALS
# =========================================================

st.subheader(
    "International arrivals"
)

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

st.subheader(
    "International departures"
)

fig_departures = create_region_swarm(
    swarm_df,
    "Int. Dep. Inventory"
)

st.plotly_chart(
    fig_departures,
    use_container_width=True
)

# =========================================================
# DEVELOPMENT STATUS SWARM + BOX PLOT
# =========================================================


# ---------------------------------------------------------
# Prepare data
# ---------------------------------------------------------

status_df = df[
    df["Inventory"].isin([
        "Int. Arr. Inventory",
        "Int. Dep. Inventory"
    ])
].copy()


# Remove rows with missing status / invalid totals
status_df = status_df[
    status_df["status"].notna()
    & status_df[total_col].notna()
    & (status_df[total_col] > 0)
    & status_df[port_col].notna()
].copy()


# ---------------------------------------------------------
# Calculate Port % for each inventory
# ---------------------------------------------------------

status_df["Port %"] = (
    status_df[port_col]
    / status_df[total_col]
    * 100
)


# ---------------------------------------------------------
# Give inventories shorter names
# ---------------------------------------------------------

status_df["Inventory Type"] = (
    status_df["Inventory"]
    .map({
        "Int. Arr. Inventory": "Arrivals",
        "Int. Dep. Inventory": "Departures"
    })
)


# =========================================================
# CREATE ONE ROW PER COUNTRY
# =========================================================

# ---------------------------------------------------------
# Percentage data
# ---------------------------------------------------------

percentage_df = (
    status_df
    .pivot_table(
        index=[
            "alpha-3",
            "status"
        ],
        columns="Inventory Type",
        values="Port %",
        aggfunc="first"
    )
    .reset_index()
)


# Require both arrivals and departures
percentage_df = percentage_df.dropna(
    subset=[
        "Arrivals",
        "Departures"
    ]
)


# ---------------------------------------------------------
# Average arrivals and departures Port %
# ---------------------------------------------------------

percentage_df["Average Port %"] = (
    percentage_df[
        [
            "Arrivals",
            "Departures"
        ]
    ]
    .mean(axis=1)
)


# =========================================================
# ADD ABSOLUTE VALUES FOR HOVER
# =========================================================

# ---------------------------------------------------------
# Arrivals absolute values
# ---------------------------------------------------------

arrivals_abs = (
    status_df[
        status_df["Inventory"]
        == "Int. Arr. Inventory"
    ]
    [
        [
            "alpha-3",
            total_col,
            port_col
        ]
    ]
    .copy()
)


arrivals_abs = arrivals_abs.rename(
    columns={
        total_col: "Arrivals Total",
        port_col: "Arrivals Port"
    }
)


# ---------------------------------------------------------
# Departures absolute values
# ---------------------------------------------------------

departures_abs = (
    status_df[
        status_df["Inventory"]
        == "Int. Dep. Inventory"
    ]
    [
        [
            "alpha-3",
            total_col,
            port_col
        ]
    ]
    .copy()
)


departures_abs = departures_abs.rename(
    columns={
        total_col: "Departures Total",
        port_col: "Departures Port"
    }
)


# ---------------------------------------------------------
# Merge absolute values onto country-level data
# ---------------------------------------------------------

plot_status_df = (
    percentage_df

    .merge(
        arrivals_abs,
        on="alpha-3",
        how="left"
    )

    .merge(
        departures_abs,
        on="alpha-3",
        how="left"
    )
)


# =========================================================
# CREATE FIGURE
# =========================================================

fig_status_swarm = go.Figure()


# ---------------------------------------------------------
# Order status groups by median
# Lowest median on left -> highest on right
# ---------------------------------------------------------

status_order = (
    plot_status_df
    .groupby("status")["Average Port %"]
    .median()
    .sort_values(
        ascending=True
    )
    .index
    .tolist()
)


# ---------------------------------------------------------
# Numeric x positions
# ---------------------------------------------------------

status_positions = {
    status: i
    for i, status in enumerate(
        status_order
    )
}


# =========================================================
# LEGEND
# =========================================================

# Dummy trace so Countries appears once in legend

fig_status_swarm.add_trace(
    go.Scatter(
        x=[None],
        y=[None],

        mode="markers",

        name="Countries",

        marker=dict(
            size=7,
            color="blue",
            opacity=0.65
        ),

        showlegend=True,

        hoverinfo="skip"
    )
)


# =========================================================
# LOOP THROUGH DEVELOPMENT STATUS GROUPS
# =========================================================

for status in status_order:

    subset = plot_status_df[
        plot_status_df["status"] == status
    ].copy()

    position = status_positions[
        status
    ]


    # -----------------------------------------------------
    # Jitter
    # -----------------------------------------------------

    np.random.seed(
        42 + position
    )

    jitter = np.random.uniform(
        -0.15,
        0.15,
        size=len(subset)
    )

    x_values = (
        position
        + jitter
    )


    # -----------------------------------------------------
    # Mean for boxplot hover
    # -----------------------------------------------------

    mean_value = (
        subset["Average Port %"]
        .mean()
    )


    # =====================================================
    # BOX PLOT
    # =====================================================

    fig_status_swarm.add_trace(
        go.Box(

            x=[
                position
            ] * len(subset),

            y=subset[
                "Average Port %"
            ],

            name=status,

            boxpoints=False,

            width=0.5,

            showlegend=False,

            # Display mean visually
            boxmean=True,

            hovertemplate=(
                "<b>"
                + status
                + "</b><br>"
                "Maximum: %{upper:.2f}%<br>"
                "Q3 (75%): %{q3:.2f}%<br>"
                "Median: %{median:.2f}%<br>"
                "Mean: "
                + f"{mean_value:.2f}%"
                + "<br>"
                "Q1 (25%): %{q1:.2f}%<br>"
                "Minimum: %{lower:.2f}%<br>"
                "Countries: "
                + str(len(subset))
                + "<extra></extra>"
            )
        )
    )


    # =====================================================
    # COUNTRY DOTS
    # =====================================================

    customdata = np.column_stack([
        subset["alpha-3"],

        subset["Arrivals"],
        subset["Departures"],

        subset["Arrivals Port"],
        subset["Arrivals Total"],

        subset["Departures Port"],
        subset["Departures Total"]
    ])


    fig_status_swarm.add_trace(
        go.Scatter(

            x=x_values,

            y=subset[
                "Average Port %"
            ],

            mode="markers",

            name="Countries",

            showlegend=False,

            marker=dict(
                size=7,
                color="blue",
                opacity=0.65
            ),

            customdata=customdata,

            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                + status
                + "<br><br>"

                "Average In Port: %{y:.2f}%"
                "<br><br>"

                "<b>International Arrivals</b><br>"
                "In Port: %{customdata[1]:.2f}%<br>"
                "In Port ("
                + unit
                + "): %{customdata[3]:,.2f}<br>"
                "Total ("
                + unit
                + "): %{customdata[4]:,.2f}"
                "<br><br>"

                "<b>International Departures</b><br>"
                "In Port: %{customdata[2]:.2f}%<br>"
                "In Port ("
                + unit
                + "): %{customdata[5]:,.2f}<br>"
                "Total ("
                + unit
                + "): %{customdata[6]:,.2f}"

                "<extra></extra>"
            )
        )
    )


# =========================================================
# LAYOUT
# =========================================================

fig_status_swarm.update_layout(

    height=600,

    template="plotly_white",

    hovermode="closest",

    hoverdistance=5,

    margin=dict(
        l=70,
        r=30,
        t=40,
        b=110
    ),

    xaxis=dict(

        tickmode="array",

        tickvals=list(
            status_positions.values()
        ),

        ticktext=list(
            status_positions.keys()
        ),

        range=[
            -0.5,
            len(status_order) - 0.5
        ],

        title=None
    ),

    yaxis=dict(

        title="Average percentage of country's total in port",

        ticksuffix="%",

        range=[
            0,
            100
        ]
    ),

    legend=dict(
        orientation="h",

        yanchor="top",
        y=-0.18,

        xanchor="center",
        x=0.5
    )
)


# =========================================================
# DISPLAY
# =========================================================

st.subheader(
    "By development status"
)

st.plotly_chart(
    fig_status_swarm,
    use_container_width=True
)

# =========================================================
# DEVELOPMENT STATUS SWARM + BOX PLOT
# INTERNATIONAL ARRIVALS ONLY
# =========================================================


# ---------------------------------------------------------
# Prepare data
# ---------------------------------------------------------

status_arrivals_df = df[
    df["Inventory"] == "Int. Arr. Inventory"
].copy()


# Remove rows with missing status / invalid totals
status_arrivals_df = status_arrivals_df[
    status_arrivals_df["status"].notna()
    & status_arrivals_df[total_col].notna()
    & (status_arrivals_df[total_col] > 0)
    & status_arrivals_df[port_col].notna()
].copy()


# ---------------------------------------------------------
# Calculate each country's percentage in port
# ---------------------------------------------------------

status_arrivals_df["Port %"] = (
    status_arrivals_df[port_col]
    / status_arrivals_df[total_col]
    * 100
)


# =========================================================
# CREATE FIGURE
# =========================================================

fig_status_arrivals = go.Figure()


# ---------------------------------------------------------
# Order status groups by median
# Lowest median on left -> highest on right
# ---------------------------------------------------------

status_order = (
    status_arrivals_df
    .groupby("status")["Port %"]
    .median()
    .sort_values(
        ascending=True
    )
    .index
    .tolist()
)


# ---------------------------------------------------------
# Numeric x positions
# ---------------------------------------------------------

status_positions = {
    status: i
    for i, status in enumerate(
        status_order
    )
}


# =========================================================
# LEGEND
# =========================================================

# Dummy trace so Countries appears once in legend

fig_status_arrivals.add_trace(
    go.Scatter(
        x=[None],
        y=[None],

        mode="markers",

        name="Countries",

        marker=dict(
            size=7,
            color="blue",
            opacity=0.65
        ),

        showlegend=True,

        hoverinfo="skip"
    )
)


# =========================================================
# LOOP THROUGH DEVELOPMENT STATUS GROUPS
# =========================================================

for status in status_order:

    subset = status_arrivals_df[
        status_arrivals_df["status"] == status
    ].copy()

    position = status_positions[
        status
    ]


    # -----------------------------------------------------
    # Jitter
    # -----------------------------------------------------

    np.random.seed(
        42 + position
    )

    jitter = np.random.uniform(
        -0.15,
        0.15,
        size=len(subset)
    )

    x_values = (
        position
        + jitter
    )


    # -----------------------------------------------------
    # Mean for boxplot hover
    # -----------------------------------------------------

    mean_value = (
        subset["Port %"]
        .mean()
    )


    # =====================================================
    # BOX PLOT
    # =====================================================

    fig_status_arrivals.add_trace(
        go.Box(

            x=[
                position
            ] * len(subset),

            y=subset["Port %"],

            name=status,

            boxpoints=False,

            width=0.5,

            showlegend=False,

            # Display mean visually
            boxmean=True,

            hovertemplate=(
                "<b>"
                + status
                + "</b><br>"
                "Maximum: %{upper:.2f}%<br>"
                "Q3 (75%): %{q3:.2f}%<br>"
                "Median: %{median:.2f}%<br>"
                "Mean: "
                + f"{mean_value:.2f}%"
                + "<br>"
                "Q1 (25%): %{q1:.2f}%<br>"
                "Minimum: %{lower:.2f}%<br>"
                "Countries: "
                + str(len(subset))
                + "<extra></extra>"
            )
        )
    )


    # =====================================================
    # COUNTRY DOTS
    # =====================================================

    customdata = np.column_stack([
        subset["alpha-3"],
        subset[total_col],
        subset[port_col]
    ])


    fig_status_arrivals.add_trace(
        go.Scatter(

            x=x_values,

            y=subset["Port %"],

            mode="markers",

            name="Countries",

            showlegend=False,

            marker=dict(
                size=7,
                color="blue",
                opacity=0.65
            ),

            customdata=customdata,

            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                + status
                + "<br><br>"
                "In Port: %{y:.2f}%<br>"
                "In Port ("
                + unit
                + "): %{customdata[2]:,.2f}<br>"
                "Total ("
                + unit
                + "): %{customdata[1]:,.2f}"
                "<extra></extra>"
            )
        )
    )


# =========================================================
# LAYOUT
# =========================================================

fig_status_arrivals.update_layout(

    height=600,

    template="plotly_white",

    hovermode="closest",

    hoverdistance=5,

    margin=dict(
        l=70,
        r=30,
        t=40,
        b=110
    ),

    xaxis=dict(

        tickmode="array",

        tickvals=list(
            status_positions.values()
        ),

        ticktext=list(
            status_positions.keys()
        ),

        range=[
            -0.5,
            len(status_order) - 0.5
        ],

        title=None
    ),

    yaxis=dict(

        title="Percentage of country's total in port",

        ticksuffix="%",

        range=[
            0,
            100
        ]
    ),

    legend=dict(
        orientation="h",

        yanchor="top",
        y=-0.18,

        xanchor="center",
        x=0.5
    )
)


# =========================================================
# DISPLAY
# =========================================================

st.subheader(
    "International arrivals by development status"
)

st.plotly_chart(
    fig_status_arrivals,
    use_container_width=True
)
