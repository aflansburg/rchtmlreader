import urllib.request
from bs4 import BeautifulSoup as BS
import re
import json
import csv
import datetime

# TEST URLs
# url="http://www.roughcountry.com/jeep-suspension-lift-kit-609s.html" # item with fitment
# url="http://www.roughcountry.com/neon-orange-shock-boot-87172.html" # shock boot
# url ="http://www.roughcountry.com/10-inch-x5-led-light-bar-76912.html" # item without fitment

url = 'http://www.roughcountry.com/neon-orange-shock-boot-87172.html'

writeToFile = True

def uri_cleaner(uri):

    uri_regex = r"^(.*product)\/cache.*(\/\w\/\w\/.*)"

    uri_matches = re.findall(uri_regex, uri)

    u_match = ''

    for uri_match in uri_matches:
        u_match = ''.join(uri_match)

    cleaned_uri = u_match.replace('http://cdn.roughcountry.com', 'https://d11wx52d6i5kyf.cloudfront.net')

    return cleaned_uri


with urllib.request.urlopen(url) as response:

    html = response.read()

    soup = BS(html, "html.parser")

    description = soup.find('p', {'id': 'product-description'})
    description = description.text
    description = description.replace(' Read More', '').rstrip(' ')

    print(description)

    price = soup.find('span', {'class': 'price'})
    price = price.text

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
        notes = '; '.join(notes)
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

    if 'SKU' in specs:
        itemSku = specs['SKU']
    else:
        itemSku = ''

    fitmentData = soup.find('table', {'id': 'fitment-detail'})
    fitmentDataString = str(fitmentData)
    fitmentDataString = fitmentDataString.replace("\n", "").replace("\r", "").replace("\n", "")

    # print(fitmentDataString)

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
            'SKU': itemSku,
            'Description': description,
            'Price': price,
            'Features': '; '.join(features),
            'Notes': notes,
            'Specs': specs,
            'MainImg': mainImgUrl
        }

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

            specsFlat =  []
            for k, v in content["Specs"].items():
                thisSpec = k + ': ' + v
                specsFlat.append(thisSpec)

            content["Specs"] = '; '.join(specsFlat)
            content["Fitment"] = '; '.join(content["Fitment"])

            writer.writeheader()
            writer.writerow(content)
            csvfile.close()

        ## create jobber file
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

            if len(allImages) == 1:
                jobberWriter.writerow({'MPN': content['SKU'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0]})
            if len(allImages) == 2:
                jobberWriter.writerow({'MPN': content['SKU'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1]})
            if len(allImages) == 3:
                jobberWriter.writerow({'MPN': content['SKU'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2]})
            if len(allImages) == 4:
                jobberWriter.writerow({'MPN': content['SKU'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3]})
            if len(allImages) == 5:
                jobberWriter.writerow({'MPN': content['SKU'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3], 'Image 5': allImages[4]})
            if len(allImages) == 6:
                jobberWriter.writerow({'MPN': content['SKU'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3], 'Image 5': allImages[4], 'Image 6': allImages[5]})
            if len(allImages) == 7:
                jobberWriter.writerow({'MPN': content['SKU'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3], 'Image 5': allImages[4], 'Image 6': allImages[5],
                                       'Image 7': allImages[6]})
            if len(allImages) == 8:
                jobberWriter.writerow({'MPN': content['SKU'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3], 'Image 5': allImages[4], 'Image 6': allImages[5],
                                       'Image 7': allImages[6], 'Image 8': allImages[7]})
            if len(allImages) >= 9:
                jobberWriter.writerow({'MPN': content['SKU'], 'Description': content['Description'],
                                       'Benefits': content['Features'], 'Combined Fitment': content['Fitment'],
                                       'Kit Contents': content['In The Box'], 'Technical Notes': content['Notes'],
                                       'MAP': content['Price'], 'Item Specifics': content['Specs'],
                                       'Image 1': allImages[0], 'Image 2': allImages[1], 'Image 3': allImages[2],
                                       'Image 4': allImages[3], 'Image 5': allImages[4], 'Image 6': allImages[5],
                                       'Image 7': allImages[6], 'Image 8': allImages[7], 'Image 9': allImages[8]})

            jobberCsvFile.close()

        print(f'File created: {filename}')
        print('Jobber file created: ' + jobberFilename)

        ## this section for jobber line write out
