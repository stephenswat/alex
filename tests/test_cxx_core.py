import pytest
import itertools

import alex.definitions
import __alex_core

@pytest.mark.parametrize("pattern,precision", itertools.product(list(alex.definitions.Pattern), list(alex.definitions.Precision)))
def test_function_available(pattern, precision):
    assert hasattr(__alex_core, "_{}_{}_sim_entry".format(str(pattern), str(precision)))
    assert hasattr(__alex_core, "_{}_{}_bench_entry".format(str(pattern), str(precision)))
