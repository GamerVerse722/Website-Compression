from compress.config import Information
from bs4 import BeautifulSoup
import base64
import os
import re


class Compress:
    def __init__(self):
        with open(os.path.join(os.getcwd(), Information.folder, Information.file), "r") as mainFile:
            self.doc = BeautifulSoup(mainFile.read(), "html.parser")

    def compress(self):
        self.lines()
        self.find_script()
        self.lines()
        self.find_links()
        self.lines()
        self.find_images()
        self.lines()

    def find_script(self) -> None:
        for script_tag in self.doc.find_all("script"):
            src: str | None = script_tag.get("src")

            if src is None or src.startswith("http"):
                print(type(src), src)
                continue
            else:
                print(script_tag)

                with open(os.path.join(os.getcwd(), Information.folder, src), "r") as scriptFile:
                    script_tag.clear()
                    del script_tag["src"]
                    script_tag.string = scriptFile.read()

    def find_links(self) -> None:
        for link_tag in self.doc.find_all("link"):
            href: str = link_tag.get("href")
            filepath: str = os.path.join(os.getcwd(), Information.folder, href)

            if href is None or href.startswith("http"):
                print(type(href), href)
                continue

            elif "icon" in link_tag.get("rel"):
                print(link_tag)
                favicon: str = base64.b64encode(open(filepath, 'rb').read()).decode('utf-8')
                link_tag["href"] = "data:image/x-icon;base64," + favicon
                link_tag["rel"] = "icon"

            elif href.endswith(".css"):
                print(link_tag.unwrap())
                with open(filepath, "r") as styleFile:
                    css: str = styleFile.read()

                css_content_modified = re.sub(r"url\(['\"]?([^'\")]+)['\"]?\)", self.re_encode_img, css)
                head = self.doc.find("head")
                head.append(BeautifulSoup(f"<style>\n{css_content_modified}</style>", "html.parser"))


    def find_images(self) -> None:
        for img_tag in self.doc.find_all("img"):
            image: str | None = img_tag["src"]
            if image is None or image.startswith("http"):
                print(type(image), image)
                continue

            else:
                print(img_tag)
                img_tag['src'] = self.encode_img(image)


    @staticmethod
    def encode_img(image_path: str) -> str:
        image_path.replace("\\", "/")
        filepath: str = os.path.join(os.getcwd(), Information.folder, image_path)
        with open(filepath, 'rb') as image_file:
            base64_data = base64.b64encode(image_file.read()).decode('utf-8')
        return f'data:image/{os.path.splitext(filepath)[-1]};base64,{base64_data}'

    def re_encode_img(self, match: re.Match[str]) -> str:
        return f"url({self.encode_img(match.group(1))})"

    @staticmethod
    def lines() -> None:
        print("----------------------------------------------------------------------------")

    def save(self) -> None:
        with open(os.path.join(os.getcwd(), "result", Information.output), "w") as outputFile:
            outputFile.write(str(self.doc))

