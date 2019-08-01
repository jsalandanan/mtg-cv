import cv2
import numpy as np

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

  valid_bounding_rectangles = []

  for contour in contours:
    x,y,w,h = cv2.boundingRect(contour)
    inbounds = x > SEARCH_AREA_MIN_X and x + w < SEARCH_AREA_MAX_X and y > SEARCH_AREA_MIN_Y and y + h < SEARCH_AREA_MAX_Y
    if inbounds:
      valid_bounding_rectangles.append((x,y,w,h))

  return valid_bounding_rectangles

def process_image(card_name):
  """
  card_name (str): The name of a card
  """
  THRESHOLD = 75 # is there a better way to get this other than trial and error?
  extension = '.jpg'
  
  image = cv2.imread('img/' + card_name + extension)

  grayscale = cv2.cvtColor(src = image, code = cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(grayscale, (3, 3), 0)

  retval, binary = cv2.threshold(src = blur, thresh = THRESHOLD, maxval = 255, type = cv2.THRESH_BINARY)

  contours, _ = cv2.findContours(image = binary, mode = cv2.RETR_LIST, method = cv2.CHAIN_APPROX_SIMPLE)

  bounding_rects = find_bounds(contours)

  height, width, _ = image.shape
  mask = np.zeros((height, width), np.uint8)
  for rect in bounding_rects:
    x,y,w,h = rect
    cv2.rectangle(mask, (x, y), (x+w, y+h), 255, thickness=-1)

  final = cv2.inpaint(image,mask,3,cv2.INPAINT_TELEA)

  cv2.imwrite('output/' + card_name + extension, final)
  print('written')
