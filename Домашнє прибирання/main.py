from typing import List, Optional

class JunkItem:
    def __init__(self, name: str, quantity: int, value: float):
        self.name = name
        self.quantity = quantity
        self.value = value

    def __repr__(self):
        return f"Item(name='{self.name}', quantity={self.quantity}, value={self.value})"

class JunkStorage:
    def serialize(self, items: List[JunkItem], filename: str) -> None:
        formatter = lambda item: f"{item.name}|{item.quantity}|{str(item.value).replace('.', ',')}\n"
        with open(filename, 'w', encoding='utf-8') as file:
            file.writelines(map(formatter, items))

    def parse(self, filename: str) -> List[JunkItem]:
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return list(filter(None, map(self._parse_line, file)))
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []

    def _parse_line(self, line: str) -> Optional[JunkItem]:
        line = line.strip()
        if not line: return None
        
        parts = line.split('|')
        if len(parts) != 3:
            print(f"Warning: Invalid format -> {line}")
            return None

        try:
            return JunkItem(
                name=parts[0], 
                quantity=int(parts[1]), 
                value=float(parts[2].replace(',', '.'))
            )
        except ValueError:
            print(f"Warning: Data type error -> {line}")
            return None

if __name__ == "__main__":
    inventory = [
        JunkItem("Бляшанка", 5, 2.5),
        JunkItem("Стара плата", 3, 7.8),
        JunkItem("Купка дротів", 10, 1.2)
    ]

    storage = JunkStorage()
    filename = "warehouse_data.txt"

    print("Serializing...")
    storage.serialize(inventory, filename)

    with open(filename, "a", encoding="utf-8") as f:
        f.write("Broken|Item\nBad|1|NaN\n")

    print("Parsing...")
    loaded_items = storage.parse(filename)

    print("\n--- Loaded Inventory ---")
    print(*loaded_items, sep='\n')