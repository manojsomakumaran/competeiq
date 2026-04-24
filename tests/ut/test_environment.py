import sys

import pytest

from competeiq import environment


@pytest.mark.unit
def test_is_colab_false_by_default():
    assert environment.is_colab() is False


@pytest.mark.unit
def test_is_colab_true_when_module_present(monkeypatch):
    import types

    monkeypatch.setitem(sys.modules, "google.colab", types.ModuleType("google.colab"))
    assert environment.is_colab() is True


@pytest.mark.unit
def test_is_jupyter_false_when_not_in_ipython():
    assert environment.is_jupyter() is False


@pytest.mark.unit
def test_is_local_inverse_of_colab():
    assert environment.is_local() != environment.is_colab()
