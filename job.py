import re, prettytable, csv
from prettytable import PrettyTable

translator = {"name": "Название", "description": "Описание", "key_skills": "Навыки",
              "experience_id": "Опыт работы", "premium": "Премиум-вакансия",
              "employer_name": "Компания", "salary_from": "Нижняя граница вилки оклада",
              "salary_to": "Верхняя граница вилки оклада",
              "salary_gross": "Оклад указан до вычета налогов",
              "salary_currency": "Идентификатор валюты оклада", "area_name": "Название региона",
              "published_at": "Дата публикации вакансии",
              "AZN": "Манаты", "BYR": "Белорусские рубли", "EUR": "Евро",
              "GEL": "Грузинский лари", "KGS": "Киргизский сом", "KZT": "Тенге",
              "RUR": "Рубли", "UAH": "Гривны", "USD": "Доллары", "UZS": "Узбекский сум",
              "True": "Да", "False": "Нет", "FALSE": "Нет", "TRUE": "Да",
              "noExperience": "Нет опыта", "between1And3": "От 1 года до 3 лет",
              "between3And6": "От 3 до 6 лет", "moreThan6": "Более 6 лет"}

currency_to_rub = {"Манаты": 35.68, "Белорусские рубли": 23.91,
                   "Евро": 59.90, "Грузинский лари": 21.74,
                   "Киргизский сом": 0.76, "Тенге": 0.13, "Рубли": 1,
                   "Гривны": 1.64, "Доллары": 60.66, "Узбекский сум": 0.0055, }

field_names = ["Навыки", "Оклад", "Дата публикации вакансии", "Опыт работы", "Премиум-вакансия",
               "Идентификатор валюты оклада", "Название", "Название региона", "Компания", ""]

experience = {"Нет опыта": 0, "От 1 года до 3 лет": 1, "От 3 до 6 лет": 2, "Более 6 лет": 3}


def quit_code(string):
    print(string)
    quit()


def check_inputs(requested_filter, requested_sorter, is_reverse):
    if len(requested_filter) == 1 and requested_filter[0] != "":
        quit_code("Формат ввода некорректен")
    elif requested_filter[0] not in field_names:
        quit_code("Параметр поиска некорректен")
    elif requested_sorter not in field_names:
        quit_code("Параметр сортировки некорректен")
    elif is_reverse != "Да" and is_reverse != "Нет" and is_reverse != "":
        quit_code("Порядок сортировки задан некорректно")


def read_file(data_frame):
    jobs_list = []
    headers_list = []
    first_element_flag = True
    length = 0
    rows_counter = 0
    with open(data_frame, encoding="utf-8-sig") as csv_file:
        file = csv.reader(csv_file)
        for row in file:
            rows_counter += 1
            if first_element_flag:
                headers_list = row
                length = len(row)
                first_element_flag = False
            else:
                break_flag = False
                if length != len(row):
                    break_flag = True
                for word in row:
                    if word == "":
                        break_flag = True
                if break_flag:
                    continue
                jobs_list.append(row)
    if rows_counter == 0:
        quit_code("Пустой файл")
    if rows_counter == 1:
        quit_code("Нет данных")
    return headers_list, jobs_list


def reformat_date(date):
    return date[8: 10] + "." + date[5: 7] + "." + date[: 4]


def clean_string(string):
    new_string = re.compile(r'<[^>]+>').sub('', string) \
        .replace(" ", " ").replace(" ", " ").replace("  ", " ").replace("  ", " ").strip()
    if new_string in translator:
        new_string = translator[new_string]
    return new_string


def clean_job_position(data, names_list):
    jobs_list = []
    for job in data:
        job_position = {}
        for i in range(len(names_list)):
            job_position[names_list[i]] = clean_string(job[i])
        jobs_list.append(job_position)
    return jobs_list


def reformat_number(num):
    first_digit_counter = len(str(int(float(num)))) % 3
    triplets_counter = len(str(int(float(num)))) // 3
    new_num = ""
    new_num += num[:first_digit_counter]
    for i in range(triplets_counter):
        if new_num != "":
            new_num += " "
        new_num += num[first_digit_counter + i * 3: first_digit_counter + (i + 1) * 3]
    return new_num


def format_job_fields(input_string):
    result = {}
    before_taxes = ""
    max_wage = ""
    min_wage = ""
    for key in input_string:
        if key == "Нижняя граница вилки оклада":
            min_wage = reformat_number(input_string[key])
        elif key == "Верхняя граница вилки оклада":
            max_wage = reformat_number(input_string[key])
        elif key == "Оклад указан до вычета налогов":
            if input_string[key] == "Да":
                before_taxes = "Без вычета налогов"
            else:
                before_taxes = "С вычетом налогов"
        elif key == "Идентификатор валюты оклада":
            result["Оклад"] = f"{min_wage} - {max_wage} ({input_string[key]}) ({before_taxes})"
        elif key == "Дата публикации вакансии":
            result[key] = reformat_date(input_string[key])
        else:
            result[key] = input_string[key]
    return result


def is_row_passed(input_dict, sorter):
    for key in input_dict:
        if sorter[0] == "Оклад":
            if key == "Нижняя граница вилки оклада":
                if int(float(sorter[1])) < int(float(input_dict[key])):
                    return False
            elif key == "Верхняя граница вилки оклада":
                if int(float(sorter[1])) > int(float(input_dict[key])):
                    return False
        elif sorter[0] == "Дата публикации вакансии" == key:
            if sorter[1] != reformat_date(input_dict[key]):
                return False
        elif sorter[0] == key == "Навыки":
            for element in sorter[1].split(", "):
                if element not in input_dict[key].split("\n"):
                    return False
        elif sorter[0] == key:
            if sorter[1] != input_dict[key]:
                return False
    return True


def sort_data_jobs(jobs_data, sorter, reverse):
    if reverse == "Да":
        reverse = True
    else:
        reverse = False
    if sorter == "":
        sorted_jobs = jobs_data
    elif sorter == "Оклад":
        sorted_jobs = sorted(jobs_data,
                             key=lambda dictionary:
                             (int(float(dictionary["Нижняя граница вилки оклада"])) +
                              int(float(dictionary["Верхняя граница вилки оклада"]))) *
                             currency_to_rub[dictionary["Идентификатор валюты оклада"]],
                             reverse=reverse)
    elif sorter == "Навыки":
        sorted_jobs = sorted(jobs_data,
                             key=lambda dictionary:
                             len(dictionary[sorter].split("\n")), reverse=reverse)
    elif sorter == "Опыт работы":
        sorted_jobs = sorted(jobs_data,
                             key=lambda dictionary: experience[dictionary[sorter]], reverse=reverse)
    else:
        sorted_jobs = sorted(jobs_data, key=lambda dictionary: dictionary[sorter], reverse=reverse)
    return sorted_jobs


def apply_range_table(table, from_to, headers, counter):
    from_to = from_to.split(" ")
    start = 0
    end = counter
    if from_to[0] == "":
        pass
    elif len(from_to) == 1:
        start = int(from_to[0]) - 1
    elif len(from_to) == 2:
        start = int(from_to[0]) - 1
        end = int(from_to[1]) - 1
    headers = headers.split(", ")
    if headers[0] == "":
        return table.get_string(start=start, end=end)
    headers.insert(0, "№")
    return table.get_string(start=start, end=end, fields=headers)


def print_table(jobs_data, translate, requested_sorter, is_reverse, requested_filter,
                output_range, required_columns):
    num = 0
    first_row_flag = True
    table = PrettyTable(hrules=prettytable.ALL, align='l')
    new_data_jobs = sort_data_jobs(({translate[key]:
                                         data[key] for key in data}
                                    for data in jobs_data), requested_sorter, is_reverse)
    for new_dict in new_data_jobs:
        changed_job_dict = format_job_fields(new_dict)
        if first_row_flag:
            first_row = [key for key in changed_job_dict]
            first_row.insert(0, "№")
            table.field_names = first_row
            first_row_flag = False
            num += 1
        if not is_row_passed(new_dict, requested_filter):
            continue
        job_fields = [value if len(value) <= 100 else value[:100]
                      + "..." for value in changed_job_dict.values()]
        job_fields.insert(0, num)
        table.add_row(job_fields)
        num += 1
    if num == 1:
        quit_code("Ничего не найдено")

    table.max_width = 20
    table = apply_range_table(table, output_range, required_columns, num - 1)
    print(table)


def print_job_table():
    file_name = input("Введите название файла: ")
    requested_filter = input("Введите параметр фильтрации: ")
    requested_sorter = input("Введите параметр сортировки: ")
    is_reverse = input("Обратный порядок сортировки (Да / Нет): ")
    output_range = input("Введите диапазон вывода: ")
    required_columns = input("Введите требуемые столбцы: ")
    requested_filter = requested_filter.split(": ")
    check_inputs(requested_filter, requested_sorter, is_reverse)
    headers, jobs = read_file(file_name)

    print_table(clean_job_position(jobs, headers), translator, requested_sorter,
                is_reverse, requested_filter, output_range, required_columns)


if __name__ == '__main__':
    print_job_table()