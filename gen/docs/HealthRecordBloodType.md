# HealthRecordBloodType

Blood type (e.g. A+, O+, etc.)  * `A+` - A+ * `A-` - A- * `B+` - B+ * `B-` - B- * `AB+` - AB+ * `AB-` - AB- * `O+` - O+ * `O-` - O- * `Unknown` - Unknown

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------

## Example

```python
from openapi_client.models.health_record_blood_type import HealthRecordBloodType

# TODO update the JSON string below
json = "{}"
# create an instance of HealthRecordBloodType from a JSON string
health_record_blood_type_instance = HealthRecordBloodType.from_json(json)
# print the JSON string representation of the object
print(HealthRecordBloodType.to_json())

# convert the object into a dict
health_record_blood_type_dict = health_record_blood_type_instance.to_dict()
# create an instance of HealthRecordBloodType from a dict
health_record_blood_type_from_dict = HealthRecordBloodType.from_dict(health_record_blood_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


