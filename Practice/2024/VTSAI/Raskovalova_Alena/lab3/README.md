## Лабораторные работы по "Валидация и тестирование систем ИИ"
Выполнили: <br>
Расковалова Алена, P4241 <br>
Строкова Анастасия, P4240


### Лабораторная работа 3
В рамках лабораторной работы был исследован параметр Discount factor, используемый в теории управления и обучения с подкреплением для оценки стоимости будущих вознаграждений. <br>
Выполнена следующая последовательность действий:
<li> Установка зависимостей и импорт необходимых пакетов
<li> Создание функции для извлечения значений из q-сети
<li> Создание функции для составления графика по значениям
<li> Создание окружения, модели, обучение модели, оценка модели до и после обучения, измерение времени обучения
<li> Создание функции для вычисления Q-values для некоторого набора предсказаний модели
<li> Проведение экспериментов с discount factor, discount_factors = [0.01,0.5,0.99]
<li> Подведение итогов
<br>

**Часть 1.LunarLander** <br>
[Код LunarLander](LR3_Lunar_Lander.ipynb) <br>

discount_factor = 0.01 <br>
До обучения модели с discount_factor = 0.01, mean_reward:-577.21 +/- 178.96 <br>
После обучения модели с discount_factor = 0.01, mean_reward:-179.04 +/- 132.94 <br>
<img src="Lunar_Lander_Convergence_0.01.png" width="500" height="500"/> <br>

discount_factor = 0.5 <br>
До обучения модели с discount_factor = 0.5, mean_reward:-890.24 +/- 445.62 <br>
После обучения модели с discount_factor = 0.5, mean_reward:-211.00 +/- 162.95 <br>
<img src="Lunar_Lander_Convergence_0.5.png" width="500" height="500"/> <br>

discount_factor = 0.99 <br>
До обучения модели с discount_factor = 0.99, mean_reward:-355.78 +/- 182.20 <br>
После обучения модели с discount_factor = 0.99, mean_reward:-126.10 +/- 111.77 <br>
<img src="Lunar_Lander_Convergence_0.99.png" width="500" height="500"/> <br>
Оптимальным является значении 0.5, так как средний reward при данном значении максимален.<br>
<br>

**Часть 2. Среда MountainCar** <br>
[Код MountainCar](LR3_Mountain_Car.ipynb) <br>

discount_factor = 0.01 <br>
До обучения модели с discount_factor = 0.01, mean_reward:-200.00 +/- 0.00 <br>
После обучения модели с discount_factor = 0.01, mean_reward:-200.00 +/- 0.00 <br>
<img src="Mountain_Car_Convergence_0.01.png" width="500" height="500"/>

discount_factor = 0.5 <br>
До обучения модели с discount_factor = 0.5, mean_reward:-200.00 +/- 0.00 <br>
После обучения модели с discount_factor = 0.5, mean_reward:-200.00 +/- 0.00 <br>
<img src="Mountain_Car_Convergence_0.5.png" width="500" height="500"/>

discount_factor = 0.99 <br>
До обучения модели с discount_factor = 0.5, mean_reward:-200.00 +/- 0.00 <br>
После обучения модели с discount_factor = 0.5, mean_reward:-200.00 +/- 0.00 <br>
<img src="Mountain_Car_Convergence_0.99.png" width="500" height="500"/>

На данную среду discount factor не оказывает влияния.<br>
<br>
