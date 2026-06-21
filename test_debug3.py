from pyqalculate.calculator import Calculator
from pyqalculate.unit import UnitSubtype

c = Calculator()
c.load_definitions()

# Trace psi chain
u = c.find_unit('psi')
current = u
visited = set()
print('psi chain:')
while current and current.subtype() == UnitSubtype.ALIAS_UNIT:
    if id(current) in visited:
        break
    visited.add(id(current))
    bu = current.base_unit()
    print(f'  {current.name()} -> {bu.name() if bu else None} (exp={current.exponent()}, rel={current.expression()})')
    current = bu

# Trace Pa chain
u = c.find_unit('Pa')
current = u
visited = set()
print('\nPa chain:')
while current and current.subtype() == UnitSubtype.ALIAS_UNIT:
    if id(current) in visited:
        break
    visited.add(id(current))
    bu = current.base_unit()
    print(f'  {current.name()} -> {bu.name() if bu else None} (exp={current.exponent()}, rel={current.expression()})')
    current = bu

# Test conversion
val = c.convert(14.7, c.find_unit('psi'), c.find_unit('Pa'))
print(f'\n14.7 psi = {val} Pa')
