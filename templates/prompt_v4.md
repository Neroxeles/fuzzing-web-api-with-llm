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
import random
import string

# This functions generates a random value for {animal: {type:string,pattern:'[A-Za-z0-9]{3-20}',minLength:3,maxLength:20}}
def random_animal() -> str:
  # The following characters should be used '[A-Za-z0-9]'
  characters = string.ascii_letters + string.digits
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
- {id: {type:string,pattern:'[A-Za-z0-9]{4}-[A-Za-z0-9]{6}-[0-9]{2}-[A-Z]{1}'}}
- {telephone: {type:string,pattern:'\+49\s[0-9]{11}'}}
- {password: {type:string,pattern:'[.]{8-50}'}}
Think step by step:
Solution:
```python
<filename>solutions/solution_1.py
import random
import string

# This functions generates a random value for {id: {type:string,pattern:'[A-Za-z0-9]{4}-[A-Za-z0-9]{6}-[0-9]{2}-[A-Z]{1}'}}
def random_id() -> str:
  # Build 1th part
  # The following characters should be used '[A-Za-z0-9]'
  characters = string.ascii_letters + string.digits
  length = 4
  id = ''.join(random.choice(characters) for _ in range(length)) + "-"

  # Build 2th part
  length = 6
  id = id + ''.join(random.choice(characters) for _ in range(length)) + "-"

  # Build 3th part
  # The following characters should be used '[0-9]'
  characters = string.digits
  length = 2
  id = id + ''.join(random.choice(characters) for _ in range(length)) + "-"

  # Build 4th part
  # The following characters should be used '[A-Z]'
  characters = string.ascii_uppercase
  length = 1
  id = id + ''.join(random.choice(characters) for _ in range(length))
  return id

# This functions generates a random value for {telephone: {type:string,pattern:'\+49\s[0-9]{11}'}}
def random_telephone() -> int:
  # The following characters should be used '[0-9]'
  characters = string.digits
  length = 11
  telephone = "+49 " + ''.join(random.choice(characters) for _ in range(length))
  return telephone

# This functions generates a random value for {password: {type:string,pattern:'[.]{8-50}'}}
def random_password() -> int:
  # The following characters should be used '[.]'
  characters = string.ascii_letters + string.digits + string.punctuation
  length = random.randint(8, 50)
  return ''.join(random.choice(characters) for _ in range(length))

# This functions returns a dictionary that contains all variables (id, telephone, password)
def get_dict_with_random_values() -> dict:
  # use the functions from above to generate random values
  variables = {
    "id": random_id(),
    "telephone": random_telephone(),
    "password": random_password()
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