import task_5_2
import task_2_1_3

inp = input("Введите вид обработки данных: (Вакансии или Статистика) - изменение в main")
if inp == "Статистика":
    task_2_1_3.get_result()
elif inp == "Вакансии":
    task_5_2.get_result()
else:
    print("Неверно введена команда!")
