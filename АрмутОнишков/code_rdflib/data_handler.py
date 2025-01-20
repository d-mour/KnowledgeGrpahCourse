from bs4 import BeautifulSoup
from collections import namedtuple

Pair = namedtuple('Pair', ['name', 'count'])
Pair.__annotations__ = {"name": str, "count": str}


def to_handle(response_text: list[str]) -> dict[str, list[Pair[str, str]]]:
    coffe_type: dict[str, list[Pair[str, str]]] = {}
    print(response_text)
    for text in response_text:
        soup = BeautifulSoup(text, "html.parser")

        coffe_name = soup.find("h1", class_="ty-mainbox-title").find("span").get_text(strip=True)
        coffe_name = clear_data(coffe_name)
        ingredients_html = None
        try:
            ingredients_html = soup.find("ul", class_="marked").find_all("li")
        except AttributeError:
            pass

        if ingredients_html is None:
            ingredients_html = soup.find("div", class_="cmx-blog-page__content cmx-blog-page-content").find(
                "ul").find_all("li")

        ingredients = []
        for ingredient in ingredients_html:

            ingredient = clear_data(ingredient.text)
            ingredient = ingredient.strip(";. ").split("–")

            if len(ingredient) == 1 and ":" in ingredient[0]:
                ingredient = ingredient[0].split(":")

            if len(ingredient) == 1:
                ingredient = define_mount(ingredient[0])

            ingredients.append(Pair(ingredient[0].strip(), ingredient[1].strip()))

        coffe_type[coffe_name] = ingredients

    return coffe_type


def clear_data(dirty_data: str) -> str:
    return dirty_data.replace("\\xa0", "").replace("\\u200e", "").strip()


def define_mount(data: str) -> list[str]:
    input_data = data
    ingredients = data.split(" ")
    mount_index = None

    for i in range(len(ingredients)):
        if ingredients[i].isdigit():
            mount_index = i
            break
        elif "мл" in ingredients[i]:
            mount_index = i
            temp = ingredients.pop(mount_index)
            temp = temp.replace("мл", "").strip()
            ingredients.insert(mount_index, temp)
            ingredients.insert(mount_index + 1, "мл")

    mount = []
    try:
        mount.append(ingredients[mount_index])
        mount.append(ingredients[mount_index + 1])
        ingredients.pop(mount_index)
        ingredients.pop(mount_index)
    except Exception:
        return [input_data, "0"]

    return [" ".join(ingredients), " ".join(mount)]
