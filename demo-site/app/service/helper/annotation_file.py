import os
import glob
import zipfile
from app.constant import PDFAnnotationAndExtraction


async def get_annotation_filenames():
    """
        reads annotation file names stored in Annotation Folder
        Returns:
             annotation filenames without extension
    """
    annotation_data = {}
    for file in os.listdir(PDFAnnotationAndExtraction.ANNOTATION_FOLDER):
        filename = os.path.splitext(file)[0]
        annotation_data[filename] = {}
    return annotation_data


async def extract_annotation_files():
    """
        File Watcher for adding annotations which is newly generated
    """
    for file in glob.glob(os.path.join(PDFAnnotationAndExtraction.CVAT_ANNOTATION_STORAGE_FOLDER, '*.zip')):
        with zipfile.ZipFile(file, 'r') as zip_file:
            zip_file.extractall(PDFAnnotationAndExtraction.ANNOTATION_FOLDER)

            os.rename(os.path.join(PDFAnnotationAndExtraction.ANNOTATION_FOLDER, 'annotations.xml'),
                      os.path.join(PDFAnnotationAndExtraction.ANNOTATION_FOLDER,
                                   f'{os.path.basename(os.path.splitext(file)[0]).upper()}.xml'))
