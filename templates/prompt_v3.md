<fim_prefix>You are a Code generator.
Task:
Generate a function in Python that creates random values for the following variables:
- {animal: {type:string,pattern:'[A-Za-z0-9]{3-20}',minLength:3,maxLength:20}}
- {age: {type:integer,minimum:0,maximum:20}}
- {hairy: {type:boolean}}
Think step by step:
Solution:
```python
<filename>solutions/solution_1.py
# import neccessery libraries
import random
import string

# This functions generates a random value for {animal: {type:string,pattern:'[A-Za-z0-9]{3-20}',minLength:3,maxLength:20}}
def random_animal() -> str:
  # The following characters can be used for '[A-Za-z0-9]'
  characters = string.ascii_letters + string.digits
  # There must be a minimum of 3 and a maximum of 20 characters
  length = random.randint(3, 20)
  return ''.join(random.choice(characters) for _ in range(length))

# This functions generates a random value for {age: {type:integer,minimum:0,maximum:20}}
def random_age() -> int:
  return random.randint(0,20)

# This functions generates a random value for {hairy: {type:boolean}}
def random_hairy() -> int:
  return random.randint(0,1)

# This functions returns a dictionary that contains all variables (animal, age, hairy)
def get_dict_with_random_values() -> dict:
  # use the functions from above to generate random values
  variables = {
    "animal": random_animal(),
    "age": random_age(),
    "hairy": random_hairy()
  }
  return variables
```
Task:
Generate a function in Python that creates random values for the following variables:
<!-- insert list here -->
Think step by step:
Solution:
```python
<filename>solutions/solution_2.py
<fim_suffix><fim_middle>