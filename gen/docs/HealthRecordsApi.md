# openapi_client.HealthRecordsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**health_records_create**](HealthRecordsApi.md#health_records_create) | **POST** /api/health-records/ | Create a health record
[**health_records_destroy**](HealthRecordsApi.md#health_records_destroy) | **DELETE** /api/health-records/{health_id}/ | Delete a health record
[**health_records_list**](HealthRecordsApi.md#health_records_list) | **GET** /api/health-records/ | List all health records
[**health_records_partial_update**](HealthRecordsApi.md#health_records_partial_update) | **PATCH** /api/health-records/{health_id}/ | Partially update a health record
[**health_records_retrieve**](HealthRecordsApi.md#health_records_retrieve) | **GET** /api/health-records/{health_id}/ | Retrieve a health record
[**health_records_update**](HealthRecordsApi.md#health_records_update) | **PUT** /api/health-records/{health_id}/ | Update a health record


# **health_records_create**
> HealthRecord health_records_create(health_record_request)

Create a health record

Create a new clinic consultation / health record associated with a student.

### Example

* Basic Authentication (basicAuth):
* Api Key Authentication (cookieAuth):

```python
import openapi_client
from openapi_client.models.health_record import HealthRecord
from openapi_client.models.health_record_request import HealthRecordRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: basicAuth
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure API key authorization: cookieAuth
configuration.api_key['cookieAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['cookieAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.HealthRecordsApi(api_client)
    health_record_request = openapi_client.HealthRecordRequest() # HealthRecordRequest | 

    try:
        # Create a health record
        api_response = api_instance.health_records_create(health_record_request)
        print("The response of HealthRecordsApi->health_records_create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthRecordsApi->health_records_create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **health_record_request** | [**HealthRecordRequest**](HealthRecordRequest.md)|  | 

### Return type

[**HealthRecord**](HealthRecord.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **health_records_destroy**
> health_records_destroy(health_id)

Delete a health record

Delete an existing health record by health_id.

### Example

* Basic Authentication (basicAuth):
* Api Key Authentication (cookieAuth):

```python
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: basicAuth
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure API key authorization: cookieAuth
configuration.api_key['cookieAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['cookieAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.HealthRecordsApi(api_client)
    health_id = 56 # int | 

    try:
        # Delete a health record
        api_instance.health_records_destroy(health_id)
    except Exception as e:
        print("Exception when calling HealthRecordsApi->health_records_destroy: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **health_id** | **int**|  | 

### Return type

void (empty response body)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | No response body |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **health_records_list**
> List[HealthRecord] health_records_list(blood_type=blood_type, search=search, student_id=student_id)

List all health records

Retrieve a list of all health records with optional filtering by student ID, blood type, or search keyword.

### Example

* Basic Authentication (basicAuth):
* Api Key Authentication (cookieAuth):

```python
import openapi_client
from openapi_client.models.health_record import HealthRecord
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: basicAuth
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure API key authorization: cookieAuth
configuration.api_key['cookieAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['cookieAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.HealthRecordsApi(api_client)
    blood_type = 'blood_type_example' # str | Filter health records by blood type (optional)
    search = 'search_example' # str | Search keyword matching student name, allergies, consultation notes, medical history, or student ID (optional)
    student_id = 'student_id_example' # str | Filter health records for a specific student by student ID (optional)

    try:
        # List all health records
        api_response = api_instance.health_records_list(blood_type=blood_type, search=search, student_id=student_id)
        print("The response of HealthRecordsApi->health_records_list:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthRecordsApi->health_records_list: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **blood_type** | **str**| Filter health records by blood type | [optional] 
 **search** | **str**| Search keyword matching student name, allergies, consultation notes, medical history, or student ID | [optional] 
 **student_id** | **str**| Filter health records for a specific student by student ID | [optional] 

### Return type

[**List[HealthRecord]**](HealthRecord.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **health_records_partial_update**
> HealthRecord health_records_partial_update(health_id, patched_health_record_request=patched_health_record_request)

Partially update a health record

Partially update one or more fields of an existing health record.

### Example

* Basic Authentication (basicAuth):
* Api Key Authentication (cookieAuth):

```python
import openapi_client
from openapi_client.models.health_record import HealthRecord
from openapi_client.models.patched_health_record_request import PatchedHealthRecordRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: basicAuth
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure API key authorization: cookieAuth
configuration.api_key['cookieAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['cookieAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.HealthRecordsApi(api_client)
    health_id = 56 # int | 
    patched_health_record_request = openapi_client.PatchedHealthRecordRequest() # PatchedHealthRecordRequest |  (optional)

    try:
        # Partially update a health record
        api_response = api_instance.health_records_partial_update(health_id, patched_health_record_request=patched_health_record_request)
        print("The response of HealthRecordsApi->health_records_partial_update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthRecordsApi->health_records_partial_update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **health_id** | **int**|  | 
 **patched_health_record_request** | [**PatchedHealthRecordRequest**](PatchedHealthRecordRequest.md)|  | [optional] 

### Return type

[**HealthRecord**](HealthRecord.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **health_records_retrieve**
> HealthRecord health_records_retrieve(health_id)

Retrieve a health record

Retrieve details of a specific health record by health_id.

### Example

* Basic Authentication (basicAuth):
* Api Key Authentication (cookieAuth):

```python
import openapi_client
from openapi_client.models.health_record import HealthRecord
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: basicAuth
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure API key authorization: cookieAuth
configuration.api_key['cookieAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['cookieAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.HealthRecordsApi(api_client)
    health_id = 56 # int | 

    try:
        # Retrieve a health record
        api_response = api_instance.health_records_retrieve(health_id)
        print("The response of HealthRecordsApi->health_records_retrieve:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthRecordsApi->health_records_retrieve: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **health_id** | **int**|  | 

### Return type

[**HealthRecord**](HealthRecord.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **health_records_update**
> HealthRecord health_records_update(health_id, health_record_request)

Update a health record

Update all fields of an existing health record.

### Example

* Basic Authentication (basicAuth):
* Api Key Authentication (cookieAuth):

```python
import openapi_client
from openapi_client.models.health_record import HealthRecord
from openapi_client.models.health_record_request import HealthRecordRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: basicAuth
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)

# Configure API key authorization: cookieAuth
configuration.api_key['cookieAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['cookieAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.HealthRecordsApi(api_client)
    health_id = 56 # int | 
    health_record_request = openapi_client.HealthRecordRequest() # HealthRecordRequest | 

    try:
        # Update a health record
        api_response = api_instance.health_records_update(health_id, health_record_request)
        print("The response of HealthRecordsApi->health_records_update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthRecordsApi->health_records_update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **health_id** | **int**|  | 
 **health_record_request** | [**HealthRecordRequest**](HealthRecordRequest.md)|  | 

### Return type

[**HealthRecord**](HealthRecord.md)

### Authorization

[basicAuth](../README.md#basicAuth), [cookieAuth](../README.md#cookieAuth)

### HTTP request headers

 - **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

