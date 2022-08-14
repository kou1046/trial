from __future__ import annotations
from typing import Callable, Generator, Iterable, NamedTuple, Optional
from collections import namedtuple
import inspect

def cal_ave_with_gen(data:Iterable[int|float]) -> float: #コルーチンを使った平均の算出
    def averager() -> Generator[None, Optional[float|int], float]:
        total = 0.
        count = 0
        while True:
            tmp = yield
            if tmp is None:
                break
            count += 1 
            total += tmp
        return total/count
    data_averager = averager()
    next(data_averager)
    for value in data:
        data_averager.send(value)
    try:
        data_averager.send(None)
    except StopIteration as e:
        ave = e.value
    return ave

def cal_ave_with_closure(data:Iterable[int|float]) -> float: #クロージャを使った平均の算出
    def averager() -> Callable[[Optional[int|float]], Optional[float]]:
        count = 0
        total = 0.
        def main(tmp:Optional[int|float]) -> Optional[float]:
            nonlocal count, total
            if tmp is None:
                return total/count
            count += 1
            total += tmp
            return None
        return main
    data_averager = averager()
    for value in data:
        data_averager(value)
    ave = data_averager(None)
    return ave

def averager() -> NamedTuple: #平均を算出するクラスもどきのクロージャ　なぜか型チェックにひっかかる
    count = 0
    total = 0.
    f_name = inspect.currentframe().f_code.co_name
    instance = namedtuple(f_name,'set get')
    def set(tmp:int|float) -> None:
        nonlocal total, count
        total += tmp
        count += 1
    def get() -> float:
        nonlocal total, count
        return total/count
    return instance(set, get)

if __name__ == '__main__':
    sample_data = (10., 5., 8., 12., 20.)

    data_averager = averager()
    for v in sample_data:
        data_averager.set(v)
    print(data_averager.get())

    func_list = (cal_ave_with_closure, cal_ave_with_gen)
    for func in func_list:
        print(f'{func.__name__} -> {func(sample_data)}')
        


