from abc import ABC, abstractmethod

class Transport(ABC):
    def __init__(self, name: str, speed: int, capacity: int):
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if type(speed) is not int:
            raise TypeError("speed must be an integer")
        if type(capacity) is not int:
            raise TypeError("capacity must be an integer")

        self.name = name
        self.speed = speed
        self.capacity = capacity

    @abstractmethod
    def move(self, distance: float) -> float:
        pass

    @abstractmethod
    def fuel_consumption(self, distance: float) -> float: #витрата палива
        pass

    @abstractmethod
    def info(self) -> str:
        pass

    def calculate_cost(self, distance: float, price_per_unit: float) -> float: #price_per_unit ціна за одну одиницю витрати.
        return self.fuel_consumption(distance) * price_per_unit


class Car(Transport):
    def move(self, distance):
        return distance / self.speed

    def fuel_consumption(self, distance):
        return distance * 0.07

    def info(self):
        return f"Car: {self.name}"


class Bus(Transport):
    def __init__(self, name, speed, capacity, passengers):
        super().__init__(name, speed, capacity)
        self.passengers = passengers

    def move(self, distance):
        return distance / self.speed

    def fuel_consumption(self, distance):
        return distance * 0.15

    def info(self):
        if self.passengers > self.capacity:
            return f"Bus: {self.name} — Перевантажено!"
        return f"Bus: {self.name}"


class Bicycle(Transport):
    def __init__(self, name, speed, capacity):
        super().__init__(name, min(speed, 20), capacity)

    def move(self, distance):
        return distance / self.speed

    def fuel_consumption(self, distance):
        return 0.0

    def info(self):
        return f"Bicycle: {self.name}"


class ElectricCar(Car):
    def battery_usage(self, distance):
        return distance * 0.2

    def fuel_consumption(self, distance):
        return 0.0

    def info(self):
        return f"Electric car: {self.name}"
