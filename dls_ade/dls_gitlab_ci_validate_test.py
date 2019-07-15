import pytest
import mock
import os
import dls_ade.dls_gitlab_ci_validate as ci_validate


@mock.patch("dls_ade.dls_gitlab_ci_validate.Gitlab")
def test_validate_calls_api_correctly(mock_gitlab):
    test_file_contents = "My file"
    ci_validate.validate(test_file_contents)

    assert mock_gitlab.called_once_with(content=test_file_contents)

