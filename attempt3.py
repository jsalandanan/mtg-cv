from PIL import Image, ImageDraw

# thought is to search for pixels of a certain threshold from color and switch
# them to the surrounding pixels that are not threshold.

# two pass?
# pass 1 to find the bounds of each thing that's not color
# then iterate on the perimeter, shrinking down

image = Image.open('card-images/Ash Zealot.jpg') # ash zealot
r, g, b = image.getpixel((300, 0))
print('{},{},{}'.format(r,g,b)) # black is used (255, 255, 255)ef

# import sys; sys.exit(0)
def black_like(color, threshold = 100):
  """
  takes in a tuple
  returns bool
  """
  for coordinate in color:
    if coordinate > threshold:
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
        image.putpixel((x,y), (0, 255, 0))

  return [(minX, minY), (maxX, maxY)]

draw = ImageDraw.Draw(image)
draw.rectangle(find_bounds(image))

image.show()
print('Done.')

