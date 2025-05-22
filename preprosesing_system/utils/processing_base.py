import json
import torch
import numpy as np
from monai.transforms import ResizeWithPadOrCrop
from monai.transforms import Rotate
import nibabel as nib

TARGET_SIZE = (224, 224, 224)

class PreprocessingBase:
    """
    Base class with utility functions for preprocessing.
    """

    @staticmethod
    def load_json(fname: str):
        """Load JSON file."""
        with open(fname) as jsn_ref:
            jlist = json.load(jsn_ref)
        return jlist

    @staticmethod
    def load_refrence_vectors(file_name: str) -> dict[str, np.ndarray]:
        """Load reference vectors from a JSON file."""
        ref_values = PreprocessingBase.load_json(file_name)
        return {
            "VECTOR_ALPHA": np.array(ref_values["REF_VECTOR_ALPHA"]),
            "VECTOR_BETA": np.array(ref_values["REF_VECTOR_BETA"]),
            "VECTOR_GAMMA": np.array(ref_values["REF_VECTOR_GAMMA"]),
        }

    @staticmethod
    def masked_center(array: np.ndarray, key: int) -> np.ndarray:
        """Find center of mass for a masked region."""
        indices = np.argwhere(array == key)
        if indices.size == 0:
            raise Exception("Values Not Found!")
        return np.mean(indices, axis=0)

    @staticmethod
    def normalise_vector(vector: np.ndarray) -> np.ndarray:
        """Normalize vector to unit length."""
        norm = np.linalg.norm(vector)
        return vector if norm == 0 else vector / norm

    @staticmethod
    def vector_to_stack(vk: dict[str, np.ndarray]) -> np.ndarray:
        """Stack vectors into a single array."""
        return np.stack([vk['VECTOR_ALPHA'], vk['VECTOR_BETA'], vk['VECTOR_GAMMA']], axis=0)

    @staticmethod
    def convert_size(array: np.ndarray, output_size=TARGET_SIZE) -> np.ndarray:
        """Resize array to target size."""
        array = np.expand_dims(array, axis=0)
        tensor = torch.from_numpy(array)
        spatial_resize_function = ResizeWithPadOrCrop(output_size)
        tensor = spatial_resize_function(tensor)
        return tensor.squeeze().numpy()

    @staticmethod
    def rotate_array(array: np.ndarray, rotation_radians: np.ndarray) -> np.ndarray:
        """Rotate array by given angles."""
        array = np.expand_dims(array, axis=0)
        tensor = torch.from_numpy(array)
        rotation_function = Rotate(rotation_radians)
        tensor = rotation_function(tensor)
        return tensor.squeeze().numpy()

    @staticmethod
    def compute_bounding_box(array: np.ndarray) -> dict[str, int]:
        """Compute bounding box of non-zero region."""
        arm = np.argwhere(array)
        start_x, stop_x = np.min(arm[:, 0]), np.max(arm[:, 0])
        start_y, stop_y = np.min(arm[:, 1]), np.max(arm[:, 1])
        start_z, stop_z = np.min(arm[:, 2]), np.max(arm[:, 2])

        return {
            'start_x': int(start_x),
            'stop_x': int(stop_x),
            'start_y': int(start_y),
            'stop_y': int(stop_y),
            'start_z': int(start_z),
            'stop_z': int(stop_z)
        }

    @staticmethod
    def load_and_crop(file_path: str, bounds: dict[str, int], spatial_size=(378, 378, 378), dtype=np.uint16) -> np.ndarray:
        """Load and crop image based on bounds."""
        nib_image: nib.Nifti1Image = nib.load(file_path)
        nib_array: np.ndarray = nib_image.get_fdata().astype(dtype)

        cropped_array = nib_array[
            bounds['start_x']:bounds['stop_x'],
            bounds['start_y']:bounds['stop_y'],
            bounds['start_z']:bounds['stop_z']
        ]

        padded_array = PreprocessingBase.convert_size(cropped_array, output_size=spatial_size)

        return padded_array
