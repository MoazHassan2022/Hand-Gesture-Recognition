import cv2
import os
import numpy as np
from skimage.feature import hog
from skimage.feature import local_binary_pattern
from preprocessing import preprocess

# =========================================================================
# HOG Feature Extraction
# =========================================================================
def HOG(image, orientations = 9, pixels_per_cell = (8, 8), cells_per_block = (3, 3)):
    # Calculate the HOG features
    hog_features = hog(image, orientations=orientations, pixels_per_cell=pixels_per_cell, cells_per_block=cells_per_block)
    
    # Pad the feature vector with zeros to make sure they all have the same length
    max_size = hog_features.shape[0]
    hog_features = np.pad(hog_features, (0, max_size - hog_features.shape[0]), mode='constant')
    hog_features = np.ravel(hog_features)
    return hog_features

# =========================================================================


# =========================================================================
# LBP Feature Extraction
# =========================================================================
def LBP(image, radius = 1, method = 'uniform'):
    # Define LBP parameters
    n_points = 8 * radius
    
    # Calculate the LBP features
    lbp = local_binary_pattern(image, n_points, radius, method)

    histogram, _ = np.histogram(lbp, bins=np.arange(0, n_points + 3), range=(0, n_points + 2))

    # Normalize the histogram
    histogram = histogram.astype("float")
    histogram /= (histogram.sum() + 1e-7)

    # The resulting histogram is the feature vector for the input image
    return histogram
# =========================================================================


# =========================================================================
# SIFT Feature Extraction
def SIFT(image):
    # Initialize the SIFT detector
    sift = cv2.SIFT_create()

    # Extract SIFT features from all the images
    kp, des = sift.detectAndCompute(image, None)
    
    return des 
# =========================================================================


# =========================================================================
# SURF Feature Extraction
# =========================================================================
def SURF(image):
    surf = cv2.xfeatures2d.SURF_create()
    keypoints, descriptors = surf.detectAndCompute(image, None)

    feature_list = []
    for kp, desc in zip(keypoints, descriptors):
        feature = np.concatenate((kp.pt, kp.size, kp.angle, kp.response, kp.octave, desc))
        feature_list.append(feature)
    
    if len(feature_list) == 0:
        return None
    
    feature_arr = np.array(feature_list, dtype=object)
    return feature_arr
# =========================================================================


# =========================================================================
# Mains
# =========================================================================
def HOG_MAIN(images_dir, dataset_dir, orientations = 9, pixels_per_cell = (8, 8), cells_per_block = (3, 3)):
		feature_arr = []
		label_arr = []

		for path in images_dir:
				# get all the image names
				images = os.listdir(dataset_dir + path)

				# iterate over the image names, get the label
				for image in images:
						image_path = dataset_dir + f"{path}/{image}"
						try:
								image = cv2.imread(image_path)

								# Preprocessing phase
								image = preprocess(image)

								# Feature extraction phase
								feature = HOG(image, orientations = orientations, pixels_per_cell = pixels_per_cell, cells_per_block = cells_per_block)

								# update the data and labels
								feature_arr.append(feature)
								label_arr.append(path)
						except:
								print(image_path)

		return feature_arr, label_arr

def LBP_MAIN(images_dir, dataset_dir):
		feature_arr = []
		label_arr = []

		for path in images_dir:
				# get all the image names
				images = os.listdir(dataset_dir + path)
				
				# iterate over the image names, get the label
				for image in images:
						image_path = dataset_dir + f"{path}/{image}"

						try:
								image = cv2.imread(image_path)

								# Preprocessing phase
								image = preprocess(image)

								# Feature extraction phase
								feature = LBP(image)

								# update the data and labels
								feature_arr.append(feature)
								label_arr.append(path)
						except:
								print(image_path)

		return feature_arr, label_arr

def SIFT_MAIN(images_dir, dataset_dir):
		descriptors_list = []
		label_list = []
		max_length = 0

		for path in images_dir:
				# get all the image names
				images = os.listdir(dataset_dir + path)

				# iterate over the image names, get the label
				for image in images:
						image_path = dataset_dir + f"{path}/{image}"

						try:
								# Read image
								image = cv2.imread(image_path)

								# Preprocessing phase
								image = preprocess(image)

								# SIFT feature extraction
								descriptors = SIFT(image)

								# Update max_length that will be used for padding
								if descriptors.shape[0] > max_length:
										max_length = descriptors.shape[0]

								# Append feature and label to respective lists
								descriptors_list.append(descriptors)
								label_list.append(path)
						except:
								print(image_path)

		# Padding
		for i in range(len(descriptors_list)):
				descriptors = descriptors_list[i]
				if descriptors.shape[0] < max_length:
						padding = np.zeros((max_length - descriptors.shape[0], descriptors.shape[1]), dtype=np.float32)
						descriptors = np.vstack((descriptors, padding))
						descriptors_list[i] = descriptors
		
		descriptors_list = np.array(descriptors_list)

		nsamples, nx, ny = descriptors_list.shape
		d2_train_dataset = descriptors_list.reshape((nsamples,nx*ny))

		return d2_train_dataset, np.array(label_list)

def ORB_MAIN(images_dir, dataset_dir):
    descriptors_list = []
    label_list = []
    max_length = 0

    for path in images_dir:
        # get all the image names
        images = os.listdir(dataset_dir + path)

        # iterate over the image names, get the label
        for image in images:
            image_path = dataset_dir + f"{path}/{image}"

            try:
                # Read image
                image = cv2.imread(image_path)

                # Preprocessing phase
                image = preprocess(image)

                # SIFT feature extraction
                orb = cv2.ORB_create()
                keypoints, descriptors = orb.detectAndCompute(image, None)

                if descriptors.shape[0] > max_length:
                    max_length = descriptors.shape[0]

                # Append feature and label to respective lists
                descriptors_list.append(descriptors)
                label_list.append(path)

            except:
                print(image_path)

    for i in range(len(descriptors_list)):
        descriptors = descriptors_list[i]
        if descriptors.shape[0] < max_length:
            padding = np.zeros((max_length - descriptors.shape[0], descriptors.shape[1]), dtype=np.float32)
            descriptors = np.vstack((descriptors, padding))
            descriptors_list[i] = descriptors
    
    descriptors_list = np.array(descriptors_list)

    nsamples, nx, ny = descriptors_list.shape
    d2_train_dataset = descriptors_list.reshape((nsamples,nx*ny))

    return d2_train_dataset, np.array(label_list)
# =========================================================================



def get_feature(FEATURE_METHOD, images_dir, dataset_dir):
		if FEATURE_METHOD == 0:
				return HOG_MAIN(images_dir, dataset_dir, orientations = 9, pixels_per_cell = (8, 8), cells_per_block = (3, 3))
		elif FEATURE_METHOD == 1:
				return LBP_MAIN(images_dir, dataset_dir)
		elif FEATURE_METHOD == 2:
				return SIFT_MAIN(images_dir, dataset_dir)
		elif FEATURE_METHOD == 3:
				return ORB_MAIN(images_dir, dataset_dir)