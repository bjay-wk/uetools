import argparse
from typing import Any
import textwrap


class ArgumentFormaterBase:
    def __init__(self) -> None:
        self.group_increase_indent = False
        self.show_groups = False
        self.newline_between_groups = False
        self.depth_limit = 0
        self.col = 50
        self.acc = []

    def show(self):
        for arg, kwargs in self.acc:
            print(*arg, **kwargs)
        self.acc = []

    def __call__(self, parser: argparse.ArgumentParser, depth: int = 0) -> Any:
        if self.group_increase_indent and self.show_groups:
            depth += 1

        if self.depth_limit > 0 and depth > self.depth_limit:
            return
        
        if depth == 0 and parser.description:
            self.print()
            self.print(f"{'  ' * (depth + 1)} {parser.description}")
            self.print()
            self.print(f"{'  ' * (depth + 2)} {parser.format_usage()}")
            self.print("Arguments:")

        for group in parser._action_groups:
            self.format_group(group, depth)

            for action in group._group_actions:
                if isinstance(action, argparse._SubParsersAction):
                    choices = action.choices

                    for name, choice in choices.items():
                        self.format_action(action, depth + 1, name=name)
                        self(choice, depth + 2)
                else:
                    self.format_action(action, depth + 1)

            if self.newline_between_groups:
                self.print()

    def print(self, *args, **kwargs):
        self.acc.append((args, kwargs))

    def format_group(self, group: argparse._ArgumentGroup, depth: int):
        if not self.show_groups:
            return
        
        if group._group_actions:
            line = f"{'  ' * (depth - 1)} {group.title:<{self.col - (depth - 1) * 2}} {type(group).__name__}"
            self.print(line)

    def format_action(self, action: argparse.Action, depth: int, name=None):
        name = name or action.dest

        line = f"{'  ' * depth} {name:<{self.col - depth * 2}} {type(action).__name__}"
        self.print(line)


class ArgumentFormater(ArgumentFormaterBase):
    def __init__(self) -> None:
        super().__init__()
        self.printed_help = False
        self.description_width = 80

    def format_group(self, group: argparse._ArgumentGroup, depth: int):
        if not self.show_groups:
            return

    def format_action(self, action: argparse.Action, depth: int, name=None):
        """Format an argparse action"""
        indent = "  " * depth

        # Ignore help
        if isinstance(action, argparse._HelpAction):
            if not self.printed_help:
                self.print(f"{indent}{'-h, --help':<{self.col - depth * 2}} Show help")
                self.printed_help = True
            return
        
        # Subparser
        if name is not None and (parser := action.choices[name]):
            title = name
            if parser.description is not None:
                title = parser.description.partition("\n")[0]
            self.print(f"{indent}{name:<{self.col - depth * 2}} {title}")
            return

        names = action.dest
        if action.option_strings:
            names = ", ".join(action.option_strings)

        type = ""
        if action.type:
            type = f": {action.type.__name__}"

        if isinstance(action, argparse._StoreTrueAction):
            type = ": bool"

        if action.nargs and action.nargs != 0:
            type += str(action.nargs)

        default = ""
        if action.default is not None:
            default = " = " + str(action.default)

        help = ""
        if action.help:
            help = action.help

        show_options = False
        choices = action.choices
        if choices is not None:
            choices = f'Options: {", ".join(choices)}'
            show_options = True
        
        if not help and choices is not None:
            show_options = False
            help = choices
        
        arg = f"{names}{type}{default}"
        for i, line in enumerate(textwrap.wrap(help, width=self.description_width, subsequent_indent=" ")):
            if i == 0:
                self.print(f"{indent}{arg:<{self.col - depth * 2}} {line}")
            else:
                self.print(f"{indent}{' ':<{self.col - depth * 2}} {line}")

        if show_options:
            for line in textwrap.wrap(choices, width=self.description_width, subsequent_indent=" "):
                self.print(f'{indent}{"":<{self.col - depth * 2}} {line}')



def show_parsing_tree(parser: argparse.ArgumentParser, depth: int = 0):
    format = ArgumentFormaterBase()
    format(parser, depth)
    format.show()


def recursively_show_actions(parser: argparse.ArgumentParser, depth: int = 0):
    fmt = ArgumentFormater()
    fmt.depth_limit = 2
    fmt(parser, 0)
    fmt.show()


class HelpActionException(Exception):
    pass


class HelpAction(argparse._HelpAction):
    def __init__(self, *args, docstring=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.docstring = docstring

    def __call__(self, parser, namespace, values, option_string=None):
        recursively_show_actions(parser)
        raise HelpActionException()


class DumpParserAction(argparse._HelpAction):
    def __init__(self, *args, docstring=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.docstring = docstring

    def __call__(self, parser, namespace, values, option_string=None):
        show_parsing_tree(parser)
        parser.exit()
