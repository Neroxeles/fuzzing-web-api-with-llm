<fim_prefix>You are a Code generator.
You have access to the following additional information about regex:
```cheat-sheet
Character Classes:
- [ABC] match any character in the set.
- [^ABC] match any character that is not in the set.
- [A-Z] matches a character having a character code between the two specified characters inclusive.
- . matches any character except linebreaks. Equivalent to [^\n\r].
- [\s\S] A character set that can be used to match any character, including line breaks, without the dotall flag (s). An alternative is [^].
- \w matches any word character (alphanumeric & underscore). Only matches low-ascii characters (no accented or non-roman characters). Equivalent to [A-Za-z0-9_].
- \W matches any character that is not a word character (alphanumeric & underscore). Equivalent to [^A-Za-z0-9_]
- \d matches any digit character (0-9). Equivalent to [0-9].
- \D matches any character that is not a digit character (0-9). Equivalent to [^0-9].
- \s matches any whitespace character (spaces, tabs, line breaks).
- \S matches any character that is not a whitespace character (spaces, tabs, line breaks).
Anchors:
- ^ matches the beginning of the string. This matches a position, not a character.
- $ matches the end of the string. This matches a position, not a character.
Groups and References:
- (ABC) groups multiple tokens together and creates a capture group for extracting a substring or using a backreference.
Quantifiers and Alternation
- + matches 1 or more of the preceding token.
- * matches 0 or more of the preceding token.
- {1,3} matches the specified quantity of the previous token. {1,3} will match 1 to 3. {3} will match exactly 3. {3,} will match 3 or more.
- ? Matches 0 or 1 of the preceding token, effectively making it optional.
```

Task:
Generate a function in Python that creates random values for the following variables:
- {animal: {type:string,pattern:'[A-Za-z0-9]{3-20}',example:'Frederike34'}}
- {age: {type:integer,minimum:0,maximum:20}}
- {hairy: {type:boolean}}
Think step by step:
Solution:
```python
<filename>solutions/solution_1.py
import random
import string

# This functions generates a random value for {animal: {type:string,pattern:'[A-Za-z0-9]{3-20}',example:'Frederike34'}}
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
- {caretaker_id: {type:string,pattern:'[A-Za-z0-9]{4}-[A-Za-z0-9]{6}-[0-9]{2}-[A-Z]{1}',example:'sD3r-wer43T-34-A'}}
- {telephone: {type:string,pattern:'\+49 [0-9]{11}',example:'+49 34562378342'}}
- {password: {type:string,pattern:'[.]{8-50}',example:'asdui#+349*~.,/wr'}}
Think step by step:
Solution:
```python
<filename>solutions/solution_2.py
import random
import string

# This functions generates a random value for {caretaker_id: {type:string,pattern:'[A-Za-z0-9]{4}-[A-Za-z0-9]{6}-[0-9]{2}-[A-Z]{1}',example:'sD3r-wer43T-34-A'}}
def random_caretaker_id() -> str:
  # The following characters should be used '[A-Za-z0-9]'
  characters = string.ascii_letters + string.digits
  length = 4
  caretaker_id = ''.join(random.choice(characters) for _ in range(length)) + "-"

  length = 6
  caretaker_id = caretaker_id + ''.join(random.choice(characters) for _ in range(length)) + "-"

  # The following characters should be used '[0-9]'
  characters = string.digits
  length = 2
  caretaker_id = caretaker_id + ''.join(random.choice(characters) for _ in range(length)) + "-"

  # The following characters should be used '[A-Z]'
  characters = string.ascii_uppercase
  length = 1
  caretaker_id = caretaker_id + ''.join(random.choice(characters) for _ in range(length))
  return caretaker_id

# This functions generates a random value for {telephone: {type:string,pattern:'\+49 [0-9]{11}',example:'+49 34562378342'}}
def random_telephone() -> int:
  # The following characters should be used '[0-9]'
  characters = string.digits
  length = 11
  telephone = "+49 " + ''.join(random.choice(characters) for _ in range(length))
  return telephone

# This functions generates a random value for {password: {type:string,pattern:'[.]{8-50}',example:'asdui#+349*~.,/wr'}}
def random_password() -> int:
  # The following characters should be used '[.]'
  characters = string.ascii_letters + string.digits + string.punctuation
  length = random.randint(8, 50)
  return ''.join(random.choice(characters) for _ in range(length))

# This functions returns a dictionary that contains all variables (caretaker_id, telephone, password)
def get_dict_with_random_values() -> dict:
  # use the functions from above to generate random values
  variables = {
    "caretaker_id": random_caretaker_id(),
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
<filename>solutions/solution_3.py
<fim_suffix><fim_middle>