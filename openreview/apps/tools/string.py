import os


def to_bool(value, default=None, err_empty=False):
    """
    Tries to convert `value` in to a boolean. Valid values are: {True, False, 0, 1}.

    @param var: environment value to interpret
    @type var: str

    @param default: if no (valid) value is found, use this one
    @type default: all

    @rtype: bool
    """
    if isinstance(value, bool):
        return value

    value = value.lower().strip()

    if value in ["true", "1"]:
        return True

    if value in ["false", "0"]:
        return False

    if len(value):
        raise ValueError("{value!r} not a valid boolean value.".format(**locals()))

    if err_empty:
        raise ValueError("Empty value passed.")

    return default


def get_bool(var, default=None, err_empty=False):
    """
    Gets the value of variable `var` from environment variables and tries to convert
    it to a boolean. Valid values are: {True, False, 0, 1}.

    @param var: environment value to interpret
    @type var: str

    @param default: if no (valid) value is found, use this one
    @type default: all

    @rtype: bool
    """
    value = os.environ.get(var, "")

    try:
        return to_bool(value, default=default, err_empty=err_empty)
    except ValueError as e:
        # You shouldn't use print in 'normal' code, however upon importing
        # settings cryptic (and generally unhelpful) error messages are displayed
        # in case of exceptions.
        if not value.strip():
            errmsg = "Environment variable {var!r} must be specified.".format(**locals())
            print(errmsg)
        else:
            print(e)

        raise

