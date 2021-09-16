## wcpan.logger

A RAII style logging module.

```python
from wcpan.logger import setup, DEBUG

setup([
    'module_name_1',
    'module_name_2',
], '/var/log/your.log')

DEBUG(__name__) << 'message'
```
