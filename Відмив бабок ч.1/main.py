from functools import wraps

def shadow(limit=200):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            total = 0
            gen = func(*args, **kwargs)
            for item in gen:
                try:
                    parts = item.split()
                    if len(parts) >= 2:
                        amount = float(parts[1])
                        total += amount
                        
                        if total > limit:
                            print("Тіньовий ліміт перевищено. Активую схему")
                except ValueError:
                    pass
                
                yield item
            
            return total
        return wrapper
    return decorator


@shadow(limit=200)
def transaction_stream():
    lst = [
        "payment 50", 
        "refund 50", 
        "transfer 100",    
        "garbage_data",    
        "payment 10",      
        "tax error",       
        "transfer 300"     
    ]
    for t in lst:
        yield t

if __name__ == "__main__":
    gen = transaction_stream()
    
    while True:
        try:
            print(f"Log: {next(gen)}") 
        except StopIteration as e:
            print(f"Final sum: {e.value}")
            break
