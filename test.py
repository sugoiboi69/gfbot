import datetime
import math
now = datetime.datetime.now().strftime(f"%d/%m/%Y %H:%M:%S")
print("date and time =", now)
dt_next = datetime.datetime.strptime(now, f"%d/%m/%Y %H:%M:%S")+datetime.timedelta(hours=5)
diff = dt_next - datetime.datetime.now()
minutes = math.floor(diff.total_seconds()/60)
hours = divmod(minutes, 60)
print('Total difference in minutes: ', hours[0], 'hours',
                                 hours[1], 'minutes')

