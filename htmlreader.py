import csv
import datetime
import json
import re
import urllib.request
import sys
import validators
from subprocess import call
from helpers import clean_directories
from helpers import uri_cleaner
from helpers import replace_unicode_quotes
from bs4 import BeautifulSoup as BS

# TEST URLs
testUrl = "http://www.roughcountry.com/rc-ford-pocket-fender-flares-f-f11511c.html" # without video
# testUrl="http://www.roughcountry.com/rc-ford-wheel-to-wheel-nerf-steps-rcf15cc.html" # with video
# testUrl ="http://www.roughcountry.com/10-inch-x5-led-light-bar-76912.html" # item without fitment

# test settings
useTestUrl = False
purgeFiles = False

if not useTestUrl:
    try:
        if validators.url(sys.argv[1]):
            url = str(sys.argv[1])
            print("Url validated...")
        else:
            print('No valid URL supplied - exiting....')
            exit(0)

    except IndexError:
        print('No URL supplied - exiting......')
        exit(0)

    videoLink = None
    insertVideo = False

    try:
        if sys.argv[2] == '-video' and sys.argv[3]:
            insertVideo = True
            videoLink = sys.argv[3]
            print('Video Link Processed!')
        elif sys.argv[2] == '-purge':
            purge = input('Are you sure you want to purge all files [Y/N]?: ')
            if purge.lower() == 'yes' or 'y' or 'ye' or 'si' or 'ja' or 'oui':
                clean_directories()
    except IndexError:
        print('No arguments supplied....')
elif useTestUrl:
    videoLink = None
    url = testUrl
    if purgeFiles:
        purge = input('Are you sure you want to purge all files [Y/N]?: ')
        if purge.lower() == 'yes' or 'y' or 'ye' or 'si' or 'ja' or 'oui':
            clean_directories()

writeToFile = True

with urllib.request.urlopen(url) as response:

    html = response.read()

    soup = BS(html, "html.parser")

    customSelector = False
    optPrice = None
    optImgUrl = None
    customNote = ''
    if soup.find('div', {'class': 'input-box'}):
        customSelector = True
        itemSku = input('OPTION SELECTOR FOUND - MANUALLY ENTER SKU: \n')
        selType = input('Is this an OPTION or a REQUIREMENT?\n')
        if selType.lower() in ['o', 'option', 'opt', 'opiton', 'opti', 'oo', 'ooo', 'optio', 'options']:
            option = input('Enter the option text:\n')
            optPrice = input('Enter the option price:\n')
            optImgUrl = input('Paste in the raw image url:\n')
            optImgUrl = uri_cleaner(optImgUrl)
        else:
            customNote = input('Enter the REQUIREMENT to append to tech notes:\n')
    elif soup.find('span', {'id': 'sku-id'}):
        itemSku = soup.find('span', {'id': 'sku-id'})
        itemSku = str(itemSku.text)
    else:
        itemSku = soup.find('span', {'itemprop': 'sku'})
        itemSku = str(itemSku.text)

    title = soup.find('h1', {'itemprop': 'name'})
    title = str(title.text)
    try:
        title = title + ' ' + option
    except NameError:
        print('No custom options/requirements found')

    description = soup.find('p', {'id': 'product-description'})
    if description is not None:
        description = description.text
        description = description.replace(' Read More', '').rstrip(' ')
        description = replace_unicode_quotes(description)
    else:
        description = title

    if optPrice is not None:
        price = optPrice
    else:
        price = soup.find('span', {'class': 'price'})
        price = str(price.text)
        price = price.replace('\n', '').replace(' ', '').replace('$', '').replace('>', '').replace('<', '')

    if optImgUrl is not None:
        mainImgUrl = uri_cleaner(optImgUrl)
    else:
        mainImg = soup.find('img', {'id': 'image-main'})
        mainImg = str(mainImg)
        mainImgRe = r"\ssrc=\"(.*)\"\stitle"
        mainImgMatch = re.findall(mainImgRe, mainImg)
        mainImgUrl = uri_cleaner(mainImgMatch[0])

    # find all images
    imageSoup = soup.find_all('a', {'class': 'thumb-link'})
    allImages = []

    for thumb in imageSoup:
        img = str(thumb)
        img = img.replace('\n', '')
        imgRe = r"http.*.jpg"
        imgM = re.findall(imgRe, img)
        img = imgM[0]
        img = uri_cleaner(img)
        allImages.append(img)

    # find video link
    allVids = []
    videoSoup = soup.find_all('a', {'id': 'media-vid-0'})

    if len(videoSoup) > 0:
        for vid in videoSoup:
            videoLink = vid['href']
            vidImg = vid.find_all('img')
            vidImg = uri_cleaner(vidImg[0]['src'])

    featureData = []

    for ultag in soup.find_all('ul', {'class': 'bullet-list features'}):
        featureData.append(ultag.text)

    features = list(filter(None, featureData[0].split('\n')))
    features = [i.strip(' ') for i in features]

    if len(featureData) > 1:
        notes = list(filter(None, featureData[1].split('\n')))
        notes = [i.strip(' ') for i in notes]
        notes = [i.strip('<li>') for i in notes]
        notes = [i.strip('</li>') for i in notes]
        if customSelector and customNote != '':
            notes.append(f'Fits models with {customNote} ONLY!')
        notes = '; '.join(notes)
    elif len(featureData) == 1 and customSelector:
        notes = f'Fits models with {customNote} ONLY!'
    else:
        notes = ''

    specData = []

    for prodAttr in soup.find_all('div', {'class': 'product-specs'}):
        specData.append(prodAttr.text)

    specs = list(filter(None, specData[0].split('\n')))
    if "decorateTable('product-attribute-specs-table')" in specs:
        specs.remove("decorateTable('product-attribute-specs-table')")

    spec_keys = specs[0::2]
    spec_values = specs[1::2]

    spec_values = [s.replace('\"', "-in") for s in spec_values]

    specs = {}

    v = 0

    for i in spec_keys:
        specs[f'{i}'] = spec_values[v]
        v += 1

    fitmentData = soup.find('table', {'id': 'fitment-detail'})
    fitmentDataString = str(fitmentData)
    fitmentDataString = fitmentDataString.replace("\n", "").replace("\r", "").replace("\n", "")

    regex = r"<tbody>.*<\/tbody>"

    fitMatches = re.findall(regex, fitmentDataString)

    fitments = []
    m = None
    for match in fitMatches:
        m = match.replace("<tbody>", "").replace("<tr>", "").replace("<td>", "").replace("</td>", " ")
    if m is not None:
        if m.find('</tr><td colspan="4">'):
            n = m.split('</tr><td colspan="4">')
            n = [i.replace(' </tr> </tbody>', '') for i in n]
            for fitmentRow in n:
                fitments.append(fitmentRow)
            fitments = [f.rstrip(' ') for f in fitments]
        else:
            fitments.append(m)

    fitments = [fitment.replace('<td colspan="4">', '') for fitment in fitments]
    fitments = [fitment.replace(' </tr>', '; ') for fitment in fitments]

    boxItemsOnly = []
    front = []
    rear = []
    shock = []
    body = []

    for boxItem in soup.find_all('ul', {'id': 'box-contents'}):
        boxItemsOnly.append(boxItem.text)

    if len(boxItemsOnly) >= 1:
        boxContents = list(filter(None, boxItemsOnly[0].split('\n')))
        boxContents = [i.strip(' ') for i in boxContents]
    else:
        for frontComponent in soup.find_all('ul', {'class': 'bullet-list', 'id': 'front'}):
            front.append(frontComponent.text)
        for rearComponent in soup.find_all('ul', {'class': 'bullet-list', 'id': 'rear'}):
            rear.append(rearComponent.text)
        for shockComponent in soup.find_all('ul', {'class': 'bullet-list', 'id': 'shocks'}):
            shock.append(shockComponent.text)
        for bodyComponent in soup.find_all('ul', {'class': 'bullet-list', 'id': 'body'}):
            body.append(bodyComponent.text)

    try:
        boxContents
    except NameError:
        boxContents = {}
        if len(front) != 0:
            front = list(filter(None, front[0].split('\n')))
            boxContents['Front'] = front
        if len(rear) != 0:
            rear = list(filter(None, rear[0].split('\n')))
            boxContents['Rear'] = rear
        if len(shock) != 0:
            shock = list(filter(None, shock[0].split('\n')))
            boxContents['Shocks'] = shock
        if len(body) != 0:
            body = list(filter(None, body[0].split('\n')))
            boxContents['Body'] = body

    if fitments is not None:
        content = {
            'Title': title,
            'SKU': itemSku,
            'Description': description,
            'Price': price,
            'Features': '; '.join(features),
            'Notes': notes,
            'Specs': specs,
            'Fitment': fitments,
            'In The Box': boxContents,
            'MainImg': mainImgUrl
        }
    elif boxContents is not None:
        content = {
            'Title': title,
            'SKU': itemSku,
            'Description': description,
            'Price': price,
            'Features': '; '.join(features),
            'Notes': notes,
            'Specs': specs,
            'In The Box': boxContents,
            'MainImg': mainImgUrl
        }
    else:
        content = {
            'Title': title,
            'SKU': itemSku,
            'Description': description,
            'Price': price,
            'Features': '; '.join(features),
            'Notes': notes,
            'Specs': specs,
            'MainImg': mainImgUrl
        }

    if videoLink:
        content['video_link'] = videoLink

    delKV = [k for k, v, in content.items() if v is None]
    for k in delKV:
        del content[k]

    picCount = 0
    for pic in allImages:
        picCount += 1
        keyStr = f'Image {picCount}'
        content[keyStr] = pic

    # at this point 'content' is a well structured JSON-type dict that could be exported
    print(json.dumps(content, sort_keys=True, indent=4))

    if writeToFile:

        fieldnames = []

        for k, v in content.items():
            fieldnames.append(k)

        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        fileLocation = 'C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files\\csv\\'

        if itemSku != '':
            filename = fileLocation + itemSku + '.csv'
        else:
            filename = fileLocation + 'Item_' + now + '.csv'

        try:
            open(filename, "r+")
        except FileNotFoundError:
            print("File doesn't exist. Continuing....")
        except PermissionError:
            filename = fileLocation + itemSku + '_' + now + '.csv'

        # create csv for generating templates
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            kitLoc = ['Front', 'Rear', 'Body', 'Shocks']

            if any(k in content["In The Box"] for k in kitLoc):
                allItems = []
                for loc, val in content["In The Box"].items():
                    individuals = []
                    for v in val:
                        individuals.append(v)
                    individuals = [i.rstrip(' ') for i in individuals]
                    allItems.append(str(loc).upper() + ": " + ', '.join(individuals))
                content["In The Box"] = '; '.join(allItems)
            else:
                content["In The Box"] = ', '.join(content["In The Box"])

            specsFlat = []
            for k, v in content["Specs"].items():
                thisSpec = k + ': ' + v
                specsFlat.append(thisSpec)

            content["Specs"] = '; '.join(specsFlat)
            content["Fitment"] = '; '.join(content["Fitment"])

            writer.writeheader()
            writer.writerow(content)
            csvfile.close()

        if type(content['Notes']) == list:
            for note in content['Notes']:
                note.replace('<u>', '')
                note.replace('</u>', '')
        else:
            content['Notes'].replace('<u>', '')
            content['Notes'].replace('</u>', '')

        # create jobber file
        jobberFileLocation = 'C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files\\jobber_lines\\'
        if itemSku != '':
            jobberFilename = jobberFileLocation + itemSku + '_jobber.csv'
        else:
            jobberFilename = jobberFileLocation + 'Item_' + now + '_jobber.csv'

        try:
            open(jobberFilename, "r+")
        except FileNotFoundError:
            print("File doesn't exist. Continuing....")
        except PermissionError:
            jobberFilename = jobberFileLocation + itemSku + '_' + now + '_jobber.csv'

        jobberFields = ['MPN', 'Item Type', 'MAP', 'Discount %', 'Your Cost', 'Title',
                        'Strut/Shock Series', 'Start Year', 'End Year', 'Make',
                        'Model', 'Drive', 'Combined Fitment', 'Description', 'Kit Contents',
                        'Benefits', 'Technical Notes', 'Item Specifics', 'Weight (Lbs)',
                        'US Shipping', 'CAN Shipping', 'Image 1', 'Image 2', 'Image 3', 'Image 4',
                        'Image 5', 'Image 6', 'Image 7', 'Image 8', 'Image 9', 'Superseded', 'Warranty',
                        'UPC Code', 'Flat Discount %']
        
        with open(jobberFilename, 'w', newline='') as jobberCsvFile:
            jobberWriter = csv.DictWriter(jobberCsvFile, fieldnames=jobberFields)

            jobberWriter.writeheader()

            if len(allImages) == 0 and content['MainImg']:
                jobberWriter.writerow({'MPN': content['SKU'], 'Title': content['Title'],'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': content['MainImg']})
            if len(allImages) == 1:
                jobberWriter.writerow({'MPN': content['SKU'], 'Title': content['Title'],'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0]})
            if len(allImages) == 2:
                jobberWriter.writerow({'MPN': content['SKU'], 'Title': content['Title'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1]})
            if len(allImages) == 3:
                jobberWriter.writerow({'MPN': content['SKU'], 'Title': content['Title'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2]})
            if len(allImages) == 4:
                jobberWriter.writerow({'MPN': content['SKU'], 'Title': content['Title'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3]})
            if len(allImages) == 5:
                jobberWriter.writerow({'MPN': content['SKU'], 'Title': content['Title'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3], 'Image 5': allImages[4]})
            if len(allImages) == 6:
                jobberWriter.writerow({'MPN': content['SKU'], 'Title': content['Title'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3], 'Image 5': allImages[4], 'Image 6': allImages[5]})
            if len(allImages) == 7:
                jobberWriter.writerow({'MPN': content['SKU'], 'Title': content['Title'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3], 'Image 5': allImages[4], 'Image 6': allImages[5],
                                       'Image 7': allImages[6]})
            if len(allImages) == 8:
                jobberWriter.writerow({'MPN': content['SKU'], 'Title': content['Title'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3], 'Image 5': allImages[4], 'Image 6': allImages[5],
                                       'Image 7': allImages[6], 'Image 8': allImages[7]})
            if len(allImages) >= 9:
                jobberWriter.writerow({'MPN': content['SKU'], 'Title': content['Title'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3], 'Image 5': allImages[4], 'Image 6': allImages[5],
                                       'Image 7': allImages[6], 'Image 8': allImages[7], 'Image 9': allImages[8]})

            jobberCsvFile.close()

        ## create amzFile file
        amzFileFileLocation = 'C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files\\amzFiles\\'
        if itemSku != '':
            amzFileFilename = amzFileFileLocation + itemSku + '_amzFile.csv'
        else:
            amzFileFilename = amzFileFileLocation + 'Item_' + now + '_amzFile.csv'
        
        try:
            open(amzFileFilename, "r+")
        except FileNotFoundError:
            print("File doesn't exist. Continuing....")
        except PermissionError:
            amzFileFilename = amzFileFileLocation + itemSku + '_' + now + '_amzFile.csv'

        amzFileFields = ['item_sku', 'item_name', 'part_number', 'standard_price', 'main_image_url', 'other_image_url1',
                         'other_image_url2', 'other_image_url3', 'product_description', 'bullet_point1', 'bullet_point2',
                         'bullet_point3', 'bullet_point4', 'bullet_point5']

        with open(amzFileFilename, 'w', newline='') as amzFileCsvFile:
            amzFileWriter = csv.DictWriter(amzFileCsvFile, fieldnames=amzFileFields)

            amzFileWriter.writeheader()

            if len(allImages) == 0:
                amzFileWriter.writerow({'item_sku': content['SKU'], 'product_description': content['Description'],
                                        'item_name': content['Title'], 'bullet_point1': 'Features: ' +
                                        content['Features'], 'bullet_point2': 'Fits: ' + content['Fitment'],
                                       'bullet_point4': 'Kit Contents: ' + content['In The Box'],
                                        'part_number': content['SKU'], 'bullet_point3': 'Notes: ' + content['Notes'],
                                        'standard_price': content['Price'], 'bullet_point5': 'Specs: ' +
                                        content['Specs'], 'main_image_url': content['MainImg']})

            if len(allImages) == 1:
                amzFileWriter.writerow({'item_sku': content['SKU'], 'product_description': content['Description'],
                                        'item_name': content['Title'], 'bullet_point1': 'Features: ' +
                                        content['Features'], 'bullet_point2': 'Fits: ' + content['Fitment'],
                                       'bullet_point4': 'Kit Contents: ' + content['In The Box'],
                                        'part_number': content['SKU'], 'bullet_point3': 'Notes: ' + content['Notes'],
                                        'standard_price': content['Price'], 'bullet_point5': 'Specs: ' +
                                        content['Specs'], 'main_image_url': allImages[0]})
            if len(allImages) == 2:
                amzFileWriter.writerow({'item_sku': content['SKU'], 'product_description': content['Description'],
                                        'item_name': content['Title'], 'bullet_point1': 'Features: ' +
                                        content['Features'], 'bullet_point2': 'Fits: ' + content['Fitment'],
                                       'bullet_point4': 'Kit Contents: ' + content['In The Box'],
                                        'part_number': content['SKU'], 'bullet_point3': 'Notes: ' + content['Notes'],
                                        'standard_price': content['Price'], 'bullet_point5': 'Specs: ' +
                                        content['Specs'], 'main_image_url': allImages[0],
                                        'other_image_url1': allImages[1]})
            if len(allImages) == 3:
                amzFileWriter.writerow({'item_sku': content['SKU'], 'product_description': content['Description'],
                                        'item_name': content['Title'], 'bullet_point1': 'Features: ' +
                                        content['Features'], 'bullet_point2': 'Fits: ' + content['Fitment'],
                                       'bullet_point4': 'Kit Contents: ' + content['In The Box'],
                                        'part_number': content['SKU'], 'bullet_point3': 'Notes: ' + content['Notes'],
                                        'standard_price': content['Price'], 'bullet_point5': 'Specs: ' +
                                        content['Specs'], 'main_image_url': allImages[0],
                                        'other_image_url1': allImages[1], 'other_image_url2': allImages[2]})
            if len(allImages) >= 4:
                amzFileWriter.writerow({'item_sku': content['SKU'], 'product_description': content['Description'],
                                        'item_name': content['Title'], 'bullet_point1': 'Features: ' +
                                        content['Features'], 'bullet_point2': 'Fits: ' + content['Fitment'],
                                       'bullet_point4': 'Kit Contents: ' + content['In The Box'],
                                        'part_number': content['SKU'], 'bullet_point3': 'Notes: ' + content['Notes'],
                                        'standard_price': content['Price'], 'bullet_point5': 'Specs: ' +
                                        content['Specs'], 'main_image_url': allImages[0],
                                        'other_image_url1': allImages[1], 'other_image_url2': allImages[2],
                                        'other_image_url3': allImages[3]})

            amzFileCsvFile.close()
        

        print(f'File created: {filename}')
        print('Jobber file created: ' + jobberFilename)
        print('Amazon file created: ' + amzFileFilename)

        call(["node", "C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\WebstormProjects\\template_builder\\maketemplate.js", filename])

        # generating SC new prod row
        if (content['SKU']):
            eTemp = open('C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files\\templates\\ebay_desc-' +
                         itemSku + '.html', 'r')
            ebayTemplate = eTemp.read()
            eTemp.close()

            aTemp = open('C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files\\templates\\amz_desc-' +
                         itemSku + '.html', 'r')
            amazonTemplate = aTemp.read()
            aTemp.close()

            wTemp = open('C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files\\walmartFiles\\wal_desc_' +
                         itemSku + '.html', 'r')
            walmartDesc = wTemp.read()
            wTemp.close()

            wTemp = open('C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files\\walmartFiles\\wal_shelf_' +
                         itemSku + '.html', 'r')
            walmartShelf = wTemp.read()
            wTemp.close()

            wTemp = open('C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files\\walmartFiles\\wal_short_' +
                         itemSku + '.html', 'r')
            walmartShort = wTemp.read()
            wTemp.close()

            scFieldnames = ['results', 'product custom sku', 'warehouse id', 'model number', 'product name',
                            'product weight', 'upc', 'asin', 'manufacturer', 'msrp', 'eBay Description',
                            'walmart description', 'walmart attr:shelf description', 'walmart attr:short description',
                            'walmart attr:brand', 'taxable', 'warehouse name', 'qty', 'product weight',
                            'product attribute:multifitment', 'product attribute:warranty',
                            'product attribute:superseded', 'product attribute:type', 'product attribute:height',
                            'image file', 'alternate image file 1', 'alternate image file 2', 'alternate image file 3',
                            'alternate image file 4', 'alternate image file 5', 'alternate image file 6',
                            'alternate image file 7', 'alternate image file 8', 'alternate image file 9']

            # may or may not need these later
            ''', 'walmart attr:Shipping Override-Is Shipping Allowed (#1)',
                            'walmart attr:Shipping Override-Ship Region (#1)',
                            'walmart attr:Shipping Override-Ship Method (#1)',
                            'walmart attr:Shipping Override-Ship Price (#1)',
                            'walmart attr:Shipping Override-Is Shipping Allowed (#2)',
                            'walmart attr:Shipping Override-Ship Region (#2)',
                            'walmart attr:Shipping Override-Ship Method (#2)',
                            'walmart attr:Shipping Override-Ship Price (#2)'''

            scFileLoc = 'C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files\\sc-line\\'

            if itemSku != '':
                scFilename = scFileLoc + itemSku + '_sc-line.csv'
            else:
                scFilename = scFileLoc + 'Item_' + now + '_sc-line.csv'

            try:
                open(scFilename, "r+")
            except FileNotFoundError:
                print("File doesn't exist. Continuing....")
            except PermissionError:
                scFilename = scFileLoc + itemSku + '_' + now + '_sc-line.csv'

            with open(scFilename, 'w', newline='') as scFile:
                scFileWriter = csv.DictWriter(scFile, fieldnames=scFieldnames)

                scFileWriter.writeheader()

                # map to the appropriate keys/field names
                scRowData = {}

                if (content['SKU']):
                    scRowData['product custom sku'] = content['SKU']
                    scRowData['warehouse id'] = content['SKU']
                    scRowData['model number'] = content['SKU']
                if (content['Title']):
                    scRowData['product name'] = content['SKU'] + ' - ' + content['Title']
                if (content['Price']):
                    scRowData['msrp'] = content['Price']
                if ebayTemplate:
                    scRowData['eBay Description'] = ebayTemplate
                scRowData['walmart attr:brand'] = 'Rough Country'
                if walmartDesc: # need split up
                    scRowData['walmart description'] = walmartDesc
                if walmartShelf:
                    scRowData['walmart attr:shelf description'] = walmartShelf
                if walmartShort:
                    scRowData['walmart attr:short description'] = walmartShort
                if content['MainImg']:
                    scRowData['image file'] = content['MainImg']
                if allImages:
                    scImages = allImages
                    if scRowData:
                        if content['MainImg'] in scImages:
                            scImages.remove(content['MainImg'])
                    for sImg in scImages:
                        imgKey = scImages.index(sImg) + 1
                        imgKeyStr = 'alternate image file ' + str(imgKey)
                        scRowData[imgKeyStr] = sImg
                scRowData['taxable'] = 'Yes'
                scRowData['warehouse name'] = 'Rough Country'
                scRowData['manufacturer'] = 'Rough Country'

                scFileWriter.writerow(scRowData)
            scFile.close()

        else:
            print('due to file name issues, the SC template cannot be automatically generated')