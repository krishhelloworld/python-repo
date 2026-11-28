import psycopg
from info_patient import info
from post_database import add_db
from patient import Patient
from address import Address
from colors import red, green, reset


address_dict = {"city": "gorakhpur", "state": "Up", "pincode": "273001"}
Address1 = Address(**address_dict)
patient_dict = {"name": "krish", "gender": "maLe", "address": Address1}
patient1 = Patient(**patient_dict)


info(patient1)

## without dictionary form
print(patient1)

"""
HOW TO GET THE JSON FORMAT OF THIS DATA
"""
patient1_json = patient1.model_dump()
print(red)
print(patient1_json)
print(reset, end="")
print(type(patient1_json))


"""
TO GET THE DATA IN DB
"""
add_db(patient1_json)
# patient1_name= patient1.model_dump(include=['name'])

# patient1_without_gender= patient1.model_dump(exclude=['gender'])
# patient1_without_state= patient1.model_dump(exclude={'address':['state']})
# print(patient1_without_gender)
# print(patient1_without_state)
