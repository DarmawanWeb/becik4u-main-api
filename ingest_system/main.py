#!/usr/bin/python3
import os
import sys
import json
from loguru import logger
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'helpers')))
from parameters import Becik4UParameters
from utils.dicom_ingestion import DICOMIngestion
from utils.nifti_ingestion import NIFTIIngestion

class IngestSystem:
    """
    Main class for managing DICOM and NIfTI file ingestion.
    """

    def __init__(self):
        logger.remove(0)
        logger.add(sys.stderr, format = "<red>[{level}]</red> <green>{message}</green> ", colorize=True)
        self.params = Becik4UParameters()

    def ingest_dicom(self, id: str, source_root: str) -> None:
        """Ingest DICOM files and display results."""
        dcm_nft_root = DICOMIngestion.ingest_and_convert(self.params, id, source_root)
        logger.info("JSON REPORT #")
        self.get_dir_info(dcm_nft_root)

    def ingest_nifti(self, id: str, file_name: str) -> None:
        """Ingest NIfTI files (always internal)."""
        NIFTIIngestion.internal_ingest(self.params, id, file_name)

    def get_dir_info(self, root_dir: str) -> None:
        """Get directory information of NIfTI files."""
        full_path = os.path.abspath(root_dir)
        files = [os.path.join(full_path, x) for x in os.listdir(full_path)]
        report = [NIFTIIngestion.get_nifti_file_info(x) for x in files]
        dir_jstr = json.dumps(report, indent=2)
        logger.info(dir_jstr)

def main():
    parser = argparse.ArgumentParser(description="Becik4U Ingest System")

    subparsers = parser.add_subparsers(dest="option", required=True)

    # Option DICOM
    parser_dicom = subparsers.add_parser('dicom', help='Option for DICOM ingestion')
    parser_dicom.add_argument('--id', required=True, type=str)
    parser_dicom.add_argument('--root_dir', required=True, type=str)

    # Option NIFTI
    parser_nifti = subparsers.add_parser('nifti', help='Option for NIfTI ingestion')
    parser_nifti.add_argument('--id', required=True, type=str)
    parser_nifti.add_argument('--file_name', required=True, type=str)

    args = parser.parse_args()

    ingest_system = IngestSystem()

    if args.option == "dicom":
        ingest_system.ingest_dicom(args.id, args.root_dir)
    elif args.option == "nifti":
        ingest_system.ingest_nifti(args.id, args.file_name)


if __name__ == "__main__":
    main()
