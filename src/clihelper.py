from datetime import datetime
from config import Config
from argparse import ArgumentParser, ArgumentTypeError

class SucktorialCliHelper:
    @staticmethod
    def get_args_parser():

        parser = ArgumentParser(description="Sucktorial CLI")

        credentials_group = parser.add_argument_group("Credentials")
        credentials_group.add_argument(
            "--email",
            "-e",
            type=str,
            help="Email to login with",
        )
        credentials_group.add_argument(
            "--password",
            "-p",
            type=str,
            help="Password to login with",
        )
        credentials_group.add_argument(
            "--employee-id",
            "-i",
            type=int,
            help="Employee id to filter some API calls",
        )

        action_group = parser.add_argument_group("Actions")
        action_group.add_argument(
            "--login",
            action="store_true",
            help="Login to Factorial",
        )
        action_group.add_argument(
            "--logout",
            action="store_true",
            help="Logout from Factorial",
        )
        action_group.add_argument(
            "--clock-in",
            action="store_true",
            help="Clock in",
        )
        action_group.add_argument(
            "--clock-out",
            action="store_true",
            help="Clock out",
        )
        action_group.add_argument(
            "--clocked-in",
            action="store_true",
            help="Check if you are clocked in",
        )
        action_group.add_argument(
            "--shifts",
            action="store_true",
            help="Get the shifts",
        )
        action_group.add_argument(
            "--leaves",
            action="store_true",
            help="Get the leaves",
        )
        action_group.add_argument(
            "--employee-data",
            action="store_true",
            help="Retrieve employee data",
        )
        action_group.add_argument(
            "--graphql-query",
            type=str,
            help="Execute a GraphQL query",
        )
        action_group.add_argument(
            "--insert-shift",
            action="store_true",
            help="Insert a new shift"
        )
        action_group.add_argument(
            "--start-shift",
            type=str,
            help="Specify the start of the shift to be inserted in the format HH:MM"
        )
        action_group.add_argument(
            "--end-shift",
            type=str,
            help="Specify the end of the shift to be inserted in the format HH:MM"
        )
        action_group.add_argument(
            "--date-shift",
            type=str,
            help="Specify the date of the shift to be inserted in the format YYYY-MM-DD"
        )

        customization_group = parser.add_argument_group("Customization")
        customization_group.add_argument(
            "--random-clock",
            type=int,
            nargs="?",
            const=15,
            help="Clock in/out at a random time (+/- X minutes from now)",
        )
        customization_group.add_argument(
            "--user-agent",
            type=str,
            help="User agent to use for the requests",
        )
        customization_group.add_argument(
            "--envfile",
            type=str,
            help="Name of the user custom .env file (.<envfile>.env)",
        )
        customization_group.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging",
        )

        return parser

    @staticmethod
    def validate_args(args, parser):
        if (args.email and not args.password) or (args.password and not args.email):
            parser.error("Specify both email and password")

        if args.random_clock and not (args.clock_in or args.clock_out):
            parser.error("Specify --clock-in or --clock-out with --random-clock")

        if args.insert_shift and not args.start_shift and not args.end_shift and not args.date_shift:
            parser.error("You must specify --start-shift, --end-shift and --date-shift")

        if not (
            args.login
            or args.logout
            or args.clock_in
            or args.clock_out
            or args.clocked_in
            or args.shifts
            or args.leaves
            or args.employee_data
            or args.graphql_query
            or args.insert_shift
        ):
            parser.error("Specify at least one action")

        if (
            int(args.logout)
            + int(args.clock_in)
            + int(args.clock_out)
            + int(args.clocked_in)
            + int(args.shifts)
            + int(args.leaves)
            + int(args.employee_data)
            + int(args.insert_shift)
            + (1 if args.graphql_query else 0)
        ) > 1:
            parser.error("Specify only one action")

    @staticmethod
    def parse_and_validate():
        parser = SucktorialCliHelper.get_args_parser()
        args, _ = parser.parse_known_args()
        SucktorialCliHelper.validate_args(args, parser)
        return args

    @staticmethod
    def datetime_parser(value: str):
        if value == '':
            return datetime.now()
        else:
            try:
                return datetime.strptime(value, Config.DATETIME_FORMAT)
            except ValueError:
                raise ArgumentTypeError(f"Invalid date format: {value}. Expected format: YYYY-MM-DDTHH:mm:ss")