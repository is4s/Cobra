.. _cobra-extras:

Cobra Extras
============

The top-level ``pntos.cobra.extras`` module should only directly contain plugin imports. These are all the
plugins that can be directly imported from ``pntos.cobra.extras``.  

Plugins in this submodule are separated from the core components for one or more of the following reasons:

1. They may be more advanced than core plugins
1. They may be somewhat experimental
1. They may serve a more niche purpose
1. They may not conform to the same typing and error-checking standards as core plugins.


.. automodule:: pntos.cobra.extras

Cobra Extras Config
=====================

``pntos.cobra.extras.config`` contains config for features in ``pntos.cobra.extras``, much like
``pntos.cobra.config`` contains config for features in ``pntos.cobra``.

.. automodule:: pntos.cobra.extras.config


Cobra Extras Internal
=====================

``pntos.cobra.extras.internal`` contains features used internally by the plugins in ``pntos.cobra.extras``.

.. automodule:: pntos.cobra.extras.internal
