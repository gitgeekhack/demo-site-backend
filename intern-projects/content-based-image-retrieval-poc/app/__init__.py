from app.manage import create_app
from app.resource.image_similarity.imagesimilarity import HomePage, Index, Search

app, logger = create_app()

app.router.add_view('/', HomePage, name="home")
app.router.add_view('/index', Index, name="index")
app.router.add_view('/search', Search, name="search")

