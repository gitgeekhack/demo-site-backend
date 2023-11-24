import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow.keras.models import load_model

from constants import DATASET_PATH, MODEL_PATH, IMG_SIZE, BATCH_SIZE, SHUFFLE_BUFFER_SIZE


# resize the image of same size
def format_example(pair):
    image, label = pair['image'], pair['label']
    image = tf.cast(image, tf.float32)
    image = image / 255.
    image = tf.image.resize(image, (IMG_SIZE, IMG_SIZE))
    return image, label


# Load dataset using Tensorflow Dataset Format and Load our own train, test, valid dataset
builder = tfds.folder_dataset.ImageFolder(DATASET_PATH)
train_set = builder.as_dataset(split='train', shuffle_files=True)
valid_set = builder.as_dataset(split='valid', shuffle_files=True)
test_set = builder.as_dataset(split='test', shuffle_files=True)

train = train_set.map(format_example)
validation = valid_set.map(format_example)
test = test_set.map(format_example)

# Batch creation
train_batches = train.shuffle(SHUFFLE_BUFFER_SIZE).batch(BATCH_SIZE)
validation_batches = validation.batch(BATCH_SIZE)
test_batches = test.batch(BATCH_SIZE)

model = load_model(MODEL_PATH)
train_eval = model.evaluate(train_batches)
valid_eval = model.evaluate(validation_batches)
test_eval = model.evaluate(test_batches)
print('train_batches', train_eval[1])
print('validation_batches', valid_eval[1])
print('test_batches', test_eval[1])
