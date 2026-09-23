from models import Car, Bus, Bicycle, ElectricCar


transports = [
    Car("Toyota", 100, 5),
    Bus("Mercedes", 80, 50, 45),
    Bicycle("Trek", 25, 1),
    ElectricCar("Tesla", 120, 5)
]


for transport in transports:
    print(transport.info())
    print(f"Час на 100 км: {transport.move(100):.2f} год")
    print(f"Витрати пального: {transport.fuel_consumption(100):.2f}")
    print()
