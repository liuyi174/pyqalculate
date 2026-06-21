from pyqalculate.calculator import Calculator
from pyqalculate.unit import UnitSubtype
c = Calculator()
c.load_definitions()

# Trace gallon chain
u = c.find_unit('gallon')
print('Gallon chain:')
current = u
depth = 0
while current and depth < 10:
    indent = '  ' * depth
    expr = current.expression() if hasattr(current, 'expression') else 'N/A'
    print(f'  {indent}{current.name()} (subtype={current.subtype()}, expr={expr})')
    if current.subtype() == UnitSubtype.ALIAS_UNIT:
        current = current.base_unit()
    else:
        break
    depth += 1

# Test convert method
val = c.convert(1.0, c.find_unit('gallon'), c.find_unit('L'))
print(f'\n1 gallon = {val} L')
val = c.convert(1.0, c.find_unit('gallon'), c.find_unit('m'))
print(f'1 gallon = {val} m')
val = c.convert(1.0, c.find_unit('L'), c.find_unit('m'))
print(f'1 L = {val} m')
