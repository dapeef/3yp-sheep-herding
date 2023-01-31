import cv2
import numpy as np
import matplotlib.pyplot as plt

def initialize_kernel(size , sigma):

  """ This function initializes a gaussian kernel with the desired size and sigma. """

  w, h = size
  
  x = np.linspace(-1,1,w)
  y = np.linspace(-1,1, h)
  x_cor, y_cor  = np.meshgrid(x, y)
  
  kernel = 1/(2*np.pi*np.power(sigma,2) ) *np.exp((- (x_cor ** 2 + y_cor ** 2) )/ (2*np.power(sigma,2)))
  
  """ Gaussion function: 1/(2 *pi*sigma^2) e^(-(x^2+y^2)/2sigma^2) """
  
  kernel = kernel/np.sum(kernel) # normalization 

  return kernel
  
def padding(image):

  padded_image = np.pad(image , ((1,1),(1,1)) , 'constant', constant_values=(0,0) )

  return padded_image
  
 
def conv2d(image, ftr):
    s = ftr.shape + tuple(np.subtract(image.shape, ftr.shape) + 1)
    sub_image = np.lib.stride_tricks.as_strided(image, shape = s, strides = image.strides * 2)
    return np.einsum('ij,ijkl->kl', ftr, sub_image) 
    
    

def GaussianBlur(gray_image):
  ftr = initialize_kernel(size=(3,3) , sigma=1.5)
  
  blurred_image = conv2d(gray_image, ftr)
  
  return blurred_image


def BGR2GRAY(image):
  # convert to grayscale 
  
  # mehtod 1: by using numpy 
  '''
  gray_image = np.zeros((image.shape[0],image.shape[1]),np.uint8)
  
  for i in range(image.shape[0]):
    for j in range(image.shape[1]):
      #gray_image[i,j] = np.clip( (image[i,j,0] + image[i,j,1] + image[i,j,2] )/3, 0, 255) # using average method
      gray_image[i,j] = np.clip(0.07 * image[i,j,0]  + 0.72 * image[i,j,1] + 0.21 * image[i,j,2], 0, 255) # using luminosity method
  '''  
     
  # method 2: by using cv2. This is more efficient than method 1.     
  gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
  
  # display the image
  #cv2.imshow('grayscale image',gray_image)
  #cv2.waitKey(0)
    
  return gray_image 

def canny_CV2(image,low_threshold, high_Threshold):

  edges = cv2.Canny(image,low_threshold, high_Threshold)
  
  
  return edges 
  
  

def getCoordinates(file_name, show_image=False):

  # read the image 
  image = cv2.imread(file_name) 
  
  # convert the image into grayscale
  gray_image = BGR2GRAY(image)
  
  # blur the gray image
  
  blurred_image = GaussianBlur(gray_image)
  #blurred_image = cv2.bilateralFilter(gray_image,9,75,75)
  #blurred_image = cv2.medianBlur(gray_image,3)


  # apply canny 
  edges = canny_CV2(blurred_image.astype(np.uint8),100,300)
  
  # display the result
  #cv2.imshow('M',np.uint8(edges))
  #cv2.waitKey(0)



  # contours = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
  # cv2.drawContours(image, contours[0], -1, (0,255,0), thickness = 2)
  # fig, ax = plt.subplots(1, figsize=(12,8))
  contours, h = cv2.findContours(edges, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
  filtered_contours = []
  for i in contours:
    if cv2.contourArea(i) > 25:
      filtered_contours.append(i)
  

  # cnts = cv2.drawContours(image, filtered_contours, -1, (0,255,0), thickness = 5)
  # fig, ax = plt.subplots(1, figsize=(12,8))

  coordinates = []
# loop over the contours
  for c in contours:
    # compute the center of the contour
    M = cv2.moments(c)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    # draw the contour and center of the shape on the image
    cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
    cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)
    cv2.putText(image, "center", (cX - 20, cY - 20),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    coordinates.append([cX,cY])
  
  # show the image
  if show_image == True:
    cv2.imshow("Image", image)
    cv2.waitKey(0)
  
  return coordinates
