import string, random
from HusqAM.models import Status


def random_string():
    # from https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))


def process_pyhusmow_dict(robot, robot_dict):
    """
    Applies a dictionary with the robot state as obtained from the pyhusmow API to the given robot.
    The updated Robot object is saved in the database and a new State object, if different from the
    robot's previous state, is created.
    Returns a tuple:
      - the list of fields that have changed in the robot,
      - the new Status object, if one was created
    """
    assert robot.manufac_id == robot_dict['id']

    changes = robot.update_from_dict(robot_dict)

    if changes:
        robot.save()

    st = Status(robot=robot)
    st.update_from_dict(robot_dict["status"])

    if st.should_save():
        st.save()

    return changes, st if st.id else None
