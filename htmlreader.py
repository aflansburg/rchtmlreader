import pprint
import os
import csv
import datetime
import re
import urllib.request
import urllib.error
from subprocess import call
import helpers
import creators
from bs4 import BeautifulSoup as bS
from cli_augments import ConsoleColors as cColors

base_dir = ''
ws_dir = ''
sc_dir = ''
j_dir = ''
amz_dir = ''
gen_dir = ''
csv_dir = ''
dir_slash = ''

if os.name == "posix":
    base_dir = '/Users/abram/Dropbox/Business/Rough Country/'
    ws_dir = 'WebstormProjects/template_builder/'
    sc_dir = 'generated_files/sc-line/'
    j_dir = 'generated_files/jobber_lines/'
    amz_dir = 'generated_files/amzFiles/'
    temp_dir = 'generated_files/templates/'
    wm_dir = 'generated_files/walmartFiles/'
    csv_dir = 'generated_files/csv/'
    gen_dir = 'generated_files/'
    dir_slash = '/'

elif os.name == "nt":
    base_dir = 'C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\'
    ws_dir = 'WebstormProjects\\template_builder\\'
    sc_dir = 'generated_files\\sc-line\\'
    j_dir = 'generated_files\\jobber_lines\\'
    amz_dir = 'generated_files\\amzFiles\\'
    temp_dir = 'generated_files\\templates\\'
    wm_dir = 'generated_files\\walmartFiles\\'
    csv_dir = 'generated_files\\csv\\'
    gen_dir = 'generated_files\\'
    dir_slash = '\\'

pp = pprint.PrettyPrinter(indent=4)


def read_page(arg, opts):
    write_to_file = True
    append_to_file = False
    weight = ''
    upc = ''
    video_link = ''

    # need to fix this implementation
    if opts is not None:
        if type(opts) == bool:
            if opts:
                append_to_file = True
    if type(arg) == dict:
        url = arg['URL']
        upc = arg['UPC']
        weight = arg['Weight']
        video_link = arg['Video Link']
    else:
        url = arg

    try:
        with urllib.request.urlopen(url) as response:

            html = response.read()

            soup = bS(html, "html.parser")

            custom_selector = False
            opt_price = None
            opt_img_url = None
            custom_note = ''
            option = None
            print(f'\nCurrent url: {url}')
            if soup.find('div', {'class': 'input-box'}):
                custom_selector = True
                item_sku = input(cColors.WARNING + '\nDROP DOWN SELECTOR FOUND - MANUALLY ENTER SKU: \n' + cColors.ENDC)
                sel_type = input(cColors.WARNING + '\nIs this an OPTION or a REQUIREMENT?\n' + cColors.ENDC)
                if sel_type.lower() in ['o', 'option', 'opt', 'opiton', 'opti', 'oo', 'ooo', 'optio', 'options', 'op',
                                        'otp']:
                    option = input(cColors.WARNING + '\nEnter the option text:\n' + cColors.ENDC) # not currently used
                    opt_price = input(cColors.WARNING + '\nEnter the option price:\n' + cColors.ENDC)
                    opt_img_url = input(cColors.WARNING + '\nPlease paste in the raw image url:\n' + cColors.ENDC)
                    opt_img_url = helpers.uri_cleaner(opt_img_url)
                else:
                    custom_note = input(cColors.WARNING + 'Enter the REQUIREMENT to append to tech notes:\n' + cColors.ENDC)
                    opt_price = input(cColors.WARNING + '\nEnter the option price:\n' + cColors.ENDC)
                    opt_img_url = input(cColors.WARNING + '\nPlease paste in the raw image url:\n' + cColors.ENDC)
                    opt_img_url = helpers.uri_cleaner(opt_img_url)
            elif soup.find('span', {'id': 'sku-id'}):
                item_sku = soup.find('span', {'id': 'sku-id'})
                item_sku = str(item_sku.text)
            elif soup.find('span', {'itemprop': 'sku'}):
                item_sku = soup.find('span', {'itemprop': 'sku'})
                if item_sku is not None:
                    item_sku = str(item_sku.text)
                else:
                    item_sku = input(cColors.WARNING + '\nPlease input the item SKU: ' + cColors.ENDC)
            else:
                item_sku = input(cColors.WARNING + '\nCOULD NOT LOCATE SKU - MANUALLY ENTER SKU: \n' + cColors.ENDC)

            title = soup.find('h1', {'itemprop': 'name'})
            title = str(title.text)

            description = soup.find('p', {'id': 'product-description'})
            if description is not None:
                description = description.text
                description = description.replace(' Read More', '').rstrip(' ')
                description = helpers.replace_unicode_quotes(description)
            else:
                description = title

            description = description.replace("\n", "")

            if opt_price is not None:
                price = opt_price
            else:
                price = soup.find('span', {'class': 'price'})
                price = str(price.text)
                price = price.replace('\n', '').replace(' ', '').replace('$', '').replace('>', '').replace('<', '')

            if opt_img_url is not None:
                main_img_url = opt_img_url
                # all_images = []
                print(cColors.WARNING + '\nDue to options requirements - only main image will be processed - make sure'
                                        'to add any desired additional photos manually.')

            all_images = []

            # find all images
            image_soup = soup.find('div', {'class': 'product-image-gallery'})
            # image_soup = soup.find_all('a', {'class': 'thumb-link'})
            for child in image_soup.children:
                if child.name == 'img':
                    if child.attrs['id'] == 'image-main' and opt_img_url is None:
                        main_img_url = helpers.uri_cleaner(child.attrs['src'])
                    else:
                        cl_img = helpers.uri_cleaner(child.attrs['src'])
                        if cl_img not in all_images:
                            all_images.append(cl_img)

            # for thumb in image_soup:
            #     img = str(thumb)
            #     img = img.replace('\n', '')
            #     img_re = r"http.*.jpg"
            #     img_m = re.findall(img_re, img)
            #     if len(img_m) > 0:
            #         img = img_m[0]
            #         img = helpers.uri_cleaner(img)
            #         if img != main_img_url and img.replace(".jpg", "") not in main_img_url:
            #             # overly complex img url filtering
            #             # main_match = re.search(img_dupe_re, main_img_url)
            #             # print(main_match[0])
            #             # dmatch = re.search(img_dupe_re, img)
            #             # print(dmatch[0])
            #             # if main_match[0].replace(".", "") + "_1" != dmatch[0].replace(".", "") and \
            #             #        main_match[0] != dmatch[0]:
            #             if 'base_1' not in img:
            #                 all_images.append(img)

            if len(all_images) > 0:
                all_images = helpers.check_imagelinks(all_images)

            # find video link -- this doesn't appear to be fully implemented yet....
            all_vids = []
            video_soup = soup.find_all('a', {'id': 'media-vid-0'})

            if len(video_soup) > 0:
                for vid in video_soup:
                    video_link = vid['href']
                    vid_img = vid.find_all('img')
                    vid_img = helpers.uri_cleaner(vid_img[0]['src'])

            feature_data = []
            notes_data = []

            for ultag in soup.find_all('ul', {'class': 'bullet-list features'}):
                if ultag.parent['class'] == ['features-container']:
                    feature_data.append(ultag.text)
                elif ultag.parent['class'] == ['notes-container']:
                    print(ultag.text)
                    notes_data.append(ultag.text)

            if len(feature_data) > 0:
                features = list(filter(None, feature_data[0].split('\n')))
                features = [i.strip(' ') for i in features]

            else:
                features = []

            if custom_selector and option != '' and option is not None:
                features.append(option)

            if len(notes_data) > 0:
                notes = list(filter(None, notes_data[0].split('\n')))
                notes = [i.strip(' ') for i in notes]
                notes = [i.strip('<li>') for i in notes]
                notes = [i.strip('</li>') for i in notes]
                if custom_selector and custom_note != '':
                    notes.append(f'Fits models with {custom_note} ONLY!')
                notes = '; '.join(notes)
            elif len(notes_data) == 0 and custom_selector and custom_note is not None and custom_note != "":
                notes = f'Fits models with {custom_note} ONLY!'
            else:
                notes = ''

            spec_data = []

            for prodAttr in soup.find_all('div', {'class': 'product-specs'}):
                spec_data.append(prodAttr.text)

            specs = list(filter(None, spec_data[0].split('\n')))
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

            fitment_data = soup.find('table', {'id': 'fitment-detail'})
            fitment_data_string = str(fitment_data)
            fitment_data_string = fitment_data_string.replace("\n", "").replace("\r", "").replace("\n", "")

            regex = r"<tbody>.*<\/tbody>"

            fit_matches = re.findall(regex, fitment_data_string)

            fitments = []
            m = None
            for match in fit_matches:
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

            box_items_only = []
            front = []
            rear = []
            shock = []
            body = []

            for boxItem in soup.find_all('ul', {'id': 'box-contents'}):
                box_items_only.append(boxItem.text)

            if len(box_items_only) >= 1:
                box_contents = list(filter(None, box_items_only[0].split('\n')))
                box_contents = [i.strip(' ') for i in box_contents]
                if option is not None or option != "":
                    box_items_only.append(option)
            else:
                for frontComponent in soup.find_all('ul', {'class': 'bullet-list', 'id': 'front'}):
                    front.append(frontComponent.text)
                for rearComponent in soup.find_all('ul', {'class': 'bullet-list', 'id': 'rear'}):
                    rear.append(rearComponent.text)
                for shockComponent in soup.find_all('ul', {'class': 'bullet-list', 'id': 'shocks'}):
                    shock.append(shockComponent.text)
                for bodyComponent in soup.find_all('ul', {'class': 'bullet-list', 'id': 'body'}):
                    body.append(bodyComponent.text)

            # this is unused for some reason
            # opt_price_regex = re.compile('.*\[\+\$\d+\]')
            # opt_optional_regex = re.compile('.*Optional.*')

            try:
                box_contents
            except NameError:
                box_contents = {}
                if len(front) != 0:
                    front = list(filter(None, front[0].split('\n')))
                    box_contents['Front'] = front
                if len(rear) != 0:
                    rear = list(filter(None, rear[0].split('\n')))
                    box_contents['Rear'] = rear
                if len(shock) != 0:
                    shock = list(filter(None, shock[0].split('\n')))
                    box_contents['Shocks'] = shock
                if len(body) != 0:
                    body = list(filter(None, body[0].split('\n')))
                    box_contents['Body'] = body

            if fitments is not None:
                content = {
                    'Title': title,
                    'SKU': item_sku,
                    'Description': description,
                    'Price': price,
                    'Features': '; '.join(features).replace('.', ''),
                    'Notes': notes,
                    'Specs': specs,
                    'Fitment': fitments,
                    'In The Box': box_contents,
                    'MainImg': main_img_url,
                    'Weight': weight,
                    'UPC': upc
                }
            elif box_contents is not None:
                content = {
                    'Title': title,
                    'SKU': item_sku,
                    'Description': description,
                    'Price': price,
                    'Features': '; '.join(features),
                    'Notes': notes,
                    'Specs': specs,
                    'In The Box': box_contents,
                    'MainImg': main_img_url,
                    'Weight': weight,
                    'UPC': upc
                }
            else:
                content = {
                    'Title': title,
                    'SKU': item_sku,
                    'Description': description,
                    'Price': price,
                    'Features': '; '.join(features),
                    'Notes': notes,
                    'Specs': specs,
                    'MainImg': main_img_url,
                    'Weight': weight,
                    'UPC': upc
                }

            if video_link is not None:
                content['video_link'] = video_link
            else:
                content['video_link'] = ''

            del_k_v = [k for k, v, in content.items() if v is None]
            for k in del_k_v:
                del content[k]

            pic_count = 0
            for pic in all_images:
                pic_count += 1
                key_str = f'Image {pic_count}'
                content[key_str] = pic

            if write_to_file:

                fieldnames = []

                for k, v in content.items():
                    fieldnames.append(k)

                now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

                file_location = base_dir + csv_dir

                if item_sku != '' and append_to_file is False:
                    filename = file_location + item_sku + '.csv'
                elif not append_to_file:
                    filename = file_location + 'multi-file.csv'
                else:
                    filename = file_location + 'Item_' + now + '.csv'

                try:
                    open(filename, "r+")
                except FileNotFoundError:
                    print(cColors.WARNING + "\nMaster csv doesn't exist. Creating...." + cColors.ENDC)
                except PermissionError:
                    filename = file_location + item_sku + '_' + now + '.csv'

                # create csv for generating templates
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    kit_loc = ['Front', 'Rear', 'Body', 'Shocks']

                    if any(k in content["In The Box"] for k in kit_loc):
                        all_items = []
                        for loc, val in content["In The Box"].items():
                            individuals = []
                            for v in val:
                                individuals.append(v)
                            individuals = [i.rstrip(' ') for i in individuals]
                            all_items.append(str(loc).upper() + ": " + ', '.join(individuals))
                        content["In The Box"] = '; '.join(all_items)
                    else:
                        if len(content["In The Box"]) > 1:
                            content["In The Box"] = ', '.join(content["In The Box"])
                        elif len(content["In The Box"]) == 1:
                            content["In The Box"] = content["In The Box"][0]

                    specs_flat = []
                    for k, v in content["Specs"].items():
                        this_spec = k + ': ' + v
                        specs_flat.append(this_spec)

                    content["Specs"] = '; '.join(specs_flat)
                    content["Fitment"] = '; '.join(content["Fitment"])

                    # if not append_to_file:
                    #     writer.writeheader()
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

                # create jobber
                creators.create_jobber(content, all_images)

                if append_to_file:
                    creators.append_amazon(content)
                else:
                    # create Amazon-friendly upload CSV file
                    creators.create_amazon(content, all_images)

                pp.pprint(content)
                print('\n')

                call(["node", base_dir + ws_dir + "maketemplate.js", filename])

                # generating SC new prod row
                if content['SKU']:
                    e_temp = open(base_dir + temp_dir + 'ebay_desc-' +
                                  item_sku + '.html', 'r')
                    ebay_template = e_temp.read()
                    e_temp.close()

                    a_temp = open(base_dir + temp_dir + 'amz_desc-' +
                                  item_sku + '.html', 'r')
                    # unused because SC does not upload to AMZ currently (for many reasons)
                    # amazon_template = a_temp.read()
                    # a_temp.close()

                    w_temp = open(base_dir + wm_dir + 'wal_desc_' +
                                  item_sku + '.html', 'r')
                    walmart_desc = w_temp.read()
                    w_temp.close()

                    w_temp = open(base_dir + wm_dir + 'wal_shelf_' +
                                  item_sku + '.html', 'r')
                    walmart_shelf = w_temp.read()
                    w_temp.close()

                    w_temp = open(base_dir + wm_dir + 'wal_short_' +
                                  item_sku + '.html', 'r')
                    walmart_short = w_temp.read()
                    w_temp.close()

                    sc_fieldnames = ['results', 'product custom sku', 'warehouse id', 'model number', 'product name',
                                     'product attribute:base_pn', 'upc', 'asin', 'manufacturer', 'msrp', 'eBay '
                                                                                                         'Description',
                                     'walmart description', 'walmart attr:shelf description',
                                     'walmart attr:short description',
                                     'walmart attr:brand', 'taxable', 'warehouse name', 'qty', 'product weight',
                                     'product attribute:multifitment', 'product attribute:warranty',
                                     'product attribute:superseded', 'product attribute:type', 'product '
                                                                                               'attribute:height',
                                     'image file', 'alternate image file 1', 'alternate image file 2',
                                     'alternate image file 3',
                                     'alternate image file 4', 'alternate image file 5', 'alternate image file 6',
                                     'alternate image file 7', 'alternate image file 8', 'alternate image file 9',
                                     'walmart attr:Shipping Override-Is Shipping Allowed (#1)',
                                     'walmart attr:Shipping Override-Ship Region (#1)',
                                     'walmart attr:Shipping Override-Ship Method (#1)',
                                     'walmart attr:Shipping Override-Ship Price (#1)',
                                     'walmart attr:Shipping Override-Is Shipping Allowed (#2)',
                                     'walmart attr:Shipping Override-Ship Region (#2)',
                                     'walmart attr:Shipping Override-Ship Method (#2)',
                                     'walmart attr:Shipping Override-Ship Price (#2)',
                                     'product attribute:apply_update']

                    sc_file_loc = base_dir + sc_dir

                    if item_sku != '':
                        sc_filename = sc_file_loc + item_sku + '_sc-line.csv'
                    else:
                        sc_filename = sc_file_loc + 'Item_' + now + '_sc-line.csv'

                    try:
                        open(sc_filename, "r+")
                    except FileNotFoundError:
                        print(cColors.WARNING + "\nSolid Commerce Import file doesn't exist. Creating...." + cColors.ENDC)
                    except PermissionError:
                        sc_filename = sc_file_loc + item_sku + '_' + now + '_sc-line.csv'

                    with open(sc_filename, 'w', newline='') as scFile:
                        sc_file_writer = csv.DictWriter(scFile, fieldnames=sc_fieldnames)

                        sc_file_writer.writeheader()

                        # map to the appropriate keys/field names
                        sc_row_data = {}

                        if content['SKU']:
                            sc_row_data['product custom sku'] = content['SKU']
                            sc_row_data['warehouse id'] = content['SKU']
                            sc_row_data['model number'] = content['SKU']
                        if content['Title']:
                            sc_row_data['product name'] = content['SKU'] + ' - ' + content['Title']
                        if content['Price']:
                            sc_row_data['msrp'] = content['Price']
                        if ebay_template:
                            sc_row_data['eBay Description'] = ebay_template
                        sc_row_data['walmart attr:brand'] = 'Rough Country'
                        sc_row_data['walmart attr:Shipping Override-Is Shipping Allowed (#1)'] = 'N'
                        sc_row_data['walmart attr:Shipping Override-Ship Region (#1)'] = 'STREET_48_STATES'
                        sc_row_data['walmart attr:Shipping Override-Ship Method (#1)'] = 'VALUE'
                        sc_row_data['walmart attr:Shipping Override-Ship Price (#1)'] = 0
                        sc_row_data['walmart attr:brand'] = 'Rough Country'
                        sc_row_data['walmart attr:Shipping Override-Is Shipping Allowed (#2)'] = 'Y'
                        sc_row_data['walmart attr:Shipping Override-Ship Region (#2)'] = 'STREET_48_STATES'
                        sc_row_data['walmart attr:Shipping Override-Ship Method (#2)'] = 'STANDARD'
                        sc_row_data['walmart attr:Shipping Override-Ship Price (#2)'] = 0
                        sc_row_data['product attribute:apply_update'] = 'Y'
                        if walmart_desc:  # need split up
                            sc_row_data['walmart description'] = walmart_desc
                        if walmart_shelf:
                            sc_row_data['walmart attr:shelf description'] = walmart_shelf
                        if walmart_short:
                            sc_row_data['walmart attr:short description'] = walmart_short
                        if content['MainImg']:
                            sc_row_data['image file'] = content['MainImg']
                        if all_images:
                            sc_images = []
                            for image in all_images:
                                if all_images.index(image) < 9:
                                    sc_images.append(image)
                            if sc_row_data:
                                if content['MainImg'] in sc_images:
                                    sc_images.remove(content['MainImg'])
                            for sImg in sc_images:
                                img_key = sc_images.index(sImg) + 1
                                img_key_str = 'alternate image file ' + str(img_key)
                                sc_row_data[img_key_str] = sImg
                        sc_row_data['upc'] = content['UPC']
                        if weight != '':
                            sc_row_data['product weight'] = int(round(float(weight))) * 16
                        sc_row_data['taxable'] = 'Yes'
                        sc_row_data['warehouse name'] = 'Rough Country'
                        sc_row_data['manufacturer'] = 'Rough Country'

                        sc_file_writer.writerow(sc_row_data)
                    scFile.close()

                else:
                    print('Due to a file name conflict, the SC template cannot be automatically generated')

        print(cColors.HEADER + '\nProcesses completed succesfully!')
        print(cColors.NORMAL)
    except urllib.error.HTTPError:
        print('Skipping this one - there was an HTTP error: ' + url)

