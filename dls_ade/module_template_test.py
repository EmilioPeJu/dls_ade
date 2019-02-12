
import unittest
import os
import logging

import dls_ade.module_template as mt
from mock import patch, ANY, MagicMock, mock_open, call, mock_open

from sys import version_info
if version_info.major == 2:
    import __builtin__ as builtins  # Allows for Python 2/3 compatibility, 'builtins' is namespace for inbuilt functions
else:
    import builtins

logging.basicConfig(level=logging.DEBUG)


def set_up_mock(test_case_object, path):

    patch_obj = patch(path)

    test_case_object.addCleanup(patch_obj.stop)

    mock_obj = patch_obj.start()

    return mock_obj


class ModuleTemplateInitTest(unittest.TestCase):

    def setUp(self):

        self.mock_verify_template_args = set_up_mock(self, 'dls_ade.module_template.ModuleTemplate._verify_template_args')

    def test_given_function_called_then_attributes_set_and_verify_template_args_called_correctly(self):

        mt_obj = mt.ModuleTemplate({'arg3': "argument3"})
        mt_obj.add_required_args(['arg2'])

        self.assertEqual(mt_obj._template_args['arg3'], "argument3")
        self.assertEqual(mt_obj._required_template_args, {'arg2'})

        self.assertTrue(self.mock_verify_template_args.called)


class ModuleTemplateVerifyTemplateArgsTest(unittest.TestCase):

    def setUp(self):

        self.mt_obj = mt.ModuleTemplate({})

        self.mt_obj._template_args = {'arg1': "argument1", 'arg2': "argument2"}

    def test_given_required_template_args_present_then_no_error_raised(self):

        self.mt_obj._required_template_args = ['arg1']

        self.mt_obj._verify_template_args()

    def test_given_required_template_args_not_present_then_error_raised_with_correct_message(self):

        self.mt_obj._required_template_args = ['arg1', 'arg3']

        err_message = "All required template arguments must be supplied: arg1, arg3"

        with self.assertRaises(mt.ArgumentError) as e:
            self.mt_obj._verify_template_args()

        self.assertEqual(str(e.exception), err_message)


class ModuleTemplateSetTemplateFilesFromArea(unittest.TestCase):

    def setUp(self):

        self.module_template_folder = mt.TEMPLATES_FOLDER

        self.mock_os = set_up_mock(self, 'dls_ade.module_template.os')
        self.mock_get_from_folder = set_up_mock(self, 'dls_ade.module_template.ModuleTemplate._get_template_files_from_folder')

        # I want to retain these functions
        self.mock_os.path.join = os.path.join
        self.mock_os.path.dirname = os.path.dirname

        self.mt_obj = mt.ModuleTemplate({})

    def test_given_template_folder_does_not_exist_then_exception_raised_with_correct_message(self):

        self.mock_os.path.realpath.return_value = "test_dir/script_name"
        self.mock_os.path.isdir.return_value = False

        with self.assertRaises(mt.TemplateFolderError) as e:
            self.mt_obj._set_template_files_from_area("non_existent")

        self.assertTrue(self.module_template_folder in str(e.exception))

    def test_given_template_folder_does_exist_then_get_template_files_from_folder_called_with_correct_arguments_and_template_files_set_correctly(self):

        self.mock_get_from_folder.return_value = "template dictionary"
        self.mock_os.path.realpath.return_value = "test_dir/script_name"
        self.mock_os.path.isdir.return_value = True

        self.mt_obj._set_template_files_from_area("this_folder_exists")

        self.assertEqual(self.mt_obj._template_files, "template dictionary")
        self.mock_get_from_folder.assert_called_once_with("test_dir/" + self.module_template_folder + "/this_folder_exists")


class ModuleTemplateGetTemplateFilesFromFolderTest(unittest.TestCase):

    def setUp(self):

        self.patch_os = patch('dls_ade.module_template.os')

        self.addCleanup(self.patch_os.stop)

        self.mock_os = self.patch_os.start()

        self.mt_obj = mt.ModuleTemplate({})

        self.open_mock = mock_open()  # mock_open is a function designed to help mock the 'open' built-in function

    def test_given_template_folder_is_not_directory_then_exception_raised_with_correct_message(self):

        self.mock_os.path.isdir.return_value = False

        comp_message = "Template folder test_template_folder does not exist. \nNote: This exception means there is a bug in the ModuleTemplate subclass code.".format(template_folder="test_template_folder")

        with patch.object(builtins, 'open', self.open_mock):
            with self.assertRaises(mt.TemplateFolderError) as e:
                self.mt_obj._get_template_files_from_folder("test_template_folder")

        self.assertEqual(str(e.exception), comp_message)

    def test_given_files_directly_in_folder_then_template_dict_correctly_created(self):

        self.mock_os.path.join = os.path.join  # We want 'join' and 'relpath' to work as normal here
        self.mock_os.path.relpath = os.path.relpath
        self.mock_os.path.isdir.return_value = True
        file_handle_mock = self.open_mock()

        self.mock_os.walk.return_value = iter([["test_template_folder", "", ["file1.txt", "file2.txt"]]])

        file_handle_mock.read.side_effect = ["file1 text goes here", "file2 text goes here"]

        with patch.object(builtins, 'open', self.open_mock):
            template_files = self.mt_obj._get_template_files_from_folder("test_template_folder")

        comp_dict = {"file1.txt": "file1 text goes here", "file2.txt": "file2 text goes here"}

        self.assertEqual(comp_dict, template_files)

    def test_given_files_nested_then_template_dict_correctly_created(self):

        self.mock_os.path.join = os.path.join  # We want 'join' and 'relpath' to work as normal here
        self.mock_os.path.relpath = os.path.relpath
        self.mock_os.path.isdir.return_value = True
        file_handle_mock = self.open_mock()

        self.mock_os.walk.return_value = iter([["test_template_folder/extra_folder", "", ["file1.txt", "file2.txt"]]])

        file_handle_mock.read.side_effect = ["file1 text goes here", "file2 text goes here"]

        with patch.object(builtins, 'open', self.open_mock):
            template_files = self.mt_obj._get_template_files_from_folder("test_template_folder")

        comp_dict = {"extra_folder/file1.txt": "file1 text goes here", "extra_folder/file2.txt": "file2 text goes here"}

        self.assertEqual(comp_dict, template_files)

    def test_given_multiple_nested_files_then_template_dict_correctly_created(self):

        self.mock_os.path.join = os.path.join  # We want 'join' and 'relpath' to work as normal here
        self.mock_os.path.relpath = os.path.relpath
        self.mock_os.path.isdir.return_value = True
        file_handle_mock = self.open_mock()

        self.mock_os.walk.return_value = iter([["test_template_folder/extra_folder1", "", ["file1.txt", "file2.txt"]], ["test_template_folder/extra_folder2", "", ["file3.txt", "file4.txt"]]])

        file_handle_mock.read.side_effect = ["file1 text goes here", "file2 text goes here", "file3 text goes here", "file4 text goes here"]

        with patch.object(builtins, 'open', self.open_mock):
            template_files = self.mt_obj._get_template_files_from_folder("test_template_folder")

        comp_dict = {"extra_folder1/file1.txt": "file1 text goes here", "extra_folder1/file2.txt": "file2 text goes here", "extra_folder2/file3.txt": "file3 text goes here", "extra_folder2/file4.txt": "file4 text goes here"}

        self.assertEqual(comp_dict, template_files)

    def test_given_file_ends_with_py_template_then_template_dict_correctly_created(self):

        self.mock_os.path.join = os.path.join  # We want 'join' and 'relpath' to work as normal here
        self.mock_os.path.relpath = os.path.relpath
        self.mock_os.path.isdir.return_value = True
        file_handle_mock = self.open_mock()

        self.mock_os.walk.return_value = iter([["test_template_folder", "", ["file1.py_template", "file2.txt"]]])

        file_handle_mock.read.side_effect = ["file1 text goes here", "file2 text goes here"]

        with patch.object(builtins, 'open', self.open_mock):
            template_files = self.mt_obj._get_template_files_from_folder("test_template_folder")

        comp_dict = {"file1.py": "file1 text goes here", "file2.txt": "file2 text goes here"}

        self.assertEqual(comp_dict, template_files)


class ModuleTemplateCreateFilesTest(unittest.TestCase):

    @patch('dls_ade.module_template.ModuleTemplate._create_files_from_template_dict')
    @patch('dls_ade.module_template.ModuleTemplate._create_custom_files')
    def test_create_files_from_template_dict_called(self, mock_create_custom_files, mock_create_files_from_template):

        mt_obj = mt.ModuleTemplate({})

        mt_obj.create_files()

        mock_create_custom_files.assert_called_once_with()
        mock_create_files_from_template.assert_called_once_with()


class ModuleTemplateCreateFilesFromTemplateDictTest(unittest.TestCase):

    def setUp(self):

        self.patch_isdir = patch('dls_ade.module_template.os.path.isdir')
        self.patch_makedirs = patch('dls_ade.module_template.os.makedirs')
        self.patch_isfile = patch('dls_ade.module_template.os.path.isfile')
        self.addCleanup(self.patch_isdir.stop)
        self.addCleanup(self.patch_makedirs.stop)
        self.addCleanup(self.patch_isfile.stop)
        self.mock_isdir = self.patch_isdir.start()
        self.mock_makedirs = self.patch_makedirs.start()
        self.mock_isfile = self.patch_isfile.start()

        self.mock_isdir.return_value = False
        self.mock_isfile.return_value = False

        self.mt_obj = mt.ModuleTemplate({})
        self.mt_obj._template_args = {"arg1": "argument_1", "arg2": "argument_2"}
        self.open_mock = mock_open()  # mock_open is function designed to help mock the 'open' built-in function

    def test_given_folder_name_in_template_files_then_exception_raised_with_correct_message(self):

        self.mt_obj._template_files = {"folder_name/": "Written contents"}
        comp_message = "{dir:s} in template dictionary is not a valid file name".format(dir="folder_name")

        with patch.object(builtins, 'open', self.open_mock):  # This is to prevent accidental file creation
            with self.assertRaises(mt.ArgumentError) as e:
                self.mt_obj._create_files_from_template_dict()

        self.assertEqual(str(e.exception), comp_message)
        self.assertFalse(self.open_mock.called)
        file_handle_mock = self.open_mock()
        self.assertFalse(file_handle_mock.write.called)

    def test_given_single_file_that_already_exists_then_file_not_created(self):

        self.mt_obj._template_files = {"already_exists.txt": "Written contents"}
        self.mock_isfile.return_value = True

        with patch.object(builtins, 'open', self.open_mock):
            self.mt_obj._create_files_from_template_dict()

        self.assertFalse(self.open_mock.called)

        file_handle_mock = self.open_mock()
        self.assertFalse(file_handle_mock.called)

    def test_given_single_file_then_file_created_and_correctly_written_to(self):

        self.mt_obj._template_files = {"file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mt_obj._create_files_from_template_dict()

        self.open_mock.assert_called_once_with("file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_single_file_in_folder_that_does_not_exist_then_folder_and_file_created_and_file_correctly_written_to(self):

        self.mt_obj._template_files = {"test_folder/file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mt_obj._create_files_from_template_dict()

        self.mock_makedirs.asset_called_once_with("test_folder")
        self.open_mock.assert_called_once_with("test_folder/file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_single_file_in_folder_that_exists_then_folder_not_created_but_file_created_and_file_correctly_written_to(self):

        self.mock_isdir.return_value = True

        self.mt_obj._template_files = {"test_folder/file1.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mt_obj._create_files_from_template_dict()

        self.assertFalse(self.mock_makedirs.called)
        self.open_mock.assert_called_once_with("test_folder/file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_two_files_in_separate_folders_then_both_folders_created_and_files_correctly_written_to(self):

        self.mt_obj._template_files = {"test_folder1/file1.txt": "Written contents1", "test_folder2/file2.txt": "Written contents2"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mt_obj._create_files_from_template_dict()

        self.mock_makedirs.assert_has_calls([call("test_folder1"), call("test_folder2")], any_order=True)

        self.open_mock.assert_has_calls([call("test_folder1/file1.txt", "w"), call("test_folder2/file2.txt", "w")], any_order=True)

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_has_calls([call("Written contents1"), call("Written contents2")], any_order=True)

    def test_given_two_files_in_same_folder_then_both_created_and_written_to_but_directory_only_made_once(self):

        self.mock_isdir.side_effect = [False, True]

        self.mt_obj._template_files = {"test_folder/file1.txt": "Written contents1", "test_folder/file2.txt": "Written contents2"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mt_obj._create_files_from_template_dict()

        self.mock_makedirs.assert_called_once_with("test_folder")

        self.open_mock.assert_has_calls([call("test_folder/file1.txt", "w"), call("test_folder/file2.txt", "w")], any_order=True)

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_has_calls([call("Written contents1"), call("Written contents2")], any_order=True)

    def test_given_single_file_with_placeholder_in_name_then_file_created_and_correctly_written_to(self):

        self.mt_obj._template_files = {"{arg:s}.txt": "Written contents"}
        self.mt_obj._template_args = {'arg': "my_argument"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mt_obj._create_files_from_template_dict()

        self.open_mock.assert_called_once_with("my_argument.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_any_call("Written contents")

    def test_given_args_and_template_then_arguments_are_inserted_correctly(self):

        self.mt_obj._template_files = {"file1.txt": "{arg1:s} and {arg2:s}"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mt_obj._create_files_from_template_dict()

        self.open_mock.assert_called_once_with("file1.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_called_once_with("argument_1 and argument_2")

    def test_given_nested_directory_then_folder_and_file_both_created_and_file_correctly_written_to(self):

        self.mt_obj._template_files = {"test_folder/another_folder/yet_another_folder/file.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mt_obj._create_files_from_template_dict()

        self.mock_makedirs.assert_called_once_with("test_folder/another_folder/yet_another_folder")

        self.open_mock.assert_called_once_with("test_folder/another_folder/yet_another_folder/file.txt", "w")

        file_handle_mock = self.open_mock()
        file_handle_mock.write.assert_called_once_with("Written contents")

    def test_given_file_with_no_folder_then_makedirs_not_called(self):

        self.mt_obj._template_files = {"file.txt": "Written contents"}

        with patch.object(builtins, 'open', self.open_mock):
            self.mt_obj._create_files_from_template_dict()

        self.assertFalse(self.mock_makedirs.called)


class ModuleTemplatePrintMessageTest(unittest.TestCase):

    def setUp(self):

        self.mt_obj = mt.ModuleTemplate({})

    def test_given_print_message_called_then_not_implemented_error_raised(self):

        with self.assertRaises(NotImplementedError):
            self.mt_obj.get_print_message()


class ModuleTemplateToolsPrintMessageTest(unittest.TestCase):

    def test_given_print_message_called_then_message_printed(self):

        mt_obj = mt.ModuleTemplateTools({'module_name': "test_module_name",
                                         'module_path': "test_module_path",
                                         'user_login': "test_login"})

        comp_message = ("\nPlease add your patch files to the test_module_path"
                        "\ndirectory and edit test_module_path/build script "
                        "appropriately.")

        msg = mt_obj.get_print_message()
        self.assertEqual(msg, comp_message)


class ModuleTemplatePythonPrintMessageTest(unittest.TestCase):

    def test_given_print_message_called_then_message_printed(self):

        mt_obj = mt.ModuleTemplatePython({'module_name': "test_module_name",
                                          'module_path': "test_module_path",
                                          'user_login': "test_login"})

        mt_obj._template_args.update({'module_path': "test_module_path",
                                    'area': "test_area"})
        message_dict = {'module_path': "test_module_path",
                        'setup_path': "test_module_path/setup.py"}

        comp_message = ("\nPlease add your python files to the {module_path:s}"
                        "\ndirectory and edit {setup_path} appropriately.")
        comp_message = comp_message.format(**message_dict)

        msg = mt_obj.get_print_message()
        self.assertEqual(msg, comp_message)


class ModuleTemplateWithAppsPrintMessageTest(unittest.TestCase):

    def test_given_print_message_called_then_message_printed(self):

        mt_obj = mt.ModuleTemplateWithApps({'module_name': "test_module_name",
                                                  'module_path': "test_module_path",
                                                  'user_login': "test_login",
                                                  'app_name': "test_app_name"})

        message_dict = {
            'RELEASE': "test_module_path/configure/RELEASE",
            'srcMakefile': "test_module_path/test_app_nameApp/src/Makefile",
            'DbMakefile': "test_module_path/test_app_nameApp/Db/Makefile"
        }

        comp_message = ("\nPlease now edit {RELEASE:s} to put in correct paths "
                        "for dependencies.\nYou can also add dependencies to "
                        "{srcMakefile:s}\nand {DbMakefile:s} if appropriate.")
        comp_message = comp_message.format(**message_dict)

        msg = mt_obj.get_print_message()
        self.assertEqual(msg, comp_message)


class ModuleTemplateSupportCreateCustomFilesTest(unittest.TestCase):

    @patch('dls_ade.module_template.os.system')
    def test_given_create_files_called_then_correct_functions_called(self, mock_os_system):

        mt_obj = mt.ModuleTemplateSupport({'module_name': "test_module_name",
                                            'module_path': "test_module_path",
                                            'user_login': "test_login",
                                            'app_name': "test_app_name"})

        mt_obj._create_custom_files()

        os_system_call_list = [call("makeBaseApp.pl -t dls {app_name:s}".format(app_name="test_app_name")), call("dls-make-etc-dir.py && make clean uninstall")]

        mock_os_system.assert_has_calls(os_system_call_list)


class ModuleTemplateIOCCreateCustomFilesTest(unittest.TestCase):

    def setUp(self):

        self.mock_os_system = set_up_mock(self, 'dls_ade.module_template.os.system')
        self.mock_rmtree = set_up_mock(self, 'dls_ade.module_template.shutil.rmtree')
        self.mock_exists = set_up_mock(self, 'dls_ade.module_template.os.path.exists')

    def test_given_neither_boot_folder_nor_app_folder_already_exist_then_no_files_deleted_before_creation_functions_called(self):
        self.mock_exists.side_effect = [False, False]

        mt_obj = mt.ModuleTemplateIOC({'module_name': "test_module_name",
                                       'module_path': "test_module_path",
                                       'user_login': "test_login",
                                       'app_name': "test_app_name"})

        mt_obj._create_custom_files()

        exists_call_list = [call("test_app_nameApp"),
                            call("ioc_boot/ioctest_app_name")]

        rmtree_call_list = [call("test_app_nameApp/opi")]

        os_system_call_list = [call("makeBaseApp.pl -t dls {app_name:s}".format(app_name="test_app_name")),
                               call("makeBaseApp.pl -i -t dls {app_name:s}".format(app_name="test_app_name"))]

        self.mock_exists.assert_has_calls(exists_call_list)
        self.mock_rmtree.assert_has_calls(rmtree_call_list)
        self.mock_os_system.assert_has_calls(os_system_call_list)

    def test_given_app_folder_already_exists_then_app_deleted_and_correct_functions_called(self):
        self.mock_exists.side_effect = [True, False]

        mt_obj = mt.ModuleTemplateIOC({'module_name': "test_module_name",
                                       'module_path': "test_module_path",
                                       'user_login': "test_login",
                                       'app_name': "test_app_name"})

        mt_obj._create_custom_files()

        exists_call_list = [call("test_app_nameApp"),
                            call("ioc_boot/ioctest_app_name")]

        rmtree_call_list = [call("test_app_nameApp"),
                            call("test_app_nameApp/opi")]

        os_system_call_list = [call("makeBaseApp.pl -t dls {app_name:s}".format(app_name="test_app_name")),
                               call("makeBaseApp.pl -i -t dls {app_name:s}".format(app_name="test_app_name"))]

        self.mock_exists.assert_has_calls(exists_call_list)
        self.mock_rmtree.assert_has_calls(rmtree_call_list)
        self.mock_os_system.assert_has_calls(os_system_call_list)

    def test_given_ioc_boot_folder_already_exists_then_boot_file_deleted_and_correct_functions_called(self):
        self.mock_exists.side_effect = [False, True]

        mt_obj = mt.ModuleTemplateIOC({'module_name': "test_module_name",
                                       'module_path': "test_module_path",
                                       'user_login': "test_login",
                                       'app_name': "test_app_name"})

        mt_obj._create_custom_files()

        exists_call_list = [call("test_app_nameApp"),
                            call("ioc_boot/ioctest_app_name")]

        rmtree_call_list = [call("ioc_boot/ioctest_app_name"),
                            call("test_app_nameApp/opi")]

        os_system_call_list = [call("makeBaseApp.pl -t dls {app_name:s}".format(app_name="test_app_name")),
                               call("makeBaseApp.pl -i -t dls {app_name:s}".format(app_name="test_app_name"))]

        self.mock_exists.assert_has_calls(exists_call_list)
        self.mock_rmtree.assert_has_calls(rmtree_call_list)
        self.mock_os_system.assert_has_calls(os_system_call_list)

    def test_given_both_boot_folder_and_app_folder_already_exist_then_both_folders_deleted_before_creation_functions_called(self):
        self.mock_exists.side_effect = [True, True]

        mt_obj = mt.ModuleTemplateIOC({'module_name': "test_module_name",
                                       'module_path': "test_module_path",
                                       'user_login': "test_login",
                                       'app_name': "test_app_name"})

        mt_obj._create_custom_files()

        exists_call_list = [call("test_app_nameApp"),
                            call("ioc_boot/ioctest_app_name")]

        rmtree_call_list = [call("test_app_nameApp"),
                            call("ioc_boot/ioctest_app_name"),
                            call("test_app_nameApp/opi")]

        os_system_call_list = [call("makeBaseApp.pl -t dls {app_name:s}".format(app_name="test_app_name")),
                               call("makeBaseApp.pl -i -t dls {app_name:s}".format(app_name="test_app_name"))]

        self.mock_exists.assert_has_calls(exists_call_list)
        self.mock_rmtree.assert_has_calls(rmtree_call_list)
        self.mock_os_system.assert_has_calls(os_system_call_list)


class ModuleTemplateIOCBLCreateCustomFilesTest(unittest.TestCase):

    @patch('dls_ade.module_template.os.system')
    def test_given_create_files_called_then_correct_functions_called(self, mock_os_system):

        mt_obj = mt.ModuleTemplateIOCBL({'module_name': "test_module_name",
                                          'module_path': "test_module_path",
                                          'user_login': "test_login",
                                          'app_name': "test_app_name"})

        mt_obj._create_custom_files()

        mock_os_system.assert_called_once_with("makeBaseApp.pl -t dlsBL {app_name:s}".format(app_name="test_app_name"))


class ModuleTemplateIOCBLPrintMessageTest(unittest.TestCase):

    def test_given_print_message_called_then_message_printed(self):

        mt_obj = mt.ModuleTemplateIOCBL({'module_name': "test_module_name",
                                         'module_path': "test_module_path",
                                         'user_login': "test_login",
                                         'app_name': "test_app_name"})

        message_dict = {
            'RELEASE': "test_module_path/configure/RELEASE",
            'srcMakefile': "test_module_path/test_app_nameApp/src/Makefile",
            'opi/edl': "test_module_path/test_app_nameApp/opi/edl"
        }

        comp_message = ("\nPlease now edit {RELEASE:s} to put in correct paths "
                        "for the ioc's other technical areas and path to scripts."
                        "\nAlso edit {srcMakefile:s} to add all database files "
                        "from these technical areas.\nAn example set of screens"
                        " has been placed in {opi/edl}. Please modify these.")

        comp_message = comp_message.format(**message_dict)

        msg = mt_obj.get_print_message()
        self.assertEqual(msg, comp_message)


class ModuleTemplateIOCUITest(unittest.TestCase):

    def setUp(self):
        self.mt_obj = mt.ModuleTemplateIOCUI({'module_name': "test_module_name",
                                              'module_path': "test_module_path",
                                              'user_login': "test_login",
                                              'app_name': "test_app_name"})
        self.template_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            mt.COOKIECUTTER_TEMPLATES_FOLDER,
            self.mt_obj.cookiecutter_template
        )

    @patch("dls_ade.module_template.cookiecutter")
    def test_given_create_files_called_then_cookiecutter_called(self, mock_cookiecutter):
        mock_cookiecutter.return_value = 'dummy-basename'
        self.mt_obj._run_cookiecutter()
        self.assertEqual(mock_cookiecutter.call_args[1].get("template"),
                         self.template_path)

    def test_cookiecutter_template_folder_exists(self):
        self.assertTrue(os.path.isdir(self.template_path))
