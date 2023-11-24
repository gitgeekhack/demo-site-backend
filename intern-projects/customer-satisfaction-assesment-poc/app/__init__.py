from app.manage import create_app

app, logger = create_app()

from app.resource.pinger import Pinger
from app.resource.sentiment_analysis_app import Dashboard, Index

app.router.add_view('/', Index, name="index")
app.router.add_view('/dashboard/{time}', Dashboard, name='dashboard')

