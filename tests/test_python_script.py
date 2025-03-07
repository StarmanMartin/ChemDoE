from ChemDoE.registration import check_doe_script, register_python_doe_script


@check_doe_script('json', 'json')
def test_json_script():
    import ChemDoE.examples.json_sample


@check_doe_script('csv', 'csv')
def test_csv_script():
    import ChemDoE.examples.csv_sample


def test_no_script():
    try:
        @check_doe_script('csv', 'json')
        def run_test():
            pass
        run_test()
        assert False
    except ValueError as e:
        assert e.__str__() == 'Script did not write an output file'


def test_wrong_script():
    try:
        @check_doe_script('csv', 'json')
        def run_test():
            import ChemDoE.examples.csv_sample
        run_test()
        assert False
    except ValueError as e:
        assert e.__str__() == 'Script did not write an output file'



def test_registration():
    register_python_doe_script('ChemDoE.examples.json_sample', 'json', 'json')