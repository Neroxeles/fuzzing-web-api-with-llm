You are a Code generator.
Task:
Create a function called 'get_dict_with_random_values' in Python that generates random values for the following variables:
- {vendor: {type:string, pattern:'[a-zA-Z ]{2,50}'}}
- {product_id: {type:integer,format:int32,description: Signed 64-bit integers}}
Think step by step.
Result:
```python
# import packages
import random
import string

# This functions generates a random value for {vendor: {type:string, pattern:'[a-zA-Z ]{2,50}'}}
def random_vendor() -> str:
  # The following characters should be used '[a-zA-Z ]'
  characters = string.ascii_letters + string.digits + " "
  # The string can be 2 to 50 characters long
  length = random.randint(3, 20)
  return ''.join(random.choice(characters) for _ in range(length))

# This functions generates a random value for {product_id: {type:integer,format:int32}}
def random_product_id() -> int:
  return random.randint(-2**63, 2**63 - 1)

# This functions returns a dictionary that contains all variables (vendor, product_id)
def get_dict_with_random_values() -> dict:
  # use the functions from above to generate random values
  variables = {
    "vendor": random_vendor(),
    "product_id": random_product_id()
  }
  return variables
```
Task:
Create a function called 'get_dict_with_random_values' in Python that generates random values for the following variables: 
<!-- insert list here -->
Think step by step.
Result:
```python
# Here is the correct implementation of the code exercise
