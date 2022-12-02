import job, statistic

job_or_statistic = input('Введите что то для печати: ')
if job_or_statistic == 'Вакансии':
    job.print_job_table()
elif job_or_statistic == 'Статистика':
    statistic.Main()
else:
    print('Неправильный ввод')