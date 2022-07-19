import sys,os,signal
import zipfile
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import RMSprop

import PIL

# local_zip = 'D:\downloads\horse-or-human.zip'
# zip_ref = zipfile.ZipFile(local_zip, 'r')
# zip_ref.extractall('D:\downloads\horse-or-human')
# local_zip = 'D:\downloads\\validate-horse-or-human.zip'
# zip_ref = zipfile.ZipFile(local_zip, 'r')
# zip_ref.extractall('D:\downloads\\validate-horse-or-human')
# zip_ref.close()


# Directory with our training horse pictures
train_horse_dir = os.path.join('D:/downloads/horse-or-human/horses')

# Directory with our training human pictures
train_human_dir = os.path.join('D:/downloads/horse-or-human/humans')

# Directory with our training horse pictures
validation_horse_dir = os.path.join('D:/downloads/validation-horse-or-human/horses')

# Directory with our training human pictures
validation_human_dir = os.path.join('D:/downloads/validation-horse-or-human/humans')


# All images will be rescaled by 1./255
train_datagen = ImageDataGenerator(rescale=1/255)
validation_datagen = ImageDataGenerator(rescale=1/255)

train_generator = train_datagen.flow_from_directory('D:/downloads/horse-or-human/',
                                                   target_size = (300,300),
                                                   batch_size = 128,
                                                   class_mode = 'binary')

validation_generator = validation_datagen.flow_from_directory('D:/downloads/validate-horse-or-human/',
                                                   target_size = (300,300),
                                                   batch_size = 32,
                                                   class_mode = 'binary')




class epoch_end_callback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if logs.get('acc') > 0.9:
            print("\nReached 80% accuracy!")
            self.model.stop_training = True

# model = tf.keras.Sequential([keras.layers.Dense(units = 1,input_shape=[1])])
# model.compile(optimizer='sgd', loss='mean_squared_error')
#
# xs = np.array([-1.0,  0.0, 1.0, 2.0, 3.0, 4.0], dtype=float)
# ys = np.array([-3.0, -1.0, 1.0, 3.0, 5.0, 7.0], dtype=float)
#
# model.fit(xs,ys,epochs=500)
# print(model.predict([10.0]))


fashion_mnist = keras.datasets.fashion_mnist
(training_images, training_labels), (test_images, test_labels) = fashion_mnist.load_data()

training_images  = training_images.reshape(60000, 28, 28, 1) / 255.0
test_images = test_images.reshape(10000, 28, 28, 1) / 255.0

# model = tf.keras.models.Sequential([tf.keras.layers.Flatten(),
#                                     tf.keras.layers.Dense(units=128, activation= tf.nn.relu),
#                                     tf.keras.layers.Dense(10, activation=tf.nn.softmax)])

model = tf.keras.models.Sequential([tf.keras.layers.Conv2D(16,(3,3),activation='relu',input_shape=(300,300,3)),
                                    tf.keras.layers.MaxPool2D(pool_size=(2,2)),
                                    tf.keras.layers.Conv2D(32,(3,3),activation='relu'),
                                    tf.keras.layers.MaxPool2D(pool_size=(2,2)),
                                    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                                    tf.keras.layers.MaxPool2D(pool_size=(2, 2)),
                                    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                                    tf.keras.layers.MaxPool2D(pool_size=(2, 2)),
                                    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                                    tf.keras.layers.MaxPool2D(pool_size=(2, 2)),
                                    tf.keras.layers.Flatten(),
                                    tf.keras.layers.Dense(units=512, activation='relu'),
                                    tf.keras.layers.Dense(1, activation='sigmoid')])
model.compile(optimizer=RMSprop(lr=0.001),loss='binary_crossentropy',metrics=['acc'])

model.summary()

callbacks = epoch_end_callback()

model.fit_generator(train_generator, steps_per_epoch=10,epochs=20,verbose=1,validation_data=validation_generator, validation_steps=10)
os.kill(os.getpid(), signal.SIGKILL)