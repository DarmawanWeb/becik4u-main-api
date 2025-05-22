import os
import sys
from loguru import logger

class Becik4UParameters:
    """
    A class to handle environment setup and directory management for the Becik4U system.
    """

    def __init__(self):
        """
        Initializes the class by checking the OS and setting up necessary environment variables.
        """
        self._check_os()

        # Check if Environment Variables are set
        self.freesurfer = self._get_env("FREESURFER_HOME")
        self.becik4u_root = self._get_env("BECIK4U_ROOT")
        self.becik4u_core = self._get_env("BECIK4U_CORE")

    def _check_os(self) -> None:
        """
        Checks if the operating system is Linux. Raises an exception if not.
        """
        if sys.platform != "linux":
            logger.error("Linux Only - Becik4U Software System")
            raise Exception("Linux Only - Becik4U Software System")

    def _get_env(self, name: str) -> str:
        """
        Retrieves the value of an environment variable. Raises an exception if not found.

        Args:
            name (str): The name of the environment variable to retrieve.

        Returns:
            str: The value of the environment variable.

        Raises:
            Exception: If the environment variable is not set.
        """
        value = os.getenv(name)
        if value is None:
            logger.error(f"Environment Variable '{name}' is not Set")
            raise Exception(f"Environment Variable '{name}' is not Set")
        return value

    def get_app_dir(self, app_name: str) -> str:
        """
        Gets the absolute directory path for a specific application.

        Args:
            app_name (str): The name of the application.

        Returns:
            str: The absolute directory path of the application.
        """
        app_dir = os.path.join(self.becik4u_root, "application", app_name.lower())
        return os.path.abspath(app_dir)

    def get_root_scan_dir(self, id: str) -> str:
        """
        Gets the absolute directory path for the root scan directory based on the provided ID.

        Args:
            id (str): The ID used to locate the root scan directory.

        Returns:
            str: The absolute directory path of the root scan directory.
        """
        root_scan_dir = os.path.join(self.becik4u_root, "media", "storage", id)
        return os.path.abspath(root_scan_dir)
