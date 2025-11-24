def tokenize(expr: str):
    expr = expr.replace(" ", "")
    tokens = []
    number = ""

    for i, ch in enumerate(expr):
        if ch.isdigit() or ch == ".":
            number += ch
            continue

        if number:
            tokens.append(number)
            number = ""

        if ch == "-" and (i == 0 or expr[i-1] in "+-*/^%("):
            tokens.append("0")
            tokens.append("-")
            continue

        tokens.append(ch)

    if number:
        tokens.append(number)

    return tokens

def to_rpn(tokens:list[str] ):
    output = []
    stack = []
    p = {"+":1, "-":1, "*":2, "/":2, "^":3, "%":4}
    right_ = {"^"}

    def should_pop(op1, op2):
        return p[op1] < p[op2] if op1 in right_ else p[op1] <= p[op2]

    for token in tokens:
        if token.replace(".", "", 1).isdigit():
            output.append(token)
        elif token in p:
            while stack and stack[-1] in p and should_pop(token, stack[-1]):
                output.append(stack.pop())
            stack.append(token)
        elif token == "(":
            stack.append(token)
        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            if stack:
                stack.pop()
            else:
                raise ValueError("Mismatched parentheses")
        else:
            raise ValueError(f"Invalid token: {token}")

    while stack:
        if stack[-1] in {"(", ")"}:
            raise ValueError("Mismatched parentheses")
        output.append(stack.pop())
    return output

def eval_rpn(rpn):
    stack = []
    for token in rpn:
        if token.replace(".", "", 1).isdigit():
            stack.append(float(token))
        else:
            if token == "%":
                a = stack.pop()
                stack.append(a / 100)
                continue
            b = stack.pop()
            a = stack.pop()
            match token:
                case "+":
                    stack.append(a + b)
                case "-":
                    stack.append(a - b)
                case "*":
                    stack.append(a * b)
                case "/":
                    if b == 0:
                        raise ZeroDivisionError("Division by zero")
                    stack.append(a / b)
                case "^":
                    stack.append(a ** b)
                case _:
                    raise ValueError(f"Unknown operator: {token}")
    return stack[0]

def calculate(expr: str):
    try:
        tokens = tokenize(expr)
        rpn = to_rpn(tokens)
        result = eval_rpn(rpn)
        return int(result) if result.is_integer() else result
    except ZeroDivisionError:
        return "Error: Division by zero is not allowed."
    except ValueError as e:
        return f"Error: {e}"
    except Exception:
        return "Error: Invalid expression."

def main():
    print("Enter expression (type 'exit' or 'quit' to quit):")
    while True:
        s = input("> ")
        if s.lower() in {"exit", "quit"}:
            break
        print(calculate(s))

if __name__ == "__main__":
    main()