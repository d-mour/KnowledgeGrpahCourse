import xml.etree.ElementTree as ET
import csv
import json
import os
from urllib.parse import quote
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD

# Создаём граф
g = Graph()

# Определяем пространства имён
EX = Namespace("http://example.org/experiment/")
SIGNAL = Namespace("http://example.org/signal/")
ANNOTATION = Namespace("http://example.org/annotation/")
PHASE = Namespace("http://example.org/phase/")
MODE = Namespace("http://example.org/mode/")
PARAM = Namespace("http://example.org/parameter/")

g.bind("ex", EX)
g.bind("signal", SIGNAL)
g.bind("ann", ANNOTATION)
g.bind("phase", PHASE)
g.bind("mode", MODE)
g.bind("param", PARAM)


def safe_uri(text):
    """Преобразует текст в безопасный для URI формат"""
    # Заменяем русские символы и пробелы на безопасные
    import re
    # Заменяем кириллицу на латиницу (простая транслитерация)
    cyrillic_to_latin = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }

    # Транслитерация
    result = ''.join(cyrillic_to_latin.get(c, c) for c in text)
    # Заменяем пробелы и другие небезопасные символы на подчёркивания
    result = re.sub(r'[^a-zA-Z0-9_-]', '_', result)
    # Убираем множественные подчёркивания
    result = re.sub(r'_+', '_', result)
    return result


# Список экспериментов с их путями
experiments = [
    {
        "id": 0,
        "paths": {
            "signal": "id_0/img_analyses/signal.xml",
            "weight": "id_0/img_analyses/weight.xml",
            "mode": "id_0/sound_analyses/mode.csv",
            "phase": "id_0/sound_analyses/phase.csv",
            "params": "id_0/parameters.json"
        }
    },
    {
        "id": 40,
        "paths": {
            "signal": "id_40/img_analyses/signal.xml",
            "weight": "id_40/img_analyses/weight.xml",
            "mode": "id_40/sound_analyses/mode.csv",
            "phase": "id_40/sound_analyses/phase.csv",
            "params": "id_40/parameters.json"
        }
    },
    {
        "id": 60,
        "paths": {
            "signal": "id_60/img_analyses/signal.xml",
            "weight": "id_60/img_analyses/weight.xml",
            "mode": "id_60/sound_analyses/mode.csv",
            "phase": "id_60/sound_analyses/phase.csv",
            "params": "id_60/parameters.json"
        }
    }
]


def process_parameters(exp_uri, params_file):
    """Обработка параметров эксперимента"""
    try:
        if not os.path.exists(params_file):
            print(f"  Предупреждение: файл параметров {params_file} не найден")
            return

        with open(params_file, "r", encoding='utf-8') as f:
            params = json.load(f)

        for key, value in params.items():
            safe_key = safe_uri(key)
            param_uri = PARAM[f"{safe_key}_{exp_uri.split('/')[-1]}"]
            g.add((exp_uri, EX.hasParameter, param_uri))
            g.add((param_uri, RDF.type, EX.Parameter))
            g.add((param_uri, EX.parameterName, Literal(key)))
            g.add((param_uri, EX.parameterValue, Literal(value, datatype=XSD.float)))
    except Exception as e:
        print(f"  Ошибка при обработке {params_file}: {e}")


def process_phases(exp_uri, phase_file):
    """Обработка фаз эксперимента"""
    try:
        if not os.path.exists(phase_file):
            print(f"  Предупреждение: файл фаз {phase_file} не найден")
            return

        with open(phase_file, "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                start = float(row["start_time"])
                end = float(row["end_time"])
                label = row["label"]
                safe_label = safe_uri(label)
                exp_id = exp_uri.split('/')[-1]
                phase_uri = PHASE[f"phase_{exp_id}_{safe_label}_{idx}"]
                g.add((phase_uri, RDF.type, PHASE.Phase))
                g.add((phase_uri, PHASE.startTime, Literal(start, datatype=XSD.float)))
                g.add((phase_uri, PHASE.endTime, Literal(end, datatype=XSD.float)))
                g.add((phase_uri, PHASE.label, Literal(label)))
                g.add((exp_uri, EX.hasPhase, phase_uri))
    except Exception as e:
        print(f"  Ошибка при обработке {phase_file}: {e}")


def process_modes(exp_uri, mode_file):
    """Обработка режимов эксперимента"""
    try:
        if not os.path.exists(mode_file):
            print(f"  Предупреждение: файл режимов {mode_file} не найден")
            return

        with open(mode_file, "r", encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                start = float(row["start_time"])
                end = float(row["end_time"])
                label = row["label"]
                safe_label = safe_uri(label)
                exp_id = exp_uri.split('/')[-1]
                mode_uri = MODE[f"mode_{exp_id}_{safe_label}_{idx}"]
                g.add((mode_uri, RDF.type, MODE.Mode))
                g.add((mode_uri, MODE.startTime, Literal(start, datatype=XSD.float)))
                g.add((mode_uri, MODE.endTime, Literal(end, datatype=XSD.float)))
                g.add((mode_uri, MODE.label, Literal(label)))
                g.add((exp_uri, EX.hasMode, mode_uri))
    except Exception as e:
        print(f"  Ошибка при обработке {mode_file}: {e}")


def process_signal_annotations(exp_uri, signal_file):
    """Обработка аннотаций сигнала из signal.xml"""
    try:
        if not os.path.exists(signal_file):
            print(f"  Предупреждение: файл сигнала {signal_file} не найден")
            return

        tree = ET.parse(signal_file)
        root = tree.getroot()
        image = root.find("image")
        if image is not None:
            image_id = image.get("id")
            image_name = image.get("name")
            width = int(float(image.get("width")))
            height = int(float(image.get("height")))

            exp_id = exp_uri.split('/')[-1]
            img_uri = SIGNAL[f"image_{exp_id}_{image_id}"]
            g.add((img_uri, RDF.type, SIGNAL.Image))
            g.add((img_uri, SIGNAL.name, Literal(image_name)))
            g.add((img_uri, SIGNAL.width, Literal(width, datatype=XSD.integer)))
            g.add((img_uri, SIGNAL.height, Literal(height, datatype=XSD.integer)))
            g.add((exp_uri, EX.hasSignal, img_uri))

            # Обработка всех аннотаций на изображении
            ann_counter = 0
            for elem in image:
                elem_type = safe_uri(elem.tag)
                elem_label = safe_uri(elem.get("label", "unknown"))

                ann_uri = ANNOTATION[f"ann_{exp_id}_{elem_type}_{elem_label}_{ann_counter}"]
                g.add((ann_uri, RDF.type, ANNOTATION.Annotation))
                g.add((ann_uri, ANNOTATION.type, Literal(elem.tag)))
                g.add((ann_uri, ANNOTATION.label, Literal(elem.get("label"))))
                g.add((ann_uri, ANNOTATION.source, Literal(elem.get("source"))))

                if elem.get("occluded") == "1":
                    g.add((ann_uri, ANNOTATION.occluded, Literal(True, datatype=XSD.boolean)))
                else:
                    g.add((ann_uri, ANNOTATION.occluded, Literal(False, datatype=XSD.boolean)))

                if elem.tag == "box":
                    xtl = float(elem.get("xtl"))
                    ytl = float(elem.get("ytl"))
                    xbr = float(elem.get("xbr"))
                    ybr = float(elem.get("ybr"))
                    g.add((ann_uri, ANNOTATION.xtl, Literal(xtl, datatype=XSD.float)))
                    g.add((ann_uri, ANNOTATION.ytl, Literal(ytl, datatype=XSD.float)))
                    g.add((ann_uri, ANNOTATION.xbr, Literal(xbr, datatype=XSD.float)))
                    g.add((ann_uri, ANNOTATION.ybr, Literal(ybr, datatype=XSD.float)))

                elif elem.tag == "polygon":
                    points = elem.get("points")
                    g.add((ann_uri, ANNOTATION.points, Literal(points)))

                elif elem.tag == "polyline":
                    points = elem.get("points")
                    g.add((ann_uri, ANNOTATION.points, Literal(points)))

                g.add((img_uri, SIGNAL.hasAnnotation, ann_uri))
                ann_counter += 1
    except Exception as e:
        print(f"  Ошибка при обработке {signal_file}: {e}")


def process_weight_annotations(exp_uri, weight_file):
    """Обработка треков и аннотаций из weight.xml"""
    try:
        if not os.path.exists(weight_file):
            print(f"  Предупреждение: файл весов {weight_file} не найден")
            return

        tree = ET.parse(weight_file)
        root = tree.getroot()
        exp_id = exp_uri.split('/')[-1]

        for track in root.findall(".//track"):
            track_id = track.get("id")
            track_label = track.get("label")
            track_source = track.get("source")

            safe_label = safe_uri(track_label) if track_label else "unknown"
            track_uri = ANNOTATION[f"track_{exp_id}_{safe_label}_{track_id}"]
            g.add((track_uri, RDF.type, ANNOTATION.Track))
            g.add((track_uri, ANNOTATION.label, Literal(track_label)))
            g.add((track_uri, ANNOTATION.source, Literal(track_source)))

            exp_track_uri = EX[f"track_{exp_id}_{track_id}"]
            g.add((exp_track_uri, RDF.type, EX.Track))
            g.add((exp_track_uri, EX.hasTrackAnnotation, track_uri))
            g.add((exp_uri, EX.hasTrack, exp_track_uri))

            for poly in track.findall("polygon"):
                try:
                    frame = int(poly.get("frame"))
                    points = poly.get("points")
                    keyframe = poly.get("keyframe") == "1"
                    outside = poly.get("outside") == "1"
                    occluded = poly.get("occluded") == "1"

                    shape_uri = ANNOTATION[f"polygon_{exp_id}_{track_id}_{frame}"]
                    g.add((shape_uri, RDF.type, ANNOTATION.Polygon))
                    g.add((shape_uri, ANNOTATION.frame, Literal(frame, datatype=XSD.integer)))
                    g.add((shape_uri, ANNOTATION.points, Literal(points)))
                    g.add((shape_uri, ANNOTATION.keyframe, Literal(keyframe, datatype=XSD.boolean)))
                    g.add((shape_uri, ANNOTATION.outside, Literal(outside, datatype=XSD.boolean)))
                    g.add((shape_uri, ANNOTATION.occluded, Literal(occluded, datatype=XSD.boolean)))
                    g.add((track_uri, ANNOTATION.hasShape, shape_uri))
                except Exception as e:
                    continue

        # Добавляем информацию об исходном размере
        orig_size = root.find(".//original_size")
        if orig_size is not None:
            orig_width = int(orig_size.get("width"))
            orig_height = int(orig_size.get("height"))
            g.add((exp_uri, EX.originalWidth, Literal(orig_width, datatype=XSD.integer)))
            g.add((exp_uri, EX.originalHeight, Literal(orig_height, datatype=XSD.integer)))

        meta = root.find(".//meta")
        if meta is not None:
            job = meta.find(".//job")
            if job is not None:
                job_id = job.get("id") or job.find("id").text if job.find("id") is not None else None
                if job_id:
                    g.add((exp_uri, EX.jobId, Literal(job_id)))

                created = job.find("created")
                if created is not None:
                    g.add((exp_uri, EX.created, Literal(created.text)))

                updated = job.find("updated")
                if updated is not None:
                    g.add((exp_uri, EX.updated, Literal(updated.text)))

                owner = job.find(".//owner/username")
                if owner is not None:
                    g.add((exp_uri, EX.owner, Literal(owner.text)))

    except Exception as e:
        print(f"  Ошибка при обработке {weight_file}: {e}")


# Основной цикл обработки экспериментов
print("Начинаем обработку экспериментов...")
print("=" * 60)

for exp in experiments:
    exp_id = exp["id"]
    exp_uri = EX[f"experiment_{exp_id}"]
    paths = exp["paths"]

    print(f"\nОбработка эксперимента ID = {exp_id}")
    print(f"  Путь к данным: id_{exp_id}/")

    # Добавляем информацию об эксперименте
    g.add((exp_uri, RDF.type, EX.Experiment))
    g.add((exp_uri, EX.hasId, Literal(exp_id, datatype=XSD.integer)))

    # Обрабатываем параметры
    print("  Обработка параметров...")
    process_parameters(exp_uri, paths["params"])

    # Обрабатываем фазы
    print("  Обработка фаз...")
    process_phases(exp_uri, paths["phase"])

    # Обрабатываем режимы
    print("  Обработка режимов...")
    process_modes(exp_uri, paths["mode"])

    # Обрабатываем аннотации сигнала
    print("  Обработка аннотаций сигнала...")
    process_signal_annotations(exp_uri, paths["signal"])

    # Обрабатываем веса и треки
    print("  Обработка весов и треков...")
    process_weight_annotations(exp_uri, paths["weight"])

    print(f"  Завершена обработка эксперимента {exp_id}")

print("\n" + "=" * 60)
print("Все эксперименты обработаны!")

# Сохраняем граф в файл
try:
    output_file = "all_experiments.ttl"
    g.serialize(destination=output_file, format="turtle")
    print(f"\nRDF-граф сохранён в {output_file}")
    print(f"Всего троек в графе: {len(g)}")

    # Статистика по экспериментам
    print("\nСтатистика по экспериментам:")
    print("-" * 40)
    for exp in experiments:
        exp_id = exp["id"]
        exp_uri = EX[f"experiment_{exp_id}"]

        # Подсчитываем различные типы данных для эксперимента
        phases = list(g.subjects(EX.hasPhase, None))
        modes = list(g.subjects(EX.hasMode, None))
        signals = list(g.subjects(EX.hasSignal, None))
        tracks = list(g.subjects(EX.hasTrack, None))
        params = list(g.subjects(EX.hasParameter, None))

        # Фильтруем только относящиеся к текущему эксперименту
        phases = [s for s in phases if str(s).startswith(str(exp_uri))]
        modes = [s for s in modes if str(s).startswith(str(exp_uri))]
        signals = [s for s in signals if str(s).startswith(str(exp_uri))]
        tracks = [s for s in tracks if str(s).startswith(str(exp_uri))]
        params = [s for s in params if str(s).startswith(str(exp_uri))]

        print(f"Эксперимент ID {exp_id}:")
        print(f"  - Фаз: {len(phases)}")
        print(f"  - Режимов: {len(modes)}")
        print(f"  - Сигналов: {len(signals)}")
        print(f"  - Треков: {len(tracks)}")
        print(f"  - Параметров: {len(params)}")

except Exception as e:
    print(f"\nОшибка при сохранении графа: {e}")
    print("Пробуем сохранить в формате XML...")
    try:
        output_file = "all_experiments.xml"
        g.serialize(destination=output_file, format="xml")
        print(f"RDF-граф сохранён в {output_file} в формате XML")
    except Exception as e2:
        print(f"Не удалось сохранить граф: {e2}")