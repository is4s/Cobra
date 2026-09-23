from dataclasses import dataclass

from pntos.cobra.config import BaseConfig, ImuConfig


@dataclass
class SimpleDynamicInitializationConfig(BaseConfig):
    """Configuration specifically for a dynamic PVA alignment which is used in the 'DynamicInitializationPlugin'."""

    pos_channel: str
    """
    Channel containing position measurements from which to initialize.
    """

    imu_model: ImuConfig
    """
    A nested config that contains IMU model info.

    For more information, see ImuConfig.py.
    """

    tilt_sigma: tuple[float, float, float]
    """NED tilt uncertainty (degrees) to associate with attitude derived from positions."""
