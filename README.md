## wcpan.logging

A configuration generator for builtin logging module.

This module does not have any side effect, it is the user's choice to put it
into `logging.dictConfig`.

```python
import logging

from wcpan.logging import ConfigBuilder


logging.dictConfig(
    ConfigBuilder(path="/your/log", rotate=True)
    .add("moduleA", level="DEBUG")
    .add("moduleB", "moduleC", level="INFO")
    .to_dict()
)
```
