#!/bin/env dls-python

import pytest
import unittest
import mock
import dls_ade.dls_last_release as dls_last_release

from argparse import _StoreAction
from argparse import _StoreTrueAction

import re
from requests.models import Response

response_etc = [{'build_name': 'build_20191101-181325_mef65357_etc_init_3-515', 'timestamp': '2019-11-01T18:13:30.302Z', 'message': 'Build complete'}, {'build_name': 'build_20191101-181325_mef65357_etc_init_3-515', 'timestamp': '2019-11-01T18:13:29.712Z', 'message': 'Running make'}, {'build_name': 'build_20191101-181325_mef65357_etc_init_3-515', 'timestamp': '2019-11-01T18:13:26.664Z', 'message': 'Building etc in /dls_sw/prod/etc'}]

response_tools = [{'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T15:07:55.279Z', 'message': 'Build complete'}, {'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T15:07:42.490Z', 'message': 'make-defaults: /dls_sw/work/etc/build/test/local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1 /dls_sw/prod/etc/build/tools_build/RELEASE.RHEL7-x86_64 7 x86_64'}, {'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T14:58:33.551Z', 'message': 'Building tool. Build log: /dls_sw/work/etc/build/test/local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1/ffmpeg/4-2-1/local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1.log'}, {'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T14:58:33.494Z', 'message': 'Checking out tag: 4-2-1'}, {'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T14:58:32.509Z', 'message': 'Cloning repo: https://gitlab.diamond.ac.uk/controls/tools/ffmpeg.git'}, {'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T14:58:32.506Z', 'message': 'version dir: /dls_sw/work/etc/build/test/local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1/ffmpeg/4-2-1'}]

response_ioc = [{'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:49.619Z', 'message': 'Build complete'}, {'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:45.900Z', 'message': 'Starting build. Build log: /dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10/build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10.log errors: /dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10/build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10.err'}, {'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:45.891Z', 'message': 'Wrote configure/RELEASE.linux-x86_64[.Common]: EPICS_BASE=/dls_sw/epics/R3.14.12.3/base SUPPORT=/dls_sw/prod/R3.14.12.3/support'}, {'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:45.507Z', 'message': 'Checking out tag: 5-10'}, {'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:44.987Z', 'message': 'Cloning repo: https://gitlab.diamond.ac.uk/controls/ioc/SR09J/SR09J-CS-IOC-01.git'}, {'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:44.983Z', 'message': 'version dir: /dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10'}]

status_dict_etc = {'Log file': 'No log file available', 'Err msgs': 'No err file available', 'Job status': 'Build complete at 18:13:30 2019-11-01', 'Job name': 'build_20191101-181325_mef65357_etc_init_3-515'}

status_dict_ioc = {'Log file': '/dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10/build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10.log', 'Err msgs': '/dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10/build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10.err', 'Job status': 'Build complete at 10:30:49 2019-11-01', 'Job name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10'}

test_content = '"timestamp","message","build_name"\n"2019-11-04T14:04:45.337Z","M1"\n"2019-11-04T14:04:45.332Z","M2"\n"2019-11-04T14:04:47.566Z","M3","BN3"\n"2019-11-04T14:04:46.706Z","M4","BN4"'

class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = dls_last_release.make_parser()
        print("set")

    def test_wait_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-w']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "wait")
        self.assertIn("--wait", option.option_strings)

    def test_user_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-u']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.dest, "user")
        self.assertIn("--user", option.option_strings)

    def test_errors_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-e']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "errors")
        self.assertIn("--errors", option.option_strings)

    def test_nresults_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-n']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.dest, "nresults")
        self.assertIn("--nresults", option.option_strings)

    def test_local_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-l']
        self.assertIsInstance(option, _StoreTrueAction)
        self.assertEqual(option.dest, "local")
        self.assertIn("--local", option.option_strings)


@pytest.mark.parametrize("build_name,status_dict_area,expected", [
    (response_etc[0]["build_name"], response_etc, status_dict_etc),
    (response_ioc[0]["build_name"], response_ioc, status_dict_ioc)
])
def test_build_status(build_name,status_dict_area, expected):
    assert dls_last_release.build_status(build_name, status_dict_area) == expected

@mock.patch("dls_ade.dls_last_release.requests")
def test_graylog_request_calls_correctly(mock_graylog):
    test_request = "Test request"
    dls_last_release.graylog_request(test_request)

    assert mock_graylog.called_once_with(content=test_request)

@pytest.mark.parametrize("response", [
    (response_etc),
])
def test_parse_timestamp(response):
    timestamp_list = dls_last_release.get_timestamp_list(response)
    timestamp = dls_last_release.parse_timestamp(timestamp_list[0])
    match = re.match('(\d{2}):(\d{2}):(\d{2})(\s{1})(\d{4})-(\d{2})-(\d{2})', timestamp)
    assert match is not None

@pytest.mark.parametrize("status_dict_area,expected", [
    (response_etc, True),
    (response_ioc, True)
])
def test_is_finished(status_dict_area, expected):
    assert dls_last_release.is_finished(status_dict_area) == expected

@pytest.mark.parametrize("status_dict_area,expected", [
    (response_etc, True),
    (response_ioc, True)
])
def test_is_started(status_dict_area, expected):
    assert dls_last_release.is_started(status_dict_area) == expected

@pytest.mark.parametrize("status_dict_area,ext,expected", [
    (response_etc, "log", "No log file available"),
    (response_ioc, "log", "/dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10/build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10.log")
])
def test_find_log_file(status_dict_area, expected, ext):
    assert dls_last_release.find_file(status_dict_area, ext) == expected

