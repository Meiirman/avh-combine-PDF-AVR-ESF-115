# x = "3111 ЭСФ_АВР_XX_ATR_SAGIZ2_U21L81821_ATR_SAGIZ2_U21L81821_ATR_SAGIZ2_U21L81821_ATR_SAGIZ2_ATR_SAGIZ2379914315_ATR_SAGIZ2379914315_ATR_SAGIZ379914715_ATR_SAGIZ2__ATR_SAGIZ2__243_AVS"

# print(x)
# print(x[:100])
# # output_file_name
# quit()


import Levenshtein
import os
import re

from pypdf import PdfReader, PdfMerger
from pyautogui import alert


def extract_word_from_pdf(pdf_path):
    word_list = []

    with open(pdf_path, 'rb') as pdf:
        pdf_reader = PdfReader(pdf)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        # Ищем слова, содержащие более 5 латинских букв и завершающиеся "_"
        latin_words = re.findall(r'[a-zA-Z]{2,}_(?:[0-9]*)?(?:[a-zA-Z]{2,})', text)
        order_number = re.findall(r'\b(?:\S*\/\S*){2,}\b', text)
        order_number_esf = re.findall(r'\b\w*00000\w{4}\b', text)
        f_name_from_file2 = "0_не нашел"
        match = re.search(r'АВР_(.*?)_AVS', text)
        if match:
            f_name_from_file2 = "АВР_" + match.group(1) + "_AVS"

        if order_number_esf:
            order_number_esf = order_number_esf[0][-4:]
        order_number_number = re.findall(r'\b(?:\S*\/\S*){2,}\b', text)
        if order_number:
            order_number = order_number[0]
            if len(order_number.split("/")) > 0:
                order_number_number = order_number.split("/")[0]
            
        


        for word in latin_words:
            # os.system('cls')
            # print(word)
            
            word_list.append({"word": word,"f_name_from_file2":f_name_from_file2, "file": os.path.basename(pdf_path), "order_number" : order_number, "order_number_number" : order_number_number,"order_number_esf":order_number_esf, "latin_words":list(set(latin_words))})
            # print(f'Записано - {pdf_path} - ({word_list})')
            break
    # os.system('cls')
    # print("ЗАВЕРШЕНИЕ ПОИСКА НУЖНЫХГО СЛОВА")
    return word_list


def merge_pdfs(pdf_files, output_path):
    pdf_merger = PdfMerger()
    
    for pdf_file in pdf_files:
        pdf_merger.append(pdf_file)
    if len(output_path):
        pass
    with open(output_path, 'wb') as output_file:
        pdf_merger.write(output_file)



def combine_pdfs_with_same_word(pdf_files):
    # print(pdf_files)
    word_to_files = []

    for pdf_file in pdf_files:
        # os.system('cls')
        # print(pdf_file)
        x = extract_word_from_pdf(pdf_file)
        word_to_files += x
        print(x)
    # os.system('cls') 
    # print(word_to_files)
    unique_data = []
    # quit()



    # Создаем множество для отслеживания уже встреченных значений
    seen_values = set()

    for item in word_to_files:
        # os.system('cls')
        # print(item)
        # Извлекаем значение 'word' из элемента
        word_value = item['file']

        # Если значение 'word' уже было встречено, пропускаем элемент
        if word_value in seen_values:
            continue
        
        # Добавляем значение 'word' во множество просмотренных
        seen_values.add(word_value)

        # Добавляем элемент в уникальный список
        unique_data.append(item)




    matching_pairs = []

    # Итерируемся по каждому элементу
    for i, item1 in enumerate(unique_data):
        word1 = item1['word']
        num1 = item1['order_number']

        # Вложенный цикл для сравнения со всеми остальными элементами после текущего
        for j, item2 in enumerate(unique_data[i + 1:], start=i + 1):
            word2 = item2['word']
            num2 = item2['order_number']

            # Проверяем, содержит ли word1 word2 или наоборот
            # if (word1 in word2 or word2 in word1) and (num1 in num2 or num2 in num1):

            
            similarities = []
            for word1 in item1["latin_words"]:
                # is_zero_distance = True
                for word2 in item2["latin_words"]:
                    distance = Levenshtein.distance(word1.lower(), word2.lower())
                    similarity = 1 - (distance / max(len(word1), len(word2)))
                    # if similarity > 0.5:
                        # is_zero_distance = False
                    similarities.append(similarity)
                # if is_zero_distance :
                    # similarities.append(0.0)
            try:
                
                if sum(similarities)/len(similarities) > 0.5:
                    print(f'added')
                    # print(f'\nsimilarityes={similarities}')
                    # print(f'similarity={sum(similarities)/len(similarities)}')
                    # print(f'item1 = {item1}')
                    # print(f'item2 = {item2}')
                    matching_pairs.append((item1, item2))
            except:
                print("Нельзя делить на ноль")
                pass

            print(f'similarityes={similarities}')
            print(f'similarity={sum(similarities)/len(similarities)}')
            print(f'item1 = {item1}')
            print(f'item2 = {item2}\n')


    # Выводим найденные пары
    # os.system('cls')
    # print(matching_pairs)

    


    for items in matching_pairs:
        pdf_merger = PdfMerger()
        has_schet = False  # Флаг, указывающий наличие "счет" в item['file']

        # Создаем новый список для элементов в нужном порядке
        new_items = []

        # Проверяем каждый элемент items на наличие "счет"
        for item in items:
            if "счет" in item['file'].lower():  # Проверяем, нечувствительно к регистру
                has_schet = True
                # Если "счет" найден, добавляем его в начало нового списка
                new_items.insert(0, item)
            else:
                new_items.append(item)

        if has_schet:
            # Теперь new_items содержит элемент с "счет" в начале (если он был)
            for item in new_items:
                pdf_merger.append(item['file'])

        # Остальной код для объединения файлов остается без изменений


        if not os.path.exists("ВЫВОД"):
            # Если не существует, создаем её
            os.makedirs("ВЫВОД")
            
        
        # print("items[0] - start")
        # print(items[0])
        # print("items[0] - end")

        name_words = []
        file = items[0]["file"]
        order_number = items[0]["order_number"]
        order_number_number = items[0]["order_number_number"]
        order_number_esf = items[0]["order_number_esf"]
        f_name_from_file2 = items[0]["f_name_from_file2"] if items[0]["f_name_from_file2"] == "0_не нашел" else "0_не нашел"
        print(f'198 = {f_name_from_file2}')


        try:
            # print("items[1] - start")
            # print(items[1])
            # print("items[1] - end")
            file = items[1]["file"] 
            order_number = items[1]["order_number"] 
            order_number_number = items[1]["order_number_number"] 
            order_number_esf = items[1]["order_number_esf"] if order_number_esf == [] else order_number_esf 
            f_name_from_file2 = items[1]["f_name_from_file2"] if items[1]["f_name_from_file2"] and f_name_from_file2 == "0_не нашел" else f_name_from_file2
            print(f'210 = {f_name_from_file2}')


            
            for i in items[0]["latin_words"]:
                for j in items[0]["latin_words"]:
                    if i.lower == j.lower:
                        name_words.append(j)
                    if i.lower in j.lower:
                        name_words.append(j)
                    elif j.lower in i.lower:
                        name_words.append(i)

        except:
            pass
        
        name_wordsx = []
        name_words = list(set(name_words))
        if len(name_words)==1:
            name_wordsx = name_words
        else:
            for i, e in enumerate(name_words):
                for ii, ee in enumerate(name_words):
                    if i != ii and (ee.lower in e.lower or e.lower in ee.lower):
                        name_wordsx.append(e)
        word = "_".join(name_wordsx)
        
        f_name_from_file = "_".join(f_name_from_file2.split("_")[1:])
        output_file_name = f'ВЫВОД/{order_number_esf} ЭСФ_{f_name_from_file}'
        if len(output_file_name) > 150:
            output_file_name = output_file_name[:100]
        output_file_name += ".pdf"
        
        print(f'word = {word}')
        print(f'name_words = {name_words}')
        print(f'output_file_name = {output_file_name}')
        
        

        if order_number_esf != []:
            pdf_merger.write(output_file_name)
        # os.system('cls')
            print(f'\n_________________')
            print(f'items[0] - {items[0]}')
            print(f'items[1] - {items[1]}')
            print(f'MERGE - {output_file_name}')
        # Закрываем объединитель
        pdf_merger.close()



if __name__ == "__main__":
    script_dir = os.getcwd()
    pdf_files = [file for file in os.listdir(script_dir) if file.endswith('.pdf')]

    combine_pdfs_with_same_word(pdf_files)
    # os.system('cls')
    print("ПРОЦЕСС ЗАВЕРШЕН")
    alert("ПРОЦЕСС ЗАВЕРШЕН")

