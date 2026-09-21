# Оценка гитар по текстам, изображениям и аудио

Учебный проект по курсу «Структурирование, разметка и обогащение данных». 

## Задача и система

Система помогает подобрать примеры электрогитар по конструкции: найти модель, прочитать о звукоснимателях и управлении, увидеть соответствующие детали и перейти к звуковой демонстрации. Пользователь получает ответ со ссылками на исходные материалы. Из этих неодинаково записанных демонстраций нельзя обоснованно выводить рейтинг качества гитар.

Объект — **модель с конкретной версией**, а не доказанно один физический экземпляр. Текст, изображение и аудио связываются по `guitar_id`. Для каждого объекта выбран один обзор Premier Guitar и прикреплённая к нему демонстрация официального канала издания в SoundCloud.

## Что собрано

**10 объектов, 10 текстов, 10 фотографий и 10 полных аудиозаписей.** Первые пять моделей удобнее для начальной подробной разметки: к их аудио даны наиболее полезные пояснения. Остальные пять также имеют все три модальности; неизвестные настройки отмечаются явно.

Тексты — составленные для проекта русскоязычные описания по фактам обзоров

| ID | Модель | Источники | Слов в TXT | Аудио, с |
|---|---|---|---:|---:|
| GTR001 | Reverend Six Gun HPP | [Обзор](https://www.premierguitar.com/gear/reviews/reverend-six-gun-hpp-review) · [Аудио](https://soundcloud.com/premierguitar/clip-1-reverend-six-gun-hpp) | 136 | 82.6 |
| GTR002 | Harmony Comet | [Обзор](https://www.premierguitar.com/gear/reviews/harmony-comet-the-premier-guitar-review) · [Аудио](https://soundcloud.com/premierguitar/harmony-comet-review-premier-guitar) | 132 | 102.1 |
| GTR003 | Squier Contemporary Jaguar HH-ST | [Обзор](https://www.premierguitar.com/gear/reviews/squier-contemporary-jaguar) · [Аудио](https://soundcloud.com/premierguitar/squier-contemporary-jaguar-hh-st) | 137 | 120.0 |
| GTR004 | Ernie Ball Music Man Dustin Kensrue Artist Series StingRay | [Обзор](https://www.premierguitar.com/gear/reviews/ernie-ball-music-man-dustin-kensrue-stingray) · [Аудио](https://soundcloud.com/premierguitar/clip-1-clean-ernie-ball-music) | 145 | 64.9 |
| GTR005 | Schecter Sun Valley Super Shredder Exotic Hardtail Black Limba | [Обзор](https://www.premierguitar.com/gear/reviews/schecter-sun-valley-super-shredder-exotic-hardtail-review) · [Аудио](https://soundcloud.com/premierguitar/clip-2-schecter-sun-valley) | 143 | 75.9 |
| GTR006 | Eastman Romeo LA | [Обзор](https://www.premierguitar.com/gear/reviews/eastman-guitars-romeo-la) · [Аудио](https://soundcloud.com/premierguitar/clip-1-clean-eastman-romeo-la) | 141 | 45.5 |
| GTR007 | Fender Noventa Stratocaster | [Обзор](https://www.premierguitar.com/gear/reviews/fender-noventa-stratocaster) · [Аудио](https://soundcloud.com/premierguitar/fender-noventa-strat) | 139 | 183.7 |
| GTR008 | Reverend Flatroc Bigsby | [Обзор](https://www.premierguitar.com/gear/reviews/reverend-flatroc-bigsby) · [Аудио](https://soundcloud.com/premierguitar/reverend-flatroc-bigsby-review) | 136 | 115.5 |
| GTR009 | Squier Paranormal Super-Sonic | [Обзор](https://www.premierguitar.com/gear/reviews/squier-paranormal-super-sonic) · [Аудио](https://soundcloud.com/premierguitar/squier-paranormal-super-sonic-review-premierguitar) | 142 | 139.0 |
| GTR010 | Gretsch G2622T-P90 Streamliner | [Обзор](https://www.premierguitar.com/gear/reviews/gretsch-g2622t-p90-streamliner) · [Аудио](https://soundcloud.com/premierguitar/gretsch-streamliner-center-block-p90-main) | 135 | 112.4 |

Общая длительность аудио: **17.4 мин**. Авторы и даты обзоров, версии моделей, прямые URL изображений, параметры аудио, ограничения и SHA-256 всех файлов находятся в [реестре материалов](data/manifest.json). 

## Структура папки

```text
README.md
presentation.pptx            # 11 слайдов: проект, схема, разметка и результаты
.gitignore
data/
  manifest.json             # ID, источники, происхождение, параметры и права
  text/                     # GTR001.txt … GTR010.txt, UTF-8
  images/                   # десять фотографий, JPG/PNG
  audio/                    # GTR001.wav … GTR010.wav
annotations/
  text/                     # CoNLL-U, WebAnno TSV 3 и архив INCEpTION
  images/                   # Label Studio: 10 фото, 80 рамок, JSON
  audio/                    # 10 Praat TextGrid
docs/
  annotation_schema.md      # схема и правила по шагам ЛР2
code/
  collect.py                # восстановление отсутствующих медиа
  verify.py                 # проверка комплекта
  verify_text_annotations.py # проверка аннотаций и статистика
  requirements.txt
ontology/
  knowledge_graph.rdf
  ontologe.rdf
```

Текстовая разметка завершена в INCEpTION: 10 документов, 1 595 токенов с UPOS, 121 упоминание сущностей и 98 связей HAS_PART.  Результаты включают CoNLL-U, WebAnno TSV 3 и штатный архив проекта. Все 10 изображений размечены в Label Studio: 80 рамок с ID и признаками. Для аудио подготовлены 10 TextGrid. Исходные файлы и аннотации хранятся раздельно. 


## Примеры и аннотационная схема

- Текст: [описание GTR001](data/text/GTR001.txt), модель и три звукоснимателя.
- Изображение: [фотография GTR001](data/images/GTR001.jpg), видимые датчики и органы управления.
- Аудио: [GTR004, чистый звук](data/audio/GTR004.wav), в подписи источника указаны переходы между датчиками на 0, 16 и 34 с.
- [Аннотационная схема](docs/annotation_schema.md): матрица объектов и модальностей, уровни, метки, признаки, координаты, форматы и верификация.
- [Презентация](presentation.pptx): одиннадцать слайдов: проект, таблица уровней, правила разметки, пример INCEpTION, результаты текста, окно Praat, результаты аудио, пример Label Studio и результаты изображений.


## Аудио: комплект для проверки в Praat

Подготовлены **10 TextGrid с четырьмя слоями**, полная длительность **1041,674 с (17 мин 21,67 с)**. В сохранённых файлах **15 кандидатов крупных фраз и 29 кандидатов пауз**. 

 [Скрипт Praat](code/open_audio.praat) открывает выбранную запись с разметкой. `python3 code/prepare_audio.py --stats` пересчитывает числа из TextGrid.

## Изображения: результаты Label Studio

В Label Studio Community сохранены **10 фотографий и 80 рамок**: GUITAR — 10, PICKUP — 21, BRIDGE — 13, CONTROL — 36. [Штатный экспорт](annotations/images/label_studio.json), [конфигурация](annotations/images/label_config.xml) содержат признаки областей, статистику и порядок восстановления.

## Составлена онтология в Protégé и SPARQL-запросы
