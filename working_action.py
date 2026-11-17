"""Refresh motor presentation from existing canonical YAML."""


def main(**kwargs):
    run_svg = kwargs.get("action_svg", True)
    run_models = kwargs.get("action_models", True)
    run_documentation = kwargs.get("action_documentation", True)
    if run_svg:
        import working_motor_drawing
        working_motor_drawing.main(**kwargs)
    if run_models:
        import working_three_d_model
        working_three_d_model.main(**kwargs)
    if run_documentation:
        import working_motor_documentation
        working_motor_documentation.main(**kwargs)


if __name__ == "__main__":
    main()
