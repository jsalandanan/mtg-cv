from PIL import Image
from PIL import ImageFilter

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

print(image.size)
width, height = image.size # 672, 936
for x in range(33, 336):
  for y in range(880, 900):
    if black_like(image.getpixel((x, y))):
      image.putpixel((x,y), (0, 255, 0))

image.show()

# we actually just need to find the bounds of these pixels



# blur with "color?"

print('Done.')

