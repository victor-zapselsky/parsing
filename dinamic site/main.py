import json
import os
import random
import re
import time
import requests
from bs4 import BeautifulSoup


def get_data(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Mobile Safari/537.36"
    }

    projects_data_list = []
    iteration_count = 23
    print(f"Всего итераций: #{iteration_count}")

    for item in range(1, 24):
        req = requests.get(url + f"&PAGEN_1={item}&PAGEN_2={item}", headers)

        folder_name = f"{item}"

        if os.path.exists(folder_name):
            print("Папка уже существует!")
        else:
            os.mkdir(folder_name)

        with open(f"{folder_name}/projects_{item}.html", "w") as file:
            file.write(req.text)

        with open(f"{folder_name}/projects_{item}.html") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        articles = soup.find_all("article", class_="ib19")

        projects_urls = []
        for article in articles:
            project_url = "http://www.edutainme.ru" + article.find("div", class_="txtBlock").find("a").get("href")
            projects_urls.append(project_url)

        for project_url in projects_urls:
            req = requests.get(project_url, headers)
            project_name = project_url.split("/")[-2]

            with open(f"{folder_name}/{project_name}.html", "w") as file:
                file.write(req.text)

            with open(f"{folder_name}/{project_name}.html") as file:
                src = file.read()

            soup = BeautifulSoup(src, "lxml")
            project_data = soup.find("div", class_="inside")

            try:
                project_logo = "http://www.edutainme.ru" + project_data.find("div", class_="Img logo").find("img").get("src")
            except Exception:
                project_logo = "No project logo"

            try:
                project_name = project_data.find("div", class_="txt").find("h1").text
            except Exception:
                project_name = "No project name"

            try:
                project_short_description = project_data.find("div", class_="txt").find("h4", class_="head").text
            except Exception:
                project_short_description = "No project short description"

            try:
                project_website = project_data.find("div", class_="txt").find("p").find("a").text
            except Exception:
                project_website = "No project website"

            try:
                project_full_description = project_data.find("div", class_="textWrap").find("div", class_="rBlock").text
            except Exception:
                project_full_description = "No project full description"

            def replace_string(string):
                return ''.join(re.sub(r'(<p>|</p>)', "", string))
            project_full_description = replace_string(project_full_description)

            # rep = ["<p>", "</p>"]
            # for s in rep:
            #     if s in project_full_description:
            #         project_full_description = project_full_description.replace(s, "")

            projects_data_list.append(
                {
                    "Имя проекта": project_name,
                    "URL логотипа проекта": project_logo,
                    "Короткое описание проекта": project_short_description,
                    "Сайт проекта": project_website,
                    "Полное описание проекта": project_full_description.strip()
                }
            )

        iteration_count -= 1
        print(f"Итерация #{item} завершена, осталось итераций #{iteration_count}")
        if iteration_count == 0:
            print("Сбор данных завершен")
        time.sleep(random.randrange(2, 4))

    with open("data/projects_data.json", "a", encoding="utf-8") as file:
        json.dump(projects_data_list, file, indent=4, ensure_ascii=False)


def main():
    get_data("http://www.edutainme.ru/edindex/")


if __name__ == "__main__":
    main()