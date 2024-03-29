import sys
import requests
import time
import json
import urllib.request
import re
import os
from process_images import process_image
from tinydb import TinyDB, Query
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--cardlist", help="Input file", type=str)
parser.add_argument("-d", "--debug", help="Test mode", type=bool)

args = parser.parse_args()

def parse_type_line(type_line):
  """
  type_line (str): A string representing the card's type.
  """
  type_line = type_line.lower()
  if 'land' in type_line:
    return 'land'
  elif 'artifact' in type_line:
    return 'artifact'
  elif 'creature' in type_line:
    return 'creature'
  elif 'planeswalker' in type_line:
    return 'planeswalker'
  else:
    return 'other'

def parse_color(colors):
  """
  colors (arr): An array of the card's color(s).
  """
  if len(colors) == 0:
    return 'colorless'
  elif len(colors) == 1:
    color = colors[0]
    if color == 'W':
      return 'white'
    elif color == 'U':
      return 'blue'
    elif color == 'B':
      return 'black'
    elif color == 'R':
      return 'red'
    elif color == 'G':
      return 'green'
  else:
    return 'multicolor'

def download_images(card_list):
  """
  card_list (arr): An array of card name strings.
  """
  db = TinyDB('db.json')
  q = Query()

  i = 1
  num_cards = len(card_list)
  for card_name in card_list:
    print('{} card of {}'.format(i, num_cards))
    print(card_name)
    i += 1
    if os.path.isfile('img/' + card_name) == False:
      url = 'https://api.scryfall.com/cards/named?fuzzy=' + card_name
      time.sleep(0.1)

      response = requests.get(url)
      content = json.loads(response.content)

      get_tokens(content)

      try:
        image_uri = content['image_uris']['large']
        urllib.request.urlretrieve(image_uri, 'img/' + card_name + ".jpg")
      except KeyError as e:
        card_faces = content['card_faces']
        image_uri = card_faces[0]['image_uris']['large']
        urllib.request.urlretrieve(image_uri, 'img/' + card_name + " Front.jpg")
        image_uri = card_faces[1]['image_uris']['large']
        urllib.request.urlretrieve(image_uri, 'img/' + card_name + " Back.jpg")

      # store card info (frame, color) (creature/non-creature, story spotlight, border color?)
      if not db.search(q.card_name == card_name):
        db.insert({'card_name': card_name, 'color': parse_color(content['colors']), 'frame': content['frame'], 'type': parse_type_line(content['type_line'])})

def get_tokens(content):
  related_objects = content["all_parts"]
  i = 0
  for obj in related_objects:
    if obj["object"] == "related_card" and obj["component"]  == "token":
      response = requests.get(obj["uri"])
      content = json.loads(response.content)
      image_uri = content['image_uris']['large']
      urllib.request.urlretrieve(image_uri, 'img/tokens/' + obj["name"] + "{}.jpg".format(i))
      i += 1

def main(cards_file, debug=False):
  with open(cards_file) as f:
    content = f.readlines()

  card_list = [line.rstrip('\n') for line in content]

  download_images(card_list)

  for card_name in card_list:
    print(card_name)
    process_image(card_name, debug)

main(args.cardlist, debug=args.debug)
