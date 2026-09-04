# StudentRequest

Serializer for the Student model. Handles student CRUD with validation on unique student_id and fields.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** | Student&#39;s first name | 
**last_name** | **str** | Student&#39;s last name | 
**birth_date** | **date** | Date of birth (YYYY-MM-DD) | [optional] 
**sex** | [**PatchedStudentRequestSex**](PatchedStudentRequestSex.md) |  | [optional] 
**course** | **str** | Degree program or course (e.g. BSIT, BSCS, BSN) | 
**section** | **str** | Class section (e.g. 3A, 1-1, CS401) | 
**contact_no** | **str** | Contact number or mobile phone | [optional] 

## Example

```python
from openapi_client.models.student_request import StudentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of StudentRequest from a JSON string
student_request_instance = StudentRequest.from_json(json)
# print the JSON string representation of the object
print(StudentRequest.to_json())

# convert the object into a dict
student_request_dict = student_request_instance.to_dict()
# create an instance of StudentRequest from a dict
student_request_from_dict = StudentRequest.from_dict(student_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


