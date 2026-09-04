# Student

Serializer for the Student model. Handles student CRUD with validation on unique student_id and fields.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**student_id** | **int** | Auto-incrementing unique student identifier | [readonly] 
**first_name** | **str** | Student&#39;s first name | 
**last_name** | **str** | Student&#39;s last name | 
**birth_date** | **date** | Date of birth (YYYY-MM-DD) | [optional] 
**sex** | [**PatchedStudentRequestSex**](PatchedStudentRequestSex.md) |  | [optional] 
**course** | **str** | Degree program or course (e.g. BSIT, BSCS, BSN) | 
**section** | **str** | Class section (e.g. 3A, 1-1, CS401) | 
**contact_no** | **str** | Contact number or mobile phone | [optional] 
**health_records_count** | **int** |  | [readonly] 
**created_at** | **datetime** | Timestamp when student record was created | [readonly] 
**updated_at** | **datetime** | Timestamp when student record was last updated | [readonly] 

## Example

```python
from openapi_client.models.student import Student

# TODO update the JSON string below
json = "{}"
# create an instance of Student from a JSON string
student_instance = Student.from_json(json)
# print the JSON string representation of the object
print(Student.to_json())

# convert the object into a dict
student_dict = student_instance.to_dict()
# create an instance of Student from a dict
student_from_dict = Student.from_dict(student_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


