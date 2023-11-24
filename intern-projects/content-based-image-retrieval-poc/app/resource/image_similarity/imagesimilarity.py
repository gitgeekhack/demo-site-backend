import aiohttp_jinja2
import cv2
import numpy as np
from aiohttp import web
from app.constant import UPLOAD_FOLDER, MAXIMUM_UPLOAD, NO_OF_NEIGHBORS
from app.common.utils import allowed_file
from app.service.image_similarity.indexer import Indexer
from app.service.image_similarity.searcher import Searcher


def save_file(file):
    np_array = np.asarray(bytearray(file.file.read()), dtype=np.uint8)
    input_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    file_path = UPLOAD_FOLDER + '/' + file.filename
    cv2.imwrite(file_path, input_image)
    return file_path


class HomePage(web.View):
    @aiohttp_jinja2.template('index.html')
    async def get(self):
        return {}


class Index(web.View):
    @aiohttp_jinja2.template('indexing.html')
    async def get(self):
        return {}

    @aiohttp_jinja2.template('indexing.html')
    async def post(self):
        data = await self.request.post()
        files = data.getall('files')

        if len(files) > MAXIMUM_UPLOAD:
            raise web.HTTPFound('/index')

        file_paths = []
        for file in files:
            if allowed_file(file.filename):
                file_paths.append(save_file(file))

        indexer = Indexer()
        indexer.indexing(file_paths)

        return {}


class Search(web.View):
    @aiohttp_jinja2.template('searching.html')
    async def get(self):
        return {}

    @aiohttp_jinja2.template('searching.html')
    async def post(self):
        data = await self.request.post()
        file = data.get('input_image')
        if not allowed_file(file.filename):  # checking for allowed file
            raise web.HTTPFound('/search')

        file_path = save_file(file)

        searcher = Searcher()
        similar_images = searcher.searching([file_path])

        if not similar_images:
            return {"image_names": [], "search_image": file.filename, "neighbors": NO_OF_NEIGHBORS}

        # converting image paths to image names

        image_names = []
        for i in similar_images:
            image_names.append(i.split('/')[-1])

        return {"image_names": image_names, "search_image": file.filename, "neighbors": NO_OF_NEIGHBORS}

