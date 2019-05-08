# -*- coding: utf-8 -*-
"""
Created on Tue Jan 09 13:24:57 2018

@author: xuenene
"""


import win32gui, win32ui, win32con
import urllib
from bs4 import BeautifulSoup  
import re
import webbrowser
import time
from aip import AipOcr

APP_ID = '******'
API_KEY = '******'
SECRET_KEY = '******'

baidu_search_url = 'http://www.baidu.com/s?wd='
question_name = "Q.jpg"
options_name = "O.jpg"
question_options_name = "Q_O.jpg"
same_words_file = "same_words.txt"
no_words_file = "no_words.txt"
q_cut_words_file = "q_cut_words.txt"
o_cut_words_file = "o_cut_words.txt"
q_cut_words = []
o_cut_words = []
same_words = []
no_words = []
question_num = 0

q_top_left_x = 543
q_top_left_y = 230
q_width = 285
q_height = 100

o_top_left_x = 543
o_top_left_y = 340
o_width = 285
o_height = 200

i_top_left_x = 522
i_top_left_y = 116
i_width = 322
i_height = 572

q_o_top_left_x = q_top_left_x
q_o_top_left_y = q_top_left_y
q_o_width = q_width
q_o_height = q_height + o_height

min_search = False
    
def window_capture(filename, left_top_x, left_top_y, w, h):
    hwnd = 0
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (left_top_x, left_top_y), win32con.SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC, filename)

def regular_question(question):    
    keys = []
    keys.extend(re.findall(r'\"(.+?)\"', question))
    keys.extend(re.findall(r'“(.+?)”', question))
    keys.extend(re.findall(r'<<(.+?)>>', question))
    keys.extend(re.findall(r'《(.+?)》', question))
    for word in no_words:
        if(question.find(word) != -1):
            global min_search
            min_search = True
            #question = question.replace(word, "")
            break;              
    global question_num
    if(question[:2].isdigit()):
        question_num = int(question[:2])
        question = question[2:]
    elif(question[:1].isdigit()):
        question_num = int(question[:1])
        question = question[1:]
    if(question[:1] == "."):
        question = question[1:]
    for key in q_cut_words:
        question = question.replace(key, "")
    return question, keys

def regular_option(option):    
    for key in o_cut_words:
        option = option.replace(key, "")
    return option

def key_words_question(keys):
    key_count = []
    unique_keys = list(set(keys))

    for key in unique_keys:
        key_count.append(keys.count(key))

    for i in range(len(key_count) - 1):
        for j in range(len(key_count) - i - 1):
            if(key_count[j] < key_count[j + 1]):
                key_count[j], key_count[j + 1] = key_count[j + 1], key_count[j]
                unique_keys[j], unique_keys[j + 1] = unique_keys[j + 1], unique_keys[j]
    question = ""
    for i in range(min(len(unique_keys), 7)):
        question += unique_keys[i] + " "
    return question

def baidu_search(question, options, keys):
    url = baidu_search_url + urllib.quote(question)    
    response = urllib.urlopen(url)
    data = response.read()
    soup = BeautifulSoup(data, "html.parser")
    soup_keys = soup.find_all('em')
    for soup_key in soup_keys:
        key = soup_key.string.encode('utf-8')
        for cut_word in q_cut_words:
            key = key.replace(cut_word, "")
        keys.append(key)
    content = ""
    for tag in soup.find_all('div', ):
        content += str(tag)
    for tag in soup.find_all('div', class_ = 'c-row'):
        content += str(tag)
    dr = re.compile(r'<[^>]+>', re.S)
    final_str = dr.sub('', content)
    count = []
    for i in range(len(options)):
        cnt = 0
        flag = False
        for same_word in same_words:
            for word in same_word:
                if(options[i].find(word) != -1):
                    flag = True
                    for word2 in same_word:
                        cnt += final_str.count(options[i].replace(word, word2))
    
        if(flag == False):
            cnt += final_str.count(options[i])
        count.append(cnt)
    return key_words_question(keys), count

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def img_ocr(img_name):
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    img = get_file_content(img_name)
    return client.basicGeneral(img);
def load_data():
    with open(q_cut_words_file, 'r') as words:
        for word in words:
            #print(chardet.detect(word))
            q_cut_words.append(word[:-1].decode('gbk').encode('utf-8'))
    with open(o_cut_words_file, 'r') as words:
        #print(len(words))
        for word in words:
            o_cut_words.append(word[:-1].decode('gbk').encode('utf-8'))
    with open(no_words_file, 'r') as words:
        for word in words:
            no_words.append(word[:-1].decode('gbk').encode('utf-8'))
    with open(same_words_file, 'r') as lines:
        for line in lines:
            same_words.append(line[:-1].decode('gbk').encode('utf-8').split())

load_data()
question = ""
options = []

"""
window_capture(question_options_name, q_o_top_left_x, q_o_top_left_y, q_o_width, q_o_height)

dic = img_ocr(question_options_name)

end = 0

for i in range(int(dic['words_result_num'])):
    for ch in dic['words_result'][i]['words']:
        question += ch.encode('utf-8')
    if(question[-1] == '?'):
        end = i
        break
question, keys = regular_question(question)
print(question)

for i in range(end + 1, int(dic['words_result_num'])):
    option = ""
    for ch in dic['words_result'][i]['words']:
        option += ch.encode('utf-8')
    #if(len(option) > 0 and option[0].isalpha):
        #option = option[1:]
    #if(len(option) > 0 and option[0] == '.'):
        #option = option[1:]
    option = regular_option(option)
    options.append(option)
    
    
"""
window_capture(question_name, q_top_left_x, q_top_left_y, q_width, q_height)
window_capture(options_name, o_top_left_x, o_top_left_y, o_width, o_height)    
#time_begin = time.clock()
q_dic = img_ocr(question_name)
#print(str(q_dic.encode('gbk')))
#time_end = time.clock()
#print(time_end - time_begin)
#time_begin = time.clock()
o_dic = img_ocr(options_name)
#print(str(o_dic))
#time_end = time.clock()
#print(time_end - time_begin)
for i in range(int(q_dic['words_result_num'])):
    question += q_dic['words_result'][i]['words'].encode('utf-8');

question, keys = regular_question(question)
print(question)
for i in range(int(o_dic['words_result_num'])):
    option = o_dic['words_result'][i]['words'].encode('utf-8')
    #if(len(option) > 0 and option[0].isalpha):
        #option = option[1:]
    #if(len(option) > 0 and option[0] == '.'):
        #option = option[1:]
    option = regular_option(option)
    options.append(option)

# 截屏保存数据
window_capture(str(question_num) + ".jpg", i_top_left_x, i_top_left_y, i_width, i_height) 
question, count = baidu_search(question, options, keys)


url = baidu_search_url + urllib.quote(question)
response = urllib.urlopen(url)
data = response.read().decode('utf-8')

soup = BeautifulSoup(data, "html.parser")
#count = []
content = ""
for tag in soup.find_all('div', ):
    content += str(tag)
for tag in soup.find_all('div', class_ = 'c-row'):
    content += str(tag)
dr = re.compile(r'<[^>]+>', re.S)
final_str = dr.sub('', content)

num_words = []
for i in range(len(options)):
    cnt = 0
    flag = False
    for same_word in same_words:
        for word in same_word:
            if(options[i].find(word) != -1):
                flag = True
                for word2 in same_word:
                    cnt += final_str.count(options[i].replace(word, word2))

    if(flag == False):
        cnt += final_str.count(options[i])
    count[i] += cnt
loc = -1
if(min_search == False):
    maxi = 0
    for i in range(len(options)):
        if(count[i] > maxi):
            maxi = count[i]
            loc = i
    for i in range(len(options)):
        if(count[i] == maxi):
            print("\033[1;31;47m" + options[i] + " = " + str(count[i]) + "\033[0m")
        else:
            print(options[i] + " = " + str(count[i]))
else:
    mini = float("inf")
    for i in range(len(options)):
        if(count[i] < mini):
            mini = count[i]
            loc = i
    for i in range(len(options)):
        if(count[i] == mini):
            print("\033[1;31;47m" + options[i] + " = " + str(count[i]) + "\033[0m")
        else:
            print(options[i] + " = " + str(count[i]))   

url = baidu_search_url + urllib.quote(question)
webbrowser.open(url, new=2, autoraise=True)