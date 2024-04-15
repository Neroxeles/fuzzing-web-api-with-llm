<fim_prefix>You are a Code generator.
Task:
Generate a function in Python that creates random values for the following variables:
- {item: {type:integer}}
- {product_id: {type:integer}}
- {amount: {type:integer}}
Think step by step:
1. import necessary libraries
2. Create a single function without parameters
3. Create a dictionary that contains all variables
5. Return the dictionary
Result:
```python
<filename>solutions/solution_1.py
# Here is the correct implementation of the code exercise
import random

def function_1() -> dict:
  variables = {
    "item": random.randint(1,100),
    "product_id": random.randint(1,100),
    "amount": random.randint(1,100)
  }
  return variables
```
Task:
Generate a function in Python that creates random values for the following variables:
<!-- insert list here -->
Think step by step:
1. import necessary libraries
2. Create a single function without parameters
3. Create a dictionary that contains all variables
5. Return the dictionary
Result:
```python
<filename>solutions/solution_1.py
# Here is the correct implementation of the code exercise
<fim_suffix><fim_middle>