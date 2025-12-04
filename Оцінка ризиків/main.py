import threading
import time
import random

PRICE = 50

class Warehouse:
    def __init__(self, name, meds):
        self.name = name
        self.meds = meds
        self.lock = threading.Lock()
        self.start_meds = meds

    def steal(self, amount):
        with self.lock:
            if random.random() < 0.1:
                return 0, 'caught'
            if random.random() < 0.1:
                loss = min(self.meds, amount)
                self.meds -= loss
                return 0, 'fail'
            
            stolen = min(self.meds, amount)
            self.meds -= stolen
            return stolen, 'ok'

class Runner(threading.Thread):
    def __init__(self, wh, name):
        super().__init__()
        self.wh = wh
        self.runner_name = name
        self.profit = 0
        self.log = []

    def run(self):
        for i in range(10):
            amt = random.randint(10, 30)
            got, st = self.wh.steal(amt)
            
            if st == 'ok':
                self.profit += got * PRICE
                self.log.append('+')
            elif st == 'fail':
                self.log.append('-')
            elif st == 'caught':
                self.log.append('x')

            bar = '#' * (i + 1)
            print(f"[{self.runner_name}] {self.wh.name} [{bar:<10}] prof: {self.profit}")
            time.sleep(random.uniform(0.1, 0.5))

def sim(n_runners=5):
    print(f"start sim: {n_runners} runners")
    
    whs = [Warehouse(f"wh_{i+1}", random.randint(100, 300)) for i in range(3)]
    runners = [Runner(random.choice(whs), f"r_{i+1}") for i in range(n_runners)]

    for r in runners:
        r.start()

    for r in runners:
        r.join()

    print("\n--- report ---")
    
    tot_profit = 0
    
    print("runners:")
    for r in runners:
        print(f"{r.runner_name} | prof: {r.profit} | log: {''.join(r.log)}")
        tot_profit += r.profit

    print("-" * 20)
    print("warehouses:")
    for w in whs:
        lost = w.start_meds - w.meds
        print(f"{w.name} | init: {w.start_meds} | left: {w.meds} | gone: {lost}")

    print("=" * 20)
    print(f"tot_profit: {tot_profit}")

if __name__ == "__main__":
    sim(3)
    time.sleep(1)
    print("\nNext run...")
    sim(5)
    
