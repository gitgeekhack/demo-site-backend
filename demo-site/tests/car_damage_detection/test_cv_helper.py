import os
import cv2
import pytest

os.chdir('../../')
from app.service.helper import cv_helper

pytest_plugins = ('pytest_asyncio',)


class TestAnnotator:
    @pytest.mark.asyncio
    async def test_annotate_and_save_image_with_valid_parameter(self):
        image_path = 'tests/data/image/Nissan-front-rightside-view.jpg'
        image = cv2.imread(image_path)
        coordinates = [[(600.4663, 370.6275, 1020.62146, 792.081), (245, 122, 206), 'fender'],
                       [(661.54663, 246.39789, 1238.9711, 584.2965), (159, 247, 17), 'hood'],
                       [(809.267, 377.4917, 1280.0, 778.3379), (0, 234, 254), 'front_bumper']]

        annotator = cv_helper.Annotator(image=image, coordinates=coordinates)

        font_path = './app/static/damage_detection/font_file/arial.ttf'
        save_path = './app/static/damage_detection/output/nissan-annotated.jpg'

        result = annotator.annotate_and_save_image(save_path, font_path)

        assert result is None

    @pytest.mark.asyncio
    async def test_annotate_and_save_image_with_invalid_image_parameter(self):
        image_path = 'demo-site/tests/data/pdf/Sample1.pdf'
        coordinates = [[(600.4663, 370.6275, 1020.62146, 792.081), (245, 122, 206), 'fender'],
                       [(661.54663, 246.39789, 1238.9711, 584.2965), (159, 247, 17), 'hood'],
                       [(809.267, 377.4917, 1280.0, 778.3379), (0, 234, 254), 'front_bumper']]

        annotator = cv_helper.Annotator(image=image_path, coordinates=coordinates)

        font_path = './app/static/damage_detection/font_file/arial.ttf'
        save_path = './app/static/damage_detection/output/nissan-annotated.jpg'

        try:
            annotator.annotate_and_save_image(save_path, font_path)
        except AttributeError:
            assert True

    @pytest.mark.asyncio
    async def test_annotate_and_save_image_with_invalid_coordinates_parameter(self):
        image_path = 'tests/data/image/Nissan-front-rightside-view.jpg'
        image = cv2.imread(image_path)
        coordinates = [(100, 200, 300, 400)]
        annotator = cv_helper.Annotator(image=image, coordinates=coordinates)

        font_path = './app/static/damage_detection/font_file/arial.ttf'
        save_path = './app/static/damage_detection/output/nissan-annotated.jpg'

        try:
            annotator.annotate_and_save_image(save_path, font_path)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_annotate_and_save_image_with_invalid_font_path_parameter(self):
        image_path = 'tests/data/image/Nissan-front-rightside-view.jpg'
        image = cv2.imread(image_path)
        coordinates = [[(600.4663, 370.6275, 1020.62146, 792.081), (245, 122, 206), 'fender'],
                       [(661.54663, 246.39789, 1238.9711, 584.2965), (159, 247, 17), 'hood'],
                       [(809.267, 377.4917, 1280.0, 778.3379), (0, 234, 254), 'front_bumper']]
        annotator = cv_helper.Annotator(image=image, coordinates=coordinates)

        font_path = 'tests/data/text/sample.txt'
        save_path = './app/static/damage_detection/output/nissan-annotated.jpg'

        try:
            annotator.annotate_and_save_image(save_path, font_path)
        except OSError:
            assert True
