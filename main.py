import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image

image = Image.open('19368.jpg')

st.image(image, width=300)
st.title("Vendor Management Portal")
st.markdown("Enter the details of the new vendor below")

conn = st.connection("gsheets", type=GSheetsConnection)

existing_data = conn.read(worksheet="Vendor", usecols=list(range(6)), ttl=5)
existing_data = existing_data.dropna(how="all")

#st.dataframe(existing_data)

BUSINESS_TYPES = [
    "Manufacturer",
    "Distributor",
    "Wholesaler",
    "Retailer",
    "Service Provider",
]
PRODUCTS = [
    "Electronics",
    "Apparel",
    "Groceries",
    "Software",
    "Other",
]

action = st.selectbox(
    "Choose an Action",
    [
        "Onboard New Vendor",
        "Update Existing Vendor",
        "View All Vendors",
        "Delete Vendor",
    ],
)

if action == "Onboard New Vendor":
    st.markdown("Enter the details of the new vendor below.")
    with st.form(key="vendor_form"):
        company_name = st.text_input(label="Company Name*")
        business_type = st.selectbox(
            "Business Type*", options=BUSINESS_TYPES, index=None
        )
        products = st.multiselect("Products Offered", options=PRODUCTS)
        years_in_business = st.slider("Years in Business", 0, 50, 5)
        onboarding_date = st.date_input(label="Onboarding Date")
        additional_info = st.text_area(label="Additional Notes")

        st.markdown("**required*")
        submit_button = st.form_submit_button(label="Submit Vendor Details")

        if submit_button:
            if not company_name or not business_type:
                st.warning("Ensure all mandatory fields are filled.")
            elif existing_data["Company_Name"].astype('str').str.contains(company_name).any():
                st.warning("A vendor with this company name already exists.")
            else:
                vendor_data = pd.DataFrame(
                    [
                        {
                            "Company_Name": company_name,
                            "Business_Type": business_type,
                            "Products": ", ".join(products),
                            "Years": years_in_business,
                            "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
                            "AdditionalInfo": additional_info,
                        }
                    ]
                )
                updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)
                conn.update(worksheet="Vendor", data=updated_df)
                st.success("Vendor details successfully submitted!")

elif action == "Update Existing Vendor":
    st.markdown("Select a vendor and update their details.")

    vendor_to_update = st.selectbox(
        "Select a Vendor to Update", options=existing_data["Company_Name"].tolist()
    )
    vendor_data = existing_data[existing_data["Company_Name"] == vendor_to_update].iloc[
        0
    ]

    with st.form(key="update_form"):
        company_name = st.text_input(
            label="Company Name*", value=vendor_data["Company_Name"]
        )
        business_type = st.selectbox(
            "Business Type*",
            options=BUSINESS_TYPES,
            index=BUSINESS_TYPES.index(vendor_data["Business_Type"]),
        )
        products = st.multiselect(
            "Products Offered",
            options=PRODUCTS,
            default=vendor_data["Products"].split(", "),
        )
        years_in_business = st.slider(
            "Years in Business", 0, 50, int(vendor_data["Years"])
        )
        onboarding_date = st.date_input(
            label="Onboarding Date", value=pd.to_datetime(vendor_data["OnboardingDate"])
        )
        additional_info = st.text_area(
            label="Additional Notes", value=vendor_data["AdditionalInfo"]
        )

        st.markdown("**required*")
        update_button = st.form_submit_button(label="Update Vendor Details")

        if update_button:
            if not company_name or not business_type:
                st.warning("Ensure all mandatory fields are filled.")
            else:
                # Removing old entry
                existing_data.drop(
                    existing_data[
                        existing_data["Company_Name"] == vendor_to_update
                    ].index,
                    inplace=True,
                )
                # Creating updated data entry
                updated_vendor_data = pd.DataFrame(
                    [
                        {
                            "Company_Name": company_name,
                            "Business_Type": business_type,
                            "Products": ", ".join(products),
                            "Years": years_in_business,
                            "OnboardingDate": onboarding_date.strftime("%Y-%m-%d"),
                            "AdditionalInfo": additional_info,
                        }
                    ]
                )
                # Adding updated data to the dataframe
                updated_df = pd.concat(
                    [existing_data, updated_vendor_data], ignore_index=True
                )
                conn.update(worksheet="Vendor", data=updated_df)
                st.success("Vendor details successfully updated!")

# View All Vendors
elif action == "View All Vendors":
    st.dataframe(existing_data)

# Delete Vendor
elif action == "Delete Vendor":
    vendor_to_delete = st.selectbox(
        "Select a Vendor to Delete", options=existing_data["Company_Name"].tolist()
    )

    if st.button("Delete"):
        existing_data.drop(
            existing_data[existing_data["Company_Name"] == vendor_to_delete].index,
            inplace=True,
        )
        conn.update(worksheet="Vendor", data=existing_data)
        st.success("Vendor successfully deleted!")