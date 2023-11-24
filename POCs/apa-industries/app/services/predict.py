import numpy as np
from datetime import datetime
from app.common.utils import timeit


class Predictor:
    def get_flags(self, flags):
        if 'isDevelopment' in flags:
            is_development = True
        else:
            is_development = False
        if 'HasPartsAuthorityPurchased' in flags:
            has_pa_purchased = True
        else:
            has_pa_purchased = False
        if 'HasWorldPacPurchased' in flags:
            has_wp_purchased = True
        else:
            has_wp_purchased = False
        if 'HasSSFPurchased' in flags:
            has_ssf_purchased = True
        else:
            has_ssf_purchased = False
        return is_development, has_pa_purchased, has_wp_purchased, has_ssf_purchased

    def find_sale_year_rank(self, first_sold_year, year):
        v = int(year) - int(first_sold_year)
        return v

    @timeit
    def predict(self, input):
        from app import model, category_encoder, make_encoder, scalar_x, scalar_y, sub_cat_encoder, part_encoder, logger
        total_vio = int(input['total_vio'])
        is_development, has_pa_purchased, has_wp_purchased, has_ssf_purchased = self.get_flags(input['flags'])
        # first_sold_date = input['FirstSold']
        make = make_encoder.transform([input["make"]])[0]
        cat = category_encoder.transform([input["category"]])[0]
        sub_cat = sub_cat_encoder.transform([input["sub_category"]])[0]
        part = part_encoder.transform([input["part"]])[0]
        year = int(input["Year"])
        arr = []
        syr = input['sale_year_rank']
        arr.append(
            (part, int(input['vehicle_max_qty']), is_development, make, cat, sub_cat, year,
             total_vio, has_pa_purchased, has_wp_purchased,
             has_ssf_purchased, syr))
        arr1 = np.array(arr)
        logger.info(f'model syr: {syr}')
        test_X = scalar_x.transform(arr1)
        test_X.astype('float64')
        test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
        # make a prediction
        forecast = model.predict(test_X)
        forecast = scalar_y.inverse_transform(forecast).reshape(len(forecast))
        forecast = forecast.astype('int64')
        return sum(forecast)
