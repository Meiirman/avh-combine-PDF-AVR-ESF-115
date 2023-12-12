import os
import tkinter as tk
from tkinter import filedialog
import Levenshtein
from pypdf import PdfReader, PdfMerger
from pyautogui import alert
from tqdm import tqdm
import re
import requests

alert("Выберите папку, в которой находятся файлы HTML")
root = tk.Tk()
root.withdraw()
current_directory = filedialog.askdirectory()
root.destroy()


def get_content(pdf_files):
    pdf_as_text = []
    for file_path in tqdm(pdf_files, desc="Считывание данных"):
        with open(current_directory + "/" + file_path, 'rb') as pdf:
            pdf_reader = PdfReader(pdf)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            pdf_as_text.append({
                "file_name" : file_path,
                "content" : text
            })
    return pdf_as_text

def divide_types(pdf_as_text):
    pdf_schet = []
    pdf_avrka = []
    pdf_error = []
    for i, e in enumerate(pdf_as_text):
        if "счет-фактура" in e["file_name"]:
            pdf_as_text[i]["type"] = "счет"
            pdf_schet.append(pdf_as_text[i])
        elif "АВР_" in e["file_name"] and "_AVS" in e["file_name"]:
            pdf_as_text[i]["type"] = "АВР"
            pdf_avrka.append(pdf_as_text[i])
        else:
            pdf_as_text[i]["type"] = "не распознан"
            pdf_error.append(pdf_as_text[i])

    return pdf_schet, pdf_avrka, pdf_error


def get_output_file_name(pdf_avrka):
    for i, avrka in enumerate(pdf_avrka):
        avrka['file_name']

        match = re.search(r'АВР_(.*?)_AVS', avrka['file_name'])
        if match:
            pdf_avrka[i]["output_file_name"] = " ЭСФ_АВР_" + match.group(1) + "_AVS.pdf"
    return pdf_avrka


def get_bs_names(pdf_schet):
    for i, element in enumerate(pdf_schet):
        splited_data = "".join(element["content"].split("\n")).split("\"")
        result = []
        for wordX in splited_data:
            
            pattern = r'[a-zA-Z]{3}_(?:[0-9]*)?(?:[a-zA-Z]{2,})'

            for match in re.finditer(pattern, wordX):
                result.append(match.group()) 
        pdf_schet[i]["words"] = result
        
    return pdf_schet


def get_sf_number(pdf_schet):
    for i, element in enumerate(pdf_schet):
        splited_data = "".join(element["content"].split("\n")).split("\"")
        result = []
        for wordX in splited_data:
            
            pattern = r'0000000[0-9]{4}'

            for match in re.finditer(pattern, wordX):
                result.append(match.group())
        try: pdf_schet[i]["sf_number"] = result[0].replace("0000000", "")
        except: pdf_schet[i]["sf_number"] = []

    return pdf_schet


def get_similarities(pdf_schet, pdf_avrka):
    pdf_similarities = []
    for schet in pdf_schet:
        for avrka in pdf_avrka:
            similarities = []
            for word1 in schet["words"]:
                for word2 in avrka["words"]:
                    distance = Levenshtein.distance(word1.lower(), word2.lower())
                    similarity = 1 - (distance / max(len(word1), len(word2)))
                    similarities.append(similarity)

            if len(similarities) > 0:
                pdf_similarities.append({
                    "schet" : schet,
                    "avrka" : avrka,
                    "similariti" : sum(similarities)/len(similarities)
                })
            else:
                pdf_similarities.append({
                    "schet" : schet,
                    "avrka" : avrka,
                    "similariti" : 0
                })
    return pdf_similarities

    
def merge_files(similar_pdfs):
    
    if not os.path.exists(current_directory + "/ВЫВОД"):
            os.makedirs(current_directory + "/ВЫВОД")
    pdf_merger = PdfMerger()
    pdf_merger.append(current_directory + "/" + similar_pdfs["schet"]['file_name'])
    pdf_merger.append(current_directory + "/" + similar_pdfs["avrka"]['file_name'])
    pdf_merger.write(current_directory + "/ВЫВОД/" + similar_pdfs["schet"]["sf_number"] + similar_pdfs["avrka"]["output_file_name"])
    pdf_merger.close()









script_dir = current_directory
pdf_files = [file for file in os.listdir(script_dir) if file.endswith('.pdf')]


pdf_dict = get_content(pdf_files)
pdf_dict = get_bs_names(pdf_dict)
pdf_schet, pdf_avrka, pdf_error = divide_types(pdf_dict)
pdf_avrka = get_output_file_name(pdf_avrka)
pdf_schet = get_sf_number(pdf_schet)


pdf_similarities = get_similarities(pdf_schet, pdf_avrka) 


similar_files = []
for i in tqdm(pdf_similarities, desc="Процесс объединение"):
    if i["similariti"] > 0.79:
        merge_files(i)
        similar_files.append(i["schet"]["file_name"])
        similar_files.append(i["avrka"]["file_name"])


passed_files_log = ""
for i in pdf_files:
    not_similar = True
    for j in similar_files:
        if i == j:
            not_similar = False
    if not_similar:
        passed_files_log += i + "\n"




if len(pdf_error) > 0 :
    alert("По названиям данных файлов программа не смогла определить Счет ли это или АВР\n\n" + pdf_error)
if passed_files_log != "":
    alert("Эти файлы не сопоставились так как не нашлись схожие данные\n\n" + passed_files_log)


if len(similar_files) > 0:
    alert(f"Процесс завершен!\nСоеденены {len(similar_files)} файлов.\nФайлы сохранены в файле \"ВЫВОД\"")
    

            
    
    
    
import requests
import datetime

def send_report(text=None, process=None, responsible=None):
    requests.post(f"https://script.google.com/macros/s/AKfycbzDwjE6Pu1a7otho2EHwbI-4yNoEmLijTfwWfI3toWpDpJ6rc-O1pKljV6XMLJmQIyJ/exec?time={datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}&process={process}&responsible={responsible}&text={text}")
send_report(text="AVR_merge_ATP_115_project", process="AVR_merge_ATP_115_project", responsible=os.getlogin())



