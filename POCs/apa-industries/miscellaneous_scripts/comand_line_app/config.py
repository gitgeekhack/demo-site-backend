class Config:
    URL = "https://apaind.com/nos/part.marutitech/export.json"
    API_KEY = "19e4b04cd5d9a3d39b06bfb5ef97e0ac"
    OUTLIER_THRASH = 5
    TEST_DATA_SPLIT_RATIO = 0.30
    VALIDATION_DATA_SPLIT_RATIO = 0.10


class Constant:
    DATA_PATH = "./data/"
    DATA_FILE_PATH = DATA_PATH + 'data.json'
    PREPROCESSED_WITH_PART_ID_DATA_FILE = DATA_PATH + 'pre_processed_with_id.csv'
    PREPROCESSED_WITHOUT_PART_ID_DATA_FILE = DATA_PATH + 'pre_processed_without_id.csv'
    RANGE_PREPROCESSED_WITHOUT_PART_ID_DATA_FILE = DATA_PATH + 'range_pre_processed_without_id.csv'
    PREPROCESSED_WITH_PART_ID_COLUMN_LIST = ["units_sold", "id", "firstSold", "vehicleMaxQty",
                                             "isDevelopment", "make", "category", "year", "TotalVIO",
                                             "SaleYearRank", "HasPartsAuthorityPurchased",
                                             "HasWorldPacPurchased",
                                             "HasSSFPurchased"]
    PREPROCESSED_WITHOUT_PART_ID_COLUMN_LIST = ["units_sold", "firstSold", "vehicleMaxQty", "isDevelopment",
                                                "make", "category", "year", "TotalVIO",
                                                "SaleYearRank", "HasPartsAuthorityPurchased",
                                                "HasWorldPacPurchased",
                                                "HasSSFPurchased"]
    RANGE_PREPROCESSED_WITHOUT_PART_ID_COLUMN_LIST = ["sales_range", "firstSold", "vehicleMaxQty", "isDevelopment",
                                                      "make", "category", "year", "TotalVIO",
                                                      "SaleYearRank", "HasPartsAuthorityPurchased",
                                                      "HasWorldPacPurchased",
                                                      "HasSSFPurchased"]
    OUTLIER_DATA_FILE_PATH = DATA_PATH + 'outliers.csv'
    OUTLIER_FILTERED_DATA_FILE_PATH = DATA_PATH + 'outlier_removed.csv'
    TRAINING_DATA_FILE_PATH = DATA_PATH + 'Training_data.csv'
    TEST_DATA_FILE_PATH = DATA_PATH + 'Test_data.csv'
    VALIDATION_DATA_FILE_PATH = DATA_PATH + 'Valid_data.csv'
    FIRST_SALE_YEAR_DATA_FILE_PATH = DATA_PATH + 'Fisrt_sale_data.csv'
    MODLE_BASE_PATH = './model/RANGE_Model_epoch({})_lstm({})_batch({})_optimizer({})_loss({})_activation({})/'
    LOG_BASE_PATH = './log/RANGE_Model_epoch({})_lstm({})_batch({})_optimizer({})_loss({})_activation({})/'
