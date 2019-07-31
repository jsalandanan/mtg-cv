import sys
import requests
import json
import urllib.request
import re
import os
from process_images import process_image

cards_file = sys.argv[1]

def format_card_name(card_name):
  card_name = card_name.replace('-', ' ')
  card_name = re.sub(r'([^\s\w]|_)+', '', card_name)
  return card_name

def download_images(card_list):
  """
  card_list (arr): An array of card name strings.
  """
  i = 1
  num_cards = len(card_list)
  for card_name in card_list:
    print('{} card of {}'.format(i, num_cards))
    print(card_name)
    i += 1
    if os.path.isfile('img/' + format_card_name(card_name)) == False:
      print("don't be too annoying")
      url = 'https://api.scryfall.com/cards/named?fuzzy=' + card_name
      response = requests.get(url)
      content = json.loads(response.content)

      try:
        image_uri = content['image_uris']['large']
        urllib.request.urlretrieve(image_uri, 'img/' + format_card_name(card_name) + ".jpg")
      except KeyError as e:
        card_faces = content['card_faces']
        image_uri = card_faces[0]['image_uris']['large']
        urllib.request.urlretrieve(image_uri, 'img/' + format_card_name(card_name) + " Front.jpg")
        image_uri = card_faces[1]['image_uris']['large']
        urllib.request.urlretrieve(image_uri, 'img/' + format_card_name(card_name) + " Back.jpg")

def main(cards_file):
  with open(cards_file) as f:
    content = f.readlines()

  card_list = [line.rstrip('\n') for line in content]

  download_images(card_list)

  for card_name in card_list:
    print(card_name)
    process_image(card_name)

main(cards_file)
