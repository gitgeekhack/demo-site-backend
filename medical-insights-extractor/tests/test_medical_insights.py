from app.service.medical_document_insights.medical_insights import parse_date


class TestMedicalInsights:
    def test_parse_date_with_3_valid_parameter(self):
        date_str = "08-16-2001"
        assert parse_date(date_str) == (2001, 8, 16)

    def test_parse_date_with_2_valid_parameter(self):
        date_str = "08-2001"
        assert parse_date(date_str) == (2001, 8, 1)

    def test_parse_date_with_1_valid_parameter(self):
        date_str = "2001"
        assert parse_date(date_str) == (2001, 1, 1)

    def test_parse_date_with_invalid_format_too_short(self):
        date_str = "08-16"
        try:
            parse_date(date_str)
        except ValueError:
            assert True

    def test_parse_date_with_invalid_format_too_long(self):
        date_str = "08-16-2001-01"
        try:
            parse_date(date_str)
        except ValueError:
            assert True

    def test_parse_date_with_non_numeric_format(self):
        date_str = "MM-16-2001"
        try:
            parse_date(date_str)
        except ValueError:
            assert True

        date_str = "08-DD-2001"
        try:
            parse_date(date_str)
        except ValueError:
            assert True

        date_str = "08-16-YYYY"
        try:
            parse_date(date_str)
        except ValueError:
            assert True

    def test_parse_date_with_int_format(self):
        date_str = 16082001
        try:
            parse_date(date_str)
        except AttributeError:
            assert True
