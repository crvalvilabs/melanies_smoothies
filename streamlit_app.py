# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col


# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """
    Choose the fruits you want in your custom Smoothie!
  """
)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table('SMOOTHIES.PUBLIC.FRUIT_OPTIONS').select(col('SEARCH_ON'))

# Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be: ', name_on_order)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections= 5
)

if ingredients_list:

    ingredients_string = ''
    
    for each_fruit in ingredients_list:
        ingredients_string += each_fruit + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == each_fruit, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', each_fruit, ' is ', search_on, ',')
      
        st.subheader(each_fruit = 'Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=fruityvice_response.json(), use_dataframe_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


