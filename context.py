from os import getcwd


class Context:
    _cwd: str = None
    _variables: dict = None

    def __init__(self, **kwargs):
        self._variables = {}

        for key, val in kwargs.items():
            if key not in dir(Context):
                raise Exception(f"Bad key: '{key}' (ignored)")
            setattr(self, f"_{key}", val)

    @property
    def cwd(self):
        return self._cwd

    @property
    def variables(self):
        return self._variables

    def set_variable(self, key, value):
        self._variables[key] = value

    def _get_default_variables(self):
        return {
            "allusersprofile": None,
            "appdata": None,
            "clientname": None,
            "commonprogramfiles": None,
            "computername": None,
            "comspec": None,
            "devmgr_show_nonpresent_devices": None,
            "fp_no_host_check": None,
            "homedrive": None,
            "homepath": None,
            "logonserver": None,
            "number_of_processors": None,
            "os": None,
            "path": None,
            "pathext": None,
            "processor_architecture": None,
            "processor_identifier": None,
            "processor_level": None,
            "processor_revision": None,
            "programfiles": None,
            "prompt": None,
            "sessionname": None,
            "systemdrive": None,
            "systemroot": None,
            "temp": None,
            "tmp": None,
            "userdomain": None,
            "username": None,
            "userprofile": None,
            "windir": None
        }


def get_context() -> dict:
    cwd = getcwd().replace("/", "\\")
    return Context(cwd=cwd)
