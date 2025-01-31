from app.manage import create_app

app, logger = create_app()

from app.resource.index import Index
from app.resource.driving_license.extract import DLExtractor
from app.resource.get_user_files.get_file import GetResourceData
from app.resource.certificate_of_title.extract import COTExtractor
from app.resource.car_damage_detection.damage_detect import DamageExtractor
from app.resource.barcode_extraction.extract_barcode import BarCodeExtraction

app.router.add_view('/', Index)
app.router.add_view('/get-resource', GetResourceData)

app.router.add_route('POST', '/driving-license/extract', DLExtractor.post)
app.router.add_route('POST', '/certificate-of-title/extract', COTExtractor.post)
app.router.add_route('POST', '/car-damage-detection/detect', DamageExtractor.post)
app.router.add_route('POST', '/barcode-detection/detect', BarCodeExtraction.post)
