
def f(hour, mins, dura):
    time_hour = (hour + dura//60 + (mins+ dura%60)//60) % 24
    time_min = (mins+ dura%60)%60
    return str(time_hour) + ":" + str(time_min)


assert f(1, 30, 30) == computeEndTime(1, 30, 30)

assert f(12, 59, 2) == computeEndTime(12, 59, 2)

assert f(23, 59, 2) == computeEndTime(23, 59, 2)

assert f(23, 58, 1) == computeEndTime(23, 58, 1)