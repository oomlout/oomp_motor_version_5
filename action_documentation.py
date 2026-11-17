"""Refresh motor READMEs and navigation without rebuilding geometry or renders."""


def main(**kwargs):
    import working_motor_documentation
    return working_motor_documentation.main(**kwargs)


if __name__ == "__main__":
    main()
