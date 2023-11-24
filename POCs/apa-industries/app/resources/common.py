import os
import traceback

from flask import Blueprint, render_template, request, redirect, url_for, session, current_app

from app.services.predict import Predictor

parent_dir = os.path.dirname(os.path.abspath(__file__))
common_app = Blueprint('common', __name__)
from datetime import datetime


def get_sale_year_rank(input_data):
    from app import sale_year_rank_lookup, sale_year_rank_search_format
    pa = True if 'HasPartsAuthorityPurchased' in input_data['flags'] else False
    wp = True if 'HasWorldPacPurchased' in input_data['flags'] else False
    ssf = True if 'HasSSFPurchased' in input_data['flags'] else False
    is_d = True if 'isDevelopment' in input_data['flags'] else False
    part = input_data['part']
    make = input_data['make']
    category = input_data['category']
    vehicle_max_qty = input_data['vehicle_max_qty']
    sub_category = input_data['sub_category']
    total_vio = input_data['total_vio']
    x = sale_year_rank_search_format.format(part, vehicle_max_qty, is_d, make, category, sub_category,
                                            pa, wp, ssf)
    try:

        syr_list = [v for k, v in sale_year_rank_lookup.items() if x in k]
        current_app.logger.info(f"searching Sale Year Rank for Key: {x}")
        for i in syr_list:
            i['variance'] = abs(i['vio'] - total_vio) / total_vio
        syr = 0
        min_variance = syr_list[0]['variance']
        for i in syr_list:
            if i['variance'] <= min_variance:
                min_variance = i['variance']
                syr = i['syr']
        current_app.logger.info(f"searching Sale Year Rank:[{syr}] for Key: {x}")
        return syr
    except Exception as e:
        current_app.logger.warning(f"Key not found: {x}")
        current_app.logger.warning('%s -> %s', e, traceback.format_exc())
        return 0


@common_app.route("/", methods=['GET', 'POST'])
def index():
    today = datetime.now()
    year = today.year
    from app import make, category, part, sub_cat
    try:
        if session['username'] == 'admin':
            if request.method == "POST":
                input_data = {}
                input_data['make'] = request.form.get('make')
                input_data['category'] = request.form.get('category')
                input_data['sub_category'] = request.form.get('sub-category')
                input_data['part'] = request.form.get('part')
                input_data['vehicle_max_qty'] = int(request.form.get('vehicleMaxQty'))
                input_data['total_vio'] = int(request.form.get('TotalVIO'))
                input_data['flags'] = request.form.getlist('flags')
                input_data['sale_year_rank'] = get_sale_year_rank(input_data)
                input_data['Year'] = int(year)
                p = Predictor()
                current_app.logger.info(f"Input: {input_data}")
                result = p.predict(input_data)
                current_app.logger.info(f"Result: {result}")
                return render_template('index.html',
                                       part=part,
                                       sub_cat=sub_cat,
                                       category=category,
                                       make=make,
                                       predict_year=year,
                                       result=result)
            return render_template('index.html', part=part, sub_cat=sub_cat, category=category, make=make,
                                   predict_year=year)
    except KeyError as e:
        pass
    except Exception as e:
        current_app.logger.error('%s -> %s', e, traceback.format_exc())
        return render_template('error.html')
    return redirect(url_for('common.login'))


@common_app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form['username']
        password = request.form['password']
        if user_name == 'Michael' and password == 'Tm8RpxKR':
            session['username'] = 'admin'
            return redirect(url_for('common.index'))
        else:
            return render_template('login.html', invalid=True)
    return render_template('login.html')
