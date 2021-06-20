# autoPinFileToPinata.py
# Automatically add and pin files to IPFS using Pinata.cloud
#
# usage : python autoPinFileToPinata.py xmlfilename.xml

import sys
import os
from os import path

sys.stdout.reconfigure(encoding='utf-8')

# Copy your Pinata API Key and Secret here
endpoint = "https://api.pinata.cloud/pinning/pinFileToIPFS"
headers = {
"pinata_api_key": "your_api_key",
"pinata_secret_api_key": "your_api_secret"}


# Parsing Parameter
if(len(sys.argv) != 2):
    print("usage: python autoPinFileToPinata.py xmlfile")
    raise SystemExit

xml_filename = sys.argv[1]

# Load XML file
import xml.etree.ElementTree as ET
print('Reading ', xml_filename, '...... ', end = '', flush= True)
with open(xml_filename, mode='r', encoding="utf-8") as xml_file:
    mytree = ET.parse(xml_file)
    myroot = mytree.getroot()
    print('Done')



def removeBracketedString(s):
    s.replace(" ", "")
    start = s.find("{")
    end = s.find("}")
    if start != -1 and end != -1:
        result = s[end+1:len(s)]
        return result
    return s

listedDict = []
# Read XML data
for item in myroot[0].iter('item'):
    itemDict = {}
    itemDict['filename'] = ''
    itemDict['hash'] = ''
    for child in item:
        tag = removeBracketedString(child.tag)
        if(tag == 'title'):
            itemDict[tag] = child.text
        if(tag == 'link'):
            itemDict[tag] = child.text
        if(tag == 'author'):
            itemDict[tag] = child.text
        if(tag == 'subtitle'):
            itemDict[tag] = child.text
        if(tag == 'image'):
            itemDict['image_href'] = child.attrib['href']
        if(tag == 'summary'):
            itemDict[tag] = child.text
        if(tag == 'enclosure'):
            itemDict['enclosure_url'] = child.attrib['url']
            itemDict['enclosure_length'] = child.attrib['length']
            itemDict['enclosure_type'] = child.attrib['type']
        if(tag == 'guid'):
            itemDict[tag] = child.text
            filename = path.basename(child.text)
            itemDict['filename'] = filename
        if(tag == 'pubDate'):
            itemDict[tag] = child.text
        if(tag == 'explicit'):
            itemDict[tag] = child.text
        if(tag == 'duration'):
            itemDict[tag] = child.text
    listedDict.append(itemDict)


import csv

# Load CSV file with the same name, if not exist, create a new one
pre, ext = path.splitext(xml_filename)
csv_filename = pre + '.csv'
if path.isfile(csv_filename):
    # Read the CSV and update our listed dictionary
    with open(csv_filename, mode='r', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            for item in listedDict:
                if(row['guid'] == item['guid']):
                    item['hash'] = row['hash']
    print('Read Successful')
else:
    # Create a new csv file
    with open(csv_filename, mode='w', encoding="utf-8") as csv_file:
        fieldnames = ['filename', 'hash', 'title', 'link', 'author', 'subtitle', 'image_href', 'summary', 'enclosure_url', 'enclosure_length', 'enclosure_type', 'guid', 'pubDate', 'explicit', 'duration']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for item in listedDict:
            print("Writing row ", item)
            writer.writerow(item)
    print('Write Successful')

import requests

# Check each record and upload
for item in listedDict:
    if(item['hash'] == ''):
        filename = item['filename']
        if path.isfile(filename):
            print('Uploading ', filename, '...... ', end = '', flush= True)
            files = {"file":open(filename, 'rb')}
            resp = requests.post(endpoint, headers=headers, files=files)
            if(resp.status_code == 200):
                print("Upload success")
                item['hash'] = resp.json()["IpfsHash"]
                # Update csv file
                with open(csv_filename, mode='w', encoding="utf-8") as csv_file:
                    fieldnames = ['filename', 'hash', 'title', 'link', 'author', 'subtitle', 'image_href', 'summary', 'enclosure_url', 'enclosure_length', 'enclosure_type', 'guid', 'pubDate', 'explicit', 'duration']
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()
                    for item in listedDict:
                        writer.writerow(item)                
            else:
                print("Upload failed: status code ", resp.status_code)
        else:
            print("File ", filename," is missing.")
    else:
        print(item['filename'], " already uploaded before")


