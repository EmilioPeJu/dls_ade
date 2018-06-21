#!/bin/env dls-python

import unittest
from dls_ade import dls_environment
from mock import patch, ANY, MagicMock


class EnvironmentInitTest(unittest.TestCase):

    def test_given_epics_then_set(self):
        epics = 'R3.14.8.2'

        env = dls_environment.environment(epics)

        self.assertEqual(env.epics, epics)

    def test_not_given_epics_then_default(self):
        env = dls_environment.environment()

        self.assertEqual(env.epics, None)

    @patch('dls_ade.dls_environment.re.compile', return_value="reg_ex")
    def test_reg_exp_set(self, mock_compile):
        expected_reg_ex = r"R\d(\.\d+)+"
        env = dls_environment.environment()

        mock_compile.assert_called_once_with(expected_reg_ex)
        self.assertEqual(env.epics_ver_re, "reg_ex")

    def test_areas_set(self):
        areas = ["support", "ioc", "matlab", "python", "etc", "tools", "epics"]

        env = dls_environment.environment()

        for area in areas:
            self.assertIn(area, env.areas)


class CheckEpicsVersionTest(unittest.TestCase):

    @patch('dls_ade.dls_environment.environment.setEpics')
    def test_given_epics_version_with_R_and_match_then_set(self, mock_set_epics):
        env = dls_environment.environment()
        epics_version = "R3.14.8.2"

        env.check_epics_version(epics_version)

        mock_set_epics.assert_called_once_with(epics_version)

    @patch('dls_ade.dls_environment.environment.setEpics')
    def test_given_epics_version_without_R_and_match_then_set(self, mock_set_epics):
        env = dls_environment.environment()
        epics_version = "3.14.8.2"

        env.check_epics_version(epics_version)

        mock_set_epics.assert_called_once_with("R" + epics_version)

    @patch('dls_ade.dls_environment.environment.setEpics')
    def test_given_epics_version_with_R_and_not_match_then_raise_error(self, mock_set_epics):
        env = dls_environment.environment()
        epics_version = "R3"
        expected_error_message = "Expected epics version like R3.14.8.2, got: " + epics_version

        try:
            env.check_epics_version(epics_version)
        except Exception as error:
            self.assertEqual(str(error), expected_error_message)


class SetEpicsFromEnvTest(unittest.TestCase):

    def test_given_dls_epics_release_exists_then_set(self):
        env = dls_environment.environment()

        with patch.dict('os.environ', {'DLS_EPICS_RELEASE': "test_dls_release"}, clear=True):
            env.setEpicsFromEnv()

        self.assertEqual(env.epics, "test_dls_release")

    def test_given_epics_release_exists_then_set(self):
        env = dls_environment.environment()

        with patch.dict('os.environ', {'EPICS_RELEASE': "test_release"}, clear=True):
            env.setEpicsFromEnv()

        self.assertEqual(env.epics, "test_release")

    def test_given_neither_exists_then_set_default(self):
        env = dls_environment.environment()

        with patch.dict('os.environ', {'DOESNT_EXIST': "test_release"}, clear=True):
            env.setEpicsFromEnv()

        self.assertEqual(env.epics, "R3.14.12.3")


class SetEpicsTest(unittest.TestCase):

    def test_given_epics_value_then_epics_set(self):
        epics = "test_epics"
        env = dls_environment.environment()

        env.setEpics(epics)

        self.assertEqual("test_epics", env.epics)


class EpicsDirTest(unittest.TestCase):

    @patch('dls_ade.dls_environment.environment.epicsVer', return_value="R3.12")
    @patch('dls_ade.dls_environment.environment.epicsVerDir', return_value="test")
    def test_given_epics_ver_less_than_R314_then_home(self, _1, _2):
        env = dls_environment.environment()

        epics_dir = env.epicsDir()

        self.assertEqual(epics_dir, "/home/epics/test")

    @patch('dls_ade.dls_environment.environment.epicsVer', return_value="R3.15")
    @patch('dls_ade.dls_environment.environment.epicsVerDir', return_value="test")
    def test_given_epics_ver_more_than_R314_then_home(self, _1, _2):
        env = dls_environment.environment()

        epics_dir = env.epicsDir()

        self.assertEqual(epics_dir, "/dls_sw/epics/test")


class EpicsVerTest(unittest.TestCase):

    @patch('dls_ade.dls_environment.environment.setEpicsFromEnv')
    def test_given_epics_not_set_then_set_and_return(self, mock_set_epics_from_env):
        env = dls_environment.environment()

        env.epicsVer()

        mock_set_epics_from_env.assert_called_once_with()

    @patch('dls_ade.dls_environment.environment.setEpicsFromEnv')
    def test_given_epics_set_then_return(self, mock_set_epics_from_env):
        env = dls_environment.environment()
        env.epics = "test_epics"

        epics = env.epicsVer()

        self.assertFalse(mock_set_epics_from_env.call_count)
        self.assertEqual(epics, "test_epics")


class EpicsVerDirTest(unittest.TestCase):

    @patch('dls_ade.dls_environment.environment.setEpicsFromEnv')
    def test_given_epics_not_set_then_set_dir_and_return(self, mock_set_epics_from_env):
        env = dls_environment.environment()
        env.epics = ""

        env.epicsVerDir()

        mock_set_epics_from_env.assert_called_once_with()

    @patch('dls_ade.dls_environment.environment.setEpicsFromEnv')
    def test_given_epics_set_then_return_dir(self, mock_set_epics_from_env):
        env = dls_environment.environment()
        env.epics = "dir_test_epics"

        epics = env.epicsVerDir()

        self.assertFalse(mock_set_epics_from_env.call_count)
        self.assertEqual(epics, "dir")


class DevAreaTest(unittest.TestCase):

    def test_given_area_not_in_areas_then_exception_raised(self):
        area = "not/an/area"
        env = dls_environment.environment()

        with self.assertRaises(Exception):
            env.devArea(area)

    @patch('dls_ade.dls_environment.environment.epicsVerDir', return_value='dir')
    def test_given_version_less_and_support_then_home_diamond_dir(self, _1):
        expected_path = "/home/diamond/dir/work/support"
        env = dls_environment.environment()
        env.epics = "R3.1"

        path = env.devArea()

        self.assertEqual(path, expected_path)

    @patch('dls_ade.dls_environment.environment.epicsVerDir', return_value='dir')
    def test_given_version_less_and_ioc_then_home_diamond_dir(self, _1):
        area = "ioc"
        expected_path = "/home/diamond/dir/work/" + area

        env = dls_environment.environment()
        env.epics = "R3.1"
        path = env.devArea(area)

        self.assertEqual(path, expected_path)

    def test_given_version_less_and_epics_then_home_work(self):
        area = "epics"
        expected_path = "/home/work/" + area

        env = dls_environment.environment()
        env.epics = "R3.1"
        path = env.devArea(area)

        self.assertEqual(path, expected_path)

    def test_given_version_less_and_etx_then_home_work(self):
        area = "etc"
        expected_path = "/home/work/" + area

        env = dls_environment.environment()
        env.epics = "R3.1"
        path = env.devArea(area)

        self.assertEqual(path, expected_path)

    def test_given_version_less_and_tools_then_home_work(self):
        area = "tools"
        expected_path = "/home/work/" + area

        env = dls_environment.environment()
        env.epics = "R3.1"
        path = env.devArea(area)

        self.assertEqual(path, expected_path)

    def test_given_version_less_and_matlab_then_home_diamond_common(self):
        area = "matlab"
        expected_path = "/home/diamond/common/work/" + area

        env = dls_environment.environment()
        env.epics = "R3.1"
        path = env.devArea(area)

        self.assertEqual(path, expected_path)

    def test_given_version_less_and_python_then_home_diamond_common(self):
        area = "python"
        expected_path = "/home/diamond/common/work/" + area

        env = dls_environment.environment()
        env.epics = "R3.1"
        path = env.devArea(area)

        self.assertEqual(path, expected_path)

    @patch('dls_ade.dls_environment.environment.epicsVerDir', return_value='dir')
    def test_given_version_more_and_support_then_dls_diamond_dir(self, _1):
        expected_path = "/dls_sw/work/dir/support"
        env = dls_environment.environment()
        env.epics = "R3.15"

        path = env.devArea()

        self.assertEqual(path, expected_path)

    @patch('dls_ade.dls_environment.environment.epicsVerDir', return_value='dir')
    def test_given_version_more_and_ioc_then_dls_diamond_dir(self, _1):
        area = 'ioc'
        expected_path = "/dls_sw/work/dir/" + area
        env = dls_environment.environment()
        env.epics = "R3.15"

        path = env.devArea(area)

        self.assertEqual(path, expected_path)

    def test_given_version_more_and_epics_then_dls_work(self):
        area = 'epics'
        expected_path = "/dls_sw/work/" + area
        env = dls_environment.environment()
        env.epics = "R3.15"

        path = env.devArea(area)

        self.assertEqual(path, expected_path)

    def test_given_version_more_and_etc_then_dls_work(self):
        area = 'etc'
        expected_path = "/dls_sw/work/" + area
        env = dls_environment.environment()
        env.epics = "R3.15"

        path = env.devArea(area)

        self.assertEqual(path, expected_path)

    def test_given_version_more_and_tools_then_dls_work(self):
        area = 'tools'
        expected_path = "/dls_sw/work/" + area
        env = dls_environment.environment()
        env.epics = "R3.15"

        path = env.devArea(area)

        self.assertEqual(path, expected_path)

    def test_given_version_more_and_matlab_then_dls_work_common(self):
        area = 'matlab'
        expected_path = "/dls_sw/work/common/" + area
        env = dls_environment.environment()
        env.epics = "R3.15"

        path = env.devArea(area)

        self.assertEqual(path, expected_path)

    def test_given_version_more_and_python_then_dls_work_common(self):
        area = 'python'
        expected_path = "/dls_sw/work/common/" + area
        env = dls_environment.environment()
        env.epics = "R3.15"

        path = env.devArea(area)

        self.assertEqual(path, expected_path)


class ProdAreaTest(unittest.TestCase):

    def test_given_epics_then_dls(self):
        area = 'epics'
        expected_path = "/dls_sw/" + area

        env = dls_environment.environment()
        path = env.prodArea(area)

        self.assertEqual(path, expected_path)

    @patch('dls_ade.dls_environment.environment.devArea')
    def test_given_support_then_prod(self, mock_dev_area):
        area = 'support'
        expected_path = "test/prod/test/" + area

        env = dls_environment.environment()
        env.devArea.return_value = "test/work/test/" + area
        path = env.prodArea(area)

        self.assertEqual(path, expected_path)
        mock_dev_area.assert_called_once_with(area)

    @patch('dls_ade.dls_environment.environment.devArea')
    def test_given_ioc_then_prod(self, mock_dev_area):
        area = 'ioc'
        expected_path = "test/prod/test/" + area

        env = dls_environment.environment()
        env.devArea.return_value = "test/work/test/" + area
        path = env.prodArea(area)

        self.assertEqual(path, expected_path)
        mock_dev_area.assert_called_once_with(area)

    @patch('dls_ade.dls_environment.environment.devArea')
    def test_given_etc_then_prod(self, mock_dev_area):
        area = 'etc'
        expected_path = "test/prod/test/" + area

        env = dls_environment.environment()
        env.devArea.return_value = "test/work/test/" + area
        path = env.prodArea(area)

        self.assertEqual(path, expected_path)
        mock_dev_area.assert_called_once_with(area)

    @patch('dls_ade.dls_environment.environment.devArea')
    def test_given_tools_then_prod(self, mock_dev_area):
        area = 'tools'
        expected_path = "test/prod/test/" + area

        env = dls_environment.environment()
        env.devArea.return_value = "test/work/test/" + area
        path = env.prodArea(area)

        self.assertEqual(path, expected_path)
        mock_dev_area.assert_called_once_with(area)

    @patch('dls_ade.dls_environment.environment.devArea')
    def test_given_matlab_then_prod(self, mock_dev_area):
        area = 'matlab'
        expected_path = "test/prod/test/" + area

        env = dls_environment.environment()
        env.devArea.return_value = "test/work/test/" + area
        path = env.prodArea(area)

        self.assertEqual(path, expected_path)
        mock_dev_area.assert_called_once_with(area)

    @patch('dls_ade.dls_environment.environment.devArea')
    def test_given_python_then_prod(self, mock_dev_area):
        area = 'python'
        expected_path = "test/prod/test/" + area

        env = dls_environment.environment()
        env.devArea.return_value = "test/work/test/" + area
        path = env.prodArea(area)

        self.assertEqual(path, expected_path)
        mock_dev_area.assert_called_once_with(area)


class NormaliseReleaseTest(unittest.TestCase):

    def test_normalises_3(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("3"),
                         [3, 'z', 0, '', 0, '', 0, '', 0, '', 0, ''])

    def test_normalises_1_3(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("1-3"),
                         [1, 'z', 3, 'z', 0, '', 0, '', 0, '', 0, ''])

    def test_normalises_dash_1_3(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("-1-3"),
                         [0, '', 1, 'z', 3, 'z', 0, '', 0, '', 0, ''])

    def test_normalises_1_15(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("1-15"),
                         [1, 'z', 15, 'z', 0, '', 0, '', 0, '', 0, ''])

    def test_normalises_12_15(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("12-15"),
                         [12, 'z', 15, 'z', 0, '', 0, '', 0, '', 0, ''])

    def test_normalises_3_2_1(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("3-2-1"),
                         [3, 'z', 2, 'z', 1, 'z', 0, '', 0, '', 0, ''])

    def test_normalises_4_3_21(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("4-3-21"),
                         [4, 'z', 3, 'z', 21, 'z', 0, '', 0, '', 0, ''])

    def test_normalises_12_18_10(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("12-18-10"),
                         [12, 'z', 18, 'z', 10, 'z', 0, '', 0, '', 0, ''])

    def test_normalises_12_18_125(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("12-18-125"),
                         [12, 'z', 18, 'z', 125, 'z', 0, '', 0, '', 0, ''])

    def test_normalises_1_2_3_4(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("1-2-3-4"),
                         [1, 'z', 2, 'z', 3, 'z', 4, 'z', 0, '', 0, ''])

    def test_normalises_1_2_3_4_5_6_7(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("1-2-3-4-5-6-7"),
                         [1, 'z', 2, 'z', 3, 'z', 4, '-5-6-7', 0, '', 0, ''])

    def test_normalises_3_dls_12(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("3dls12"),
                         [3, 'z', 0, '', 0, '', 12, 'z', 0, '', 0, ''])

    def test_normalises_3_dash_dls_12(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("3-dls12"),
                         [3, 'z', 0, '', 0, '', 12, 'z', 0, '', 0, ''])

    def test_normalises_3_10_dls_12(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("3-10dls12"),
                         [3, 'z', 10, 'z', 0, '', 12, 'z', 0, '', 0, ''])

    def test_normalises_1_7_12_1dls_16(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("1-7-12-1dls16"),
                         [1, 'z', 7, 'z', 12, 'z', 1, 'z', 16, 'z', 0, ''])

    def test_normalises_1_7_12_1dls16_2_13_2(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("1-7-12-1dls16-2-13"),
                         [1, 'z', 7, 'z', 12, 'z', 1, 'z', 16, 'z', 2, 'z', 13, 'z'])

    def test_normalises_4_5_beta2_dls_1_3(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("4-5beta2dls1-3"),
                         [4, 'z', 5, 'beta2', 0, '', 1, 'z', 3, 'z', 0, ''])

    def test_normalises_1_7_12_beta1dls16_2_13_2(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("1-7-12-beta1dls16-2-13"),
                         [1, 'z', 7, 'z', 12, 'z', 0, 'beta1', 16, 'z', 2, 'z', 13, 'z'])

    def test_normalises_1_7_12beta1dls16_2_13_2(self):
        env = dls_environment.environment()
        self.assertEqual(env.normaliseRelease("1-7-12beta1dls16-2-13"),
                         [1, 'z', 7, 'z', 12, 'beta1', 16, 'z', 2, 'z', 13, 'z'])


class SortReleasesTest(unittest.TestCase):

    def test_sorts_singles(self):
        env = dls_environment.environment()
        a = '2'
        a_norm = [2, 'z', 0, 'z', 0, '', 0, '', 0, '', 0, '']
        b = '3'
        b_norm = [3, 'z', 0, 'z', 0, '', 0, '', 0, '', 0, '']
        c = '1'
        c_norm = [1, 'z', 0, 'z', 0, '', 0, '', 0, '', 0, '']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]), ['1', '2', '3'])

    def test_sorts_doubles(self):
        env = dls_environment.environment()
        a = '1-2'
        a_norm = [1, 'z', 2, 'z', 0, '', 0, '', 0, '', 0, '']
        b = '1-3'
        b_norm = [1, 'z', 3, 'z', 0, '', 0, '', 0, '', 0, '']
        c = '1-1'
        c_norm = [1, 'z', 1, 'z', 0, '', 0, '', 0, '', 0, '']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]), ['1-1', '1-2', '1-3'])

    def test_sorts_triples(self):
        env = dls_environment.environment()
        a = '1-2-3'
        a_norm = [1, 'z', 2, 'z', 3, '', 0, '', 0, '', 0, '']
        b = '1-3-2'
        b_norm = [1, 'z', 3, 'z', 2, '', 0, '', 0, '', 0, '']
        c = '1-2-1'
        c_norm = [1, 'z', 2, 'z', 1, '', 0, '', 0, '', 0, '']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]), ['1-2-1', '1-2-3', '1-3-2'])

    def test_sorts_x_dls_y(self):
        env = dls_environment.environment()
        a = '3dls12'
        a_norm = [3, 'z', 0, '', 0, '', 12, 'z', 0, '', 0, '']
        b = '2dls12'
        b_norm = [2, 'z', 0, '', 0, '', 12, 'z', 0, '', 0, '']
        c = '3dls10'
        c_norm = [3, 'z', 0, '', 0, '', 10, 'z', 0, '', 0, '']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]), ['2dls12', '3dls10', '3dls12'])

    def test_sorts_x_x_dls_y(self):
        env = dls_environment.environment()
        a = '3-10dls12'
        a_norm = [3, 'z', 10, 'z', 0, '', 12, 'z', 0, '', 0, '']
        b = '3-8dls12'
        b_norm = [3, 'z', 8, 'z', 0, '', 12, 'z', 0, '', 0, '']
        c = '3-10dls15'
        c_norm = [3, 'z', 10, 'z', 0, '', 15, 'z', 0, '', 0, '']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]), ['3-8dls12', '3-10dls12', '3-10dls15'])

    def test_sorts_x_x_beta_dls_y(self):
        env = dls_environment.environment()
        a = '4-5beta2dls1-3'
        a_norm = [4, 'z', 5, 'beta2', 0, '', 1, 'z', 3, 'z', 0, '']
        b = '4-5beta1dls1-3'
        b_norm = [4, 'z', 5, 'beta1', 0, '', 1, 'z', 3, 'z', 0, '']
        c = '4-5beta2dls2-3'
        c_norm = [4, 'z', 5, 'beta2', 0, '', 2, 'z', 3, 'z', 0, '']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]),
                         ['4-5beta1dls1-3', '4-5beta2dls1-3', '4-5beta2dls2-3'])

    def test_sorts_x_x_x_beta_dls_y(self):
        env = dls_environment.environment()
        a = '1-7-12beta1dls16-2-13-1'
        a_norm = [1, 'z', 7, 'z', 12, 'beta1', 16, 'z', 2, 'z', 13, 'z', 1, 'z']
        b = '1-7-12beta1dls17'
        b_norm = [1, 'z', 7, 'z', 12, 'beta1', 17, 'z', 0, '', 0, '']
        c = '1-7-12beta2dls2-3'
        c_norm = [1, 'z', 7, 'z', 12, 'beta2', 2, 'z', 3, '', 0, '']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]),
                         ['1-7-12beta1dls16-2-13-1', '1-7-12beta1dls17', '1-7-12beta2dls2-3'])

    def test_sorts_x_x_x_x_dls_y(self):
        env = dls_environment.environment()
        a = '1-7-12-3dls16-2-13-1'
        a_norm = [1, 'z', 7, 'z', 12, 'z', 3, 'z', 16, 'z', 2, 'z', 13, 'z', 1, 'z']
        b = '1-7-12-2dls16-2-13-1'
        b_norm = [1, 'z', 7, 'z', 12, 'z', 2, 'z', 16, 'z', 2, 'z', 13, 'z', 1, 'z']
        c = '1-7-12-3dls16-2-14-1'
        c_norm = [1, 'z', 7, 'z', 12, 'z', 3, 'z', 16, 'z', 2, 'z', 14, 'z', 1, 'z']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]),
                         ['1-7-12-2dls16-2-13-1', '1-7-12-3dls16-2-13-1', '1-7-12-3dls16-2-14-1'])

    def test_sorts_x_x_x_x_beta_dls_y(self):
        env = dls_environment.environment()
        a = '1-7-12-3alpha1dls16'
        a_norm = [1, 'z', 7, 'z', 12, 'z', 3, 'alpha1', 16, 'z', 0, '', 0, '', 0, '']
        b = '1-7-12-3alpha2dls16'
        b_norm = [1, 'z', 7, 'z', 12, 'z', 3, 'alpha2', 16, 'z', 0, '', 0, '', 0, '']
        c = '1-7-12-3dls16'
        c_norm = [1, 'z', 7, 'z', 12, 'z', 3, 'z', 16, 'z', 0, '', 0, '', 0, '']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]),
                         ['1-7-12-3alpha1dls16', '1-7-12-3alpha2dls16', '1-7-12-3dls16'])

    def test_sorts_x_x_x_x_alpha_alpha2_dls_y(self):
        env = dls_environment.environment()
        a = '1-7-12-3alpha1dls16'
        a_norm = [1, 'z', 7, 'z', 12, 'z', 3, 'alpha1', 16, 'z', 0, '', 0, '', 0, '']
        b = '1-7-12-3alpha2dls16'
        b_norm = [1, 'z', 7, 'z', 12, 'z', 3, 'alpha2', 16, 'z', 0, '', 0, '', 0, '']
        c = '1-7-12-3dls16'
        c_norm = [1, 'z', 7, 'z', 12, 'z', 3, 'z', 16, 'z', 0, '', 0, '', 0, '']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]),
                         ['1-7-12-3alpha1dls16', '1-7-12-3alpha2dls16', '1-7-12-3dls16'])

    def test_sorts_dash_doubles(self):
        env = dls_environment.environment()
        a = '-1-3'
        a_norm = [0, '', 1, 'z', 3, 'z', 0, '', 0, '', 0, '']
        b = '1-3'
        b_norm = [1, 'z', 3, 'z', 0, '', 0, '', 0, '', 0, '']
        c = '-1-2'
        c_norm = [0, '', 1, 'z', 2, 'z', 0, '', 0, '', 0, '']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]), ['-1-2', '-1-3', '1-3'])

    def test_sorts_letters(self):
        env = dls_environment.environment()
        a = '1-f'
        a_norm = [1, 'z', 0, 'fz', 0, '', 0, '', 0, '', 0, '']
        b = '1-a'
        b_norm = [1, 'z', 0, 'az', 0, '', 0, '', 0, '', 0, '']
        c = '1-1'
        c_norm = [1, 'z', 1, 'z', 0, '', 0, '', 0, '', 0, '']

        if isinstance(env.normaliseRelease, MagicMock):
            env.normaliseRelease.side_effect = [a_norm, b_norm, c_norm]

        self.assertEqual(env.sortReleases([a, b, c]), ['1-a', '1-f', '1-1'])


class SortReleasesTestWithPatch(SortReleasesTest):

    @patch('dls_ade.dls_environment.environment.normaliseRelease')
    def test_sorts_singles(self, _1):
        super(SortReleasesTestWithPatch, self).test_sorts_singles()

    @patch('dls_ade.dls_environment.environment.normaliseRelease')
    def test_sorts_doubles(self, _1):
        super(SortReleasesTestWithPatch, self).test_sorts_doubles()

    @patch('dls_ade.dls_environment.environment.normaliseRelease')
    def test_sorts_dash_doubles(self, _1):
        super(SortReleasesTestWithPatch, self).test_sorts_dash_doubles()

    @patch('dls_ade.dls_environment.environment.normaliseRelease')
    def test_sorts_triples(self, _1):
        super(SortReleasesTestWithPatch, self).test_sorts_triples()

    @patch('dls_ade.dls_environment.environment.normaliseRelease')
    def test_sorts_x_dls_y(self, _1):
        super(SortReleasesTestWithPatch, self).test_sorts_x_dls_y()

    @patch('dls_ade.dls_environment.environment.normaliseRelease')
    def test_sorts_x_x_beta_dls_y(self, _1):
        super(SortReleasesTestWithPatch, self).test_sorts_x_x_beta_dls_y()

    @patch('dls_ade.dls_environment.environment.normaliseRelease')
    def test_sorts_x_x_x_beta_dls_y(self, _1):
        super(SortReleasesTestWithPatch, self).test_sorts_x_x_x_beta_dls_y()

    @patch('dls_ade.dls_environment.environment.normaliseRelease')
    def test_sorts_x_x_x_x_dls_y(self, _1):
        super(SortReleasesTestWithPatch, self).test_sorts_x_x_x_x_dls_y()

    @patch('dls_ade.dls_environment.environment.normaliseRelease')
    def test_sorts_x_x_x_x_beta_dls_y(self, _1):
        super(SortReleasesTestWithPatch, self).test_sorts_x_x_x_x_beta_dls_y()

    @patch('dls_ade.dls_environment.environment.normaliseRelease')
    def test_sorts_letters(self, _1):
        super(SortReleasesTestWithPatch, self).test_sorts_letters()

