import pkgutil
import sys
from argparse import ArgumentParser
from importlib import import_module

import os

from ..__version__ import __title__, __version__, __module__


class CommandError(Exception):
    """
    Exception class indicating a problem while executing a command.
    """

    def __init__(self, msg="", *args):
        self.msg = msg
        super(CommandError, self).__init__(*args)


class ManagementUtility(object):
    def __init__(self, argv=None, stdin=sys.stdin, stdout=sys.stdout,
                 stderr=sys.stderr):
        self.argv = argv or sys.argv
        self.prog = __title__
        self.version = "%s %s" % (__title__, __version__)
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    @property
    def subcommands(self):
        """
        :rtype: list[str]
        """
        command_dir = os.path.join(__path__[0], "commands")
        subcommands = [name for _, name, is_pkg in
                       pkgutil.iter_modules([command_dir])
                       if not is_pkg and not name.startswith("_")]
        subcommands.sort()
        return subcommands

    @property
    def main_help_text(self):
        """
        Returns the script's main help text, as a string.
        """
        usage = [
            "Type '%s help <subcommand>' for help on a specific subcommand." % self.prog,
            "",
            "Available subcommands:",
        ]
        for subcommand in self.subcommands:
            usage.append("  %s" % subcommand)
        usage.append("")

        return "\n".join(usage)

    def unknown_command_text(self, subcommand):
        text = [
            "Unknown command: %r" % subcommand,
            "Type '%s help' for usage." % self.prog,
            "",
        ]
        return "\n".join(text)

    def fetch_subcommand(self, subcommand):
        if subcommand not in self.subcommands:
            self.stderr.write(self.unknown_command_text(subcommand))
            sys.exit(1)
        cmd_module = import_module("{module}.core.commands.{command}".format(
            module=__module__, command=subcommand))
        return cmd_module.Command(prog=self.prog, stdin=self.stdin,
                                  stdout=self.stdout, stderr=self.stderr)

    def create_parser(self):
        parser = ArgumentParser(prog=self.prog, usage=self.main_help_text)
        parser.add_argument("-v", "--version", action="store_true",
                            help="show the current version")
        return parser

    def execute(self):
        subcommand = "help" if len(self.argv) <= 1 else self.argv[1].lower()
        if subcommand == "help":
            if len(self.argv) < 3:
                self.create_parser().print_help()
            else:
                self.fetch_subcommand(self.argv[2]).print_help()
        elif subcommand in ("-h", "--help"):
            self.create_parser().print_help()
        elif subcommand in ("-v", "--version", "version"):
            self.stdout.write(self.version + "\n")
        else:
            self.fetch_subcommand(subcommand).run_from_argv(self.argv)


class BaseCommand(object):
    def __init__(self, prog=__title__, stdin=sys.stdin, stdout=sys.stdout,
                 stderr=sys.stderr):
        self.prog = prog
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    @property
    def command(self):
        return self.__module__.split(".")[-1]

    @property
    def description(self):
        return ""

    def create_parser(self):
        """
        Create and return the ``ArgumentParser`` which will be used to
        parse the arguments to this command.
        """
        prog = "%s %s" % (self.prog, self.command)
        parser = ArgumentParser(prog=prog, description=self.description)
        self.add_arguments(parser)
        return parser

    def add_arguments(self, parser):
        """
        Entry point for subclassed commands to add custom arguments.

        Examples:
            parser.add_argument('--foo', help='foo help')
            parser.add_argument('integers', metavar='N', type=int, nargs='+',
                                help='an integer for the accumulator')
        :type parser: ArgumentParser
        """
        pass

    def print_help(self):
        """
        Print the help message for this command, derived from ``self.usage()``.
        """
        parser = self.create_parser()
        parser.print_help()

    def run_from_argv(self, argv):
        parser = self.create_parser()

        opts, args = parser.parse_known_args(argv[2:])
        cmd_opts = vars(opts)
        try:
            self.execute(*args, **cmd_opts)
        except Exception as e:
            if not isinstance(e, CommandError):
                raise e
            self.stderr.write(e.msg + "\n")
            sys.exit(1)

    def execute(self, *args, **options):
        """
        Try to execute this command.
        """
        output = self.handle(*args, **options)
        if output:
            self.stdout.write(output)

    def handle(self, *args, **options):
        """
        The actual logic of the command.
        Subclasses must implement this method.
        """
        raise NotImplementedError(
            "subclasses of BaseCommand must provide a handle() method")


def execute_from_command_line(argv=None):
    utility = ManagementUtility(argv)
    utility.execute()
