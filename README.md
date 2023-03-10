## wcpan.logging

A configuration generator for builtin logging module.

```python
import logging

from wcpan.logging import ConfigBuilder


logging.dictConfig(
    ConfigBuilder(path="/your/log", level="DEBUG")
    .add("moduleA", "moduleB")
    .add("moduleB", level="INFO")
)
```
