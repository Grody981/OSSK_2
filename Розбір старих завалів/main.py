from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import csv


@dataclass(order=True)
class Item:
    sort_index: tuple = field(init=False, repr=False)

    name: str
    category: str
    quantity: int
    value: float
    condition: str
    location: str
    added_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __post_init__(self):
        self.sort_index = (self.category, self.value)

    def total_value(self) -> float:
        return self.quantity * self.value

    def __str__(self):
        return f"[{self.category}] {self.name} ({self.quantity} pcs) — {self.value} UAH/each, condition: {self.condition}"

@dataclass
class Inventory:
    items: List[Item] = field(default_factory=list)

    def add_item(self, item: Item):
        self.items.append(item)
        self.items.sort()

    def remove_item(self, name: str):
        self.items = [i for i in self.items if i.name != name]

    def find_by_category(self, category: str) -> List[Item]:
        return [i for i in self.items if i.category == category]

    def total_inventory_value(self) -> float:
        return sum(i.total_value() for i in self.items)

    def save_to_csv(self, filename: str):
        with open(filename, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "category", "quantity", "value", "condition", "location", "added_at"])
            for item in self.items:
                writer.writerow([
                    item.name,
                    item.category,
                    item.quantity,
                    item.value,
                    item.condition,
                    item.location,
                    item.added_at
                ])

    def load_from_csv(self, filename: str):
        self.items.clear()
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = Item(
                    name=row["name"],
                    category=row["category"],
                    quantity=int(row["quantity"]),
                    value=float(row["value"]),
                    condition=row["condition"],
                    location=row["location"],
                    added_at=row["added_at"]
                )
                self.items.append(item)
        self.items.sort()

    def export_summary(self) -> dict:
        summary = {}
        for item in self.items:
            summary[item.category] = summary.get(item.category, 0) + item.quantity
        return summary

    def filter(self,
               name: Optional[str] = None,
               category: Optional[str] = None,
               condition: Optional[str] = None,
               location: Optional[str] = None,
               min_value: Optional[float] = None,
               max_value: Optional[float] = None) -> List[Item]:

        results = self.items

        if name:
            results = [i for i in results if name.lower() in i.name.lower()]
        if category:
            results = [i for i in results if i.category == category]
        if condition:
            results = [i for i in results if i.condition == condition]
        if location:
            results = [i for i in results if i.location == location]
        if min_value is not None:
            results = [i for i in results if i.value >= min_value]
        if max_value is not None:
            results = [i for i in results if i.value <= max_value]

        return results

    def sort_by(self, field_name: str, reverse: bool = False):
        if field_name not in Item.__dataclass_fields__:
            raise ValueError(f"Can't sort by '{field_name}' — no such field in Item")

        self.items.sort(key=lambda x: getattr(x, field_name), reverse=reverse)


if __name__=="__main__":
    
    inv = Inventory()

    inv.add_item(Item("Wrench", "tools", 3, 15.0, "used", "garage"))
    inv.add_item(Item("Copper wire", "scrap", 10, 5.0, "used", "shed"))
    inv.add_item(Item("Flashlight", "electronics", 1, 120.0, "new", "storage"))
    print(inv.total_inventory_value())


    test_item = Item("Test", "test", 2, 10.0, "new", "storage")
    assert test_item.total_value() == 20.0

    inv_test = Inventory()
    inv_test.add_item(Item("A", "cat1", 1, 5.0, "new", "garage"))
    inv_test.add_item(Item("B", "cat1", 1, 10.0, "new", "garage"))
    inv_test.add_item(Item("C", "cat0", 1, 50.0, "new", "garage"))
    assert inv_test.items[0].name == "C"
    assert inv_test.items[1].name == "A"
    assert inv_test.items[2].name == "B"

    summary = inv_test.export_summary()
    assert summary == {"cat0": 1, "cat1": 2}

    filtered = inv_test.filter(category="cat1", min_value=7)
    assert len(filtered) == 1 and filtered[0].name == "B"

    inv_test.sort_by("value", reverse=True)
    assert inv_test.items[0].value == 50.0
