import os

from cookiecutter.main import cookiecutter

from uetools.command import Command, newparser
from uetools.conf import load_conf

COOKIECUTTER = "https://github.com/kiwi-lang/UEDocs"


# pylint: disable=too-few-public-methods
class Arguments:
    """Add a Sphinx + Doxygen documentation to a project

    Attributes
    ----------
    name: str
        Name of the project

    """

    name: str


class Docs(Command):
    """Add a docs folder to your project"""

    name: str = "docs"

    @staticmethod
    def arguments(subparsers):
        parser = newparser(subparsers, Docs)
        parser.add_argument("project", type=str, help="name of your project")
        parser.add_argument(
            "--no-input",
            action="store_true",
            default=False,
            help="Do not show user prompts",
        )
        parser.add_argument(
            "--config",
            type=str,
            default=None,
            help="Configuration file used to initialize the project (json)",
        )

    @staticmethod
    def execute(args):
        project = args.project

        projects_folder = load_conf().get("project_path")
        project_folder = os.path.join(projects_folder, project)

        os.chdir(project_folder)
        cookiecutter(COOKIECUTTER, no_input=args.no_input, config_file=args.config)


COMMANDS = Docs
