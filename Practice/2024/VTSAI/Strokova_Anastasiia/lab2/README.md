## Лабораторные работы по "Валидация и тестирование систем ИИ"
Выполнили: <br>
Расковалова Алена, P4241 <br>
Строкова Анастасия, P4240

### Лабораторная работа 2
В рамках лабораторной работы были использованы различные стратегии и влияние learning_rate на процесс обучения агента на примере сред Ant и Car Racing. <br>
Выполнена следующая последовательность действий:
<li> Установка библиотек для работы над лабораторной работой (Gym, Stable-Baselines3, PyVirtualDisplay, Xvfb)
<li> Создание окружения (Ant и Car Racing)
<li> Исследование различных стратегий (Epsilon-Greedy, Softmax, Upper Confidence Bound)
<li> Тестирование различных моделей (DDPG, SAC)
<li> Построение графика, который отображает процесс обучения этих моделей
<li> Исследование влияния Learning Rate
<br>

**Часть 1. Среда Ant** <br>
[Код Ant](LR2_Ant.py) <br>
<img src="LR2_Ant.PNG" width="500" height="500"/> <br>
<img src="LR2_Ant_Compare.PNG" width="500" height="500"/> <br>
<img src="LR2_Ant_Compare_Learning_Rate.PNG" width="500" height="500"/> <br>

<br>

**Часть 2. Среда CarRacing** <br>
[Код CarRacing](LR1_Car_Racing.py) <br>
<img src="LR2_Car_Racing.PNG" width="500" height="500"/>
<img src="LR2_Car_Racing_Compare.PNG" width="500" height="500"/>
<img src="LR2_Car_Racing_Compare_Learning_Rate.PNG" width="500" height="500"/>
<br>
P.S. Размер файла ipynb из Google Collab превышает допустимый размер загружаемого файла на GitHub, поэтому выгрузка прилагается в формате py.
