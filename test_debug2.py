from pyqalculate.calculator import Calculator
from pyqalculate.unit import UnitSubtype
c = Calculator()
c.load_definitions()

# Manual conversion trace
u = c.find_unit('gallon')
value = 1.0
exp = 1
current = u
while current and current.subtype() == UnitSubtype.ALIAS_UNIT:
    new_val, new_exp = current.convert_to_base_unit(value, exp)
    print(f'{value} {current.name()} = {new_val} {current.base_unit().name()}')
    value = new_val
    exp = new_exp
    current = current.base_unit()

print(f'\nFinal: {value} m (exp={exp})')

# Now convert 1 L to m
u = c.find_unit('L')
value = 1.0
exp = 1
current = u
while current and current.subtype() == UnitSubtype.ALIAS_UNIT:
    new_val, new_exp = current.convert_to_base_unit(value, exp)
    print(f'{value} {current.name()} = {new_val} {current.base_unit().name()}')
    value = new_val
    exp = new_exp
    current = current.base_unit()

print(f'\nFinal: {value} m (exp={exp})')

# Test the convert method
val = c.convert(1.0, c.find_unit('gallon'), c.find_unit('m'))
print(f'\nconvert(1 gal, m) = {val}')

val = c.convert(1.0, c.find_unit('L'), c.find_unit('m'))
print(f'convert(1 L, m) = {val}')

val = c.convert(1.0, c.find_unit('gallon'), c.find_unit('L'))
print(f'convert(1 gal, L) = {val}')
