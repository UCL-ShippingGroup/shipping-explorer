import pandas as pd
import requests
from io import StringIO
import streamlit as st

# Load Country ISO data
country_iso_codes_c = ["name", "alpha-2", "alpha-3", "country-code"]
country_iso_codes_d = {"alpha-2":str, "alpha-3":str, "country-code":str}
country_iso_codes_r = {"name":"iso_country", "alpha-2":"iso_2", "alpha-3":"iso_3", "country-code":"iso_code"}

country_iso_codes = pd.read_csv(
  "https://raw.githubusercontent.com/james-stewart-808/inventory-tracker/main/datasets/country_iso_codes.csv",
  usecols=country_iso_codes_c, 
  dtype=country_iso_codes_d).rename(
  columns=country_iso_codes_r)

# Fix Namibia ISO issue
country_iso_codes.loc[country_iso_codes.iso_country == "Namibia", "iso_2"] = "NA"
country_iso_codes.loc[country_iso_codes.iso_country == "Congo, Democratic Republic of the", "iso_country"] = "Democratic Republic of the Congo"


# Homepage Description
st.title("The Shipping Emissions Explorer")
st.write(
  """
  The International Maritime Organisation (IMO) is currently deliberating over the adoption of a Net-Zero Framework to \
  oversee the elimiation of GHG emissions from international shipping by 2050. In light of these negotiations, there is a \
  pressing need for statistics and indicators to concisely summarise key trends in maritime activity occurring at country- \
  level scales. 
    
  This 'Shipping Explorer' tool from the UCL Shipping and Oceans Research Group has been built to provide \
  users with the functionality to easily summarise key trends in shipping activity associated with individual member states of the \
  IMO. The dropdown menu below can be used to select for a specific country, with data characterising the number of voyages, energy demands and GHG emissions \
  associated with internationally arriving and internationally departing voyages for the country presented on the 'Voyage Inventories' page.

  In addition, there is a growing interest in data able to capture the decarbonisation potential associated with \
  port electrification technologies. Port electrification is a growing and immediate priority within the
  context of maritime decarbonization, where the switching of fossil-powered port activities to renewable electricity via onshore power will cut GHG \
  emissions, local air pollution and operating costs, as well as serve to prepare ports for incoming zero-emission shipping fuels. Energy \
  demand and GHG emission statistics associated with maritime activity taking place 'at sea' versus 'in port' are therefore provided via the 'Global Overview' and 'Regional\
  Overview' pages to provide additional context on the aggregate mitigation potential that port electrification can offer.
  """
)

st.write(
    """
    The public dashboard is available via the UCL Shipping and Oceans Research Group website and via the following link:
    """
)

st.markdown(
  """
  **Dashboard**: https://shipping-explorer-production.up.railway.app/
  """, 
  text_alignment="center"
)

st.subheader("Country selection", divider = 'grey')

# Country Selector
country_choice = st.selectbox(
    "For which country would you like statistics on international shipping activity and emissions? Ensure a country is selected before moving on to the following pages.",
    country_iso_codes.iso_country.unique(),
    index=2)

# set as global variable
st.session_state.iso_country = country_choice
st.session_state.iso_2 = country_iso_codes[(country_iso_codes.iso_country == country_choice)].iso_2.values[0]
st.session_state.iso_3 = country_iso_codes[(country_iso_codes.iso_country == country_choice)].iso_3.values[0]
st.session_state.iso_code = country_iso_codes[(country_iso_codes.iso_country == country_choice)].iso_code.values[0]

#st.write("""Use the sidebar to explore the different components of the dashboard...""")
#st.page_link("inventories.py", label="**Voyage-based Inventories**", icon="🚢")
#st.page_link("trade.py", label="**Merchandise Trade Portfolios**", icon="📦")

st.divider()


st.markdown(
"""
##### Disclaimer

The content on this website is for informational and educational purposes only. It should not be considered as \
financial, investment, or legal advice. We are not financial advisors, and the information provided is not a substitute \
for professional advice from a qualified expert who is aware of your individual circumstances. Always conduct your own \
research and consult with a licensed financial professional before making any investment or financial decisions. Any \
reliance you place on the information provided on this site is strictly at your own risk. We are not liable for any \
losses or damages incurred from the use of this information.
"""
)
#st.divider()



#st.markdown("##### References")

#st.write(
#"""
#IPCC (2006). 2006 IPCC Guidelines for National Greenhouse Gas Inventories. \
#    Volume 2 (Energy), Chapter 3 on Mobile combustion – Section 5 on Water-borne \
#    Navigation. Intergovernmental Panel on Climate Change.
#"""
#)
