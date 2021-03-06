# the value from locals will be removed, which is desired
# pylint: disable=import-outside-toplevel
# pylint: disable=missing-function-docstring,missing-class-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-lines,too-many-locals
import sys
import pickle
from io import StringIO
from typing import Callable
from unittest import main, TestCase
from unittest.mock import patch, call as mock_call, _CallList
from os.path import join, dirname, abspath, exists
ROOT = dirname(abspath(__file__))
BATCH_FOLDER = join(ROOT, "batch")


def default_output_splitter(text: str) -> list:
    return text.rstrip("\n").split(" ")


def assert_bat_output_match(
        batch_path: str, mock_calls: _CallList,
        splitter: Callable = default_output_splitter,
        concat: bool = False, file_buff: StringIO = None
):
    with open(join(BATCH_FOLDER, f"{batch_path}.out")) as file:
        output = file.readlines()
    mock_call_len = len(mock_calls)
    output_len = len(output)
    assert mock_call_len == output_len, (
        mock_calls, output, mock_call_len, output_len
    )

    pipe_text = "<pipe> "
    stderr_text = "<stderr> "
    devnull_text = "<null>"
    for idx, out in enumerate(output):
        buff = sys.stdout
        if out.startswith(pipe_text):
            out = out[len(pipe_text):]
            buff = file_buff
        elif out.startswith(stderr_text):
            out = out[len(stderr_text):]
            buff = sys.stderr
        elif out.startswith(devnull_text):
            continue
        text = splitter(out)

        left = mock_calls[idx]
        if concat:
            right = mock_call(" ".join(text), file=buff)
        else:
            right = mock_call(*text, file=buff)
        assert left == right, (left, right)


def assert_bat_token_match(batch_path: str):
    from butch.context import Context
    from butch.tokenizer import tokenize

    ctx = Context()
    with open(batch_path) as bat_file:
        text = bat_file.read()
        tokens_newline = tokenize(text=text, ctx=ctx)
        tokens_stripped = tokenize(text=text.rstrip("\n"), ctx=ctx)

    with open(join(BATCH_FOLDER, f"{batch_path}.pickle"), "rb") as file:
        expected = pickle.load(file)

    assert tokens_newline == expected, (tokens_newline, expected)
    assert tokens_stripped == expected, (tokens_stripped, expected)
    assert ctx.error_level == 0


class BatchFiles(TestCase):
    # pylint: disable=too-many-public-methods

    @patch("builtins.print")
    def test_hello_execution(self, stdout):
        script_name = "hello.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context()
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls)
        self.assertEqual(ctx.error_level, 0)

    @staticmethod
    @patch("builtins.print")
    def test_hello_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "hello.bat"))

    @patch("builtins.print")
    def test_cd_existing_execution(self, stdout):
        script_name = "cd_existing.bat"

        from butch.context import Context
        from butch.handler import handle

        with patch("butch.context.chdir") as cdr:
            ctx = Context()
            handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            cdr.assert_called_once_with("..")
            assert_bat_output_match(script_name, stdout.mock_calls)
            self.assertEqual(ctx.error_level, 0)

    @staticmethod
    @patch("builtins.print")
    def test_cd_existing_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "cd_existing.bat"))

    @patch("builtins.print")
    def test_cd_nonexisting_execution(self, stdout):
        script_name = "cd_nonexisting.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context()
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(
            script_name, stdout.mock_calls,
            concat=True
        )
        self.assertEqual(ctx.error_level, 1)

    @staticmethod
    @patch("builtins.print")
    def test_cd_nonexisting_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "cd_nonexisting.bat"))

    @patch("builtins.print")
    def test_set_join_execution(self, stdout):
        script_name = "set_join.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context()
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls)
        self.assertEqual(ctx.error_level, 0)

    @staticmethod
    @patch("builtins.print")
    def test_set_join_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "set_join.bat"))

    @patch("builtins.print")
    def test_echo_quote_execution(self, stdout):
        script_name = "hello_quote.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

    @staticmethod
    @patch("builtins.print")
    def test_echo_quote_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "hello_quote.bat"))

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_execution(stdout):
        script_name = "set_quote.bat"

        from butch.context import Context
        from butch.handler import handle as handle_new

        ctx = Context(history_enabled=False)
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "set_quote.bat"))

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_2_execution(stdout):
        script_name = "set_quote_2.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_2_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "set_quote_2.bat"))

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_3_execution(stdout):
        script_name = "set_quote_3.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_3_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "set_quote_3.bat"))

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_4_execution(stdout):
        script_name = "set_quote_4.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_4_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "set_quote_4.bat"))

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_5_execution(stdout):
        script_name = "set_quote_5.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_5_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "set_quote_5.bat"))

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_6_execution(stdout):
        script_name = "set_quote_6.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_6_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "set_quote_6.bat"))

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_7_execution(stdout):
        script_name = "set_quote_7.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_set_quote_7_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "set_quote_7.bat"))

    @patch("builtins.print")
    def test_delete_file_execution(self, stdout):
        from os import remove

        script_name = "delete_file.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        tmp = script_name.replace(".bat", ".tmp")

        if exists(tmp):
            remove(tmp)
        with open(tmp, "w") as file:
            file.write(".")

        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        self.assertFalse(exists(tmp))
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_delete_file_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "delete_file.bat"))

    @staticmethod
    @patch("builtins.print")
    def test_delete_file_syntax_execution(stdout):
        script_name = "delete_file_syntax.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_delete_file_syntax_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "delete_file_syntax.bat"))

    def test_delete_folder_pipe_execution(self):
        from os import mkdir, rmdir, listdir
        from shutil import rmtree

        script_name = "delete_folder_files.bat"
        out_name = f"{script_name}.out"
        folder = BATCH_FOLDER
        tmp_folder = join("/tmp", "butch-tmp")

        from butch.context import Context
        from butch.constants import SURE
        from butch.handler import handle

        with open(join(folder, script_name)) as file:
            script = file.readlines()
        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout, patch("os.remove") as rmv:
            ctx = Context(history_enabled=True)

            if exists(tmp_folder):
                rmtree(tmp_folder)

            mkdir(tmp_folder)

            handle(text=join(folder, script_name), ctx=ctx)
            rmv.assert_not_called()  # captured STDOUT prevents the call

            mcalls = stdout.mock_calls
            self.assertEqual(len(output), 2)
            self.assertEqual(len(mcalls), 3)

            self.assertTrue("|" in script[0])
            self.assertEqual(mcalls[0].args[0], output[0].rstrip("\n")[-1])
            self.assertEqual(str(ctx.error_level), output[1].rstrip("\n"))

            tmp = ctx.history[0].right.args[0].value.replace("/", "\\")
            self.assertEqual(mcalls[1].args[0], f"{tmp}\\*, {SURE} ")
            self.assertEqual(mcalls[2].args[0], str(ctx.error_level))

            self.assertTrue(exists(tmp_folder))
            self.assertEqual(listdir(tmp_folder), [])
            rmdir(tmp_folder)

    @staticmethod
    @patch("builtins.print")
    def test_delete_folder_pipe_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "delete_folder_files.bat"))

    @patch("builtins.print")
    def test_mkdir_nonexisting_execution(self, stdout):
        script_name = "mkdir_nonexisting.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context()
        self.assertFalse(exists("new-folder"))

        with patch("butch.commands.makedirs") as mdrs:
            handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            mdrs.assert_called_once()

        self.assertFalse(exists("new-folder"))
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_mkdir_nonexisting_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "mkdir_nonexisting.bat"))

    @patch("builtins.print")
    def test_mkdir_tree_execution(self, stdout):
        script_name = "mkdir_tree.bat"

        from butch.context import Context
        from butch.handler import handle

        tree = join("new-folder", "with", "sub", "folders")
        ctx = Context()
        self.assertFalse(exists(tree))

        with patch("butch.commands.makedirs") as mdrs:
            handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            mdrs.assert_called_once()

        self.assertFalse(exists(tree))
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_mkdir_tree_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "mkdir_tree.bat"))

    @patch("builtins.print")
    def test_type_file_execution(self, stdout):
        from os import remove

        script_name = "type_print.bat"

        from butch.context import Context
        from butch.handler import handle

        filename = "new-file.txt"
        ctx = Context()

        if exists(filename):
            remove(filename)

        with open(filename, "w") as file:
            file.write("hello type")

        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        self.assertTrue(exists(filename))
        remove(filename)

        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_type_file_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "type_print.bat"))

    @patch("builtins.print")
    def test_type_folder_execution(self, stdout):
        from os import rmdir, mkdir

        script_name = "type_print_folder.bat"

        from butch.context import Context
        from butch.handler import handle

        filename = "new-folder"
        ctx = Context()

        if exists(filename):
            rmdir(filename)
        mkdir(filename)

        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        self.assertTrue(exists(filename))
        rmdir(filename)

        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

    @staticmethod
    @patch("builtins.print")
    def test_type_folder_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "type_print_folder.bat"))

    @patch("builtins.print")
    def test_type_multifile_execution(self, stdout):
        from os import remove

        script_name = "type_print_multiple.bat"

        from butch.context import Context
        from butch.handler import handle as handle_new

        first = "new-file.txt"
        second = "new-file-2.txt"
        paths = (first, second)
        ctx = Context()

        for path in paths:
            if exists(path):
                remove(path)

        with open(first, "w") as file:
            file.write("hello type")

        with open(second, "w") as file:
            file.write("hello multiple")

        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        for path in paths:
            self.assertTrue(exists(path))
            remove(path)

        def preserve_lf(text):
            parts = text.rstrip("\n").split(" ")
            parts = [word or "\n" for word in parts]
            return parts

        assert_bat_output_match(
            script_name, stdout.mock_calls, concat=True,
            splitter=preserve_lf
        )

    @staticmethod
    @patch("builtins.print")
    def test_type_multifile_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "type_print_multiple.bat"))

    @patch("builtins.print")
    def test_type_multifile_halffail(self, stdout):
        from os import remove, mkdir, rmdir

        script_name = "type_print_multiple_halffail.bat"

        from butch.context import Context
        from butch.handler import handle as handle_new

        first = "new-file.txt"
        second = "new-folder"
        paths = (first, second)
        ctx = Context()

        if exists(first):
            remove(first)
        if exists(second):
            rmdir(second)

        with open(first, "w") as file:
            file.write("hello type")
        mkdir(second)

        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        for path in paths:
            self.assertTrue(exists(path))
        remove(first)
        rmdir(second)
        self.assertEqual(ctx.error_level, 1)

        def preserve_lf(text):
            parts = text.rstrip("\n").split(" ")
            parts = [word or "\n" for word in parts]
            return parts

        assert_bat_output_match(
            script_name, stdout.mock_calls, concat=True,
            splitter=preserve_lf
        )

    @patch("builtins.print")
    def test_redir_newfile_mocked(self, stdout):
        from os import remove

        script_name = "redir_echo_newfile.bat"

        from butch.context import Context
        from butch.outputs import CommandOutput
        from butch.handler import handle as handle_new

        filename = "new-file.txt"
        ctx = Context()

        if exists(filename):
            remove(filename)
        self.assertFalse(exists(filename))

        cmd_out = CommandOutput()
        with patch("butch.commands.CommandOutput") as out_mock:
            out_mock.return_value = cmd_out

            handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            self.assertTrue(exists(filename))
            with open(filename) as dest_descr:
                output = dest_descr.read()
                # empty due to mocked print
                self.assertEqual(output, "")
            remove(filename)

            assert_bat_output_match(
                script_name, stdout.mock_calls, concat=True,
                file_buff=cmd_out.stdout
            )

    def test_redir_newfile_passthrough(self):
        from os import remove

        script_name = "redir_echo_newfile.bat"

        from butch.context import Context
        from butch.outputs import CommandOutput
        from butch.handler import handle as handle_new

        filename = "new-file.txt"
        ctx = Context()

        if exists(filename):
            remove(filename)
        self.assertFalse(exists(filename))

        cmd_out = CommandOutput()
        with patch("butch.commands.CommandOutput") as out_mock:
            out_mock.return_value = cmd_out

            with patch("sys.stdout"):
                handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            self.assertTrue(exists(filename))
            with open(filename) as dest_descr:
                output = dest_descr.readlines()
                self.assertEqual(output, ["hello\n"])
            remove(filename)

    @patch("builtins.print")
    def test_redir_newappend_mocked(self, stdout):
        from os import remove

        script_name = "redir_echo_newappend.bat"

        from butch.context import Context
        from butch.outputs import CommandOutput
        from butch.handler import handle as handle_new

        filename = "new-file.txt"
        ctx = Context()

        if exists(filename):
            remove(filename)
        self.assertFalse(exists(filename))

        cmd_out = CommandOutput()
        with patch("butch.commands.CommandOutput") as out_mock:
            out_mock.return_value = cmd_out

            handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            self.assertTrue(exists(filename))
            remove(filename)

            assert_bat_output_match(
                script_name, stdout.mock_calls, concat=True,
                file_buff=cmd_out.stdout
            )

    def test_redir_newappend_passthrough(self):
        from os import remove

        script_name = "redir_echo_newappend.bat"

        from butch.context import Context
        from butch.outputs import CommandOutput
        from butch.handler import handle as handle_new

        filename = "new-file.txt"
        ctx = Context()

        if exists(filename):
            remove(filename)
        self.assertFalse(exists(filename))

        cmd_out = CommandOutput()
        with patch("butch.commands.CommandOutput") as out_mock:
            out_mock.return_value = cmd_out

            with patch("sys.stdout"):
                handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            self.assertTrue(exists(filename))
            with open(filename) as dest_descr:
                output = dest_descr.readlines()
                self.assertEqual(output, ["hello\n", "butch\n"])
            remove(filename)

    @patch("builtins.print")
    def test_redir_fromfile_mocked(self, stdout):
        return
        from os import remove

        script_name = "redir_set_fromfile.bat"

        from butch.context import Context
        from butch.outputs import CommandOutput
        from butch.handler import handle as handle_new

        filename = "input.txt"
        ctx = Context()

        if exists(filename):
            remove(filename)
        self.assertFalse(exists(filename))

        cmd_out = CommandOutput()
        with patch("butch.commands.CommandOutput") as out_mock:
            out_mock.return_value = cmd_out

            handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            self.assertTrue(exists(filename))
            remove(filename)

            assert_bat_output_match(
                script_name, stdout.mock_calls, concat=True,
                file_buff=cmd_out.stdout
            )

    def test_redir_fromfile_passthrough(self):
        from os import remove

        script_name = "redir_set_fromfile.bat"

        from butch.context import Context
        from butch.outputs import CommandOutput
        from butch.handler import handle as handle_new

        filename = "input.txt"
        ctx = Context()

        if exists(filename):
            remove(filename)
        self.assertFalse(exists(filename))

        cmd_out = CommandOutput()
        with patch("butch.commands.CommandOutput") as out_mock:
            out_mock.return_value = cmd_out

            with patch("sys.stdout"):
                handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
            self.assertTrue(exists(filename))
            with open(filename) as dest_descr:
                output = dest_descr.readlines()
                self.assertEqual(output, ["my-input\n"])
            remove(filename)

    @patch("builtins.print")
    def test_path_set(self, stdout):
        script_name = "path_set.bat"

        from butch.context import Context
        from butch.handler import handle as handle_new

        ctx = Context()
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

    @patch("builtins.print")
    def test_path_unset(self, stdout):
        script_name = "path_unset.bat"

        from butch.context import Context
        from butch.handler import handle as handle_new

        ctx = Context()
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

    @patch("builtins.print")
    def test_path_append(self, stdout):
        script_name = "path_append.bat"

        from butch.context import Context
        from butch.handler import handle as handle_new

        ctx = Context()
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

    @patch("builtins.print")
    def test_rem_comment(self, stdout):
        script_name = "rem_comment.bat"

        from butch.context import Context
        from butch.handler import handle as handle_new

        ctx = Context()
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 1)

    @patch("builtins.print")
    def test_rem_colon_comment(self, stdout):
        script_name = "rem_colon_comment.bat"

        from butch.commandtype import CommandType
        from butch.context import Context
        from butch.handler import handle as handle_new

        ctx = Context()
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 1)
        comments = 0
        for command in ctx.history:
            if command.cmd != CommandType.REM:
                continue
            comments += 1
        self.assertEqual(comments, 48)

    @staticmethod
    @patch("builtins.print")
    def test_rem_complex_comment_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "rem_complex.bat"))

    @patch("builtins.print")
    def test_pushd_tmp(self, stdout):
        script_name = "pushd_tmp.bat"

        if not sys.platform.startswith('linux'):
            return

        from os import getcwd, chdir
        from shutil import rmtree
        from butch.context import Context
        from butch.handler import handle as handle_new

        ctx = Context()
        original = getcwd()
        tmpdir = ctx.get_variable("temp")
        folder = join(tmpdir, "some-temp-file-name")

        if exists(folder):
            rmtree(folder)

        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

        rmtree(folder)
        chdir(original)

    @patch("builtins.print")
    def test_popd(self, stdout):

        if not sys.platform.startswith('linux'):
            return
        script_name = "popd.bat"

        from os import getcwd, chdir
        from shutil import rmtree
        from butch.context import Context
        from butch.handler import handle as handle_new

        ctx = Context()
        original = getcwd()
        tmpdir = ctx.get_variable("temp")
        folder = join(tmpdir, "butch-tmp-folder")

        if exists(folder):
            rmtree(folder)

        self.assertFalse(exists(folder))
        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)
        self.assertTrue(exists(folder))

        rmtree(folder)
        chdir(original)

    @patch("builtins.print")
    def test_popd_removed(self, stdout):
        script_name = "popd_removed.bat"

        if not sys.platform.startswith('linux'):
            return

        from os import getcwd, chdir
        from shutil import rmtree
        from butch.context import Context
        from butch.handler import handle as handle_new

        ctx = Context()
        original = getcwd()
        tmpdir = ctx.get_variable("temp")
        folder = join(tmpdir, "butch-tmp-folder")

        if exists(folder):
            rmtree(folder)
        self.assertFalse(exists(folder))

        handle_new(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

        self.assertFalse(exists(folder))
        chdir(original)

    @patch("builtins.print")
    def test_goto_eof(self, stdout):
        script_name = "goto_eof.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

    @patch("builtins.print")
    def test_goto_label(self, stdout):
        script_name = "goto_label.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

    @patch("builtins.print")
    def test_block_echo_execution(self, stdout):
        script_name = "block_echo.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

    @staticmethod
    @patch("builtins.print")
    def test_block_echo_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "block_echo.bat"))

    @patch("builtins.print")
    def test_block_errorlevel_execution(self, stdout):
        script_name = "block_errorlevel.bat"

        from butch.context import Context
        from butch.handler import handle

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

    @staticmethod
    @patch("builtins.print")
    def test_block_errorlevel_tokenization(stdout):
        assert_bat_token_match(join(BATCH_FOLDER, "block_errorlevel.bat"))

    @patch("builtins.print")
    def test_move_execution(self, stdout):
        script_name = "move.bat"

        from butch.context import Context
        from butch.handler import handle
        from os import remove

        with open(join(ROOT, "existing"), "w") as file:
            file.write("hello")

        with open(join(ROOT, "first1"), "w") as file:
            file.write("hello")

        with open(join(ROOT, "first2"), "w") as file:
            file.write("world")

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)
        self.assertEqual(ctx.error_level, 0)

        self.assertFalse(exists(join(ROOT, "existing")))
        self.assertFalse(exists(join(ROOT, "first1")))
        self.assertFalse(exists(join(ROOT, "first2")))

    @patch("builtins.print")
    def test_move_overwrite_execution(self, stdout):
        script_name = "move_overwrite.bat"

        from butch.context import Context
        from butch.handler import handle
        from os import remove, mkdir

        source = "source"
        dest = "dest"
        for folder in (source, dest):
            middle = join(ROOT, folder)
            mkdir(middle)
            with open(join(middle, "file1"), "w") as file:
                file.write(f"{folder}-hello")

            with open(join(middle, "file2"), "w") as file:
                file.write(f"{folder}-world")

        ctx = Context(history_enabled=False)
        handle(text=join(BATCH_FOLDER, script_name), ctx=ctx)
        assert_bat_output_match(script_name, stdout.mock_calls, concat=True)

        self.assertEqual(ctx.error_level, 0)
        self.assertFalse(exists(join(ROOT, source)))
        self.assertFalse(exists(join(ROOT, dest)))

    def ignore_test_set_join_expansion(self):
        script_name = "set_join_expansion.bat"
        out_name = f"{script_name}.out"
        folder = BATCH_FOLDER

        from butch.context import Context
        from butch.handler import handle as handle_new

        with open(join(folder, out_name)) as file:
            output = file.readlines()

        with patch("builtins.print") as stdout:
            ctx = Context()
            handle_new(text=join(folder, script_name), ctx=ctx)
            self.assertTrue(ctx.delayed_expansion_enabled)
            mcalls = stdout.mock_calls
            self.assertEqual(len(mcalls), len(output))

            for idx, out in enumerate(output):
                self.assertEqual(
                    mcalls[idx],
                    mock_call(out.rstrip("\n"))
                )


if __name__ == "__main__":
    main()
