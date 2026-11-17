import copy
import working_scad

def main(**kwargs):
    kwargs["run_oomp_populate"] = True

    kwargs["run_oomp"] = True

    kwargs["run_action"] = False
    #kwargs["run_action"] = False

    kwargs["run_scad"] = True

    kwargs["generate_stl"] = False
    kwargs["run_svg"] = True
    kwargs["run_three_d_model"] = False
    kwargs["run_documentation"] = True

    import working
    working.run(**kwargs)

if __name__ == '__main__':
    kwargs = {}
    main(**kwargs)
