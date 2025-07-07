"""Module configuration"""

import importlib
import sys


class Settings:
    """Configuration manager"""

    def __init__(self):
        # settings is a stack of dicts which should allow arbitrary nested deferred
        # modules
        self.settings = [{}]

    def get_module(self, module, **kwargs):
        """Load a module by path with specified options set

        Parameters
        ----------
        module : str
            Module path that would be used in an import statement, e.g.
            ``"my_package.module"``
        **kwargs
            Settings declared by `module` (see :meth:`get_settings`).

        Returns
        -------
        mod : module
            Configured module object.
        """
        self.settings.append(kwargs)

        if module not in sys.modules:
            mod = importlib.import_module(module)
        else:
            mod = sys.modules[module]
            mod = importlib.reload(mod)
        self.settings.pop()
        return mod

    def get_settings(self, **defaults):
        """Declare available settings with default values

        Parameters
        ----------
        **defaults
            Declared available settings with default values.

        Returns
        -------
        settings : dict
            Module configuration as set by :meth:`get_module`.
        """
        current = self.settings[-1]
        # Use set difference for faster extra detection and reduce number of lookups
        extra_keys = current.keys() - defaults.keys()
        if extra_keys:
            extra_kwargs = {k: current[k] for k in extra_keys}
            # TODO warn instead?
            msg = f"Extra keyword arguments provided to configuration {extra_kwargs}"
            raise ValueError(msg)

        # Construct settings dict faster using {**defaults, **current} but only for declared defaults
        # This is more efficient than a comprehension when few overrides may be present
        configured_kwargs = defaults.copy()
        configured_kwargs.update({k: v for k, v in current.items() if k in defaults})

        return configured_kwargs


#: singleton :class:`Settings` instance
settings = Settings()
