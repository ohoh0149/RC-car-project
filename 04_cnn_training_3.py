from tensorflow.keras.preprocessing import image as keras_image
import os
import numpy as np
from tqdm import tqdm
from PIL import ImageFile
import pandas as pd

dirname = "data.1640251313.592068/"

def image_to_tensor(img_path):
	img = keras_image.load_img(
		os.path.join(dirname, img_path),
		target_size=(120,160))
	x = keras_image.img_to_array(img)
	return np.expand_dims(x, axis=0)

def data_to_tensor(img_paths):
	list_of_tensors = [
		image_to_tensor(img_path) for img_path in tqdm(img_paths)]
	return np.vstack(list_of_tensors)

ImageFile.LOAD_TRUNCATED_IMAGES = True
# Load the data
data = pd.read_csv(os.path.join(dirname, "0_road_labels.csv"))

files = data['file']
targets = data['label'].values

tensors = data_to_tensor(files)

print(data.tail())
print(tensors.shape)
print(targets.shape)

###

import cv2
import matplotlib.pyplot as plt

# Name list
names = ['forward', 'right', 'left', 'forward']

def display_images(img_path, ax):
	img = cv2.imread(os.path.join(dirname, img_path))
	ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

fig = plt.figure(figsize=(10, 3))
for i in range(4):
	ax = fig.add_subplot(1, 4, i + 1, xticks=[], yticks=[])
	ax.set_title(names[targets[i+4]], color='blue')
	display_images(files[i+4], ax)
plt.show()

###

from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

tensors = tensors.reshape(-1,120,160,3)
print(tensors.shape)

tensors = tensors.astype('float32')/255
targets = to_categorical(targets, 4)

x_train, x_test, y_train, y_test = train_test_split(
		tensors,
		targets,
		test_size = 0.2,
		random_state = 1)

n = int(len(x_test)/2)
x_valid, y_valid = x_test[:n], y_test[:n]
x_test, y_test = x_test[n:], y_test[n:]

print(x_train.shape, y_train.shape)
print(x_test.shape, y_test.shape)
print(x_valid.shape, y_valid.shape)