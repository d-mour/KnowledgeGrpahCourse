## Лабораторная работа 6

Студент гр. 4215 Денисенков Артем
Студент гр. 4216 Лопатин Алексей

#### Результаты

В процессе работы было проведено обучение графовой нейронной сети на датасете 'countries' с использованием библиотеки PyKEEN. Модель ComplEx была обучена в течение разного количества эпох - от 1 до 250, что позволило взглянуть на динамику обучения модели.

Было замечено, что с каждой новой эпохой f1-метрика имеет тенденцию к увеличению, что говорит о повышении качества работы модели с увеличением количества эпох обучения.

В ходе работы также был изучен метод predict_target() из PyKEEN, который позволяет прогнозировать связи в графе. С его помощью были сделаны прогнозы относительно связи "americas - locatedin". Было обнаружено, что при малом количестве эпох обучения модели часто возникают ошибки в предсказаниях, но при увеличении количества эпох их количество уменьшается.
