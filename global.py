import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import altair as alt
import plotly.graph_objects as go

st.set_page_config(layout='wide')
st.title('Global Overview')

df = pd.read_csv("https://raw.githubusercontent.com/UCL-ShippingGroup/shipping-explorer/main/datasets/inventories_total.csv")

all_int = df[
    df["Inventory"] == "All International Voyages"
].iloc[0]


# ============================================================
# GHG EMISSIONS
# ============================================================

total_ghg = all_int["co2e_t"]
port_ghg = all_int["co2e_t_stop"]
voyage_ghg = all_int["co2e_t_voy"]


# ============================================================
# ENERGY DEMAND
# ============================================================

total_energy = all_int["ene_tj"]
port_energy = all_int["ene_tj_stop"]
voyage_energy = all_int["ene_tj_voy"]


# ============================================================
# NUMBER OF VOYAGES
# ============================================================

total_voyages = all_int["n_vys"]


# ============================================================
# AVERAGES PER VOYAGE
# ============================================================

avg_ghg = total_ghg / total_voyages
avg_port_ghg = port_ghg / total_voyages
avg_voyage_ghg = voyage_ghg / total_voyages

avg_energy = total_energy / total_voyages
avg_port_energy = port_energy / total_voyages
avg_voyage_energy = voyage_energy / total_voyages


# ============================================================
# PERCENTAGES
# ============================================================

port_ghg_pct = port_ghg / total_ghg * 100
voyage_ghg_pct = voyage_ghg / total_ghg * 100

port_energy_pct = port_energy / total_energy * 100
voyage_energy_pct = voyage_energy / total_energy * 100

# ============================================================
# THREE COLUMN LAYOUT
# ============================================================

c1, c2, c3 = st.columns([2.3, 1, 1])


# ============================================================
# LEFT — TEXT
# ============================================================

with c1:

    st.markdown(
        """
        ### International shipping

        International arrivals and departures capture the
        energy demand and greenhouse gas emissions associated
        with international shipping.

        The figures distinguish between activity occurring
        **in port** and **during the voyage**.

        Average values are calculated per international voyage.
        """
    )


# ============================================================
# MIDDLE — GHG EMISSIONS
# ============================================================

with c2:

    st.markdown("### GHG emissions")

    st.metric(
        "Total international voyages",
        f"{total_ghg:,.0f} t CO₂e",
        border=True
    )

    st.metric(
        "In port",
        f"{port_ghg:,.0f} t CO₂e",
        f"{port_ghg_pct:.2f}%",
        border=True
    )

    st.metric(
        "In voyage",
        f"{voyage_ghg:,.0f} t CO₂e",
        f"{voyage_ghg_pct:.2f}%",
        border=True
    )

    st.metric(
        "Average per voyage",
        f"{avg_ghg:,.2f} t CO₂e",
        border=True
    )

    st.metric(
        "Average in port",
        f"{avg_port_ghg:,.2f} t CO₂e",
        border=True
    )

    st.metric(
        "Average in voyage",
        f"{avg_voyage_ghg:,.2f} t CO₂e",
        border=True
    )


# ============================================================
# RIGHT — ENERGY DEMAND
# ============================================================

with c3:

    st.markdown("### Energy demand")

    st.metric(
        "Total international voyages",
        f"{total_energy:,.0f} TJ",
        border=True
    )

    st.metric(
        "In port",
        f"{port_energy:,.0f} TJ",
        f"{port_energy_pct:.2f}%",
        border=True
    )

    st.metric(
        "In voyage",
        f"{voyage_energy:,.0f} TJ",
        f"{voyage_energy_pct:.2f}%",
        border=True
    )

    st.metric(
        "Average per voyage",
        f"{avg_energy:,.2f} TJ",
        border=True
    )

    st.metric(
        "Average in port",
        f"{avg_port_energy:,.2f} TJ",
        border=True
    )

    st.metric(
        "Average in voyage",
        f"{avg_voyage_energy:,.2f} TJ",
        border=True
    )

#arr = inventories[inventories['Inventory']== 'Int. Arr. Inventory']
#dep = inventories[inventories['Inventory']== 'Int. Dep. Inventory']
# First segmented control
chart_choice = st.segmented_control(
    label="What type of voyages would you like to view?",
    options=["International Arrivals", "International Departures"],
    default="International Arrivals"
)

# Second segmented control
chart_choice2 = st.segmented_control(
    label="Which indicator would you like to view?",
    options=["GHG Emissions (t CO2e)", "Energy Demand (TJ)"],
    default="GHG Emissions (t CO2e)"
)

# Third segmented control
chart_choice3 = st.segmented_control(
    label="What breakdown of the voyage would you like?",
    options=["Total", "In Voyage", "In Port"],
    default="Total"

)

  # Fourth segmented control
chart_choice4 = st.segmented_control(
    label="Select statistical view",
    options=["Absolute", "Average per voyage"],
    default="Absolute"
)


# ARRIVALS / DEPARTURES

if chart_choice == "International Arrivals":

    plot_df = df[
        df["Inventory"] == "Int. Arr. Inventory"
    ].copy()

else:

    plot_df = df[
        df["Inventory"] == "Int. Dep. Inventory"
    ].copy()


# -----------------------------
# COLUMN SELECTION
# -----------------------------

column_map = {

    # GHG - Absolute
    ("GHG Emissions (t CO2e)", "Total", "Absolute"): "co2e_t",
    ("GHG Emissions (t CO2e)", "In Voyage", "Absolute"): "co2e_t_voy",
    ("GHG Emissions (t CO2e)", "In Port", "Absolute"): "co2e_t_stop",

    # Energy - Absolute
    ("Energy Demand (TJ)", "Total", "Absolute"): "ene_tj",
    ("Energy Demand (TJ)", "In Voyage", "Absolute"): "ene_tj_voy",
    ("Energy Demand (TJ)", "In Port", "Absolute"): "ene_tj_stop",
}

if chart_choice4 == "Absolute":

    selected_column = column_map[
        (chart_choice2, chart_choice3, chart_choice4)
    ]

else:

    # Select the appropriate absolute column
    selected_column = column_map[
        (chart_choice2, chart_choice3, "Absolute")
    ]

    # Calculate average per voyage
    plot_df["Average per voyage"] = (
        plot_df[selected_column] / plot_df["n_vys"]
    )

    selected_column = "Average per voyage"



# -----------------------------
# GRAPH LABELS
# -----------------------------

if chart_choice4 == "Average per voyage":

    if chart_choice2 == "GHG Emissions (t CO2e)":
        unit = "t CO2e / voyage"
    else:
        unit = "TJ / voyage"

elif chart_choice2 == "GHG Emissions (t CO2e)":

    unit = "t CO2e"

else:

    unit = "TJ"


# -----------------------------
# PLOTLY MAP
# -----------------------------

fig = px.choropleth(
    plot_df,
    locations="alpha-3",
    locationmode="ISO-3",
    color=selected_column,
    hover_name='alpha-3',
    color_continuous_scale="RdYlGn_r",
    labels={selected_column: unit},
    title=f"{chart_choice2} — {chart_choice3} — {chart_choice4} — {chart_choice}"
)
fig.update_layout(paper_bgcolor="white",height= 600, width=400,font_size=18)
fig.update_geos(
    showcoastlines=True,
    coastlinecolor="Black",
    #showland=True,
    showcountries=True,
    countrycolor="gray",
    fitbounds="locations"
)
st.plotly_chart(
    fig,
    width='stretch'
)

#"Reds"
st.subheader(
    "A Closer Look at {0} in the Global Context".format(
        st.session_state.iso_country),
    divider = 'grey')


input_dir = "https://raw.githubusercontent.com/UCL-ShippingGroup/shipping-explorer/main/datasets/"

df_1 = pd.read_csv(
    input_dir + "activity_inventories_v0.4/{0}/inventories.csv".format(
        st.session_state.iso_code
    )
)

#Metric selector

metric = st.segmented_control(
    "Metric",
    options=["GHG emissions (t CO2e)", "Energy Demand (TJ)"],
    default="GHG emissions (t CO2e)",
    key="metric_selection"
)

#Select columns

if metric == "GHG emissions (t CO2e)":

    voy_col = "co2e_t_voy"
    stop_col = "co2e_t_stop"
    total_col = "co2e_t"
    value_title = "CO₂e (tonnes)"

else:

    voy_col = "ene_tj_voy"
    stop_col = "ene_tj_stop"
    total_col = "ene_tj"
    value_title = "Energy demand (TJ)"



#Pie chart function


def create_voyage_stop_pie(df, voy_col, stop_col, total_col):

    voyage = df[voy_col].iloc[0]
    stop = df[stop_col].iloc[0]
    total = df[total_col].iloc[0]

    voyage_pct = voyage / total * 100
    stop_pct = stop / total * 100

    pie_df = pd.DataFrame({
        "State": ["In voyage", "In Port"],
        "Value": [voyage, stop],
        "Percentage": [voyage_pct, stop_pct],
        "Percentage_label": [
            f"{voyage_pct:.2f}%",
            f"{stop_pct:.2f}%"
        ],
        "Total": [total, total]
    })

    chart = (
        alt.Chart(pie_df)
        .mark_arc(
            outerRadius=100
        )
        .encode(
            theta=alt.Theta(
                "Value:Q",
                stack=True
            ),
            color=alt.Color(
                "State:N",
                legend=alt.Legend(title=None)
            ),
            tooltip=[
                alt.Tooltip(
                    "State:N",
                    title="State"
                ),
                alt.Tooltip(
                    "Value:Q",
                    title=value_title,
                    format=",.2f"
                ),
                alt.Tooltip(
                    "Percentage:Q",
                    title="Percentage",
                    format=".2f"
                ),
                alt.Tooltip(
                    "Total:Q",
                    title=f"Total {value_title}",
                    format=",.2f"
                )
            ]
        )
    )

    text = (
        alt.Chart(pie_df)
        .mark_text(
            radius=60,
            size=14
        )
        .encode(
            theta=alt.Theta(
                "Value:Q",
                stack=True
            ),
            text=alt.Text("Percentage_label:N")
        )
    )

    return chart + text

#Filter arrivals and departures


arr = df_1[
    df_1["Inventory"] == "Int. Arr. Inventory"
].copy()

dep = df_1[
    df_1["Inventory"] == "Int. Dep. Inventory"
].copy()



# Display charts


col1, col2 = st.columns(2)

with col1:

    st.markdown("#### International arrivals")

    arrivals_chart = create_voyage_stop_pie(
        arr,
        voy_col,
        stop_col,
        total_col
    )

    st.altair_chart(
        arrivals_chart,
        use_container_width=True
    )


with col2:

    st.markdown("#### International departures")

    departures_chart = create_voyage_stop_pie(
        dep,
        voy_col,
        stop_col,
        total_col
    )

    st.altair_chart(
        departures_chart,
        use_container_width=True
    )


if metric == "GHG emissions (t CO2e)":

    total_col = "co2e_t"
    port_col = "co2e_t_stop"
    voyage_col = "co2e_t_voy"

    unit = "t CO2e"

else:

    total_col = "ene_tj"
    port_col = "ene_tj_stop"
    voyage_col = "ene_tj_voy"

    unit = "TJ"



# GET SELECTED COUNTRY FROM SESSION STATE


selected_iso3 = st.session_state.get(
    "iso_3",
    None
)

# prepare data

plot_df = df.copy()

# Remove countries with missing/zero totals
plot_df = plot_df[
    plot_df[total_col].notna()
    & (plot_df[total_col] > 0)
].copy()



# country level percentages


plot_df["Port %"] = (
    plot_df[port_col]
    / plot_df[total_col]
    * 100
)

plot_df["Voyage %"] = (
    plot_df[voyage_col]
    / plot_df[total_col]
    * 100
)

fig = go.Figure()

# function 

def add_panel(data, inventory_name, x_offset):

    panel_data = data[
        data["Inventory"] == inventory_name
    ].copy()

    categories = [
        ("In Port", "Port %", x_offset),
        ("In Voyage", "Voyage %", x_offset + 1)
    ]

    for label, value_col, position in categories:

        subset = panel_data.copy()

        np.random.seed(42 + position)

        jitter = np.random.uniform(
            -0.15,
            0.15,
            size=len(subset)
        )

        x_values = position + jitter

        # box plot

        fig.add_trace(
    go.Box(
        x=[position] * len(subset),
        y=subset[value_col],

        name=label,

        boxpoints=False,

        width=0.5,

        showlegend=False,

        hovertemplate=(
            "<b>" + label + "</b><br>"
            "Maximum: %{upper:.2f}%<br>"
            "Q3 (75%): %{q3:.2f}%<br>"
            "Median: %{median:.2f}%<br>"
            "Q1 (25%): %{q1:.2f}%<br>"
            "Minimum: %{lower:.2f}%<br>"
            "Countries: " + str(len(subset)) +
            "<extra></extra>"
        )
    )
)

        is_selected = (
            subset["alpha-3"] == selected_iso3
        )
  
        # Normal Countries
    
        normal = subset[~is_selected]

        normal_x = x_values[~is_selected]

        if len(normal) > 0:

            customdata_normal = np.column_stack([
                normal["alpha-3"],
                normal[total_col],
                normal[port_col],
                normal[voyage_col]
            ])

            fig.add_trace(
                go.Scatter(
                    x=normal_x,
                    y=normal[value_col],

                    mode="markers",

                    showlegend=False,

                    marker=dict(
                        size=7,
                        color="blue",
                        opacity=0.65
                    ),

                    customdata=customdata_normal,

                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        + label +
                        ": %{y:.2f}%<br>"
                        "Total: %{customdata[1]:,.2f} "
                        + unit + "<br>"
                        "In port: %{customdata[2]:,.2f} "
                        + unit + "<br>"
                        "In voyage: %{customdata[3]:,.2f} "
                        + unit +
                        "<extra></extra>"
                    )
                )
            )

        # selected country
       
        selected = subset[is_selected]

        selected_x = x_values[is_selected]

        if len(selected) > 0:

            customdata_selected = np.column_stack([
                selected["alpha-3"],
                selected[total_col],
                selected[port_col],
                selected[voyage_col]
            ])

            fig.add_trace(
                go.Scatter(
                    x=selected_x,
                    y=selected[value_col],

                    mode="markers",

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
                        + label +
                        ": %{y:.2f}%<br>"
                        "Total: %{customdata[1]:,.2f} "
                        + unit + "<br>"
                        "In port: %{customdata[2]:,.2f} "
                        + unit + "<br>"
                        "In voyage: %{customdata[3]:,.2f} "
                        + unit +
                        "<extra></extra>"
                    )
                )
            )



# Add International arrivals

add_panel(
    plot_df,
    "Int. Arr. Inventory",
    0
)



# Add international departures


add_panel(
    plot_df,
    "Int. Dep. Inventory",
    3
)

fig.update_layout(

    height=600,

    template="plotly_white",

    hovermode="closest",

    margin=dict(
        l=70,
        r=30,
        t=90,
        b=60
    ),

    xaxis=dict(
        tickmode="array",

        tickvals=[
            0,
            1,
            3,
            4
        ],

        ticktext=[
            "In Port",
            "In Voyage",
            "In Port",
            "In Voyage"
        ],

        range=[
            -0.5,
            4.5
        ],

        title=None
    ),

    yaxis=dict(
        title="Percentage of country's total",

        ticksuffix="%",

        range=[
            0,
            100
        ]
    )
)

fig.add_vline(
    x=2,
    line_width=1,
    line_dash="dash"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# arr = df[
#     df["Inventory"] == "Int. Arr. Inventory"
# ].copy()

# arr = arr[
#     ["alpha-3", "co2e_t", "co2e_t_voy", "co2e_t_stop", "ene_tj", "ene_tj_voy", "ene_tj_stop", "n_vys", "apt_flt"]
# ].rename(columns={
#     "co2e_t_voy": "co2e_t__voy_arr",
#     "co2e_t_stop": "co2e_t_stop_arr",
#     "co2e_t": "co2e_t_arr",
#     "ene_tj": "ene_tj_arr",
#     "ene_tj_voy": "ene_tj_stop_arr",
#     "ene_tj_stop": "ene_tj_stop_arr",
#     "n_vys": "n_vys_arr",
#     "apt_flt": "apt_flt_arr"
# })


# # -----------------------------
# # DEPARTURES
# # -----------------------------

# dep = df[
#     df["Inventory"] == "Int. Dep. Inventory"
# ].copy()

# dep = dep[
#     ["alpha-3", "co2e_t", "co2e_t_voy", "co2e_t_stop", "ene_tj", "ene_tj_voy", "ene_tj_stop", "n_vys", "apt_flt"]
# ].rename(columns={
#    "co2e_t_voy": "co2e_t__voy_dep",
#     "co2e_t_stop": "co2e_t_stop_dep",
#     "co2e_t": "co2e_t_dep",
#     "ene_tj": "ene_tj_dep",
#     "ene_tj_voy": "ene_tj_stop_dep",
#     "ene_tj_stop": "ene_tj_stop_dep",
#     "n_vys": "n_vys_dep",
#     "apt_flt": "apt_flt_dep"
# })


# # -----------------------------
# # MERGE
# # -----------------------------

# bubble_df = arr.merge(
#     dep,
#     on="alpha-3",
#     how="inner"
# )


# # -----------------------------
# # BUBBLE VARIABLES
# # -----------------------------

# # Total number of voyages
# bubble_df["total_voyages"] = (
#     bubble_df["n_vys_arr"] +
#     bubble_df["n_vys_dep"]
# )

# # Average time in port
# bubble_df["avg_time_in_port"] = (
#     bubble_df["apt_flt_arr"] +
#     bubble_df["apt_flt_dep"]
# ) / 2

# fig = px.scatter(
#     bubble_df,
#     x="co2e_t_arr",
#     y="co2e_t_dep",
#     size="avg_time_in_port",
#     color="total_voyages",
#     hover_name="alpha-3",
#     size_max=60,
#     color_continuous_scale="Reds",
#     labels={
#         "arr_ghg": "International Arrivals GHG Emissions (t CO2e)",
#         "dep_ghg": "International Departures GHG Emissions (t CO2e)",
#         "total_voyages": "Total Voyages",
#         "avg_time_in_port": "Average Time in Port"
#     }
# )

# fig.update_layout(
#     title="International Arrivals vs Departures GHG Emissions",
#     xaxis_title="International Arrivals GHG Emissions (t CO2e)",
#     yaxis_title="International Departures GHG Emissions (t CO2e)"
# )

# st.plotly_chart(
#     fig,
#     use_container_width=True
# )
