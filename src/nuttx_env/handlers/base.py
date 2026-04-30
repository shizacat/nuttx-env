"""
Base handler module for NuttX environment management.
"""

import argparse


class BaseHandler:
    """
    Base handler class for NuttX environment commands.
    """
    command: str
    command_help: str = "Base command handler"

    def __init__(self):
        super().__init__()

    @classmethod
    def register_subparser(cls, subparsers: argparse._SubParsersAction):
        """
        Register the subparser for this command.
        """
        parser = subparsers.add_parser(
            cls.command, help=cls.command_help
        )
        cls.add_arguments(parser)

    @classmethod
    def get_handler_by_command(cls, command: str) -> "BaseHandler":
        """
        Get the handler class for the given command.

        Raises:
            ValueError: If no handler is found for the command.
        """
        for subclass in cls.__subclasses__():
            if subclass.command == command:
                return subclass()
        raise ValueError(f"No handler found for command: {command}")

    def __call__(self, args: argparse.Namespace):
        """
        Execute the command with provided arguments.
        """
        self.execute(args)

    # --- Overridable methods ----

    def execute(self, args: argparse.Namespace):
        """
        Execute the command with provided arguments.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError(
            "Execute method must be implemented by subclasses.")

    @classmethod
    def add_arguments(self, parser: argparse.ArgumentParser):
        """
        Add command-specific arguments to the parser.
        This method can be overridden by subclasses.
        """
        pass
