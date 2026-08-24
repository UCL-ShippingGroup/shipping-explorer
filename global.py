import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

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
    default="GHG Emisions (t CO2e)"
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

    plot_df = inventories_total[
        inventories_total["Inventory"] == "Int. Arr. Inventory"
    ].copy()

else:

    plot_df = inventories_total[
        inventories_total["Inventory"] == "Int. Dep. Inventory"
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
    ("GHG Emissions (t CO2e)", "In Port", "Percentage"): "co2_t_stop_pc",

    # Energy - Absolute
    ("Energy Demand (TJ)", "Total", "Absolute"): "ene_te",
    ("Energy Demand (TJ)", "In Voyage", "Absolute"): "ene_te_voy",
    ("Energy Demand (TJ)", "In Port", "Absolute"): "ene_te_stop",

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
    color_continuous_scale="Reds",
    labels={selected_column: unit},
    title=f"{chart_choice2} — {chart_choice3} — {chart_choice}"
)


  
  
