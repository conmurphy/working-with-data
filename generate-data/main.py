
'''
Copyright (c) 2023 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
'''

from faker import Faker
from faker.providers import DynamicProvider
import random
import locale
import pandas as pd
from datetime import datetime

NUMBER_OF_CUSTOMERS = 1000

locale.setlocale(locale.LC_ALL, '')

fake = Faker()


products_provider = DynamicProvider(
    provider_name="products_provider",
    elements=set(['Anchovies','Aspirin','Batteries','Beer','Candle','Candy','Canned Fruit','Canned Vegetables','Cereal','Cheese','Chips','Chocolate','Cleaner','Coffee','Cookies','Cooking Oil','Cottage Cheese','Crackers','Deoderant','Dish Soap','Donut','Dried Fruit','Eggs','Flavored Drink','Fresh Chicken','Fresh Fish','Fresh Fruit','Fresh Vegetables','Frozen Chicken','Frozen Vegetables','Hamburger','Hot Dog','Ice Cream','Jam','Juice','Magazine','Milk','Mouthwash','Muffin','Nuts','Oysters','Pancake Mix','Paper Towel','Pasta','Peanut Butter','Pizza','Plastic Utensils','Popcorn','Pots and Pans','Rice','Sardines','Sauce','Shampoo','Soap','Shrimp','Sliced Bread','Soda','Soup','Sour Cream','Spices','Sponge','Sugar','Sunglasses','Tofu','Toothbrush','Tuna','Wine','Yogurt']),
)

fake.add_provider(products_provider)

data = []

for _ in range(NUMBER_OF_CUSTOMERS):
    
    customer_id = fake.unique.random_int(min=111111111, max=999999999)
    customer_name = fake.name()
    city = fake.city()
    address = fake.street_address()
    buying_program = random.choice(["B2B","B2C","C2C","A2D","E2F"])
    repeat_customer = random.choice(["Yes",""])
    internal_customer_code_A = fake.bothify(text='????-########', letters='ABCDE')
    internal_customer_code_B = fake.bothify(text='????-########', letters='FGHIJK')
    back_office_flag = random.choice(["Y","N"])
    contract_number = random.choice(["",fake.unique.random_int(min=100000, max=999999)])
    contract_type = fake.bothify(text='????', letters='ABCDEFGHIJKL')
    
    for shopping_trips_to_take in range(fake.random_int(min=10, max=20)):
        
        order_date = fake.date_between(start_date='-5y', end_date='today').strftime('%Y-%m-%d')
        order_year = datetime.strptime(order_date, '%Y-%m-%d').year
        public_holiday = random.choice(["Y","N"])
        order_quarter = fake.random_int(min=1, max=4)
        order_id = fake.unique.random_int(min=1111111, max=9999999)
        store_id = fake.postcode()
        store_size = random.choice(["Micro","Small", "Medium","Large","X-Large"])
        are_balloons_in_stock = random.choice(["Y","N"])
        random_code = fake.bothify(text='INTERNAL: ###-???', letters='ABCDEFGHIJKLMNOPQRSTUVWXZY')

        for number_of_items_to_buy in range(fake.random_int(min=3, max=30)):
            product_bu = random.choice(["ABC","BCD","CDE","DEF"])
            product_type = random.choice(["Perishable","Non-perishable"])
            product = fake.products_provider()
            description = fake.sentence(nb_words=10)
            num_letters_in_product_name = len(product)
            random_colour = fake.color_name()
            internal_product_flag = fake.bothify(text='????-####', letters='WXYZ')
            best_before = fake.date_between(start_date='today', end_date='+1y').strftime('%Y-%m-%d')
            quantity = fake.random_int(min=1, max=10)
            item_cost = round(random.uniform(2.0, 12.0),2)
            total_cost = locale.currency(quantity*item_cost)

            

            data.append([customer_id,customer_name,city, address,buying_program, repeat_customer,internal_customer_code_A, internal_customer_code_B, back_office_flag,contract_number, contract_type, order_year,public_holiday, order_date,order_id,store_id, store_size,are_balloons_in_stock,random_code,product_bu,product_type, product,description,num_letters_in_product_name,random_colour,internal_product_flag, best_before, quantity, item_cost,total_cost ])

sample_data = pd.DataFrame(data, columns=['Customer ID', 'Customer Name', 'City','Address', 'Buying Program', 'Repeat Customer', 'Internal Customer Code A', 'Internal Customer Code B','Back Office Flag', 'Contract Number', 'Contract Type','Order Year', 'Is it a Public Holiday?','Order Date', 'Order ID','Store ID','Store Size','Are Balloons In Stock?','Random Code','Product BU','Product Type','Product','Product Description','Number of Letters in Product Name','Random Colour','Internal Product Flag','Before Before Date','Quantity', 'Item Cost', 'Total Cost'])


sample_data.to_excel(r'sample_data.xlsx', index = False)

