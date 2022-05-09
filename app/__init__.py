from app.manage import create_app

app, logger = create_app()

from app.resource.pinger import Pinger
from app.resource.index import Index
from app.resource.driving_license.extract import DLExtractor
from app.resource.certificate_of_title.extract import COTExtractor

app.router.add_view('/', Index)
app.router.add_view('/driving-license', DLExtractor)
app.router.add_view('/certificate-of-title', COTExtractor)
