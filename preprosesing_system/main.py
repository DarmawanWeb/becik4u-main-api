#!/usr/bin/python3

import os
import sys
import argparse

from loguru import logger
from utils.processing_wrapper import PreprocessingWrapper

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'helpers')))
from parameters import Becik4UParameters

class BrainProcessingSystem:
    """
    Command-line interface and brain scan processing system.
    """
    def __init__(self):
        logger.remove(0)
        logger.add(sys.stderr, format = "<red>[{level}]</red> <green>{message}</green> ", colorize=True)
        self.params = Becik4UParameters()
        self.prp_warp = PreprocessingWrapper()

    def run_pipeline(self, scan_id: str):
        """
        Runs the processing pipeline for the given scan ID.
        """
        logger.info(f"Running iBrain2u command with ID: {scan_id}")
        vector_reference = self.plp_warp.load_refrence_vectors()

        self.plp_warp.preprocessing_pipeline(
            prams=self.params,
            scan_id=scan_id,
            refrence_vectors=vector_reference
        )

def main():
    """
    Main function to initialize the system and run the pipeline.
    """
    parser = argparse.ArgumentParser(description="Becik4U Brain Processing System")

    parser.add_argument('--id', required=True, type=str, help='Unique identifier for the brain scan.')

    args = parser.parse_args()

    processing_system = BrainProcessingSystem()
    processing_system.run_pipeline(args.id)
    logger.info("Processing completed successfully.")

if __name__ == "__main__":
    main()
