#默认加1
def zs(func):
    def add():
        print('所有结果装饰+1')
        temp = func()
        print('原方法数字:%i' % temp)
        temp = temp + 1
        print('装饰后结果：%i' % temp)
    return add

@zs
def js():
    c = 3 + 4
    return c


if __name__ == "__main__":
    js()