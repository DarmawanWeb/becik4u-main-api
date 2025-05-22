import os
import nibabel as nib
import numpy as np
from nilearn.image import resample_img
from loguru import logger
from parameters import Becik4UParameters


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
        try:
            nifti_img = nib.load(file_path)
        except Exception as e:
            logger.error(f"Failed to load NIfTI file: {file_path} - {str(e)}")
            raise

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

    @staticmethod
    def get_nifti_file_info(file_path: str) -> dict:
        """
        Retrieves metadata and validation information for a NIfTI file.

        Args:
            file_path (str): Path to the NIfTI file.

        Returns:
            dict: A dictionary containing metadata about the NIfTI file, including shape, data type, and voxel size.
        """
        fname = os.path.basename(file_path)

        # Initialize report dictionary
        report = {
            'fname': fname,
            'full_path': os.path.abspath(file_path),
            'valid': False
        }

        try:
            # Check if the file is valid or not
            if not fname.endswith(('nii', 'nii.gz')):
                raise Exception("Invalid File Format")

            nifti_image = nib.load(file_path)
            nifti_header = nifti_image.header

            data_shape = nifti_header.get_data_shape()
            data_type = str(nifti_header.get_data_dtype())
            data_voxel = nifti_header.get_zooms()

            data_shape = [int(x) for x in data_shape]
            data_voxel = [float(x) for x in data_voxel]
            data_voxel = [round(x, 3) for x in data_voxel]

            # Populate report with metadata
            report['dshape'] = data_shape
            report['dtype'] = data_type
            report['dsize'] = data_voxel
            report['valid'] = True

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            pass

        return report
