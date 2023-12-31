# -*- coding: utf-8 -*-
"""flowersCNN_VGG-19.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hASX1jNYcjlMjNnsUxNg2-fombjhg5i3

Импорт библиотек
"""

import tensorflow as tf
from tensorflow.keras.applications import VGG19
from tensorflow.keras import layers, models
from tensorflow.keras.optimizers import Adam
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

"""Распакова архива и генерация данных"""

!unzip  /content/drive/MyDrive/Flowers/flowers.zip -d flowers

!pip install split-folders

import splitfolders
splitfolders.ratio('/content/flowers/flowers', output="output", seed=1337, ratio=(.8, 0.1,0.1))

data_dir = '/content/flowers/flowers'

BATCH_SIZE = 64
IMG_WIDTH = 224
IMG_HEIGHT = 224


train_loader = tf.keras.preprocessing.image_dataset_from_directory(
    "./output/train",
    seed=123,
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE
)

test_loader = tf.keras.preprocessing.image_dataset_from_directory(
    "./output/test",
    seed=123,
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE
)

validation_loader = tf.keras.preprocessing.image_dataset_from_directory(
    "./output/val",
    seed=123,
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE
)


class_names = list(train_loader.class_names)

plt.figure(figsize=(10, 10))
for images, labels in train_loader.take(1):
    for i in range(9):
        plt.subplot(3, 3, i + 1)

        plt.imshow(images[i].numpy().astype("uint8") / 255.0)
        plt.title(class_names[labels[i]])
        plt.axis("off")
plt.show()


train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)


train_generator = train_datagen.flow_from_directory(
    "./output/train",
    target_size=(IMG_WIDTH, IMG_HEIGHT),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_generator = train_datagen.flow_from_directory(
    "./output/train",
    target_size=(IMG_WIDTH, IMG_HEIGHT),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)


base_model = VGG19(weights='imagenet', include_top=False, input_shape=(IMG_WIDTH, IMG_HEIGHT, 3))
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.Flatten(),
    layers.Dropout(0.3),
    layers.Dense(512, activation='relu'),
    layers.Dense(len(class_names), activation='softmax')
])


model.compile(optimizer=Adam(learning_rate=0.0001),
              loss='categorical_crossentropy',
              metrics=['accuracy', 'categorical_accuracy'])


epochs = 25
history = model.fit(
    train_generator,
    epochs=epochs,
    validation_data=val_generator
)


test_generator = train_datagen.flow_from_directory(
    "./output/test",
    target_size=(IMG_WIDTH, IMG_HEIGHT),
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)

evaluation_results = model.evaluate(test_generator)
test_loss = evaluation_results[0]
test_acc = evaluation_results[1]
print(f"Accuracy on test data: {test_acc}")


acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

plt.figure(figsize=(10, 10))
for images, labels in test_loader.take(1):
    for i in range(9):
        ax = plt.subplot(3, 3, i + 1)
        plt.imshow(images[i].numpy().astype("uint8"))
        predictions = model.predict(tf.expand_dims(images[i], 0))
        score = tf.nn.softmax(predictions[0])
        plt.ylabel("Predicted: "+class_names[np.argmax(score)])
        plt.title("Actual: "+class_names[labels[i]])
        plt.gca().axes.yaxis.set_ticklabels([])
        plt.gca().axes.xaxis.set_ticklabels([])

"""Сохранение модели"""

img = tf.keras.utils.load_img(
    "/content/1.jpg", target_size=(IMG_HEIGHT, IMG_WIDTH)
)
img_array = tf.keras.utils.img_to_array(img)
img_array = tf.expand_dims(img_array, 0) # Create a batch

predictions = model.predict(img_array)
score = tf.nn.softmax(predictions[0])

print(
    f"Это изображение похоже на {class_names[np.argmax(score)]} с вероятностью {100 * np.max(score)} процентов."
    )

model.save("flowers.h5")