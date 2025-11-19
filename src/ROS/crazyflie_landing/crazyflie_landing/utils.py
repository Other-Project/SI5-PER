import math
import numpy as np


def quaternion_to_euler(qx, qy, qz, qw):
    """
    Convert quaternion (qx, qy, qz, qw) to Euler angles (roll, pitch, yaw)
    """
    sinr_cosp = 2.0 * (qw * qx + qy * qz)
    cosr_cosp = 1.0 - 2.0 * (qx * qx + qy * qy)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2.0 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)
    else:
        pitch = math.asin(sinp)

    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw


def body_rates_to_euler_rates(p, q, r, roll, pitch):
    """
    Convert p,q,r (body rates) into φ̇, θ̇, ψ̇ (Euler rates)
    """
    # φ̇ = p + sinφ tanθ q + cosφ tanθ r
    # θ̇ = cosφ q - sinφ r
    # ψ̇ = sinφ / cosθ q + cosφ / cosθ r
    cos_r = math.cos(roll)
    sin_r = math.sin(roll)
    cos_p = math.cos(pitch)
    sin_p = math.sin(pitch)
    # note: cos_p ~= cos(pitch)
    if abs(cos_p) < 1e-6:
        cos_p = 1e-6
    phi_dot = p + sin_r * math.tan(pitch) * q + cos_r * math.tan(pitch) * r
    theta_dot = cos_r * q - sin_r * r
    psi_dot = (sin_r / cos_p) * q + (cos_r / cos_p) * r
    return phi_dot, theta_dot, psi_dot


def angular_vel(current_orientation, angular_twist):
    """
    Return angular velocities expressed as Euler rates (roll_rate, pitch_rate, yaw_rate)
    """
    roll, pitch, _ = quaternion_to_euler(current_orientation.x, current_orientation.y, current_orientation.z, current_orientation.w)
    roll, pitch, yaw = body_rates_to_euler_rates(angular_twist.x, angular_twist.y, angular_twist.z, roll, pitch)
    return [roll, pitch, yaw]


def gravity_in_body(current_orientation, g=9.81):
    """
    Return the gravity vector expressed in the body frame
    """
    x, y, z, w = current_orientation.x, current_orientation.y, current_orientation.z, current_orientation.w
    # rotation matrix R (body -> world) constructed from quaternion (w,x,y,z)
    R = np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ],
        dtype=float,
    )
    # vecteur gravité dans le monde ; si votre convention est NED (z vers le bas) adaptez le signe
    g_world = np.array([0.0, 0.0, -g], dtype=float)
    # projeter dans le repère corps
    g_body = R.T.dot(g_world)
    return g_body.tolist()
