import cv2
import numpy as np
from tinydb import TinyDB, Query
import yaml

with open('settings.yaml') as stream:
  try:
    SETTINGS = yaml.safe_load(stream)
  except yaml.YAMLError as exc:
    print(exc)

def card_lookup(card_name):
  """
  card_name (str)
  """
  db = TinyDB('db.json')
  q = Query()

  card_metadata = db.search(q.card_name == card_name)
  if len(card_metadata) > 1:
    raise ValueError('Card names should be unique!')
  return card_metadata[0]

def find_bounds(contours, bounding_dict):
  minX = bounding_dict['SEARCH_AREA_MAX_X']
  maxX = bounding_dict['SEARCH_AREA_MIN_X']
  minY = bounding_dict['SEARCH_AREA_MAX_Y']
  maxY = bounding_dict['SEARCH_AREA_MIN_Y']

  SEARCH_AREA_MAX_X = bounding_dict['SEARCH_AREA_MAX_X']
  SEARCH_AREA_MIN_X = bounding_dict['SEARCH_AREA_MIN_X']
  SEARCH_AREA_MAX_Y = bounding_dict['SEARCH_AREA_MAX_Y']
  SEARCH_AREA_MIN_Y = bounding_dict['SEARCH_AREA_MIN_Y']

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
  card_metadata = card_lookup(card_name)
  card_name = card_metadata['card_name']
  color = card_metadata['color']
  frame = card_metadata['frame']
  type = card_metadata['type']

  threshold_dict = SETTINGS[frame]['type'][type]
  bounding_dict = SETTINGS[frame]['bounding_dict']

  threshold = threshold_dict[color]

  extension = '.jpg'
  
  image = cv2.imread('img/' + card_name + extension)

  grayscale = cv2.cvtColor(src = image, code = cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(grayscale, (3, 3), 0)

  retval, binary = cv2.threshold(src = blur, thresh = threshold, maxval = 255, type = cv2.THRESH_BINARY)

  contours, _ = cv2.findContours(image = binary, mode = cv2.RETR_LIST, method = cv2.CHAIN_APPROX_SIMPLE)

  bounding_rects = find_bounds(contours, bounding_dict)

  height, width, _ = image.shape
  mask = np.zeros((height, width), np.uint8)
  for rect in bounding_rects:
    x,y,w,h = rect
    cv2.rectangle(mask, (x, y), (x+w, y+h), 255, thickness=-1)

  final = cv2.inpaint(image,mask,3,cv2.INPAINT_TELEA)

  cv2.imwrite('output/' + card_name + extension, final)
  print('written')
