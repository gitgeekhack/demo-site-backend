import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from app.manage import create_app
import pandas as pd
from app.resources.common import common_app
from keras.models import load_model
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder, StandardScaler

tf.get_logger().setLevel('ERROR')

parent_dir = os.path.dirname(os.path.abspath(__file__))
app = create_app()
app.secret_key = "super secret key"
logger = app.logger

logger.info("Loading dataset")
data = pd.read_csv(os.path.join(parent_dir, app.config['DATA_PATH']))
data = data.drop("units_sold_360", axis=1)
sale_year_rank_lookup = {}
sale_year_rank_lookup_format = "{}_{}_{}_{}_{}_{}_{}_{}_{}_{}"
sale_year_rank_search_format = "{}_{}_{}_{}_{}_{}_{}_{}_{}_"
for index, row in data.iterrows():
    x = sale_year_rank_lookup_format.format(row['partType'],
                                            row['vehicleMaxQty'],
                                            row['isDevelopment'],
                                            row['make'],
                                            row['category'],
                                            row['subCat'],
                                            row['HasPartsAuthorityPurchased'],
                                            row['HasWorldPacPurchased'],
                                            row['HasSSFPurchased'],
                                            row['TotalVIO'])
    if x in sale_year_rank_lookup.keys():
        max = sale_year_rank_lookup[x]['syr']
        if row['sale_year_rank'] > max:
            sale_year_rank_lookup[x] = {'syr': row['sale_year_rank'], 'vio': row['TotalVIO']}
    else:
        sale_year_rank_lookup[x] = {'syr': row['sale_year_rank'], 'vio': row['TotalVIO']}

make = list(set(data['make']))
make.sort()
category = list(set(data['category']))
category.sort()
part = list(set(data['partType']))
part.sort()
sub_cat = list(set(data['subCat']))
sub_cat.sort()
logger.info("Dataset loaded")

logger.info("Initializing encoders")
make_encoder = LabelEncoder()
part_encoder = LabelEncoder()
sub_cat_encoder = LabelEncoder()
category_encoder = LabelEncoder()

part_encoder.fit(data.values[:, 1])
make_encoder.fit(data.values[:, 4])
category_encoder.fit(data.values[:, 5])
sub_cat_encoder.fit(data.values[:, 6])

scalar_x = StandardScaler()
scalar_y = StandardScaler()
values = data.values

values[:, 1] = part_encoder.transform(values[:, 1])
values[:, 4] = make_encoder.transform(values[:, 4])
values[:, 5] = category_encoder.transform(values[:, 5])
values[:, 6] = sub_cat_encoder.transform(values[:, 6])

scalar_x.fit(values[:, 1:])
scalar_y.fit(values[:, 0].reshape(len(values), 1))
logger.info("Encoders & Scalar initialized")
logger.info("Initializing Model")
model = load_model(os.path.join(parent_dir, app.config['MODEL_PATH']))
logger.info("Model initialized")

app.register_blueprint(common_app)
