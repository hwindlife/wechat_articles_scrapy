import datetime
import time


class DateUtil(object):
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    TIME_FORMAT = "%H:%M:%S"

    # 当前毫秒数
    @staticmethod
    def curMilis():
        return int(time.time() * 1000)

    # 当前秒数
    @staticmethod
    def curSeconds():
        return int(time.time())

    # 当前日期 格式%Y-%m-%d %H:%M:%
    @staticmethod
    def curDatetime():
        return datetime.datetime.strftime(datetime.datetime.now(), DateUtil.DATETIME_FORMAT)

    # 当前日期 格式%Y-%m-%d
    @staticmethod
    def curDate():
        return datetime.date.today()

    # 当前时间 格式%Y-%m-%d
    @staticmethod
    def curTime():
        return time.strftime(DateUtil.TIME_FORMAT)

    # 秒转日期
    @staticmethod
    def secondsToDatetime(seconds):
        return time.strftime(DateUtil.DATETIME_FORMAT, time.localtime(seconds))

    # 毫秒转日期
    @staticmethod
    def milisToDatetime(milix):
        return time.strftime(DateUtil.DATETIME_FORMAT, time.localtime(milix // 1000))

    # 日期转毫秒
    @staticmethod
    def datetimeToMilis(datetimestr):
        strf = time.strptime(datetimestr, DateUtil.DATETIME_FORMAT)
        return int(time.mktime(strf)) * 1000

    # 日期转秒
    @staticmethod
    def datetimeToSeconds(datetimestr):
        strf = time.strptime(datetimestr, DateUtil.DATETIME_FORMAT)
        return int(time.mktime(strf))

    # 当前年
    @staticmethod
    def curYear():
        return datetime.datetime.now().year

    # 当前月
    @staticmethod
    def curMonth():
        return datetime.datetime.now().month

    # 当前日
    @staticmethod
    def curDay():
        return datetime.datetime.now().day

    # 当前时
    @staticmethod
    def curHour():
        return datetime.datetime.now().hour

    # 当前分
    @staticmethod
    def curMinute():
        return datetime.datetime.now().minute

    # 当前秒
    @staticmethod
    def curSecond():
        return datetime.datetime.now().second

    # 星期几
    @staticmethod
    def curWeek():
        return datetime.datetime.now().weekday()

    # 几天前的时间
    @staticmethod
    def nowDaysAgo(days):
        daysAgoTime = datetime.datetime.now() - datetime.timedelta(days=days)
        return time.strftime(DateUtil.DATETIME_FORMAT, daysAgoTime.timetuple())

    # 几天后的时间
    @staticmethod
    def nowDaysAfter(days):
        daysAgoTime = datetime.datetime.now() + datetime.timedelta(days=days)
        return time.strftime(DateUtil.DATETIME_FORMAT, daysAgoTime.timetuple())

    # 某个日期几天前的时间
    @staticmethod
    def dtimeDaysAgo(dtimestr, days):
        daysAgoTime = datetime.datetime.strptime(dtimestr, DateUtil.DATETIME_FORMAT) - datetime.timedelta(days=days)
        return time.strftime(DateUtil.DATETIME_FORMAT, daysAgoTime.timetuple())

    # 某个日期几天前的时间
    @staticmethod
    def dtimeDaysAfter(dtimestr, days):
        daysAgoTime = datetime.datetime.strptime(dtimestr, DateUtil.DATETIME_FORMAT) + datetime.timedelta(days=days)
        return time.strftime(DateUtil.DATETIME_FORMAT, daysAgoTime.timetuple())


if __name__ == '__main__':

    print("秒转日期：", DateUtil.secondsToDatetime(1594602394))
