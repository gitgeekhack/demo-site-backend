from app.manage import create_app

app, logger = create_app()

from app.resource.index import Index
from app.resource.pinger import Pinger
from app.resource.driving_license.extract import DLExtractor
from app.resource.get_user_files.get_file import GetResourceData
from app.resource.certificate_of_title.extract import COTExtractor
from app.resource.car_damage_detection.damage_detect import DamageExtractor
from app.resource.barcode_extraction.extract_barcode import BarCodeExtraction
from app.resource.pdf_annotation_and_extraction.PDFExtractor import HomePage, DataExtraction
from app.resource.medical_document_insight_extraction.medical_insight_extraction import MedicalInsightsExtractor

app.router.add_view('/', Index)
app.router.add_route('POST', '/driving-license/extract', DLExtractor.post)
app.router.add_route('POST', '/certificate-of-title/extract', COTExtractor.post)
app.router.add_route('POST', '/car-damage-detection/detect', DamageExtractor.post)
app.router.add_view('/pdf', HomePage)
app.router.add_view('/pdf/extract', DataExtraction)
app.router.add_route('POST', '/barcode-detection/detect', BarCodeExtraction.post)
app.router.add_view('/medical-insights/extract', MedicalInsightsExtractor.post)
# app.router.add_view('/medical-insights/qna-extract', QnAExtractor.post)
app.router.add_view('/get-resource', GetResourceData)
