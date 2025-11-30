from neo4j import GraphDatabase
import numpy as np


class StorageControlSystem:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_action(self, temperature, humidity):
        temp_condition = self.fuzzify_temperature(temperature)
        hum_condition = self.fuzzify_humidity(humidity)

        # ✅ ИСПРАВЛЕННЫЙ запрос - БЕРЕТ ПЕРВОЕ ПОПАВШЕЕСЯ
        query = (
            "MATCH (temp:Condition {value: $temp_condition})-[:ACTION]->(temp_action:Action) "
            "WITH temp_action.name AS temp_action "
            "MATCH (hum:Condition {value: $hum_condition})-[:ACTION]->(hum_action:Action) "
            "RETURN temp_action, hum_action.name AS hum_action "
            "LIMIT 1"
        )

        with self.driver.session() as session:
            result = session.run(query, temp_condition=temp_condition, hum_condition=hum_condition)
            actions = result.single()
            if actions:
                return actions["temp_action"], actions["hum_action"]
            return "KeepTemperature", "KeepHumidity"

    def fuzzify_temperature(self, temperature):
        if temperature < 15:
            return "Cold"
        elif 15 <= temperature <= 25:
            return "Optimal"
        else:
            return "Hot"

    def fuzzify_humidity(self, humidity):
        if humidity < 30:
            return "Dry"
        elif 30 <= humidity <= 60:
            return "Optimal"
        else:
            return "Humid"

    def simulate(self, initial_temperature=10, initial_humidity=20, steps=15):
        temperature = initial_temperature
        humidity = initial_humidity

        print("🔥 СИМУЛЯЦИЯ КОНТРОЛЯ УСЛОВИЙ ХРАНЕНИЯ НА СКЛАДЕ")
        print("=" * 70)
        print(f"🎯 ЦЕЛЬ: Температура 15-25°C | Влажность 30-60%")
        print(f"📊 Начало: T={temperature}°C | H={humidity}%")
        print("=" * 70)

        for step in range(steps):
            temp_action, hum_action = self.get_action(temperature, humidity)

            # Применяем действия
            if temp_action == "IncreaseTemperature":
                temperature += np.random.uniform(1, 2)
            elif temp_action == "DecreaseTemperature":
                temperature -= np.random.uniform(1, 2)

            if hum_action == "IncreaseHumidity":
                humidity += np.random.uniform(3, 7)
            elif hum_action == "DecreaseHumidity":
                humidity -= np.random.uniform(3, 7)

            # Физические ограничения
            temperature = max(0, min(40, round(temperature, 1)))
            humidity = max(0, min(100, round(humidity, 1)))

            status_temp = "✅" if 15 <= temperature <= 25 else "❌"
            status_hum = "✅" if 30 <= humidity <= 60 else "❌"

            print(f"Шаг {step + 1:2d}: {status_temp} T={temperature:4.1f}°C [{temp_action:15}] | "
                  f"{status_hum} H={humidity:4.1f}% [{hum_action:13}]")

        print("=" * 70)
        final_status = "✅ УСЛОВИЯ В НОРМЕ!" if (
                    15 <= temperature <= 25 and 30 <= humidity <= 60) else "❌ НУЖНА ДОРАБОТКА"
        print(f"🏁 КОНЕЦ: T={temperature}°C | H={humidity}% | {final_status}")


if __name__ == "__main__":
    system = StorageControlSystem(password="password")  

    try:
        system.simulate(initial_temperature=10, initial_humidity=20, steps=15)
    finally:
        system.close()