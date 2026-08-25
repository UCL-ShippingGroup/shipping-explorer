st.set_page_config(layout='wide')
st.title('Regional Overview')
st.divider()

df_in = pd.read_csv("https://raw.githubusercontent.com/UCL-ShippingGroup/shipping-explorer/main/datasets/inventories_total.csv")
df_reg = pd.read_csv("https://raw.githubusercontent.com/UCL-ShippingGroup/shipping-explorer/main/datasets/country_status_labels_v3.csv")

df = df_in.merge(
    df_reg[["iso-3", "region_wb", "status"]],
    left_on="alpha-3",
    right_on="iso-3",
    how="left"
)

# Remove the duplicate ISO-3 column from df_reg
df = df.drop(columns="iso-3")

