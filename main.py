from bs4 import BeautifulSoup
import base64
import json
import re
import os

with open("config.json", "r") as config:
    configuration = json.load(config)

folder = configuration["Folder"]
html_filename = configuration["File"]
originalLocation = os.getcwd().replace(os.sep, '/')

with open(f"{folder}/index.html", "r") as mainFile:
    doc = BeautifulSoup(mainFile, "html.parser")


class SaveData:
    def __init__(self, folderlocation):
        self.folderlocation = folderlocation


def find_folder(directory, topdir):
    parent = os.path.dirname(directory)
    items_in_directory = os.listdir(parent)
    test = topdir.split("/", 1).pop(1)
    if test.split("/", 1)[0] in items_in_directory:
        return parent
    else:
        directory_parts = os.path.split(str(directory))
        parent_directory = directory_parts[0]
        os.chdir(parent_directory)
        return find_folder(parent_directory, topdir)


def replace_with_base64(match):
    image_path = match.group(1)
    if "../" in image_path:
        # work more here
        location = find_folder(f"{os.getcwd().replace(os.sep, '/')}/{Folder.folderlocation}", image_path)
        with open(f'{location}/{image_path.split("/", 1).pop(1)}', 'rb') as image_file:
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
        return f"url(data:image/{image_path.split('.')[-1]};base64,{base64_data})"
    else:
        with open(os.path.abspath(f"{folder}/{image_path}"), 'rb') as image_file:
            image_data = image_file.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
        return f"url(data:image/{image_path.split('.')[-1]};base64,{base64_data})"


for x in doc.find_all("script"):
    if x.get("src") is not None:
        site = x["src"]
        if "http" in site:
            continue

        elif "https" not in site:
            x.unwrap()
            with open(f"{folder}/{site}", "r") as scriptFile:
                javascript = scriptFile.read()
            body = doc.find("body")
            body.append(BeautifulSoup(f"<script>\n{javascript}</script>", 'html.parser'))
    else:
        pass


for y in doc.find_all("link"):
    style = y["href"]
    if "http" in style:
        continue

    elif "icon" in y["rel"] and "href" not in style:
        y.unwrap()
        favicon = base64.b64encode(open(f"{folder}/{style}", 'rb').read()).decode('utf-8')
        head = doc.find("head")
        head.append(BeautifulSoup(f'<link rel="icon" type="image/x-icon" href="data:image/x-icon;base64,{favicon}">', "html.parser"))

    elif "https" not in style:
        y.unwrap()
        with open(f"{folder}/{style}", "r") as styleFile:
            cascadingStyleSheets = styleFile.read()
        Folder = SaveData(f"{folder}/{style}")
        css_content_modified = re.sub(r"url\(['\"]?([^'\")]+)['\"]?\)", replace_with_base64, cascadingStyleSheets)
        head = doc.find("head")
        head.append(BeautifulSoup(f"<style>\n{css_content_modified}</style>", "html.parser"))


for z in doc.find_all("img"):
    image = z["src"]
    if "http" in image:
        continue

    elif "https" not in image:
        image_encoded = base64.b64encode(open(f"{folder}/{image}", 'rb').read()).decode('utf-8')
        z['src'] = f'data:image/png;base64,{image_encoded}'


outputFile = open(f"{originalLocation}/output.html", "w")
outputFile.write(str(doc))
outputFile.close()
