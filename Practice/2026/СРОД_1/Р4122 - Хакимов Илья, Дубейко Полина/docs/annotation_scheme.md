# Аннотационная схема: Мультимодальное управление IoT-устройствами (голос + жесты)

## 1. Общее описание предметной области

**Предметная область:** Управление устройствами умного дома через мультимодальные команды (голос + жесты)

**Задача системы:** Создание интеллектуальной системы распознавания и понимания мультимодальных команд пользователя для управления IoT-устройствами. Система объединяет голосовые команды (аудио) и жесты (видео) для повышения точности и надёжности распознавания.

**Почему нужны данные:**
- Аудио отдельно не справляется с шумом, реверберацией, перекрытием речи
- Видео отдельно не работает при плохом освещении, частичном перекрытии рук
- Мультимодальный подход (аудио + видео) повышает точность на 15–25%
- Необходимы размеченные данные для обучения ML-моделей интент-классификации и жестовой классификации

**Источники данных:**
- Собственные записи: 100 аудиофайлов (ogg) — 50 мужских, 50 женских голосовых команд
- Видеозаписи жестов: 80 видеофайлов (webm) — 6 типов жестов, 2 ракурса камеры

## 2. Уровни разметки

### 2.1 Архитектура многоуровневой разметки

| Уровень | Тип разметки | Модальность | Формат | Визуализация | ID сущности |
|---------|-------------|-------------|--------|-------------|-------------|
| Акустико-фонетический | Сегментация речи, выделение пауз | Аудиосигнал | Praat TextGrid | Praat, WaveSurfer | speaker_id, utterance_id, segment_id |
| Лексический | Токенизация, лемматизация | Текстовая транскрипция | CoNLL-U / TSV | WebAnno, INCEpTION | speaker_id, utter_id, token_id |
| Морфосинтаксический | Частеречная разметка (POS) | Текстовая транскрипция | CoNLL-U | WebAnno, UD tools | speaker_id, utter_id, token_id |
| Синтаксический | Дерево зависимостей | Текстовая транскрипция | CoNLL-U | WebAnno, Brat | speaker_id, utter_id, token_id |
| Семантический (интент) | Классификация намерений | Текст + Аудио (просодия) | JSON / TSV | Custom dashboard | speaker_id, utter_id, intent_id |
| Семантический (слоты) | NER + нормализация значений | Текстовая транскрипция | IOB2 / JSON | WebAnno, INCEpTION | speaker_id, utter_id, slot_id |
| **Видео-кадровый** | **Сегментация видео на кадры** | **Видеопоток** | **JSON** | **CVAT, VIA** | **video_id, frame_id** |
| **Видео-жестовый** | **Классификация жеста, bounding box** | **Видеопоток** | **JSON / COCO** | **CVAT, Label Studio** | **video_id, gesture_id** |
| **Кросс-модальный** | **Связи audio ↔ video ↔ text** | **Мета-уровень** | **RDF / JSON-LD** | **Граф знаний** | **multimodal_event_id** |

### 2.2 Аудио-уровни (1–6) — подробно

**Акустико-фонетический уровень:**
- Voice Activity Detection (VAD)
- Начало/конец речевого сигнала
- Паузы между словами
- Формат: Praat TextGrid с тирами: `words`, `phonemes`, `VAD`

**Лексический уровень:**
- Токенизация: разделение на слова
- Лемматизация: приведение к начальной форме
- Правила ID: `utt_001_t01`, без дефисов

**Морфосинтаксический уровень:**
- Universal POS tags (UD Russian)
- Примеры: VERB (повелительное наклонение), NOUN (винительный падеж), ADP (предлог)

**Синтаксический уровень:**
- Дерево зависимостей в формате CoNLL-U
- `root` → `obj` → `nmod` → `case`

**Семантический — Интенты:**
- Иерархия: `iot_command` → `device_control` → `turn_on` / `turn_off` / `set_value` / `change_mode`
- Дополнительно: `query_status`, `system_meta`

**Семантический — Слоты:**
- IOB2 разметка
- Типы: `DEVICE`, `LOCATION`, `VALUE`, `MODE`, `TIME`

### 2.3 Видео-уровни (7–8) — подробно

**Уровень 7: Видео-кадровый (Frame Level)**
- Сегментация видео на кадры (FPS=30)
- Для каждого кадра: timestamp, frame_id
- Разметка активности жеста: `gesture_active` (True/False)
- Инструменты: OpenCV, CVAT

**Уровень 8: Видео-жестовый (Gesture Level)**
- Классификация жеста: `круг`, `ладоньстоп`, `свайп`, `хлопок`, `щелчок`, `поднятиеруки`
- Bounding box руки/кисти: `x`, `y`, `width`, `height`
- Confidence score (0.0–1.0)
- Ключевые точки: MediaPipe Hands (21 точки)
- Ракурс камеры: `лицо` (фронтальный), `сбоку` (боковой)
- Инструменты: MediaPipe, CVAT, Label Studio
- Формат: JSON (COCO-like)

### 2.4 Кросс-модальный уровень (9)

**Связи между модальностями:**
- `aligns_with`: аудио-сегмент ↔ текстовый токен (по времени)
- `correspondsTo`: аудиокоманда ↔ видеожест (по диктору + устройству)
- `hasArgument`: интент ↔ слот
- `realizes`: синтаксический узел ↔ семантический интент

**Мультимодальная логика фьюжна:**
- Аудио как триггер (always-on, дешёво по энергии)
- Видео как валидатор (камера просыпается по аудио-событию)
- Late fusion: скоры классификаторов перемножаются, threshold = 0.6

## 3. Детализация уровней разметки

### 3.1 Пример аудио-разметки (Praat TextGrid)

```
IntervalTier "words"
0.0     0.5     #silence#
0.5     1.2     "включи"
1.2     1.5     #pause#
1.5     2.1     "кондиционер"
2.1     2.3     #silence#
```

### 3.2 Пример текстовой разметки (CoNLL-U)

```
1  Включи    включить   VERB  _  Mood=Imp|Number=Sing|Person=2  0  root  _  _
2  кондиционер  кондиционер  NOUN  _  Animacy=Inan|Case=Acc|Gender=Masc|Number=Sing  1  obj  _  _
```

### 3.3 Пример IOB2-разметки слотов

| token | tag | normalized_value |
|-------|-----|-----------------|
| Включи | O | — |
| кондиционер | B-DEVICE | conditioner |
| на | O | — |
| двадцать | B-VALUE | 22 |
| два | I-VALUE | 22 |
| градуса | I-VALUE | 22 |

### 3.4 Пример видео-разметки (JSON)

```json
{
  "annotation_id": "video_001",
  "file_path": "video/man/2/conditioner/круг_лицо.webm",
  "speaker": "man",
  "speaker_id": 2,
  "device": "conditioner",
  "gesture_type": "круг",
  "gesture_description": "Круговое вращение ладонью",
  "camera_angle": "лицо",
  "duration_sec": 3.5,
  "fps": 30,
  "frame_count": 105,
  "gesture_start_sec": 0.8,
  "gesture_end_sec": 2.5,
  "frames": [
    {
      "frame_id": 24,
      "timestamp": 0.8,
      "gesture_active": true,
      "bbox": {"x": 220, "y": 180, "width": 120, "height": 120},
      "confidence": 0.92
    }
  ]
}
```

## 4. Структура датасета

```
dataset/
├── audio/
│   ├── man/2/
│   │   ├── conditioner/ (*.ogg)
│   │   ├── curtains/ (*.ogg)
│   │   ├── lamp/ (*.ogg)
│   │   ├── lock/ (*.ogg)
│   │   └── tv/ (*.ogg)
│   └── woman/1/
│       ├── conditioner/ (*.ogg)
│       ├── curtains/ (*.ogg)
│       ├── lamp/ (*.ogg)
│       ├── lock/ (*.ogg)
│       └── tv/ (*.ogg)
└── video/
    ├── man/2/
    │   ├── conditioner/ (*.webm)
    │   ├── curtains/ (*.webm)
    │   ├── lamp/ (*.webm)
    │   ├── lock/ (*.webm)
    │   └── tv/ (*.webm)
    └── woman/1/
        ├── conditioner/ (*.webm)
        ├── curtains/ (*.webm)
        ├── lamp/ (*.webm)
        ├── lock/ (*.webm)
        └── tv/ (*.webm)
```

**Статистика:**
- Аудио: 100 файлов (5 устройств × 10 команд × 2 диктора)
- Видео: 80 файлов (5 устройств × жесты × 2 ракурса × 2 диктора)
- Дикторы: 2 (мужской id=2, женский id=1)
- Устройства: 5 (conditioner, curtains, lamp, lock, tv)
- Жесты: 6 (круг, ладоньстоп, свайп, хлопок, щелчок, поднятиеруки)

## 5. Форматы хранения

### 5.1 Текстовая модальность
- **Формат:** TSV (CoNLL-U совместимый)
- **Файл:** `text_annotations.tsv`
- **Колонки:** utterance_id, token_id, form, lemma, upos, xpos, feats, head, deprel, iob_tag, intent, slot_type

### 5.2 Аудио модальность
- **Формат:** CSV
- **Файл:** `audio_annotations.csv`
- **Колонки:** annotation_id, file_path, speaker, speaker_id, gender, device, command_file, text, intent, duration_sec, sample_rate, mfcc_mean, zero_crossing_rate, spectral_centroid, word_segments_json

### 5.3 Видео модальность
- **Формат:** JSON (COCO-like)
- **Файл:** `video_annotations.json`
- **Структура:** список объектов с полями annotation_id, file_path, speaker, device, gesture_type, gesture_description, camera_angle, duration_sec, fps, frame_count, gesture_start_sec, gesture_end_sec, frames[]

### 5.4 Кросс-модальный граф
- **Формат:** RDF (Turtle / RDF/XML)
- **Файлы:** `iot_multimodal_graph.ttl`, `iot_multimodal_graph.rdf`
- **Онтология:** `smart_home_ontology.rdf` (OWL)
- **Библиотека:** rdflib
- **Запросы:** SPARQL

## 6. Онтология предметной области

**Пространство имён:** `http://www.semanticweb.org/smart_home/ontologies/2025/4/iot-multimodal#`

**Классы:**
- `AudioCommand` — голосовая команда
- `VideoGesture` — видео с жестом
- `IoTDevice` — устройство (подклассы: Conditioner, Curtains, Lamp, Lock, TV)
- `GestureType` — тип жеста (подклассы: ClapGesture, SnapGesture, SwipeGesture, CircleGesture, StopGesture, WakeGesture)
- `Intent` — намерение
- `Slot` — параметр (подклассы: DeviceSlot, ValueSlot, ModeSlot, TimeSlot)
- `Speaker` — диктор
- `AudioAnnotation`, `VideoAnnotation`, `TextAnnotation` — аннотации

**Object Properties:**
- `hasDevice` — связь с устройством
- `hasGestureType` — тип жеста
- `hasIntent` — намерение
- `hasSlot` — параметр
- `performedBy` — исполнитель
- `hasAudioAnnotation`, `hasVideoAnnotation` — аннотации
- `correspondsTo` — кросс-модальная связь

**Data Properties:**
- `text`, `filePath`, `duration`, `confidence`, `timestamp`, `speakerId`, `gender`, `gestureDescription`, `cameraAngle`, `slotType`, `slotValue`

## 7. SPARQL-запросы

**Пример 1:** Все команды для лампы
```sparql
PREFIX iot: <http://www.semanticweb.org/smart_home/ontologies/2025/4/iot-multimodal#>
PREFIX ex: <http://example.org/smart_home#>
SELECT ?command ?text ?intent
WHERE {
  ?command a iot:AudioCommand ;
           iot:hasDevice ex:lamp ;
           iot:text ?text ;
           iot:hasIntent ?intent .
}
```

**Пример 2:** Cross-modal связи audio ↔ video
```sparql
SELECT ?audio ?video ?device
WHERE {
  ?audio a iot:AudioCommand ;
         iot:correspondsTo ?video ;
         iot:hasDevice ?device .
  ?video a iot:VideoGesture .
}
```

**Пример 3:** Распределение по интентам
```sparql
SELECT ?intent (COUNT(?cmd) AS ?count)
WHERE {
  ?cmd a iot:AudioCommand ;
       iot:hasIntent ?intent .
}
GROUP BY ?intent
ORDER BY DESC(?count)
```

## 8. Золотой стандарт и контроль качества

**Метрики согласия:**
- Inter-annotator agreement: Cohen's κ для интентов (>0.8)
- Fleiss' κ для IOB2-слотов
- Krippendorff's α для видео-bounding boxes (IoU > 0.85)

**Визуальная проверка:**
- Прослушивание аудио с наложенной разметкой в Praat
- Просмотр видео с overlaid bounding boxes в CVAT

**Кросс-валидация:**
- 5-fold на уровне спикеров (стратификация по gender + device)

## 9. Применение в системе

**Пайплайн мультимодального управления:**
1. Микрофон (always-on) → Audio Trigger (VAD + Onset Detection)
2. Камера (sleep mode) → Video Validator (MediaPipe + Optical Flow)
3. Fusion Layer (late fusion, threshold 0.6)
4. Device Router → Lamp / Conditioner / Curtains / TV / Lock

**Извлечённые признаки:**
- Аудио: MFCC, Spectral Centroid, Zero-Crossing Rate, Onset Detection
- Видео: MediaPipe Hands (21 keypoints), Optical Flow, Bounding Box trajectory
