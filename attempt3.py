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


def find_bounds(image):
  width, height = image.size # 672, 936

  minX = width + 1
  maxX = -1
  minY = height + 1
  maxY = -1

  for x in range(33, 336):
    for y in range(880, 900):
      if black_like(image.getpixel((x, y))):
        if x < minX:
          minX = x
        if x > maxX:
          maxX = x
        if y < minY:
          minY = y
        if y > maxY:
          maxY = y
        # image.putpixel((x,y), (0, 255, 0))

  return [(minX, minY), (maxX, maxY)]

# calculate the non-white non-black average of colors in region of interest?
avgR = 0
avgG = 0
avgB = 0
totalPixels = 0

for x in range(33, 336):
  for y in range(880, 900):
    if not black_like(image.getpixel((x, y))) and not white_like(image.getpixel((x,y))):
      r, g, b = image.getpixel((x, y))
      avgR += r
      avgG += g
      avgB += b
      totalPixels += 1

avgR = int(avgR / totalPixels)
avgG = int(avgG / totalPixels)
avgB = int(avgB / totalPixels)




# lmaooo inpainting question mark?

bounds = find_bounds(image)
minX, minY = bounds[0]
maxX, maxY = bounds[1]

draw = ImageDraw.Draw(image)
draw.rectangle(find_bounds(image), fill = (avgR, avgG, avgB))

test_text_detection = True
test_inpainting = False

THRESHOLD = 75 # is there a better way to get this other than trial and error?

if test_text_detection:
  image = cv2.imread('card-images/Ash Zealot.jpg')

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

  for contour in contours:
    (x,y,w,h) = cv2.boundingRect(contour)
    cv2.rectangle(image, (x,y), (x+w, y+h), (255, 0, 0), 2)

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
