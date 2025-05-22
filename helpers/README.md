# Becik4UParameters Class

The `Becik4UParameters` class is designed to handle environment setup and directory management for the Becik4U system. It ensures that the required environment variables are set and provides utility functions to manage application directories and root scan directories.

## Features

- **Operating System Check**: Ensures that the system is running Linux (as required by the Becik4U system).
- **Environment Variable Management**: Checks for necessary environment variables (`FREESURFER_HOME`, `BECIK4U_ROOT`, `BECIK4U_CORE`) and raises an error if any are missing.
- **Directory Management**: Provides methods for retrieving application directories and scan directories based on the provided scan ID.

## Class: `Becik4UParameters`

### Initialization (`__init__`)

When an instance of `Becik4UParameters` is created, it performs the following actions:

1. **Checks the Operating System**: Ensures the system is running on Linux.
2. **Retrieves Environment Variables**: Looks for the environment variables `FREESURFER_HOME`, `BECIK4U_ROOT`, and `BECIK4U_CORE` and assigns them to instance variables.

### Methods

#### `_check_os()`

- **Purpose**: Verifies that the operating system is Linux.
- **Raises**: `Exception` if the OS is not Linux.

#### `_get_env(name: str) -> str`

- **Purpose**: Retrieves the value of the given environment variable.
- **Arguments**:
  - `name` (str): The name of the environment variable to retrieve.
- **Returns**: The value of the environment variable.
- **Raises**: `Exception` if the environment variable is not set.

#### `get_app_dir(app_name: str) -> str`

- **Purpose**: Constructs and returns the absolute path to the directory of the specified application.
- **Arguments**:
  - `app_name` (str): The name of the application whose directory is required.
- **Returns**: The absolute directory path of the application.

#### `get_root_scan_dir(id: str) -> str`

- **Purpose**: Constructs and returns the absolute path to the root scan directory based on the given ID.
- **Arguments**:
  - `id` (str): The unique identifier of the scan.
- **Returns**: The absolute path to the root scan directory.

## Example Usage

```python
import { Becik4UParameters } from 'helpers/parameters';

const params = new Becik4UParameters();

// Get the directory for a specific application
const appDir = params.get_app_dir("example_app");
console.log(`Application directory: ${appDir}`);

// Get the root scan directory for a specific ID
const rootScanDir = params.get_root_scan_dir("scan_id_123");
console.log(`Root scan directory: ${rootScanDir}`);
```

## Environment Variables Required

The following environment variables must be set for the `Becik4UParameters` class to function correctly:

- **`FREESURFER_HOME`**: Path to the FreeSurfer installation.
- **`BECIK4U_ROOT`**: Root directory of the Becik4U system.
- **`BECIK4U_CORE`**: Core directory for the Becik4U system.

If any of these environment variables are missing, an exception will be raised indicating which variable is not set.

## Error Handling

The `Becik4UParameters` class includes error handling for the following cases:

- **Operating System Check**: If the system is not running on Linux, an exception will be raised with the message: `Linux Only - Becik4U Software System`.
- **Missing Environment Variables**: If any of the required environment variables (`FREESURFER_HOME`, `BECIK4U_ROOT`, `BECIK4U_CORE`) are not set, an exception will be raised with the message: `Environment Variable '{name}' is not Set`, where `{name}` corresponds to the missing environment variable.

These checks ensure that the system is properly configured and avoids potential runtime errors due to missing configuration.
