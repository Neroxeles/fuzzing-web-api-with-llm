You are a Code generator.
Task:
Create a function called 'get_dict_with_random_values' in Python that generates random values for the following variables:
- {'vendor': {'type':'string', 'pattern':'[a-zA-Z ]{2,50}'}}
- {'product_id': {'type':'integer'}}
Think step by step:
1. import necessary libraries
2. Create a single function without input parameters
3. Create a dictionary that contains all variables
5. Return the dictionary
Result:
```python
# Here is the correct implementation of the code exercise
import random
import string

def get_dict_with_random_values() -> dict:
  characters = string.ascii_letters + " "
  length = random.randint(2, 50)

  variables = {
    "vendor": ''.join(random.choice(characters) for _ in range(length)),
    "product_id": random.randint(1,100)
  }
  return variables
```
Task:
Create a function called 'get_dict_with_random_values' in Python that generates random values for the following variables: 
<!-- insert list here -->
Think step by step:
1. import necessary libraries
2. Create a single function without input parameters
3. Create a dictionary that contains all variables
5. Return the dictionary
Result:
```python
# Here is the correct implementation of the code exercise
