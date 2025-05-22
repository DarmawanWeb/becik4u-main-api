import os
import nibabel as nib
import numpy as np
from nibabel.processing import resample_img
from loguru import logger
from helpers.parameters import Becik4UParameters

class NIFTIIngestion:
    """
    A class responsible for ingesting NIfTI files and processing them into the required format.
    """

    @staticmethod
    def internal_ingest(params: Becik4UParameters, id: str, file_name: str) -> None:
        """
        Ingest NIfTI files already present in the Becik4U system.

        Args:
            params (Becik4UParameters): Instance of the Becik4UParameters class.
            id (str): The identifier for the scan.
            file_name (str): The name of the NIfTI file to ingest.
        """
        root_scan_dir = params.get_root_scan_dir(id)    
        raw_nifti_root = os.path.join(root_scan_dir, "raw", "nifti")
        internal_file = os.path.join(raw_nifti_root, file_name)

        # Process the NIfTI file
        NIFTIIngestion._process_nifti(params, id, internal_file)

    @staticmethod
    def _process_nifti(params: Becik4UParameters, id: str, file_path: str) -> None:
        """
        Processes and resamples a NIfTI file, converting it into the appropriate format.

        Args:
            params (Becik4UParameters): Instance of the Becik4UParameters class.
            id (str): The identifier for the scan.
            file_path (str): Path to the NIfTI file.
        """
        logger.info("PROCESSING NIFTI FILE")
        root_scan_dir = params.get_root_scan_dir(id)

        # Converted files root
        data_root = os.path.join(root_scan_dir, "data")
        os.makedirs(data_root, exist_ok=True)

        # Load NIfTI file and convert to numpy array
        nifti_img = nib.load(file_path)
        image_array = nifti_img.get_fdata()
        image_axis = image_array.shape

        # Validate dimensions
        if len(image_axis) < 3:
            logger.error("Data has less than 3 dimensions, please upload correct data.")
            raise Exception("Data has less than 3 dimensions, please upload correct data.")
        
        # Resample if needed
        if len(image_axis) > 3:
            while len(image_axis) > 3:
                image_array = image_array[0]
                image_axis = image_array.shape
        
        # Save as numpy compressed file
        npy_path = os.path.join(data_root, f"{id}_raw.npz")
        np.savez_compressed(npy_path, image_array=image_array)

        # Resample the image
        target_affine = np.diag([1.0, 1.0, 1.0])
        resampled_img = resample_img(
            nifti_img, 
            target_affine=target_affine,
            interpolation='linear',
            force_resample=True,
            copy_header=True
        )

        # Save resampled version
        resampled_path = os.path.join(data_root, f"{id}_sampled.nii.gz")
        nib.save(resampled_img, resampled_path)
