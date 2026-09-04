# HealthRecord

Serializer for the HealthRecord model. Handles foreign-key relationship with Student via student_id.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**health_id** | **int** | Unique health record identifier | [readonly] 
**student_id** | **int** | The ID of the student associated with this health record | 
**student_name** | **str** |  | [readonly] 
**allergies** | **str** | Known allergies (e.g. penicillin, peanuts, pollen) | [optional] 
**blood_type** | [**HealthRecordBloodType**](HealthRecordBloodType.md) |  | [optional] 
**medical_history** | **str** | Past medical history and chronic conditions (e.g. Asthma, Hypertension) | [optional] 
**medication** | **str** | Current medications and prescriptions | [optional] 
**weight** | **decimal.Decimal** | Weight in kilograms (kg) | [optional] 
**height** | **decimal.Decimal** | Height in centimeters (cm) | [optional] 
**visit** | **datetime** | Date and time of clinic visit | [optional] 
**consultation** | **str** | Clinic consultation notes, diagnosis, and treatment provided | [optional] 
**created_at** | **datetime** | Timestamp when health record was created | [readonly] 
**updated_at** | **datetime** | Timestamp when health record was last updated | [readonly] 

## Example

```python
from openapi_client.models.health_record import HealthRecord

# TODO update the JSON string below
json = "{}"
# create an instance of HealthRecord from a JSON string
health_record_instance = HealthRecord.from_json(json)
# print the JSON string representation of the object
print(HealthRecord.to_json())

# convert the object into a dict
health_record_dict = health_record_instance.to_dict()
# create an instance of HealthRecord from a dict
health_record_from_dict = HealthRecord.from_dict(health_record_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


