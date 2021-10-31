#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import tkinter as tk
import tkinter.filedialog
#import xml.etree.ElementTree as ET
from lxml import etree

import imdb
import pandas as pd


root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

folder = tk.filedialog.askdirectory(parent=root, title='Choose folder to generate NFO files')

ia = imdb.IMDb()

series = ia.search_movie(os.path.basename(folder))[0]
ia.update(series, 'episodes')

se_expr = re.compile(r'S(?P<season>\d+)E(?P<episode>\d+)', flags=re.IGNORECASE)

for path, dirs, files in os.walk(folder):
    for file in files:
        base, ext = os.path.splitext(file)
        if ext.lower() in ('.ts', '.mpg', '.mp4', '.mkv'):
            nfo_file = os.path.join(path, f'{base:s}.nfo')
            if not os.path.exists(nfo_file):
                se = se_expr.search(file)
                season = int(se.group('season'))
                episode = int(se.group('episode'))
                try:
                    info = series['episodes'][season][episode]
                except KeyError:
                    continue
                xml_data = etree.Element('episodedetails')
                xml_title = etree.SubElement(xml_data, 'title')
                xml_title.text = info['title']
                try:
                    air_date = info['original air date']
                    xml_aired = etree.SubElement(xml_data, 'aired')
                    xml_aired.text = pd.to_datetime(air_date).strftime('%Y-%m-%d')
                except KeyError:
                    pass
                xml_season = etree.SubElement(xml_data, 'season')
                xml_season.text = str(season)
                xml_episode = etree.SubElement(xml_data, 'episode')
                xml_episode.text = str(episode)
                xml_plot = info['plot'].strip()
                xml_id = etree.SubElement(xml_data, 'uniqueid')
                xml_id.set('type', 'imdb')
                xml_id.text = f'tt{info.movieID:s}'
                with open(nfo_file, mode='wb') as xml_file:
                    xml_file.write(etree.tostring(xml_data, encoding='utf-8', pretty_print=True,
                                                  xml_declaration=True, standalone=True))
