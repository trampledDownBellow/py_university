def read_number(prompt):
    while True:
        s = input(prompt).strip()
        try:
            return float(s)
        except ValueError:
            print("Invalid number. Try again.")

def read_operation(prompt):
    valid = {'+', '-', '*', '/'}
    while True:
        op = input(prompt).strip()
        if op in valid and len(op) == 1:
            return op
        print("Unknown operation. Allowed: +, -, *, /")

def calculate(a, b, op):
    if op == '+':
        return a + b
    if op == '-':
        return a - b
    if op == '*':
        return a * b
    if op == '/':
        if b == 0:
            raise ValueError('Division by zero')
        return a / b
    raise ValueError('Unknown operation')

def main():
    print('Simple calculator. Enter two numbers and an operation (+, -, *, /).')
    a = read_number('First number: ')
    b = read_number('Second number: ')
    op = read_operation('Operation (+, -, *, /): ')
    try:
        result = calculate(a, b, op)
    except ValueError as e:
        print('Error:', e)
        return
    if abs(result - int(result)) < 1e-12:
        print('Result:', int(result))
    else:
        print('Result:', result)

if __name__ == '__main__':
    main()