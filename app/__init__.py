from app.manage import create_app

app, logger = create_app()

from app.resource.pinger import Pinger
from app.resource.driving_license.extract import Index, DLExtractor

app.router.add_view('/', Index)
app.router.add_view('/dl-ocr', DLExtractor)
