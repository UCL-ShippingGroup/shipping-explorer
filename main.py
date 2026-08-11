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
st.title("The Shipping and Trade Explorer Dashboard")
st.write(
    """
    International frameworks assign responsibility for mitigation of maritime GHGs to the International \
    Maritime Organisation (IMO) (IPCC, 2006), the UN body tasked with governing international waters, and the organisation \
    is now deliberating over the adoption of a Net-Zero Framework (NZF) to oversee the elimination of GHGs from international \
    shipping by 2050. In light of these negotiations, there is a pressing need for statistics and indicators \
    able to concisely summarise key trends in maritime activity occuring at country-level scales.
    """
)

st.write(
    """
    This 'Shipping and Trade Explorer' tool from the UCL Shipping and Oceans research \
    group has therefore been built to enable users to easily characterise the shipping and trade activity associated with \
    individual countries. The public dashboard is available via the following link:
    """
)
st.markdown(
  """
  **Dashboard**: https://shipping-and-trade-explorer.streamlit.app/
  """, 
  text_alignment="center"
)

st.subheader("Country selection", divider = 'grey')

# Country Selector
country_choice = st.selectbox(
    "For which country would you like to statistics related to international shipping and maritime trade?",
    country_iso_codes.iso_country.unique(),
    index=2)

# set as global variable
st.session_state.iso_country = country_choice
st.session_state.iso_2 = country_iso_codes[(country_iso_codes.iso_country == country_choice)].iso_2.values[0]
st.session_state.iso_3 = country_iso_codes[(country_iso_codes.iso_country == country_choice)].iso_3.values[0]
st.session_state.iso_code = country_iso_codes[(country_iso_codes.iso_country == country_choice)].iso_code.values[0]

st.write("""Use the sidebar to explore the different components of the dashboard...""")
st.page_link("inventories.py", label="**Voyage-based Inventories**", icon="🚢")
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
st.divider()



st.markdown("##### References")

st.write(
"""
CE Delft. (2021). Study on assessment of possible global regulatory measures to \
    reduce greenhouse gas emissions from international shipping. European \
    Commission.
    
IPCC (2006). 2006 IPCC Guidelines for National Greenhouse Gas Inventories. \
    Volume 2 (Energy), Chapter 3 on Mobile combustion – Section 5 on Water-borne \
    Navigation. Intergovernmental Panel on Climate Change.
"""
)
