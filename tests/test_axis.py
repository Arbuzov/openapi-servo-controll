from openapi_servo_control.axis_container import Axis, AxisContainer


def test_axis_defaults():
    axis = Axis()
    assert axis.position is None
    assert axis.target_position is None
    assert axis.velocity is None
    assert axis.movement is None
    assert axis.tilt_angle == Axis.tilt_angle
    assert axis.max_step == 2.0


def test_set_position_from_none_snaps_instantly():
    axis = Axis()
    axis.set_position(120)
    assert axis.target_position == 120
    assert axis.position == 120
    assert axis.velocity == 0
    assert axis.movement is None


def test_set_position_when_already_positioned_keeps_current():
    axis = Axis()
    axis.position = 90
    axis.set_position(150)
    assert axis.position == 90
    assert axis.target_position == 150


def test_set_velocity_initializes_position():
    axis = Axis()
    axis.set_velocity(1.5)
    assert axis.velocity == 1.5
    assert axis.position == 0
    assert axis.movement is None


def test_set_tilt_sets_movement_and_angle():
    axis = Axis()
    axis.set_tilt(45)
    assert axis.movement == 'TILT'
    assert axis.position == Axis.tilt_base
    assert axis.tilt_angle == 45


def test_set_tilt_without_angle_keeps_default():
    axis = Axis()
    axis.set_tilt()
    assert axis.movement == 'TILT'
    assert axis.tilt_angle == Axis.tilt_angle


def test_set_swing_sets_movement_and_velocity():
    axis = Axis()
    axis.set_swing(60)
    assert axis.movement == 'SWING'
    assert axis.position == Axis.tilt_base
    assert axis.tilt_angle == 60
    assert axis.velocity == 1


def test_move_axis_advances_with_velocity():
    axis = Axis()
    axis.position = 90
    axis.velocity = 1.0
    axis.move_axis()
    assert axis.position == 91.0


def test_move_axis_step_capped_by_max_step():
    axis = Axis()
    axis.position = 90
    axis.velocity = 10.0
    axis.max_step = 2.0
    axis.move_axis()
    assert axis.position == 92.0


def test_move_axis_towards_target_when_velocity_zero():
    axis = Axis()
    axis.position = 90
    axis.velocity = 0
    axis.target_position = 100
    axis.max_step = 3.0
    axis.move_axis()
    assert axis.position == 93.0
    assert axis.target_position == 100


def test_move_axis_snaps_to_target_within_deadzone():
    axis = Axis()
    axis.position = 99.95
    axis.velocity = 0
    axis.target_position = 100
    axis.move_axis()
    assert axis.position == 100
    assert axis.target_position is None


def test_tilt_axis_stays_in_range():
    axis = Axis()
    axis.set_tilt(30)
    for _ in range(50):
        axis.tilt_axis()
        assert Axis.tilt_base - 30 <= axis.position <= Axis.tilt_base


def test_swing_axis_reverses_at_bounds():
    axis = Axis()
    axis.set_swing(20)
    axis.position = Axis.tilt_base + 50  # past positive bound
    axis.swing_axis()
    assert axis.velocity < 0

    axis.position = Axis.tilt_base - 50  # past negative bound
    axis.swing_axis()
    assert axis.velocity > 0


def test_axis_to_json_shape():
    axis = Axis()
    axis.name = 'Axis 0'
    axis.set_position(45)
    data = axis.to_json()
    assert set(data.keys()) == {
        'name', 'velocity', 'position',
        'target_position', 'movement', 'max_step',
    }
    assert data['name'] == 'Axis 0'
    assert data['position'] == 45


def test_axis_str_contains_fields():
    axis = Axis()
    axis.name = 'Axis 1'
    axis.set_velocity(0.5)
    text = str(axis)
    assert 'Axis 1' in text
    assert '0.5' in text


def test_container_creates_axises():
    container = AxisContainer(5)
    assert len(container.axises) == 5
    assert container.axises[0].name == 'Axis 0'
    assert container.axises[4].name == 'Axis 4'


def test_container_set_axis_value():
    container = AxisContainer(3)
    container.set_axis_value(1, 75)
    assert container.axises[1].position == 75


def test_container_to_json_returns_list():
    container = AxisContainer(3)
    data = container.to_json()
    assert isinstance(data, list)
    assert len(data) == 3


def test_container_apply_velocity_skips_idle_axises():
    container = AxisContainer(2)
    container.apply_velocity()
    for axis in container.axises.values():
        assert axis.position is None


def test_container_apply_velocity_moves_active_axis():
    container = AxisContainer(2)
    container.axises[0].set_velocity(1.0)
    container.axises[0].position = 90
    container.apply_velocity()
    assert container.axises[0].position == 91.0


def test_container_apply_velocity_tilts_when_movement_tilt():
    container = AxisContainer(2)
    container.axises[0].set_tilt(20)
    container.apply_velocity()
    pos = container.axises[0].position
    assert Axis.tilt_base - 20 <= pos <= Axis.tilt_base


def test_container_apply_velocity_swings_when_movement_swing():
    container = AxisContainer(2)
    container.axises[0].set_swing(20)
    start = container.axises[0].position
    container.apply_velocity()
    assert container.axises[0].position != start or \
        container.axises[0].velocity is not None
