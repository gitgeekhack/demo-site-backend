import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow import keras
from tqdm.keras import TqdmCallback
from constants import DATASET_PATH, MODEL_PATH, LOG_PATH, IMG_SIZE, BATCH_SIZE, SHUFFLE_BUFFER_SIZE, IMG_SHAPE, \
    LEARNING_RATE, NO_OF_EPOCHS


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

# Inspect a batch of data
image_batch, label_batch = [x for x in train_batches.take(1).as_numpy_iterator()][0]

# Create the base model from the pre-trained convnets
base_model = tf.keras.applications.MobileNetV2(input_shape=IMG_SHAPE,
                                               include_top=False,
                                               weights='imagenet')

# get block of feature from the base model
feature_batch = base_model(image_batch)

# Freeze the convolutional base
base_model.trainable = False

base_model.summary()

# Add a classification head. To generate predictions from the block of features, average over the spatial
global_average_layer = keras.layers.GlobalAveragePooling2D()
feature_batch_average = global_average_layer(feature_batch)

# Dense layer to convert these features into a single prediction
prediction_layer = keras.layers.Dense(1)

# stack the feature extractor, global_average_pooling layer and dense layer
model = keras.Sequential([
    base_model,
    global_average_layer,
    prediction_layer
])

# compile the model
model.compile(optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
              loss=keras.losses.BinaryCrossentropy(from_logits=True),
              metrics=['accuracy'])

model.summary()

# Early stopping to avoid over-fitting
early_stopping_callback = keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)

# log the model training loss and accuracy for debugging
my_callbacks = [
    TqdmCallback(verbose=0),
    tf.keras.callbacks.TensorBoard(
        log_dir=LOG_PATH),
]

# Train the model
history = model.fit(train_batches,
                    verbose=0,
                    epochs=NO_OF_EPOCHS,
                    validation_data=validation_batches,
                    callbacks=[my_callbacks, early_stopping_callback])

# Test the model accuracy on unseen data
print(model.evaluate(test_batches))

# Save the model
model.save(MODEL_PATH)
