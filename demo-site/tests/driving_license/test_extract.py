import os
import uuid
import pytest
os.chdir('../../')
import cv2
from app.service.driving_license import extract

pytest_plugins = ('pytest_asyncio',)


class TestDLDataPointExtractorV1:
    @pytest.mark.asyncio
    async def test_date_with_valid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)
        parse_date = [{'bbox': [288.89, 293.36, 465.92, 343.05], 'score': 0.8471530675888062},
                      {'bbox': [241.88, 237.17, 445, 269.46], 'score': 0.8440335988998413},
                      {'bbox': [239.05, 264.88, 443.9, 295.38], 'score': 0.8328210711479187}]

        result = await extractor._DLDataPointExtractorV1__multiple_dates(parse_date)
        assert result == parse_date

    @pytest.mark.asyncio
    async def test_date_with_invalid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)
        parse_date = "bbox:[288.89, 293.36, 465.92, 343.05], score:0.8471530675888062"

        try:
            await extractor._DLDataPointExtractorV1__multiple_dates(parse_date)
        except AttributeError:
            assert True

    @pytest.mark.asyncio
    async def test_detect_objects_with_valid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)

        image_path = 'tests/data/image/minnesota_license.jpg'
        image = cv2.imread(image_path)

        result = await extractor._DLDataPointExtractorV1__detect_objects(image)
        assert len(result.keys()) == 11

    @pytest.mark.asyncio
    async def test_detect_objects_with_invalid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)

        invalid_file_path = 'tests/data/text/sample.txt'

        try:
            await extractor._DLDataPointExtractorV1__detect_objects(invalid_file_path)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_get_text_from_object_with_valid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)

        image_path = 'tests/data/image/get_text_from_object.jpg'
        label = 'license_number'

        image = cv2.imread(image_path)
        result = await extractor._DLDataPointExtractorV1__get_text_from_object(label, image)
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_text_from_object_with_invalid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)

        pdf_path = 'tests/data/pdf/Sample1.pdf'
        label = 'license_number'

        try:
            await extractor._DLDataPointExtractorV1__get_text_from_object(label, pdf_path)
        except AttributeError:
            assert True

    @pytest.mark.asyncio
    async def test_extract_data_by_label_with_valid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)
        image_path = 'tests/data/image/extract_data_by_label.jpg'
        image = cv2.imread(image_path)
        result = await extractor._DLDataPointExtractorV1__extract_data_by_label(image)
        assert result is not None

    @pytest.mark.asyncio
    async def test_extract_data_by_label_with_invalid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)
        txt_path = 'tests/data/text/sample.txt'
        try:
            await extractor._DLDataPointExtractorV1__extract_data_by_label(txt_path)
        except:
            assert True

    @pytest.mark.asyncio
    async def test_dates_per_label_with_valid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)
        input_data = [
            ('license_number', 'A123-456-789-098-'),
            ('address',
             {'street': '8123 BLOOMINGTON AVE', 'city': 'Minneapolis', 'state': 'MN', 'zipcode': '55417-1234'}),
            ('weight', '135 lbs'),
            ('name', 'SAMPLE JUN MARIE'),
            ('height', '05"'),
            ('gender', 'Female'),
            ('license_class', 'D'),
            ('eye_color', 'Brown'),
            ('date1', '2001-08-20'),
            ('date2', '2018-08-20'),
            ('date3', '2022-08-20')
        ]
        expected_output = [
            ('license_number', 'A123-456-789-098-'),
            ('address',
             {'street': '8123 BLOOMINGTON AVE', 'city': 'Minneapolis', 'state': 'MN', 'zipcode': '55417-1234'}),
            ('weight', '135 lbs'),
            ('name', 'SAMPLE JUN MARIE'),
            ('height', '05"'),
            ('gender', 'Female'),
            ('license_class', 'D'),
            ('eye_color', 'Brown'),
            ('date_of_birth', '2001-08-20'),
            ('issue_date', '2018-08-20'),
            ('expiry_date', '2022-08-20')
        ]
        result = await extractor._DLDataPointExtractorV1__dates_per_label(input_data)
        assert result == expected_output

    @pytest.mark.asyncio
    async def test_dates_per_label_with_invalid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)
        input_data = [
            ('license_number', None),
            ('address',
             {'street': '8123 BLOOMINGTON AVE', 'city': 'Minneapolis', 'state': 'MN', 'zipcode': '55417-1234'}),
            ('weight', '135 lbs'),
            ('name', 'SAMPLE JUN MARIE'),
            ('height', '05"'),
            ('gender', 'Female'),
            ('license_class', 'D'),
            ('eye_color', 'Brown'),
            ('date1', None),
            ('date2', '2018-08-20'),
            ('date3', '2022-08-20')
        ]
        try:
            extractor._DLDataPointExtractorV1__dates_per_label(input_data)
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_update_labels_with_valid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)
        input_data = {'name': 'SAMPLE JUN MARIE', 'eye_color': 'Brown', 'gender': 'Female', 'hair_color': None,
                      'height': '05"', 'weight': '135 lbs', 'license_class': 'D', 'license_number': 'A123-456-789-098-',
                      'expiry_date': '2022-08-20', 'date_of_birth': '2001-08-20', 'issue_date': '2018-08-20',
                      'address': {'street': '8123 BLOOMINGTON AVE', 'city': 'Minneapolis', 'state': 'MN',
                                  'zipcode': '55417-1234'}}
        result = extractor._DLDataPointExtractorV1__update_labels(input_data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_labels_with_invalid_parameter(self):
        test_uuid = str(uuid.uuid4())
        extractor = extract.DLDataPointExtractorV1(uuid=test_uuid)
        input_data = 12345
        try:
            await extractor._DLDataPointExtractorV1__update_labels(input_data)
        except:
            assert True
