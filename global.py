import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(layout='wide')
st.title('Global Overview')

df = pd.read_csv("https://raw.githubusercontent.com/UCL-ShippingGroup/shipping-explorer/main/datasets/inventories_total.csv")

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
    options=["Absolute", "Percentage"],
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

    # GHG - Percentage
    ("GHG Emissions (t CO2e)", "Total", "Percentage"): "co2e_t_pc",
    ("GHG Emissions (t CO2e)", "In Voyage", "Percentage"): "co2e_t_voy_pc",
    ("GHG Emissions (t CO2e)", "In Port", "Percentage"): "co2e_t_stop_pc",

    # Energy - Absolute
    ("Energy Demand (TJ)", "Total", "Absolute"): "ene_tj",
    ("Energy Demand (TJ)", "In Voyage", "Absolute"): "ene_tj_voy",
    ("Energy Demand (TJ)", "In Port", "Absolute"): "ene_tj_stop",

    # Energy - Percentage
    ("Energy Demand (TJ)", "Total", "Percentage"): "ene_tj_pc",
    ("Energy Demand (TJ)", "In Voyage", "Percentage"): "ene_tj_voy_pc",
    ("Energy Demand (TJ)", "In Port", "Percentage"): "ene_tj_stop_pc",
}


selected_column = column_map[
    (chart_choice2, chart_choice3, chart_choice4)
]


# -----------------------------
# GRAPH LABELS
# -----------------------------

if chart_choice4 == "Percentage":
    unit = "%"
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
    title=f"{chart_choice2} — {chart_choice3} — {chart_choice}"
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
        st.session_state.iso_code)
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("International arrivals")
    
    # arrivals data
    # create pie chart

with col2:
    st.subheader("International departures")
    
    # departures data
    # create pie chart

metric = st.segmented_control(
    "Metric",
    options=["GHG emissions (t CO2e)", "Energy Demand (TJ)"],
    default="GHG emissions (t CO2e)",
    key="metric_selection"
)


# ---------------------------------------------------------
# 3. Select the appropriate columns
# ---------------------------------------------------------

if metric == "GHG emissions":
    voy_col = "co2e_t_voy"
    stop_col = "co2e_t_stop"
    total_col = "co2e_t"
    value_title = "CO₂e (tonnes)"

else:
    voy_col = "ene_tj_voy"
    stop_col = "ene_tj_stop"
    total_col = "ene_tj"
    value_title = "Energy demand (TJ)"


# ---------------------------------------------------------
# 4. Function to create the pie chart
# ---------------------------------------------------------

def create_voyage_stop_pie(df, voy_col, stop_col, total_col):

    # Get the values
    voyage = df[voy_col]
    stop = df[stop_col]
    total = df[total_col]

    # Calculate percentages using the existing total
    voyage_pct = voyage / total * 100
    stop_pct = stop / total * 100

    # Data for chart
    pie_df = pd.DataFrame({
        "State": ["In voyage", "In Port"],
        "Value": [voyage, stop],
        "Percentage": [voyage_pct, stop_pct]
    })

    # Create pie chart
    chart = (
        alt.Chart(pie_df)
        .mark_arc()
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
                )
            ]
        )
        .properties(
            height=300
        )
    )

    return chart


# ---------------------------------------------------------
# 5. Create arrivals and departures datasets
# ---------------------------------------------------------

arr = df_1[df_1['Inventory']== 'Int. Arr. Inventory'].copy()
dep = df_1[df_1['Inventory']== 'Int. Dep. Inventory'].copy()



# ---------------------------------------------------------
# 6. Create the two-column layout
# ---------------------------------------------------------

col1, col2 = st.columns(2)


# ---------------------------------------------------------
# 7. International arrivals
# ---------------------------------------------------------

with col1:

    st.subheader("International arrivals")

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


# ---------------------------------------------------------
# 8. International departures
# ---------------------------------------------------------

with col2:

    st.subheader("International departures")

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
