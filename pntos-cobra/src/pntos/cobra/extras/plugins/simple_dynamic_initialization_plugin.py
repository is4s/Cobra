from math import atan2, degrees, sqrt

import numpy as np
from aspn23 import (
    MeasurementPosition,
    MeasurementPositionVelocityAttitude,
    MeasurementPositionVelocityAttitudeErrorModel,
    MeasurementPositionVelocityAttitudeReferenceFrame,
)
from navtk.navutils import delta_lat_to_north, delta_lon_to_east, rpy_to_quat
from numpy.typing import NDArray
from pntos.api import (
    InertialInitializationStrategy,
    InitialInertialSolution,
    InitializationMotionNeeded,
    InitializationPlugin,
    InitializationStatus,
    InitializationType,
    LoggingLevel,
    Mediator,
    Message,
    StandardInertialErrors,
)
from pntos.cobra.config import ImuConfig, config_from_registry
from pntos.cobra.extras.config import SimpleDynamicInitializationConfig
from scipy.linalg import block_diag
from typing_extensions import override


class SimpleDynamicAlign(InertialInitializationStrategy):
    r"""
    This initialization strategy can be used to produce an initial PVA to initialize an
    inertial mechanization. It computes a PVA from 2 subsequent position measurements using a very simple method:

    .. math::
        & p = p_2

        & v_{NED} = \frac{p_2 - p_1}{\Delta{t}}

        & \phi = 0

        & \theta = atan2(v_D, \sqrt{v_N^2 + v_E^2})

        & \psi = atan2(v_E, v_N)

        & P_p = P_{p_2}

        & P_v = \frac{P_{p_2} + P_{p_1}}{\Delta{t}^2}

        & P_a = \text{user_defined}

    .. math::
        & P = \begin{pmatrix}
            P_p & 0_{3x3} & 0_{3x3} \\
            0_{3x3} & P_v & 0_{3x3} \\
            0_{3x3} & 0_{3x3} & P_a
            \end{pmatrix}

    .. warning::
        This is a coarse dynamic initialization algorithm that makes a few notable assumptions:

        * The inertial being initialized is aligned with the platform frame.
        * The platform is moving.
        * The platform longitudinal axis is aligned with the direction of travel.
        * The platform roll is approximately 0.
    """

    mediator: Mediator
    _pos1: MeasurementPosition | None
    _imu_model: ImuConfig
    _tilt_cov: NDArray[np.float64]

    def __init__(self, config_group: str, mediator: Mediator) -> None:
        self.mediator = mediator
        config = config_from_registry(
            SimpleDynamicInitializationConfig, mediator, config_group
        )
        if config is None:
            self.mediator.log_message(
                LoggingLevel.ERROR,
                f'Failed to populate config from registry to config type SimpleDynamicInitializationConfig and group {config_group}.',
            )
            return
        self._pos_channel = config.pos_channel
        self._imu_err = StandardInertialErrors(
            np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3)
        )
        self._imu_cov = np.diag(
            np.square(
                np.concatenate(
                    [
                        config.imu_model.accel_bias_initial_sigma,
                        config.imu_model.gyro_bias_initial_sigma,
                    ]
                )
            )
        )
        self._tilt_cov = np.diag(np.square(np.deg2rad(config.tilt_sigma)))
        self._status = InitializationStatus.WAITING
        self._pos1 = None
        self._init_sol = None

    @override
    def request_motion_needed(self) -> InitializationMotionNeeded:
        return InitializationMotionNeeded.MOTION_NEEDED

    @override
    def request_current_status(self) -> InitializationStatus:
        return self._status

    def calculate_pva(
        self, pos1: MeasurementPosition, pos2: MeasurementPosition
    ) -> MeasurementPositionVelocityAttitude | None:
        assert pos1.term1 is not None
        assert pos1.term2 is not None
        assert pos1.term3 is not None
        assert pos2.term1 is not None
        assert pos2.term2 is not None
        assert pos2.term3 is not None
        delta_lat = pos2.term1 - pos1.term1
        delta_lon = pos2.term2 - pos1.term2
        delta_alt = pos2.term3 - pos1.term3

        delta_north = delta_lat_to_north(delta_lat, pos2.term1, pos2.term3)
        delta_east = delta_lon_to_east(delta_lon, pos2.term1, pos2.term3)
        delta_down = -delta_alt

        dt = (
            pos2.time_of_validity.elapsed_nsec - pos1.time_of_validity.elapsed_nsec
        ) / 1e9
        vel_ned = np.array([delta_north, delta_east, delta_down]) / dt

        vel_horizontal = np.linalg.norm(vel_ned[:2])
        roll = 0
        pitch = atan2(vel_ned[2], vel_horizontal)
        yaw = atan2(vel_ned[1], vel_ned[0])
        rpy = np.array([roll, pitch, yaw])
        quat = rpy_to_quat(rpy)

        vel_cov = (pos1.covariance + pos2.covariance) / dt**2

        # compute heading uncertainty from vel uncertainty using jacobian of heading calculation
        H = np.array(
            [-vel_ned[1] / vel_horizontal**2, vel_ned[0] / vel_horizontal**2, 0]
        )
        computed_heading_var = H @ vel_cov @ H.T
        configured_heading_var = sqrt(self._tilt_cov[2, 2])
        # ensure configured heading var is at least as large as computed heading var
        if configured_heading_var < computed_heading_var:
            self.mediator.log_message(
                LoggingLevel.ERROR,
                f'Configured heading variance of {degrees(configured_heading_var)} degrees is less than computed heading variance of {degrees(computed_heading_var)} degrees. Positions used to derive PVA may be too close to one another to compute a reasonable PVA solution.',
            )
            return None

        cov = block_diag(pos2.covariance, vel_cov, self._tilt_cov)

        return MeasurementPositionVelocityAttitude(
            pos2.header,
            pos2.time_of_validity,
            MeasurementPositionVelocityAttitudeReferenceFrame.GEODETIC,
            pos2.term1,
            pos2.term2,
            pos2.term3,
            vel_ned[0],
            vel_ned[1],
            vel_ned[2],
            quat,
            cov,
            MeasurementPositionVelocityAttitudeErrorModel.NONE,
            np.array([]),
            [],
        )

    @override
    def process_pntos_message(self, message: Message) -> None:
        if self._status == InitializationStatus.INITIALIZED_GOOD:
            return

        if message.source_identifier != self._pos_channel:
            return

        if self._status == InitializationStatus.WAITING:
            self._status = InitializationStatus.INITIALIZING_COARSE

        if not isinstance(message.wrapped_message, MeasurementPosition):
            self.mediator.log_message(
                LoggingLevel.WARN,
                f'Expected position message for initialization, but got {type(message.wrapped_message)}',
            )
            return

        if self._pos1 is None:
            self._pos1 = message.wrapped_message
            return

        pva = self.calculate_pva(self._pos1, message.wrapped_message)
        if pva is not None:
            self._init_sol = InitialInertialSolution(
                Message(pva, '/solution/initial/pva'),
                self._imu_err,
                self._imu_cov,
                InitializationStatus.INITIALIZED_GOOD,
            )

            self._status = InitializationStatus.INITIALIZED_GOOD

    @override
    def request_solution(self) -> InitialInertialSolution:
        assert self._init_sol is not None
        return self._init_sol


class SimpleDynamicInitializationPlugin(InitializationPlugin):
    """
    Factory of :class:`pntos.cobra.extras.internal.SimpleDynamicAlign` initialization strategies.
    """

    mediator: Mediator

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    @override
    def init_plugin(
        self,
        plugin_resources_location: str | None = None,
        mediator: Mediator | None = None,
    ) -> None:
        if mediator is not None:
            self.mediator = mediator
        else:
            print(f'Error ({self.__class__.__name__}): mediator cannot be None')

    @override
    def shutdown_plugin(self) -> None:
        pass

    @override
    def is_initialization_type_supported(
        self, initialization_type: type[InitializationType]
    ) -> bool:
        return initialization_type == InertialInitializationStrategy

    @override
    def new_initialization_strategy(
        self,
        initialization_type: type[InitializationType],
        config_group: str | None = None,
    ) -> InitializationType | None:
        if config_group is None:
            self.mediator.log_message(
                LoggingLevel.ERROR,
                'config_group is a required parameter for this plugin and cannot be None',
            )
            return None
        if issubclass(initialization_type, InertialInitializationStrategy):
            return SimpleDynamicAlign(config_group, self.mediator)  # ty:ignore[invalid-return-type]
        self.mediator.log_message(LoggingLevel.ERROR, 'Unsupported type requested')
        return None
