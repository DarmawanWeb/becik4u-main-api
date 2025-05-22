import os
import json
import argparse
from helper_ibrain2u import iBrain2uParamters
from exec_dicom import dicom_ingest_file
from exec_nifti import nifti_internal_ingest, get_nifti_file_info


class Becik4UIngestSystem:
    """Ingest system for Becik4U"""
    def __init__(self):
        self.ib_params = iBrain2uParamters()

    def get_dir_info(self, root_dir: str) -> None:
        """Get directory information of NIfTI files"""
        full_path = os.path.abspath(root_dir)
        files = [os.path.join(full_path, x) for x in os.listdir(full_path)]
        report = [get_nifti_file_info(x) for x in files]
        dir_jstr = json.dumps(report, indent=2)
        print(dir_jstr)

    def ingest_dicom(self, id: str, root_dir: str) -> None:
        """Ingest DICOM files and display the results"""
        dcm_nft_root = dicom_ingest_file(self.ib_params, id, root_dir)
        print("#^^# JSON REPORT #**#")
        self.get_dir_info(dcm_nft_root)

    def ingest_nifti(self, id: str, file_name: str = None, file_path: str = None) -> None:
        """Ingest NIfTI files (always internal)"""
        nifti_internal_ingest(self.ib_params, id, file_name)


def main():
    parser = argparse.ArgumentParser(description="iBrain2u Ketapel Ingest System")

    subparsers = parser.add_subparsers(dest="option", required=True)

    # Option DICOM
    parser_dicom = subparsers.add_parser('dicom', help='option dicom')
    parser_dicom.add_argument('--id', required=True, type=str)
    parser_dicom.add_argument('--root_dir', required=True, type=str)

    # Option NIFTI
    option_nifti = subparsers.add_parser('nifti', help='option nifti')
    parser_nifti.add_argument('--id', required=True, type=str)
    parser_nifti.add_argument('--file_name', required=False, type=str)
    parser_nifti.add_argument('--file_path', required=False, type=str)

    args = parser.parse_args()

    ingest_system = iBrain2uIngestSystem()

    if args.option == "dicom":
        ingest_system.ingest_dicom(args.id, args.root_dir)
    elif args.option == "nifti":
        ingest_system.ingest_nifti(args.id, file_name=args.file_name)


if __name__ == "__main__":
    main()
