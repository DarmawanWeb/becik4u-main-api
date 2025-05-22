import os
import shutil

from helper_ibrain2u import iBrain2uParamters


def dicom_ingest_file(params : iBrain2uParamters, id : str, source_root: str) -> str:

    root_scan_dir = params.get_root_scan_dir(id)
    
    raw_dicom_root = os.path.join(root_scan_dir, "raw", "dicom")
    os.makedirs(raw_dicom_root, exist_ok = True)

    raw_nifti_root = os.path.join(root_scan_dir, "raw", "nifti")
    os.makedirs(raw_nifti_root, exist_ok = True)

    print("#^^# COPYING RAW FILES #**#")
    source_root = os.path.abspath(source_root)
    shutil.copytree(source_root, raw_dicom_root, dirs_exist_ok = True)
    
    print("#^^# CONVERTING TO NIFTI #**#")
    import dicom2nifti
    dicom2nifti.convert_directory(raw_dicom_root, raw_nifti_root)

    return raw_nifti_root