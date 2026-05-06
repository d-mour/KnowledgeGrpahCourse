## Лабораторная работа 5

### Выполнил Ефаринов Павел Андреевич

### Характеристика датасета

DBpedia50 - датасет, являющийся базой знаний описывающий информацию из википедии

### Процесс обучения

## Выполнение

Будем рассматривать модель ComplEx, обученную на 20 и 100 эпохах, а также HolE, обученную на 100 эпохах.

## Результаты

| Модель              | Time to learn (seconds) | Hits_1 | Hits5  | Hits_10 | Ближайшие узлы для A_Date_with_The_Smithereens (cosine)      | Ближайшие узлы для Bernt_Moen (cosine)                       |
| ------------------- | ----------------------- | ------ | ------ | ------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| ComplEx (20 epoch)  | 30                      | 0.0002 | 0.0009 | 0.0019  | 'A_Date_with_The_Smithereens', 'When_You_Come_Home', 'Sukhoi', 'Kevin_Brock_(American_football)' | 'Bernt_Moen', 'Live_for_You_(album)', 'Timetrap', 'Simon_Corbell' |
| ComplEx (100 epoch) | 167                     | 0.0035 | 0.0057 | 0.0078  | 'A_Date_with_The_Smithereens', 'Arup_Group', 'FC_Biel-Bienne', 'Ex_Norwegian' | 'Bernt_Moen', 'Neobaryssinus', 'Blue_Mode', 'Words_of_Wisdom_and_Hope' |
| HolE (100 epoch)    | 106                     | 0.2078 | 0.2460 | 0.2627  | 'A_Date_with_The_Smithereens', 'Joey_DeMaio', 'Open_Letter_(To_a_Landlord)', 'Jeff_Young' | 'Bernt_Moen', 'Sacredly_Agnezious', 'Don_Friedman', 'Doudou_Gouirand' |


## Выводы

В рамках работы модели ComplEx проигрывает по скорости обучения. Её конкурент, модель HolE, показала в разы превосходящий результат, при этом затратив на обучение меньше времени.
