## analytics-csv-provider

Creates training data for device types from multiple data sources. Training data is provided via an HTTP API.

### Configuration

`CONF_LOGGER_LEVEL`: Set logging level to `info`, `warning`, `error`, `critical` or `debug`.

`CONF_STORAGE_DB_PATH`: Set database path.

`CONF_STORAGE_DATA_PATH`: Set path for training data files.

`CONF_STORAGE_TMP_PATH`: Set path for temporary files.

`CONF_JOBS_MAX_NUM`: Set maximum number of parallel jobs.

`CONF_JOBS_CHECK`: Control how often the worker checks if new jobs are available.

`CONF_DATA_DB_API_URL`: URL of API for the database containing data of data sources.

`CONF_DATA_EXPORT_API_URL`: URL of API for managing data sources.

`CONF_DATA_TIME_FORMAT`: Time format to be used for training data.

`CONF_DATA_DB_API_TIME_FORMAT`: Time format used by database.

`CONF_DATA_START_YEAR`: Determines the year in which the training data starts after the timestamps have been shifted. Can't be earlier than 1970.

`CONF_DATA_CHUNK_SIZE`: The amount of data that will be retrieved from the database.

`CONF_DATA_COMPRESSION`: Enable or disable compression of training data.

`CONF_AUTH_API_URL`: URL of authorization API.

`CONF_AUTH_CLIENT_ID`: Client ID required by the authorization API. **(required)**

`CONF_AUTH_CLIENT_SECRET`: Secret required by the authorization API. **(required)**

`CONF_AUTH_USER_ID`: User ID required by the authorization API. **(required)**

### Data Structures

#### Job resource

    {
        "id": <string>,
        "created": <string>,
        "status": "<string>",
        "source_id": <string>,
        "reason": <string>
    }

#### Data resource

    {
        "source_id": <string>,
        "time_field": <string>,
        "delimiter": <string>,
        "sources": <object>,
        "size": <number>,
        "created": <string>,
        "columns": <object>,
        "default_values": <object>,
        "files": <array>,
        "checksum": <string>,
        "compressed": <boolean>
    }

#### Data request

    {
        "source_id": <string>,
        "time_field": <string>,
        "delimiter": <string>,
    }

#### Job request

    {
        "source_id": <string>
    }

### API

#### /data

**GET**

_List IDs of all data resources._

    # Example    
    
    curl http://<host>/data
    [
        "urn:infai:ses:service:c2872437-3e53-49c6-a5be-bf264d52430d"
    ]

**POST**

_Send a data request to create a new data resource._

    # Example

    cat new_data_request.json
    {
        "source_id": "urn:infai:ses:service:c2872437-3e53-49c6-a5be-bf264d52430d",
        "time_field": "time",
        "delimiter": ","
    }

    curl \
    -d @new_data_request.json \
    -H `Content-Type: application/json` \
    -X POST http://<host>/data

    # Response status 201 if created and 200 if resource alread exists

#### /data/{source_id}

**GET**

_Retrieve a data resource._

    # Example    
    
    curl http://<host>/data/urn:infai:ses:service:c2872437-3e53-49c6-a5be-bf264d52430d
    {
        "source_id": "urn:infai:ses:service:c2872437-3e53-49c6-a5be-bf264d52430d",
        "time_field": "time",
        "delimiter": ",",
        "sources": {
            "df656316-b57e-4e8a-a1f5-8b08ae4f85e1": {
                "start": "2021-01-26T09:34:50.000000Z",
                "end": "2021-07-27T03:59:58.000000Z",
                "year_map": {
                    "2021": "1970"
                }
            }
        },
        "size": 1050000,
        "created": "2021-07-27T13:24:25.943398Z",
        "columns": [
            "time",
            "location_ec-generator_gesamtwirkleistung",
            "location_ec-gesamt_gesamtwirkleistung",
            "location_ec-prozess_gesamtwirkleistung",
            "location_ec-roboter_gesamtwirkleistung",
            "location_roboter-ausgabe_gesamtwirkleistung",
            "location_roboter-eingabe_gesamtwirkleistung",
            "location_transport-gesamt_gesamtwirkleistung",
            "location_wm1-gesamt_gesamtwirkleistung",
            "location_wm1-heizung-reinigen_gesamtwirkleistung",
            "location_wm1-heizung-trocknung_gesamtwirkleistung",
            "location_wm2-gesamt_gesamtwirkleistung",
            "location_wm2-heizung-reinigen_gesamtwirkleistung",
            "location_wm2-heizung-trocknung_gesamtwirkleistung",
            "location_wm2-vakuumpumpe_gesamtwirkleistung",
            "module_1_errorcode",
            "module_1_errorindex",
            "module_1_state",
            "module_1_station_1_process_1_errorcode_0",
            "module_1_station_1_process_1_errorcode_1112",
            "module_1_station_1_process_1_errorcode_133",
            "module_1_station_1_process_1_errorcode_8",
            "module_1_station_1_process_1_errorcode_980",
            "module_1_station_2_process_1_errorcode_0",
            "module_1_station_2_process_1_errorcode_10922",
            "module_1_station_2_process_1_errorcode_1112",
            "module_1_station_2_process_1_errorcode_117",
            "module_1_station_2_process_1_errorcode_1212",
            "module_1_station_2_process_1_errorcode_4432",
            "module_1_station_2_process_1_errorcode_5312",
            "module_1_station_2_process_1_errorcode_8",
            "module_1_station_2_process_1_errorcode_8822",
            "module_1_station_2_process_1_errorcode_980",
            "module_1_station_31_process_1_errorcode_0",
            "module_1_station_31_process_1_errorcode_980",
            "module_1_station_31_process_1_errorcode_981",
            "module_1_station_31_process_1_errorcode_998",
            "module_1_station_3_process_1_errorcode_0",
            "module_1_station_3_process_1_errorcode_1112",
            "module_1_station_3_process_1_errorcode_133",
            "module_1_station_3_process_1_errorcode_8",
            "module_1_station_3_process_1_errorcode_980",
            "module_1_station_4_process_1_errorcode_0",
            "module_1_station_4_process_1_errorcode_10922",
            "module_1_station_4_process_1_errorcode_1112",
            "module_1_station_4_process_1_errorcode_117",
            "module_1_station_4_process_1_errorcode_1212",
            "module_1_station_4_process_1_errorcode_4432",
            "module_1_station_4_process_1_errorcode_5312",
            "module_1_station_4_process_1_errorcode_8",
            "module_1_station_4_process_1_errorcode_8822",
            "module_1_station_4_process_1_errorcode_980",
            "module_1_station_4_process_1_errorcode_981",
            "module_1_station_5_process_1_errorcode_0",
            "module_1_station_5_process_1_errorcode_1112",
            "module_1_station_5_process_1_errorcode_133",
            "module_1_station_5_process_1_errorcode_8",
            "module_1_station_5_process_1_errorcode_980",
            "module_1_station_6_process_1_errorcode_0",
            "module_1_station_6_process_1_errorcode_10922",
            "module_1_station_6_process_1_errorcode_1112",
            "module_1_station_6_process_1_errorcode_117",
            "module_1_station_6_process_1_errorcode_1212",
            "module_1_station_6_process_1_errorcode_4432",
            "module_1_station_6_process_1_errorcode_5312",
            "module_1_station_6_process_1_errorcode_8",
            "module_1_station_6_process_1_errorcode_8822",
            "module_1_station_6_process_1_errorcode_980",
            "module_1_station_6_process_1_errorcode_981",
            "module_2_errorcode",
            "module_2_errorindex",
            "module_2_state",
            "module_2_station_17_process_1_errorcode_0",
            "module_2_station_17_process_1_errorcode_998",
            "module_2_station_1_process_1_errorcode_0",
            "module_2_station_21_process_1_errorcode_999",
            "module_2_station_22_process_1_errorcode_0",
            "module_2_station_22_process_1_errorcode_999",
            "module_2_station_24_process_1_errorcode_0",
            "module_2_station_25_process_1_errorcode_51",
            "module_2_station_25_process_1_errorcode_53",
            "module_2_station_25_process_1_errorcode_55",
            "module_2_station_28_process_1_errorcode_10922",
            "module_2_station_28_process_1_errorcode_1112",
            "module_2_station_28_process_1_errorcode_117",
            "module_2_station_28_process_1_errorcode_1212",
            "module_2_station_28_process_1_errorcode_133",
            "module_2_station_28_process_1_errorcode_4432",
            "module_2_station_28_process_1_errorcode_51",
            "module_2_station_28_process_1_errorcode_53",
            "module_2_station_28_process_1_errorcode_5312",
            "module_2_station_28_process_1_errorcode_55",
            "module_2_station_28_process_1_errorcode_8",
            "module_2_station_28_process_1_errorcode_8822",
            "module_2_station_28_process_1_errorcode_980",
            "module_2_station_28_process_1_errorcode_981",
            "module_2_station_29_process_1_errorcode_0",
            "module_2_station_2_process_1_errorcode_0",
            "module_2_station_2_process_1_errorcode_999",
            "module_2_station_36_process_1_errorcode_999",
            "module_2_station_3_process_1_errorcode_0",
            "module_2_station_3_process_1_errorcode_998",
            "module_2_station_4_process_1_errorcode_0",
            "module_2_station_4_process_1_errorcode_998",
            "module_2_station_50_process_1_errorcode_0",
            "module_2_station_51_process_1_errorcode_0",
            "module_2_station_51_process_1_errorcode_51",
            "module_2_station_51_process_1_errorcode_53",
            "module_2_station_51_process_1_errorcode_55",
            "module_2_station_51_process_1_errorcode_999",
            "module_2_station_5_process_1_errorcode_0",
            "module_2_station_5_process_1_errorcode_998",
            "module_2_station_6_process_1_errorcode_0",
            "module_2_station_6_process_1_errorcode_998",
            "module_4_errorcode",
            "module_4_errorindex",
            "module_4_state",
            "module_5_errorcode",
            "module_5_errorindex",
            "module_5_state",
            "module_6_errorcode",
            "module_6_errorindex",
            "module_6_state"
        ],
        "default_values": {
            "module_2_station_4_process_1_errorcode_998": 0,
            "module_1_station_31_process_1_errorcode_0": 0,
            "module_2_station_51_process_1_errorcode_0": 0,
            "module_2_station_3_process_1_errorcode_998": 0,
            "module_2_station_50_process_1_errorcode_0": 0,
            "module_1_station_5_process_1_errorcode_0": 0,
            "module_2_station_24_process_1_errorcode_0": 0,
            "module_2_station_5_process_1_errorcode_998": 0,
            "module_1_station_2_process_1_errorcode_0": 0,
            "module_1_station_3_process_1_errorcode_0": 0,
            "module_1_station_6_process_1_errorcode_0": 0,
            "module_1_station_4_process_1_errorcode_0": 0,
            "module_1_station_1_process_1_errorcode_0": 0,
            "module_2_station_1_process_1_errorcode_0": 0,
            "module_2_station_4_process_1_errorcode_0": 0,
            "module_2_station_3_process_1_errorcode_0": 0,
            "module_2_station_5_process_1_errorcode_0": 0,
            "module_2_station_21_process_1_errorcode_999": 0,
            "module_2_station_22_process_1_errorcode_0": 0,
            "module_2_station_6_process_1_errorcode_998": 0,
            "module_2_station_6_process_1_errorcode_0": 0,
            "module_2_station_51_process_1_errorcode_51": 0,
            "module_2_station_25_process_1_errorcode_51": 0,
            "module_2_station_28_process_1_errorcode_55": 0,
            "module_2_station_28_process_1_errorcode_51": 0,
            "module_2_station_28_process_1_errorcode_980": 0,
            "module_1_station_31_process_1_errorcode_998": 0,
            "module_2_station_51_process_1_errorcode_55": 0,
            "module_2_station_25_process_1_errorcode_55": 0,
            "module_2_station_29_process_1_errorcode_0": 0,
            "module_2_station_22_process_1_errorcode_999": 0,
            "module_1_station_2_process_1_errorcode_980": 0,
            "module_1_station_31_process_1_errorcode_980": 0,
            "module_1_station_1_process_1_errorcode_980": 0,
            "module_2_station_51_process_1_errorcode_53": 0,
            "module_1_station_6_process_1_errorcode_980": 0,
            "module_2_station_25_process_1_errorcode_53": 0,
            "module_1_station_5_process_1_errorcode_980": 0,
            "module_1_station_4_process_1_errorcode_980": 0,
            "module_1_station_3_process_1_errorcode_980": 0,
            "module_2_station_28_process_1_errorcode_53": 0,
            "module_2_station_2_process_1_errorcode_0": 0,
            "module_2_station_2_process_1_errorcode_999": 0,
            "module_1_station_2_process_1_errorcode_1212": 0,
            "module_1_station_6_process_1_errorcode_1212": 0,
            "module_1_station_4_process_1_errorcode_1212": 0,
            "module_2_station_28_process_1_errorcode_1212": 0,
            "module_2_station_36_process_1_errorcode_999": 0,
            "module_2_station_17_process_1_errorcode_998": 0,
            "module_1_station_2_process_1_errorcode_1112": 0,
            "module_1_station_6_process_1_errorcode_1112": 0,
            "module_1_station_4_process_1_errorcode_1112": 0,
            "module_2_station_28_process_1_errorcode_1112": 0,
            "module_2_station_17_process_1_errorcode_0": 0,
            "module_1_station_1_process_1_errorcode_1112": 0,
            "module_1_station_5_process_1_errorcode_1112": 0,
            "module_1_station_3_process_1_errorcode_1112": 0,
            "module_1_station_2_process_1_errorcode_4432": 0,
            "module_1_station_2_process_1_errorcode_5312": 0,
            "module_1_station_6_process_1_errorcode_4432": 0,
            "module_1_station_6_process_1_errorcode_5312": 0,
            "module_1_station_4_process_1_errorcode_4432": 0,
            "module_1_station_4_process_1_errorcode_5312": 0,
            "module_1_station_31_process_1_errorcode_981": 0,
            "module_1_station_6_process_1_errorcode_981": 0,
            "module_1_station_4_process_1_errorcode_981": 0,
            "module_2_station_28_process_1_errorcode_5312": 0,
            "module_2_station_28_process_1_errorcode_4432": 0,
            "module_2_station_28_process_1_errorcode_981": 0,
            "module_1_station_2_process_1_errorcode_8822": 0,
            "module_1_station_2_process_1_errorcode_10922": 0,
            "module_1_station_6_process_1_errorcode_10922": 0,
            "module_1_station_6_process_1_errorcode_8822": 0,
            "module_1_station_4_process_1_errorcode_8822": 0,
            "module_1_station_4_process_1_errorcode_10922": 0,
            "module_2_station_28_process_1_errorcode_8822": 0,
            "module_2_station_28_process_1_errorcode_10922": 0,
            "module_1_station_1_process_1_errorcode_133": 0,
            "module_1_station_5_process_1_errorcode_133": 0,
            "module_1_station_3_process_1_errorcode_133": 0,
            "module_2_station_28_process_1_errorcode_133": 0,
            "module_2_station_51_process_1_errorcode_999": 0,
            "module_1_station_2_process_1_errorcode_8": 0,
            "module_1_station_6_process_1_errorcode_8": 0,
            "module_1_station_4_process_1_errorcode_8": 0,
            "module_2_station_28_process_1_errorcode_8": 0,
            "module_1_station_2_process_1_errorcode_117": 0,
            "module_1_station_6_process_1_errorcode_117": 0,
            "module_1_station_4_process_1_errorcode_117": 0,
            "module_2_station_28_process_1_errorcode_117": 0,
            "module_1_station_1_process_1_errorcode_8": 0,
            "module_1_station_5_process_1_errorcode_8": 0,
            "module_1_station_3_process_1_errorcode_8": 0
        },
        "files": [
            "adb607144c474b459865793f2f1351a7_16273920334791317",
            "adb607144c474b459865793f2f1351a7_16273920449616423",
            "adb607144c474b459865793f2f1351a7_16273920574766681",
            "adb607144c474b459865793f2f1351a7_16273920693257813",
            "adb607144c474b459865793f2f1351a7_16273920794238732",
            "adb607144c474b459865793f2f1351a7_16273920892823374",
            "adb607144c474b459865793f2f1351a7_16273920992794209",
            "adb607144c474b459865793f2f1351a7_1627392109905064",
            "adb607144c474b459865793f2f1351a7_16273921210630476",
            "adb607144c474b459865793f2f1351a7_16273921402968574",
            "adb607144c474b459865793f2f1351a7_16273921517773533",
            "adb607144c474b459865793f2f1351a7_1627392162350018",
            "adb607144c474b459865793f2f1351a7_16273921736337597",
            "adb607144c474b459865793f2f1351a7_1627392185776647",
            "adb607144c474b459865793f2f1351a7_16273921961827378",
            "adb607144c474b459865793f2f1351a7_1627392206188905",
            "adb607144c474b459865793f2f1351a7_1627392216009924",
            "adb607144c474b459865793f2f1351a7_16273922258080156",
            "adb607144c474b459865793f2f1351a7_1627392235563348",
            "adb607144c474b459865793f2f1351a7_16273922452968788",
            "adb607144c474b459865793f2f1351a7_16273922551728852"
        ],
        "checksum": "e33f616b934110d05cd236f5e2324044f5ea2f718c679a7aee7c53f3c1a71e03",
        "compressed": true,
        "file": null
    }

#### /data/{source_id}/files/{file_id}

_Retrieve the training data (chunked) associated with the data resource._

    # Example    
    
    curl --output training_data_chunk http://<host>/data/urn:infai:ses:service:c2872437-3e53-49c6-a5be-bf264d52430d/files/adb607144c474b459865793f2f1351a7_16273920334791317
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100 5114k  100 5114k    0     0  27.2M      0 --:--:-- --:--:-- --:--:-- 27.4M

#### /jobs

**GET**

_List IDs of all jobs._

    # Example    
    
    curl http://<host>/jobs
    {
        "current": [],
        "history": [
            "008c8baa935c48d0a092c0d9f8f547aa",
            "0885de76b99645b2b0d66700a9494fae",
            "101bf32d21104163b811dfe64cd153ce",
            "1d6af989dec8427186482028045e5d8a"
        ]
    }

**POST**

_Send a job request to start a job._

    # Example

    cat new_job_request.json
    {
        "source_id": "urn:infai:ses:service:c2872437-3e53-49c6-a5be-bf264d52430d"
    }
    
    curl \
    -d @new_job_request.json \
    -H `Content-Type: application/json` \
    -X POST http://<host>/jobs

#### /jobs/{job_id}

**GET**

Retrieve job details.

    # Example
    
    curl http://<host>/jobs/008c8baa935c48d0a092c0d9f8f547aa
    {
        "id": "008c8baa935c48d0a092c0d9f8f547aa",
        "created": "2021-05-19T06:25:19.765681Z",
        "status": "finished",
        "source_id": "urn:infai:ses:service:c2872437-3e53-49c6-a5be-bf264d52430d",
        "reason": null
    }
