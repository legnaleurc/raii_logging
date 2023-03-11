from importlib.metadata import version

from .builder import ConfigBuilder


__version__ = version(__package__ or __name__)
__all__ = ("ConfigBuilder",)
