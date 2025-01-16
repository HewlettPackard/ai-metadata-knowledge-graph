###
# Copyright (2024) Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###


from bs4 import BeautifulSoup
import requests
import json
import csv
import os

# second_child_data = json.load(open('second_child.json', 'r'))
# print("Current length of second_child_data:", len(second_child_data))
second_child_data = {}

DATA_FOLDER = 'data/pwc'

def get_area_urls(html_page):
    """
    Fetches the URL, Name and ID for the main categories such as Computer vision, NLP and etc.
    Returns a dict with IS, URL and Name
    """
    title_elements = html_page.find_all('div', class_='row task-group-title')
    area_data = {}
    for t in title_elements:
        a_tag = t.find('a')
        href = a_tag['href']
        name = a_tag.text
        url = 'https://paperswithcode.com' + str(href)
        area_id = href.split('/')[-1]
        area_data[area_id] = {'url': url, 'name': name, 'area_id': area_id}
    return area_data


def get_name_from_id(item_id):
    tokens = item_id.split("-")
    name = ' '.join(tokens)
    capitalized = name.capitalize()
    return capitalized


def get_id_from_name(item_name):
    tokens = item_name.split(" ")
    tokens_lower = [i.lower() for i in tokens]
    title_id = "-".join(tokens_lower)
    return title_id

def get_description(url):
    try:
        res = requests.get(url)
        desc_page = BeautifulSoup(res.content, 'html.parser')
        desc_main = desc_page.find('div', class_='description-content')
        p_tags = desc_main.find_all('p')
        description = ""
        for p_tag in p_tags:
            if str(p_tag.text).strip() == 'Further readings:':
                break
            else:
                description = description + str(p_tag.text)
        return description
    except:
        return ''


def get_second_child_data(first_child_id, main_card_container, flag=False):
    # TODO - use the a['href'] as the id for the data. What if there are two leaf nodes with same name but from differen parent?
    a_tags = main_card_container.find_all('a')
    img_tags = main_card_container.find_all('img', class_='task-img')
    
    second_child_ids = []
    
    for idx, tag in enumerate(a_tags):
        href = tag['href']
        url = 'https://paperswithcode.com' + str(href)
        second_child_id = href.split("/")[-1]
        second_child_ids.append(second_child_id)
        second_child_name = get_name_from_id(second_child_id)
        img_url = img_tags[idx]['src']
        desc = get_description(url)

        second_child_data[second_child_id] = {'second_child_id': second_child_id,
                                              'second_child_name': second_child_name,
                                              'first_child_id': first_child_id,
                                              'thumbnail_url': img_url,
                                              'desc': desc,
                                              'about_url': url}

    return second_child_ids


def get_second_child(first_child_data):
    counter = 0
    for f_child_id in first_child_data:
        curr_data = first_child_data[f_child_id]
        second_child_ids = curr_data['second_child_ids']
        if len(second_child_ids) == 0:
            url = curr_data['url']
            if url != 'none': # some first child do not have any second child at all
                res = requests.get(url)
                html_page = BeautifulSoup(res.content, 'html.parser')
                main_container = html_page.find('div', class_='infinite-container featured-task area-tag-page')
                cards = main_container.find_all('div', class_='card-deck card-break infinite-item')
                counter = counter + 1
                print("First Child Counter:" + str(counter) + '/' + str(len(first_child_data)))
                for element in cards:
                    # data will be stored through this function
                    ids = get_second_child_data(f_child_id, element, True)
                
                print("Length of second_child_data:", len(second_child_data))
                if counter % 10 == 0:
                    json.dump(second_child_data, open('second_child.json','w')) # Saving ocassionally
                    print("Second Child file saved. Length:", len(second_child_data))
            else:
                print("No Child task:", f_child_id)
        else:
            pass
    return 'Done'

        

def get_first_child(area_data):
    error_counter = 0
    data = {}
    for area_id in area_data:
        area_url = area_data[area_id]['url']
        res = requests.get(area_url)
        html_page = BeautifulSoup(res.content, 'html.parser')
        main_container = html_page.find('div', class_='infinite-container featured-task')

        title_elements = main_container.find_all('div', class_='row', recursive = False)
        cards = main_container.find_all('div', class_='card-deck card-break infinite-item')
        sota_all_tasks = main_container.find_all('div', class_='sota-all-tasks')

        counter = 0
        total_length = len(sota_all_tasks)
        for idx, task in enumerate(sota_all_tasks):
            title_element = title_elements[idx]
            title_text = title_element.find('h2').text
            first_child_name = title_text.strip()
            first_child_id = get_id_from_name(first_child_name)
            counter = counter + 1

            print('Area:', area_id)
            print("First Child Name:", first_child_name)
            print(str(counter) + '/' + str(total_length))

            a_tag = task.find('a')
            if a_tag == None:
                # There is no new page for these first children. Hence information is collected from the same page. Example: Computer Vision --> Data Augmentation
                second_child_ids = get_second_child_data(first_child_id, cards[idx])
                url = 'none'
            else:
                # Needs to go to a new page to collect information on second children. Hence done later using the URL
                second_child_ids = []
                url = 'https://paperswithcode.com' + str(a_tag['href'])
            

            data[first_child_id] = {'area_id': area_id,
                            'first_child_id': first_child_id,
                            'first_child_name': first_child_name,
                            'second_child_ids': second_child_ids,
                            'url': url
            }
            print("Length of First Child Data:", len(data))
            print("Length of Second Child Data:", len(second_child_data))
    json.dump(data, open('first_child.json', 'w'))
    return data



def main():
    URL = 'https://paperswithcode.com/sota'
    res = requests.get(URL)
    html_page = BeautifulSoup(res.content, 'html.parser')
    print("Fetching main areas...")
    area_data = get_area_urls(html_page)
    json.dump(area_data, open(os.path.join(DATA_FOLDER,'area_data.json', 'w')))
    
    print("Fetching first children...")
    first_child_data = get_first_child(area_data)
    json.dump(first_child_data, open('first_child.json', 'w'))
    first_child_data = json.load(open(os.path.join(DATA_FOLDER,'first_child.json', 'r')))
    
    print("Fetching second children...")
    second_child_data = get_second_child(first_child_data)
    print("Final Length of Second Child Data:", len(second_child_data))
    json.dump(second_child_data, open(os.path.join(DATA_FOLDER,'second_child.json', 'w')))



main()