
# Becik4U Ingest System

The **Becik4U Ingest System** is designed to manage the ingestion of DICOM and NIfTI files for the Becik4U platform. This system automates the process of ingesting, converting, and storing medical imaging data.

## Features

- **DICOM Ingestion**: Ingests DICOM files and converts them to NIfTI format.
- **NIfTI Ingestion**: Ingests already converted NIfTI files and processes them further.
- **Directory Management**: Organizes the raw and processed files into appropriate directories.
- **Error Handling**: Ensures that all required directories exist and that proper environment variables are set.

## Usage

The ingest system allows users to perform two main operations: **DICOM Ingestion** and **NIfTI Ingestion**.

### DICOM Ingestion

To ingest DICOM files and convert them into NIfTI format:

```bash
python main.py dicom --id <scan_id> --root_dir <source_root_directory>
```

#### Arguments:
- **`--id`**: The unique scan identifier.
- **`--root_dir`**: The source directory containing the DICOM files to be ingested.

**Process Flow**:
1. **DICOM Files**: DICOM files from the source directory are copied into the `raw/dicom` directory.
2. **Conversion**: The DICOM files are converted into NIfTI format and stored in the `raw/nifti` directory.

### NIfTI Ingestion

To ingest already converted NIfTI files into the system:

```bash
python main.py nifti --id <scan_id> --file_name <file_name.nii>
```

#### Arguments:
- **`--id`**: The unique scan identifier.
- **`--file_name`**: The name of the NIfTI file to ingest.

**Process Flow**:
1. The NIfTI file is retrieved from the `raw/nifti` directory.
2. The file is processed and converted to the required format (if necessary).
3. The processed NIfTI file is saved in the `data` directory.

## Error Handling

The **Becik4U Ingest System** includes the following error handling mechanisms:

- **Missing Environment Variables**: The system checks for the necessary environment variables (`FREESURFER_HOME`, `BECIK4U_ROOT`, `BECIK4U_CORE`). If any of these are not set, an exception is raised.

- **OS Check**: The system only works on Linux. If the operating system is not Linux, an exception is raised with the message: `Linux Only - Becik4U Software System`.

- **Directory Management**: If the required directories (`raw/dicom`, `raw/nifti`, `data`) are missing, they will be automatically created. If there are any issues, appropriate error messages will be shown.
