#!/bin/env dls-python

import pytest
import unittest
import mock
import dls_ade.dls_last_release as dls_last_release

from argparse import _StoreAction
from argparse import _StoreTrueAction

import re
from requests.models import Response

build_job_response = [{'build_name': '', 'timestamp': '2020-01-21T16:05:09.858Z', 'message': "Build server job parameters: {'dls_syslog_server': 'graylog2.diamond.ac.uk', 'force': 'false', 'epics': 'R3.14.12.7', 'module': 'BL08J-BUILDER', 'build_name': 'build_20200121-160509_ysx26594_support_BL08J-BUILDER_0-27', 'git_dir': 'https://gitlab.diamond.ac.uk/controls/support/BL08J-BUILDER.git', 'user': 'ysx26594', 'dls_syslog_server_port': '12209', 'area': 'support', 'build_dir': '/dls_sw/prod/R3.14.12.7/support', 'version': '0-27', 'email': u'tom.trafford@diamond.ac.uk'}"}, {'build_name': '', 'timestamp': '2020-01-21T16:03:17.809Z', 'message': "Build server job parameters: {'dls_syslog_server': 'graylog2.diamond.ac.uk', 'force': 'false', 'epics': 'R3.14.12.7', 'module': 'Launcher', 'build_name': 'build_20200121-160317_hgs15624_etc_Launcher_0-87', 'git_dir': 'https://gitlab.diamond.ac.uk/controls/etc/Launcher.git', 'user': 'hgs15624', 'dls_syslog_server_port': '12209', 'area': 'etc', 'build_dir': '/dls_sw/prod/etc', 'version': '0-87', 'email': u'will.rogers@diamond.ac.uk'}"}]

build_jobs = ["build_20200121-160509_ysx26594_support_BL08J-BUILDER_0-27", "build_20200121-160317_hgs15624_etc_Launcher_0-87"]

response_etc = [{'build_name': 'build_20191101-181325_mef65357_etc_init_3-515', 'timestamp': '2019-11-01T18:13:30.302Z', 'message': 'Build complete'}, {'build_name': 'build_20191101-181325_mef65357_etc_init_3-515', 'timestamp': '2019-11-01T18:13:29.712Z', 'message': 'Running make'}, {'build_name': 'build_20191101-181325_mef65357_etc_init_3-515', 'timestamp': '2019-11-01T18:13:26.664Z', 'message': 'Starting build. Building etc in /dls_sw/prod/etc'}]

response_tools = [{'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T15:07:55.279Z', 'message': 'Build complete'}, {'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T15:07:42.490Z', 'message': 'make-defaults: /dls_sw/work/etc/build/test/local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1 /dls_sw/prod/etc/build/tools_build/RELEASE.RHEL7-x86_64 7 x86_64'}, {'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T14:58:33.551Z', 'message': 'Starting build. Build log: /dls_sw/work/etc/build/test/local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1/ffmpeg/4-2-1/local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1.log'}, {'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T14:58:33.494Z', 'message': 'Checking out tag: 4-2-1'}, {'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T14:58:32.509Z', 'message': 'Cloning repo: https://gitlab.diamond.ac.uk/controls/tools/ffmpeg.git'}, {'build_name': 'local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1', 'timestamp': '2019-11-01T14:58:32.506Z', 'message': 'version dir: /dls_sw/work/etc/build/test/local_20191101-145832_cvl62853_tools_ffmpeg_4-2-1/ffmpeg/4-2-1'}]

response_ioc = [{'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:49.619Z', 'message': 'Build complete'}, {'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:45.900Z', 'message': 'Starting build. Build log: /dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10/build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10.log errors: /dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10/build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10.err'}, {'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:45.891Z', 'message': 'Wrote configure/RELEASE.linux-x86_64[.Common]: EPICS_BASE=/dls_sw/epics/R3.14.12.3/base SUPPORT=/dls_sw/prod/R3.14.12.3/support'}, {'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:45.507Z', 'message': 'Checking out tag: 5-10'}, {'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:44.987Z', 'message': 'Cloning repo: https://gitlab.diamond.ac.uk/controls/ioc/SR09J/SR09J-CS-IOC-01.git'}, {'build_name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10', 'timestamp': '2019-11-01T10:30:44.983Z', 'message': 'version dir: /dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10'}]

status_dict_etc = {'Log file': 'No log file available', 'Err msgs': 'No err file available', 'Job status': 'Build complete at 18:13:30 2019-11-01', 'Job name': 'build_20191101-181325_mef65357_etc_init_3-515'}

status_dict_ioc = {'Log file': '/dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10/build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10.log', 'Err msgs': '/dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10/build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10.err', 'Job status': 'Build complete at 10:30:49 2019-11-01', 'Job name': 'build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10'}

test_content = '"timestamp","message","build_name"\n"2019-11-04T14:04:45.337Z","M1"\n"2019-11-04T14:04:45.332Z","M2"\n"2019-11-04T14:04:47.566Z","M3","BN3"\n"2019-11-04T14:04:46.706Z","M4","BN4"'

not_windows_ioc = [{'build_name': '', 'timestamp': '2020-01-21T17:54:20.468Z', 'message': 'Build request file: build_20200121-175420_xfz39520_ioc_BL04J_BL04J-MO-IOC-02_2020-R7-Run1-5.redhat7-x86_64\\nCreated in : /dls_sw/work/etc/build/queue'}]

windows_ioc = [{'build_name': '', 'timestamp': '2020-01-17T12:58:36.192Z', 'message': 'Build request file: build_20200117-125836_cvl62853_ioc_ME13C_ME13C-EA-IOC-03_0-1.windows6_3-AMD64 Created in : /dls_sw/work/etc/build/queue'}]

time_frame = 2

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

    def test_time_frame_option_has_correct_attributes(self):
        option = self.parser._option_string_actions['-t']
        self.assertIsInstance(option, _StoreAction)
        self.assertEqual(option.dest, "time_frame")
        self.assertIn("--time_frame", option.option_strings)


def test_get_build_jobs():
    with mock.patch('dls_ade.dls_last_release.get_graylog_response') as mocked_graylog_response:
        mocked_graylog_response.return_value = build_job_response
        assert dls_last_release.get_build_jobs(time_frame, user="all", njobs=5, local=False) == build_jobs

@pytest.mark.parametrize("build_name, windows_response, expected", [
    ("build_20200121-175420_xfz39520_ioc_BL04J_BL04J-MO-IOC-02_2020-R7-Run1-5", not_windows_ioc, False),
    ("build_20200117-125836_cvl62853_ioc_ME13C_ME13C-EA-IOC-03_0-1", windows_ioc, True),
    (build_jobs[1], [], False),
])
def test_is_windows(build_name, windows_response, expected):
    with mock.patch('dls_ade.dls_last_release.get_graylog_response') as mocked_graylog_response:
          mocked_graylog_response.return_value = windows_response
          assert dls_last_release.is_windows(build_name, time_frame) == expected

@pytest.mark.parametrize("build_name, time_frame ,expected", [
    (response_ioc[0]["build_name"], time_frame, status_dict_ioc),
])
def test_build_status(build_name, time_frame, expected):
    with mock.patch('dls_ade.dls_last_release.get_completed_dict') as mocked_graylog_completed_dict:
        with mock.patch('dls_ade.dls_last_release.get_started_dict') as mocked_graylog_started_dict:
            mocked_graylog_completed_dict.return_value = response_ioc[0]
            mocked_graylog_started_dict.return_value = response_ioc[1]
            assert dls_last_release.get_build_status(build_name, time_frame) == expected

@mock.patch("dls_ade.dls_last_release.requests")
def test_graylog_request_calls_correctly(mock_graylog):
    test_request = "Test request"
    dls_last_release.graylog_request(test_request)
    assert mock_graylog.called_once_with(content=test_request)

@pytest.mark.parametrize("response", [
    (response_etc),
])
def test_parse_timestamp(response):
    timestamp = dls_last_release.parse_timestamp(response_etc[0]['timestamp'])
    match = re.match('(\d{2}):(\d{2}):(\d{2})(\s{1})(\d{4})-(\d{2})-(\d{2})', timestamp)
    assert match is not None

@pytest.mark.parametrize("started_dict,ext,expected", [
    (response_etc[2], "log", "No log file available"),
    (response_ioc[1], "log", "/dls_sw/prod/R3.14.12.3/ioc/SR09J/SR09J-CS-IOC-01/5-10/build_20191101-103043_rjq35657_ioc_SR09J_SR09J-CS-IOC-01_5-10.log")
])
def test_find_log_file(started_dict, expected, ext):
    assert dls_last_release.find_file(started_dict, ext) == expected

