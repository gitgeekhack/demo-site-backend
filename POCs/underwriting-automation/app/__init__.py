from app.manage import create_app

app, logger = create_app()

from app.resource.pinger import Pinger
from app.resource.api import v1
from app.resource.download import Downloader
from app.constant import Endpoints

API_V1 = Endpoints.API.V1

app.router.add_view(Endpoints.PINGER, Pinger)
app.router.add_view(Endpoints.DOWNLOADER, Downloader)

# V1 API routes
app.router.add_view(API_V1.CRMReceipt.EXTRACT, v1.CRMExtractV1)
app.router.add_view(API_V1.ITC.EXTRACT, v1.ITCExtractV1)
app.router.add_view(API_V1.DrivingLicense.EXTRACT, v1.DLExtractV1)
app.router.add_view(API_V1.Application.EXTRACT, v1.APPExtractV1)
app.router.add_view(API_V1.MVR.EXTRACT, v1.MVRExtractV1)
app.router.add_view(API_V1.BrokerPackage.EXTRACT, v1.BKPExtractV1)
app.router.add_view(API_V1.PleasureUseLetter.EXTRACT, v1.PULExtractV1)
app.router.add_view(API_V1.SamePersonStatement.EXTRACT, v1.SPSExtractV1)
app.router.add_view(API_V1.StripeReceipt.EXTRACT, v1.STRPExtractV1)
app.router.add_view(API_V1.VR.EXTRACT, v1.VRExtractV1)
app.router.add_view(API_V1.Registration.EXTRACT, v1.RegistrationExtractV1)
app.router.add_view(API_V1.EFT.EXTRACT, v1.EFTExtractV1)
app.router.add_view(API_V1.PromiseToProvide.EXTRACT, v1.PTPExtractV1)
app.router.add_view(API_V1.ArtisanUseLetter.EXTRACT, v1.AULExtractV1)
app.router.add_view(API_V1.NonOwnersLetter.EXTRACT, v1.NOLExtractV1)
app.router.add_view(API_V1.Application.VERIFY, v1.VerifyV1)
