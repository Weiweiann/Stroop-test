# coding: utf-8
import glob
import os
import sqlite3

os.chdir("./")
imgs_dir = glob.glob('../static/img/*')

img_table =[]

for img in imgs_dir:
    image_name = img.split("/")[3].split(".")[0]
    word = image_name.split("_")[0]
    color = image_name.split("_")[1]
    img_table.append((image_name, word, color))


db = sqlite3.connect('../stroop.db')
with db:
    db.executemany(
    'INSERT INTO image(image_name, word, color) VALUES(?,?,?)',
    img_table
    )


