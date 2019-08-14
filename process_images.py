import sys
import cv2
import numpy as np
from tinydb import TinyDB, Query
import yaml
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

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

def prettify_image(image, frame): # rename this
  """
  image (Image)
  frame(str): A string representing the frame year from Scryfall. (e.g. '2015')
  """
  # Adjust brightness
  image = ImageEnhance.Brightness(image).enhance(1.07)
  bcolor = 'black'

  # Remove old border
  if frame == '2015' or frame == '2003':
    image = image.crop((29,27,646,910))
    image = image.resize((690,984), Image.ANTIALIAS)
    image = ImageOps.expand(image,border=72,fill=bcolor)
    if frame == '2015':
      # Round off the top corners
      draw = ImageDraw.Draw(image)
      draw.line((66, 66, 74, 66), fill=bcolor)
      draw.line((66, 67, 72, 67), fill=bcolor)
      draw.line((66, 68, 69, 68), fill=bcolor)
      draw.line((66, 69, 68, 69), fill=bcolor)
      draw.line((66, 70, 68, 70), fill=bcolor)
      draw.line((66, 71, 67, 71), fill=bcolor)
      draw.line((66, 72, 67, 72), fill=bcolor)
      draw.line((66, 73, 66, 73), fill=bcolor)

      draw.line((747, 66, 755, 66), fill=bcolor)
      draw.line((749, 67, 756, 67), fill=bcolor)
      draw.line((752, 68, 757, 68), fill=bcolor)
      draw.line((753, 69, 758, 69), fill=bcolor)
      draw.line((753, 70, 759, 70), fill=bcolor)
      draw.line((754, 71, 760, 71), fill=bcolor)
      draw.line((754, 72, 761, 72), fill=bcolor)
      draw.line((755, 73, 762, 73), fill=bcolor)
  else:
    image = image.crop((33,36,638,898))
    image = image.resize((678,972), Image.ANTIALIAS)
    image = ImageOps.expand(image,border=66,fill=bcolor)

  return image


def process_image(card_name, debug=False):
  card_metadata = card_lookup(card_name)
  card_name = card_metadata['card_name']
  color = card_metadata['color']
  frame = card_metadata['frame']
  type = card_metadata['type']

  if frame == '2015':
    process_image_naive(card_name, type, debug)
  else:
    process_image_cv(card_name, color, frame, type, debug)

  image = Image.open('output/' + card_name + '.jpg')

  image = prettify_image(image, frame)

  image.save('final_output/' + card_name + '.png')
  print('written')

def process_image_cv(card_name, color, frame, type, debug=False):
  """
  card_name (str): The name of a card
  """

  if type == 'creature':
    bounding_dict = SETTINGS[frame][type]
  else:
    bounding_dict = SETTINGS[frame]['other']


  threshold_dict = SETTINGS[frame]['threshold_dict']

  if color == 'colorless':
    threshold = threshold_dict[color][type]['threshold']
    invert = threshold_dict[color][type]['invert']
  else:
    threshold = threshold_dict[color]['threshold']
    invert = threshold_dict[color]['invert']

  extension = '.jpg'
  
  image = cv2.imread('img/' + card_name + extension)
  # image = cv2.imread('img/Ravens Crime.jpg')

  grayscale = cv2.cvtColor(src = image, code = cv2.COLOR_BGR2GRAY)
  blur = cv2.GaussianBlur(grayscale, (3, 3), 0)

  if invert:
    retval, binary = cv2.threshold(src = blur, thresh = threshold, maxval = 255, type = cv2.THRESH_BINARY_INV)
  else:
    retval, binary = cv2.threshold(src = blur, thresh = threshold, maxval = 255, type = cv2.THRESH_BINARY)

  if debug:
    cv2.imshow('binary', binary)
    cv2.waitKey(0)
    sys.exit(0)

  contours, _ = cv2.findContours(image = binary, mode = cv2.RETR_LIST, method = cv2.CHAIN_APPROX_SIMPLE)

  bounding_rects = find_bounds(contours, bounding_dict)

  height, width, _ = image.shape
  mask = np.zeros((height, width), np.uint8)
  for rect in bounding_rects:
    x,y,w,h = rect
    cv2.rectangle(mask, (x, y), (x+w, y+h), 255, thickness=-1)

  final = cv2.inpaint(image,mask,3,cv2.INPAINT_TELEA)

  cv2.imwrite('output/' + card_name + extension, final)


def process_image_naive(card_name, type, debug=False):
  image = Image.open('img/' + card_name + '.jpg')
  draw = ImageDraw.Draw(image)

  if type == 'creature' or type == 'planeswalker':
    draw.rectangle([(375,892), (630, 909)], fill = (23,20,15) )
  else:
    draw.rectangle([(375,870), (630, 909)], fill = (23,20,15) )

  image.save('output/' + card_name + '.jpg')
