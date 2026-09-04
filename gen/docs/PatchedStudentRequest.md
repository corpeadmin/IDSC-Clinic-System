# PatchedStudentRequest

Serializer for the Student model. Handles student CRUD with validation on unique student_id and fields.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**first_name** | **str** | Student&#39;s first name | [optional] 
**last_name** | **str** | Student&#39;s last name | [optional] 
**birth_date** | **date** | Date of birth (YYYY-MM-DD) | [optional] 
**sex** | [**PatchedStudentRequestSex**](PatchedStudentRequestSex.md) |  | [optional] 
**course** | **str** | Degree program or course (e.g. BSIT, BSCS, BSN) | [optional] 
**section** | **str** | Class section (e.g. 3A, 1-1, CS401) | [optional] 
**contact_no** | **str** | Contact number or mobile phone | [optional] 

## Example

```python
from openapi_client.models.patched_student_request import PatchedStudentRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PatchedStudentRequest from a JSON string
patched_student_request_instance = PatchedStudentRequest.from_json(json)
# print the JSON string representation of the object
print(PatchedStudentRequest.to_json())

# convert the object into a dict
patched_student_request_dict = patched_student_request_instance.to_dict()
# create an instance of PatchedStudentRequest from a dict
patched_student_request_from_dict = PatchedStudentRequest.from_dict(patched_student_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


