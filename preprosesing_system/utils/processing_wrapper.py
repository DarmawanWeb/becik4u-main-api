import os
import subprocess
import datetime
import numpy as np
import nibabel as nib
from loguru import logger

import scipy.ndimage as scimg
from scipy.spatial.transform import Rotation as R
from scipy.linalg import orthogonal_procrustes

from .processing_base import PreprocessingBase
from helpers import iBrain2uParamters

class PreprocessingWrapper:
    def __init__(self):
        """Initialize preprocessing wrapper."""
        pass
    
    @staticmethod
    def print_status(current_step: int, total_step: int, message: str) -> None:
        """Print the status of each step in the pipeline."""
        x = {'current_step': current_step, 'total_steps': total_step, 'message': message}
        logger.info(f"#**# {x} #**#")

    def preprocessing_pipeline(self, prams: iBrain2uParamters, scan_id: str, refrence_vectors: dict[str, np.ndarray]) -> bool:
        """Run the preprocessing pipeline."""
        try:
            self.print_status(0, 10, "Setup")
            root_dir = prams.get_root_scan_dir(scan_id)
            root_dir = os.path.join(root_dir, "data")
            
            sampled_image_file  = os.path.join(root_dir, f"{scan_id}_sampled.nii.gz")
            stripped_image_file = os.path.join(root_dir, f"{scan_id}_synthstrip.nii.gz")
            brainstrp_mask_file = os.path.join(root_dir, f"{scan_id}_synthstrip_mask.nii.gz")
            segmented_mask_file = os.path.join(root_dir, f"{scan_id}_synthseg.nii.gz")
            segmented_grpd_file = os.path.join(root_dir, f"{scan_id}_synthseg_grouped.nii.gz")
            orientation_file    = os.path.join(root_dir, f"{scan_id}_orientation.npz")

            # Skull stripping process
            self.print_status(1, 10, "Skull Stripping")
            self.__image_skullstrip__(sampled_image_file, stripped_image_file, brainstrp_mask_file)

            # Brain segmentation
            self.print_status(2, 10, "Region Segmentation")
            self.__image_segmentation_grouping__(sampled_image_file, segmented_mask_file, segmented_grpd_file)
            
            self.print_status(3, 10, "Image Loading")
            # Load mask and crop scan
            mask_image: nib.Nifti1Image = nib.load(brainstrp_mask_file)
            mask_array: np.ndarray = mask_image.get_fdata().astype(bool)
            bounding_box = PreprocessingBase.compute_bounding_box(mask_array)

            # Group image segments and create coordinate groups
            self.print_status(4, 10, "Computing Bounding Box")
            grouped_array = PreprocessingBase.load_and_crop(segmented_grpd_file, bounding_box)
            self.print_status(5, 10, "Creating Group Coordinates")
            coordiate_groups = PreprocessingBase.compute_center_groups(grouped_array)
            normalised_coordinate_groups = PreprocessingBase.subtract_groups(coordiate_groups)

            # Compute reference vectors and normalize
            self.print_status(6, 10, "Computing Brain Orientation Vectors")
            computed_vectors = PreprocessingBase.create_refrence_vectors(normalised_coordinate_groups)
            stv_computed = PreprocessingBase.vector_to_stack(computed_vectors)
            stv_refrence = PreprocessingBase.vector_to_stack(refrence_vectors)

            # Compute rotation matrix and rotation angles
            self.print_status(7, 10, "Computing Brain Orientation")
            rotation_matrix, _ = orthogonal_procrustes(stv_refrence, stv_computed)
            rot_pred: R = R.from_matrix(rotation_matrix)
            rotation_angle_radians = rot_pred.as_euler("xyz", degrees=False)

            # Center of the brain
            computed_center = np.round(coordiate_groups["BRAIN_OFFSET_CENTER"])

            # Load the stripped image and compute center offset
            self.print_status(8, 10, "Loading and Orienting Brain Scan")
            stripped_array = PreprocessingBase.load_and_crop(stripped_image_file, bounding_box, dtype=np.float32)
            real_center = np.round(np.array(stripped_array.shape) / 2)
            center_offset = computed_center - real_center

            # Save orientation data
            np.savez(
                orientation_file, 
                radian_array    = rotation_angle_radians,
                computed_center = computed_center,
                bbx_array       = PreprocessingBase.convert_bounding_box_2_array(bounding_box)
            )

            # Shift image based on computed offset
            moved_stripped_array = scimg.shift(stripped_array, shift=center_offset, cval=0).astype(np.float32)

            # Resize image
            resized_array = PreprocessingBase.convert_size(moved_stripped_array)

            # Rotate the image
            rotated_array = PreprocessingBase.rotate_array(resized_array, rotation_angle_radians) 
            
            self.print_status(9, 10, "Writing Results")
            output_file = os.path.join(root_dir, f"{scan_id}_palapa.nii.gz")
            output_img = nib.Nifti1Image(rotated_array, affine=np.eye(4))
            nib.save(output_img, output_file)

            # Save as compressed numpy array
            npy_path = os.path.join(root_dir, f"{scan_id}_palapa.npz")
            np.savez_compressed(npy_path, image_array=rotated_array)

            self.print_status(10, 10, "Complete")
        except Exception as error_exc:
            logger.error(f"#!!# ERROR REPORT #**# {error_exc}")
            return False
        
        return True

    def __image_skullstrip__(self, input_path: str, output_path: str, output_mask_path: str) -> None:
        """Perform skull stripping."""
        global gbl_freesurfer_root, gbl_freesurfer_cpus
        logger.info("### FREESURFER - SYNTHSTRIP - START ###")   
        start_time = datetime.datetime.now()

        subprocess.run([
            os.path.join(gbl_freesurfer_root, "bin", "mri_synthstrip"),
            "-i", input_path, 
            "-o", output_path, 
            "-m", output_mask_path], 
            check=True
        )
        stop_time = datetime.datetime.now()
        exec_time = stop_time - start_time
        logger.info(f"### STOP : {exec_time.total_seconds()} seconds ###")

    def __image_segmentation_grouping__(self, input_path: str, output_path: str, grouped_path: str) -> None:
        """Segment image into brain sections and group."""
        global gbl_freesurfer_root, gbl_freesurfer_cpus
        logger.info("### FREESURFER - SYTHSEG - START ###")
        start_time = datetime.datetime.now()
        
        subprocess.run([
            os.path.join(gbl_freesurfer_root, "bin", "mri_synthseg"),
            "--i", input_path, 
            "--o", output_path,
            "--fast", "--cpu",
            "--threads", gbl_freesurfer_cpus], 
            check=True
        )

        self.__image_grouping__(output_path, grouped_path)
        
        stop_time = datetime.datetime.now()
        exec_time = stop_time - start_time
        logger.info(f"### STOP : {exec_time.total_seconds()} seconds ###")    

    def __image_grouping__(self, input_path: str, output_image_path: str) -> None:
        """Group image segments into a mask."""
        # Internal logic for binary mask creation
        def create_binary_mask(array: np.ndarray, masked_values: list[int]) -> np.ndarray:
            binary_array = np.zeros_like(array, dtype=bool)
            for numerical_value in masked_values:
                binary_array[array == numerical_value] = True
            return binary_array

        def compute_binary_center(array: np.ndarray) -> np.ndarray:
            """Compute center of mass for a binary mask."""
            indices = np.nonzero(array)
            return np.mean(indices, axis=1)

        def compute_masked_values(source_array: np.ndarray, masked_values: list[int], replacement_value: int = 1) -> tuple:
            """Compute masked values for the image."""
            masked_binary = create_binary_mask(source_array, masked_values)
            center_of_mass = compute_binary_center(masked_binary)
            output_array = np.uint16(masked_binary)
            output_array *= replacement_value
            return (output_array, masked_binary, center_of_mass)

        # Process the segmentation grouping logic
        base_img = nib.load(input_path)
        array = base_img.get_fdata()

        a_lcer, _, _ = compute_masked_values(array, [2, 3], 100)
        a_lcor, _, _ = compute_masked_values(array, [7, 8], 200)
        a_rcer, _, _ = compute_masked_values(array, [41, 42], 300)
        a_rcor, _, _ = compute_masked_values(array, [46, 47], 400)
        a_stem, _, _ = compute_masked_values(array, [16], 500)

        # Create the mask array 
        mask_array = np.zeros_like(array, dtype=np.uint16)
        mask_array += a_lcer
        mask_array += a_lcor
        mask_array += a_rcer
        mask_array += a_rcor
        mask_array += a_stem

        # Save the final mask
        masked_img = nib.Nifti1Image(mask_array, affine=base_img.affine, header=base_img.header)
        nib.save(masked_img, output_image_path)
