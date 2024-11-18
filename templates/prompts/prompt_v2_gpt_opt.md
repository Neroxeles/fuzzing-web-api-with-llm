**Prompt:**

You are a code generator tasked with creating Python functions to generate random values for API parameters and properties based on a given OpenAPI Specification (OAS). The purpose is to simulate random API inputs for testing purposes.

**Task:**

Using the given OAS excerpt, write a Python module that:
1. Creates a function for each parameter and property in the OAS to generate random values.
2. Implements a function `get_dict_with_random_values` that assembles and returns a dictionary containing:
   - `para_<parameter_name>`: random values for path/query/header parameters.
   - `prop_<property_name>`: random values for request body properties.

### Input: OAS Excerpt

```json
<!-- insert oas-section here -->
```

### Expected Output:

The `get_dict_with_random_values` function should return:

```json
<!-- insert data structure here -->
```

Each random value is generated using a dedicated function.

### Solution:

Write Python code to:

1. Define individual random value generators for each parameter/property.
2. Aggregate results into the required dictionary structure in `get_dict_with_random_values`.

```python
