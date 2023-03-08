from importlib.metadata import version

from .builder import ConfigBuilder


version(__package__ or __name__)

__all__ = ("ConfigBuilder",)
