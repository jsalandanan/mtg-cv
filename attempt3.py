from PIL import Image, ImageDraw, ImageColor
import cv2
import np

image = Image.open('card-images/Ash Zealot.jpg') # ash zealot
r, g, b = image.getpixel((30, 878))
print('{},{},{}'.format(r,g,b)) # black is used (255, 255, 255)ef

def black_like(color, threshold = 100):
  """
  Args:
    color (tup): An rgb integer tuple
  
  Returns:
    bool: Whether or not the color is "black-like"
  """
  for coordinate in color:
    if coordinate > threshold:
      return False
  return True

def white_like(color, threshold = 100):
  for coordinate in color:
    if coordinate < threshold:
      return False
  return True


search_area_bounding = {
  'SEARCH_AREA_MIN_X': 31,
  'SEARCH_AREA_MAX_X': 480,
  'SEARCH_AREA_MIN_Y': 885,
  'SEARCH_AREA_MAX_Y': 906
}

def find_bounds(contours, bounds_dict=search_area_bounding):
  minX = bounds_dict['SEARCH_AREA_MAX_X']
  maxX = bounds_dict['SEARCH_AREA_MIN_X']
  minY = bounds_dict['SEARCH_AREA_MAX_Y']
  maxY = bounds_dict['SEARCH_AREA_MIN_Y']

  SEARCH_AREA_MAX_X = bounds_dict['SEARCH_AREA_MAX_X']
  SEARCH_AREA_MIN_X = bounds_dict['SEARCH_AREA_MIN_X']
  SEARCH_AREA_MAX_Y = bounds_dict['SEARCH_AREA_MAX_Y']
  SEARCH_AREA_MIN_Y = bounds_dict['SEARCH_AREA_MIN_Y']

  for contour in contours:
    x,y,w,h = cv2.boundingRect(contour)
    inbounds = x > SEARCH_AREA_MIN_X and x + w < SEARCH_AREA_MAX_X and y > SEARCH_AREA_MIN_Y and y + h < SEARCH_AREA_MAX_Y
    if x < minX and inbounds:
      minX = x
    if x + w > maxX and inbounds:
      maxX = x + w
    if y < minY and inbounds:
      minY = y
    if y + h > maxY and inbounds:
      maxY = y + h

  return (minX, maxX, minY, maxY)

test_text_detection = True
test_inpainting = False

THRESHOLD = 75 # is there a better way to get this other than trial and error?

minX, maxX, minY, maxY = 31, 480, 885, 906

if test_text_detection:
  image = cv2.imread('card-images/Ash Zealot.jpg')

  # cropped = image[minY:maxY, minX:maxX]
  # cv2.imshow("test", cropped)
  # cv2.waitKey(0)

  grayscale = cv2.cvtColor(src = image, code = cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(grayscale, (3, 3), 0)

  retval, binary = cv2.threshold(src = blur, thresh = THRESHOLD, maxval = 255, type = cv2.THRESH_BINARY)

  cv2.imshow("test", binary)
  cv2.waitKey(0)

  contours, _ = cv2.findContours(image = binary, mode = cv2.RETR_LIST, method = cv2.CHAIN_APPROX_SIMPLE)

  # cv2.drawContours(image = image,
  #   contours = contours,
  #   contourIdx = -1,
  #   color = (255, 0, 0),
  #   thickness = 1)

  # find the min and max x and y of contours within the established min and max x and y
  # for contour in contours:
  #   (x,y,w,h) = cv2.boundingRect(contour)
  #   cv2.rectangle(image, (x,y), (x+w, y+h), (255,0, 0), 2)

  (minX, maxX, minY, maxY) = find_bounds(contours)
  print((minX, maxX, minY, maxY))
  cv2.rectangle(image, (minX,minY), (maxX, maxY), (255, 0, 0), 2)

  cv2.imshow("test", image)
  cv2.waitKey(0)

elif test_inpainting:
  image = cv2.imread('card-images/Ash Zealot.jpg')
  height, width, _ = image.shape

  rectangle_image = np.zeros((height, width), np.uint8)
  cv2.rectangle(rectangle_image, (minX, minY), (maxX, maxY), 255, thickness=-1)

  # masked_data = cv2.bitwise_and(image, image, mask=rectangle_image)

  cv2.imshow("mask", rectangle_image) # mask needs to be in grayscale?
  cv2.waitKey(0)

  cv2.imshow("image", image)
  cv2.waitKey(0)

  dst = cv2.inpaint(image,rectangle_image,3,cv2.INPAINT_TELEA)
  cv2.imshow('dst', dst)
  cv2.waitKey(0)

  # image.show()
print('Done.')
