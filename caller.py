from commands import Command, CMD_MAP


def call(cmd: Command, params: list):
    func = CMD_MAP.get(cmd)
    if not func:
        raise Exception(f"Unknown function: '{cmd}'")

    func(params)
