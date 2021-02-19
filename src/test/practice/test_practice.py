from practice.practice import practice_pytest

import pytest
import os


def test_practice_pytest():
    result = practice_pytest(2, 2)
    assert result == 4


def test_env():
    result = os.getenv("INPUT_FILE")
    assert result