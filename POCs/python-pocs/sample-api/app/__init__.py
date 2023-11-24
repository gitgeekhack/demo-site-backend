from app.manage import create_app

app, logger = create_app()

from app.resource.pinger import Pinger
from app.resource.api import v1
from app.constant import Endpoints

API_V1 = Endpoints.API.V1

app.router.add_view(Endpoints.PINGER, Pinger)

# V1 API routes
app.router.add_view(API_V1.RandomString.GENERATE, v1.RandomStringGenerateV1)
