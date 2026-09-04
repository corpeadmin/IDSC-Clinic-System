# PatchedHealthRecordRequest

Serializer for the HealthRecord model. Handles foreign-key relationship with Student via student_id.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**student_id** | **int** | The ID of the student associated with this health record | [optional] 
**allergies** | **str** | Known allergies (e.g. penicillin, peanuts, pollen) | [optional] 
**blood_type** | [**HealthRecordBloodType**](HealthRecordBloodType.md) |  | [optional] 
**medical_history** | **str** | Past medical history and chronic conditions (e.g. Asthma, Hypertension) | [optional] 
**medication** | **str** | Current medications and prescriptions | [optional] 
**weight** | **decimal.Decimal** | Weight in kilograms (kg) | [optional] 
**height** | **decimal.Decimal** | Height in centimeters (cm) | [optional] 
**visit** | **datetime** | Date and time of clinic visit | [optional] 
**consultation** | **str** | Clinic consultation notes, diagnosis, and treatment provided | [optional] 

## Example

```python
from openapi_client.models.patched_health_record_request import PatchedHealthRecordRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PatchedHealthRecordRequest from a JSON string
patched_health_record_request_instance = PatchedHealthRecordRequest.from_json(json)
# print the JSON string representation of the object
print(PatchedHealthRecordRequest.to_json())

# convert the object into a dict
patched_health_record_request_dict = patched_health_record_request_instance.to_dict()
# create an instance of PatchedHealthRecordRequest from a dict
patched_health_record_request_from_dict = PatchedHealthRecordRequest.from_dict(patched_health_record_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


