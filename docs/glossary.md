# Glossary
<!--FIXME: api links-->
````{glossary}
:sorted:
Cobra
    Cobra is a blanket term for a specific Python implementation of the {term}`pntOS` architecture, including a pure Python {term}`API` and the apps and plugins derived from it.

    The various components of Cobra can be found in the [Cobra repository](https://github.com/is4s/cobra):

    ```{table} Cobra Component Breakdown
    | Component name                                        | Location within the repository        | Module import location | Description                                                                                                                                                                                                                                   |
    |:----------------------------------------------------- |:------------------------------------- | ---------------------- |:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | {ref}`Cobra API <cobra_api>`                          | `pntos-cobra-api/src/pntos/api/`            | `pntos.api`            | An {term}`API` written in Python that defines a Position, Navigation, and Timing Operating System ({term}`pntOS`). Consists of [abstract plugin definitions](https://github.com/is4s/cobra/tree/main/pntos-api/src/pntos/api/plugins). |
    | [Cobra Plugins](./plugins.md)                         | `pntos-cobra/src/pntos/cobra/`        | `pntos.cobra`          | Implementation of API - functional Python plugins. Also known as Cobra "core plugins".                                                                                                                                                        |
    | [Cobra Apps](./first_app.md) **                       | `pntos-cobra-apps/src/pntos/apps/`    | `pntos.cobra.apps`     | Each app loads a set of Cobra plugins, defines any config values, and starts a {term}`Cobra` implementation.                                                                                                       |
    | [Cobra Config](./apps/pos_ins.md#config-setup)        | `pntos-cobra/src/pntos/cobra/config/` | `pntos.cobra.config`   | Contains the Cobra config dataclasses along with two important utility functions: {py:obj}`config_to_registry()<pntos.cobra.config.config_to_registry>` and {py:obj}`config_from_registry()<pntos.cobra.config.config_from_registry>`.        |
    | [Cobra Utilities](./autodocs/cobra_utils.rst)         | `pntos-cobra/src/pntos/cobra/utils`   | `pntos.cobra.utils`    | Utility objects and functions for other Cobra components                                                                                                                                                                                      |
    | [Cobra Extras](./autodocs/cobra_extras.rst)                           | `pntos-cobra/src/pntos/cobra/extras`      | `pntos.cobra.extras`   | Auxiliary Cobra plugins and tools that are more advanced or niche than the standard components.                                                                                                                                                             |
    | Cobra Internal Objects                                | `pntos-cobra/src/pntos/cobra/`        | `pntos.cobra.internal` | Any Cobra objects that are not plugins, config, or utilities. These objects should not be needed in an {term}`app<App>`.                                                                                                                      |
    ```
    ** The apps do not export in the `pntos.cobra` module, but are still a part of {term}`Cobra`.

    To get started with Cobra, check out:
    * [](./installation.md) to set up the environment.
    * [](./introduction.md) for a more in-depth introduction to Cobra.
    * [](./first_app.md) to run your first Cobra app.
    * {ref}`tutorial-apps` to start learning more details of Cobra development with the tutorials.


App
    A single Python script run by the user that produces a working {term}`Cobra` system.
    For more details on apps, see [the reference tutorial apps](./apps/pos_ins.md).

ASPN
    A data standard that describes what {term}`PNT` data should be exchanged for consistent
    usage and interoperability of {term}`PNT` estimators across different systems, sources, and
    users. For the purposes of {term}`Cobra`, ASPN is the data standard used for
    passing navigation information between plugins. For more information, see the
    [ASPN FAQ](./faq.md#aspn).

C pntOS API
    An {term}`API` written in C that defines a Position, Navigation, and Timing Operating System ({term}`pntOS`). The C pntOS API consists of abstract plugin definition header files. For more information, see [pntos.com](https://www.pntos.com/) or the [pntOS docs](https://open-pnt.github.io/pntOS-C/).

API
    Application Programming Interface

EKF
    Extended Kalman Filter

PVA
    Position, Velocity, and Attitude. This is usually in reference to a wrapped
    `MeasurementPositionVelocityAttitude` {py:obj}`Message<pntos.api.Message>`.

LCM
    Lightweight Communications and Marshalling. For more information see [the LCM
    documentation](https://lcm-proj.github.io/lcm/index.html).

IMU
    Inertial Measurement Unit

INS
    Inertial Navigation System

PNT
    Positioning, Navigation, and Timing

ROS
    [Robot Operating System](https://www.ros.org/), an open-source robotics
    software framework. In our case, it serves as an alternative transport
    mechanism to LCM.

S&T
    Science and Technology

GNSS
    Global Navigation Satellite System

pntOS
    pntOS stands for Position, Navigation, and Timing Operating System. It consists of an {term}`API` which defines a plugin architecture for implementing {term}`PNT` solutions. Since it is only an architecture, any solution created using pntOS is going to be unique from pntOS itself and may be unique from other pntOS solutions. For more information, see [the FAQ](./faq.md#pntos).

NavToolKit
    NavToolKit (navtk) is a modular navigation software library, designed to assist users in the creation of navigation filters in an efficient, pluggable, agile manner. It is written in C++ but also contains Python bindings for use in projects like {term}`Cobra`. For more information, see [the NavToolKit FAQ](./faq.md#navtoolkit) or the [NavToolKit docs](https://is4s.github.io/NavToolkit/tutorial/introduction.html).

GPS
    Global Positioning System. A constellation of 24 satellites launched by the USA which provide geolocation and timing data to a GPS receiver.
````
