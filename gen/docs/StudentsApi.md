# openapi_client.StudentsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**students_create**](StudentsApi.md#students_create) | **POST** /api/students/ | Create a new student
[**students_destroy**](StudentsApi.md#students_destroy) | **DELETE** /api/students/{student_id}/ | Delete a student
[**students_health_records_create**](StudentsApi.md#students_health_records_create) | **POST** /api/students/{student_id}/health-records/ | Create health record for a student
[**students_health_records_list**](StudentsApi.md#students_health_records_list) | **GET** /api/students/{student_id}/health-records/ | List health records for a student
[**students_list**](StudentsApi.md#students_list) | **GET** /api/students/ | List all students
[**students_partial_update**](StudentsApi.md#students_partial_update) | **PATCH** /api/students/{student_id}/ | Partially update a student
[**students_retrieve**](StudentsApi.md#students_retrieve) | **GET** /api/students/{student_id}/ | Retrieve student details
[**students_update**](StudentsApi.md#students_update) | **PUT** /api/students/{student_id}/ | Update a student


# **students_create**
> Student students_create(student_request)

Create a new student

Register a new student record in the IDSC Clinic System.

### Example

* Basic Authentication (basicAuth):
* Api Key Authentication (cookieAuth):

```python
import openapi_client
from openapi_client.models.student import Student
from openapi_client.models.student_request import StudentRequest
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
    api_instance = openapi_client.StudentsApi(api_client)
    student_request = openapi_client.StudentRequest() # StudentRequest | 

    try:
        # Create a new student
        api_response = api_instance.students_create(student_request)
        print("The response of StudentsApi->students_create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StudentsApi->students_create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **student_request** | [**StudentRequest**](StudentRequest.md)|  | 

### Return type

[**Student**](Student.md)

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

# **students_destroy**
> students_destroy(student_id)

Delete a student

Delete an existing student and all associated health records.

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
    api_instance = openapi_client.StudentsApi(api_client)
    student_id = 'student_id_example' # str | 

    try:
        # Delete a student
        api_instance.students_destroy(student_id)
    except Exception as e:
        print("Exception when calling StudentsApi->students_destroy: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **student_id** | **str**|  | 

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

# **students_health_records_create**
> HealthRecord students_health_records_create(student_id, health_record_request)

Create health record for a student

Create a new clinic consultation / health record for the specified student.

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
    api_instance = openapi_client.StudentsApi(api_client)
    student_id = 'student_id_example' # str | 
    health_record_request = openapi_client.HealthRecordRequest() # HealthRecordRequest | 

    try:
        # Create health record for a student
        api_response = api_instance.students_health_records_create(student_id, health_record_request)
        print("The response of StudentsApi->students_health_records_create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StudentsApi->students_health_records_create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **student_id** | **str**|  | 
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

# **students_health_records_list**
> List[HealthRecord] students_health_records_list(student_id)

List health records for a student

Retrieve all health records and clinic consultations for a specific student, ordered by visit date descending.

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
    api_instance = openapi_client.StudentsApi(api_client)
    student_id = 'student_id_example' # str | 

    try:
        # List health records for a student
        api_response = api_instance.students_health_records_list(student_id)
        print("The response of StudentsApi->students_health_records_list:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StudentsApi->students_health_records_list: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **student_id** | **str**|  | 

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

# **students_list**
> List[Student] students_list(course=course, search=search, section=section, sex=sex)

List all students

Retrieve a list of all students with optional search and filtering by course, section, or sex.

### Example

* Basic Authentication (basicAuth):
* Api Key Authentication (cookieAuth):

```python
import openapi_client
from openapi_client.models.student import Student
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
    api_instance = openapi_client.StudentsApi(api_client)
    course = 'course_example' # str | Filter by degree program / course (case-insensitive exact match) (optional)
    search = 'search_example' # str | Search keyword matching first name, last name, course, section, or student ID (optional)
    section = 'section_example' # str | Filter by section (case-insensitive exact match) (optional)
    sex = 'sex_example' # str | Filter by sex (Male, Female, Other) (optional)

    try:
        # List all students
        api_response = api_instance.students_list(course=course, search=search, section=section, sex=sex)
        print("The response of StudentsApi->students_list:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StudentsApi->students_list: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **course** | **str**| Filter by degree program / course (case-insensitive exact match) | [optional] 
 **search** | **str**| Search keyword matching first name, last name, course, section, or student ID | [optional] 
 **section** | **str**| Filter by section (case-insensitive exact match) | [optional] 
 **sex** | **str**| Filter by sex (Male, Female, Other) | [optional] 

### Return type

[**List[Student]**](Student.md)

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

# **students_partial_update**
> Student students_partial_update(student_id, patched_student_request=patched_student_request)

Partially update a student

Partially update one or more fields of an existing student record.

### Example

* Basic Authentication (basicAuth):
* Api Key Authentication (cookieAuth):

```python
import openapi_client
from openapi_client.models.patched_student_request import PatchedStudentRequest
from openapi_client.models.student import Student
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
    api_instance = openapi_client.StudentsApi(api_client)
    student_id = 'student_id_example' # str | 
    patched_student_request = openapi_client.PatchedStudentRequest() # PatchedStudentRequest |  (optional)

    try:
        # Partially update a student
        api_response = api_instance.students_partial_update(student_id, patched_student_request=patched_student_request)
        print("The response of StudentsApi->students_partial_update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StudentsApi->students_partial_update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **student_id** | **str**|  | 
 **patched_student_request** | [**PatchedStudentRequest**](PatchedStudentRequest.md)|  | [optional] 

### Return type

[**Student**](Student.md)

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

# **students_retrieve**
> StudentDetail students_retrieve(student_id)

Retrieve student details

Retrieve complete details for a specific student by student_id, including full nested health records history.

### Example

* Basic Authentication (basicAuth):
* Api Key Authentication (cookieAuth):

```python
import openapi_client
from openapi_client.models.student_detail import StudentDetail
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
    api_instance = openapi_client.StudentsApi(api_client)
    student_id = 'student_id_example' # str | 

    try:
        # Retrieve student details
        api_response = api_instance.students_retrieve(student_id)
        print("The response of StudentsApi->students_retrieve:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StudentsApi->students_retrieve: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **student_id** | **str**|  | 

### Return type

[**StudentDetail**](StudentDetail.md)

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

# **students_update**
> Student students_update(student_id, student_request)

Update a student

Update all fields of an existing student record.

### Example

* Basic Authentication (basicAuth):
* Api Key Authentication (cookieAuth):

```python
import openapi_client
from openapi_client.models.student import Student
from openapi_client.models.student_request import StudentRequest
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
    api_instance = openapi_client.StudentsApi(api_client)
    student_id = 'student_id_example' # str | 
    student_request = openapi_client.StudentRequest() # StudentRequest | 

    try:
        # Update a student
        api_response = api_instance.students_update(student_id, student_request)
        print("The response of StudentsApi->students_update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StudentsApi->students_update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **student_id** | **str**|  | 
 **student_request** | [**StudentRequest**](StudentRequest.md)|  | 

### Return type

[**Student**](Student.md)

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

