import os
import shutil
from loguru import logger
import dicom2nifti
from parameters import Becik4UParameters

class DICOMIngestion:
    """
    A class responsible for ingesting DICOM files and converting them to NIfTI format.
    """

    @staticmethod
    def ingest_and_convert(params: Becik4UParameters, id: str, source_root: str) -> str:
        """
        Ingest DICOM files, convert them to NIfTI, and store them in the appropriate directory.

        Args:
            params (Becik4UParameters): Instance of the Becik4UParameters class.
            id (str): The identifier for the scan.
            source_root (str): The source directory of DICOM files.

        Returns:
            str: Path to the converted NIfTI files.
        """
        root_scan_dir = params.get_root_scan_dir(id)
        
        # Define directories for DICOM and NIfTI storage
        raw_dicom_root = os.path.join(root_scan_dir, "raw", "dicom")
        os.makedirs(raw_dicom_root, exist_ok=True)

        raw_nifti_root = os.path.join(root_scan_dir, "raw", "nifti")
        os.makedirs(raw_nifti_root, exist_ok=True)

        logger.info("COPYING RAW FILES")
        source_root = os.path.abspath(source_root)
        shutil.copytree(source_root, raw_dicom_root, dirs_exist_ok=True)
        
        logger.info("CONVERTING TO NIFTI")
        dicom2nifti.convert_directory(raw_dicom_root, raw_nifti_root)

        return raw_nifti_root
