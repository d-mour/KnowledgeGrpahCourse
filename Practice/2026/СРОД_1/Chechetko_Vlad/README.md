# Medical Multimodal KG Project v6 CXR

Проект собирает мультимодальный медицинский граф знаний:

- **Text**: BC5CDR через `bigbio/bc5cdr` — документы, токены, NER Chemical/Disease, нормализация, связи Chemical-Disease.
- **Audio**: CirCor heart sounds — WAV + TSV/HEA, сегменты S1/systole/S2/diastole.
- **Audio**: ICBHI respiratory sounds — WAV + TXT, события normal/crackle/wheeze/crackle+wheeze.
- **Image**: `hf-vision/chest-xray-pneumonia` — chest X-ray изображения Normal/Pneumonia, сгенерированная ROI-маска лёгочных полей, IMG_STRUCT/IMG_FINDING/IMG_ATTR.
- **KG**: RDF через `rdflib`, SPARQL-запросы, HTML-dashboard.

## Установка

```powershell
cd D:\medical_multimodal_kg_project_v6_cxr
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Быстрый тест только фото

```powershell
python .\download_and_build_full_kg.py `
  --skip-download `
  --skip-text `
  --skip-circor `
  --skip-icbhi `
  --image-dataset hf-vision/chest-xray-pneumonia `
  --image-split train `
  --limit-image-records 50
```

Проверка:

```powershell
(Import-Csv .\exports\csv\IMG_STRUCT.csv).Count
(Import-Csv .\exports\csv\IMG_FINDING.csv).Count
(Import-Csv .\exports\csv\IMG_ATTR.csv).Count
explorer .\app\data\images
```

## Финальная сборка всех модальностей

Запускать после того, как CirCor и ICBHI уже скачаны локально в `data/raw` или в старом проекте.

```powershell
python .\download_and_build_full_kg.py `
  --skip-download `
  --compute-audio-quality `
  --copy-audio-preview 60 `
  --image-dataset hf-vision/chest-xray-pneumonia `
  --image-split train `
  --limit-image-records 300
```

Не добавляй `--include-token-rdf` для финальной сборки, иначе RDF может стать слишком большим и снова упереться в память. Токены/леммы/POS/DEP всё равно сохраняются в CSV/JSON/XML.

## Если нужно докачать CirCor WAV

```powershell
python .\download_and_build_full_kg.py `
  --include-wav-download `
  --skip-text `
  --skip-icbhi `
  --skip-images
```

После этого снова запускай финальную сборку с `--skip-download`.

## Dashboard

```powershell
python -m http.server 8000 -d app
```

Открыть:

```text
http://localhost:8000
```

## Что должно появиться

```text
exports/csv/TXT_DOC.csv
exports/csv/TXT_NER.csv
exports/csv/TXT_REL.csv
exports/csv/AUD_META.csv
exports/csv/AUD_EVT.csv
exports/csv/IMG_STRUCT.csv
exports/csv/IMG_FINDING.csv
exports/csv/IMG_ATTR.csv
exports/csv/MM_ALIGN.csv
exports/rdf/medical_kg.ttl
exports/rdf/medical_kg.nt
exports/sparql/*.rq
exports/sparql/*_result.csv
app/index.html
app/data/images/*.png
```

## Проверка counts

```powershell
(Import-Csv .\exports\csv\TXT_DOC.csv).Count
(Import-Csv .\exports\csv\TXT_NER.csv).Count
(Import-Csv .\exports\csv\TXT_REL.csv).Count
(Import-Csv .\exports\csv\AUD_META.csv).Count
(Import-Csv .\exports\csv\IMG_STRUCT.csv).Count
(Import-Csv .\exports\csv\MM_ALIGN.csv).Count
```

## SPARQL/BOM фикс

Если вручную редактировал `.rq`, можно перезапустить запросы:

```powershell
python .\rerun_sparql_fixed.py
```

