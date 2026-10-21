import importlib.util

import pytest

from prv_lab.backends import OptionalDependencyError, _load_prv_symbols


def test_optional_prv_backend_has_helpful_install_message_when_missing():
    if importlib.util.find_spec("prv_accountant") is not None:
        pytest.skip("Optional PRV dependency is installed in this environment")
    with pytest.raises(OptionalDependencyError, match=r"pip install 'prv-lab\[prv\]'"):
        _load_prv_symbols()
