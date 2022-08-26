from . import *
import click

TASKS = {
    "remind_pending_documents": RemindPendingDocuments,
}


@click.command()
@click.option(
    "-t",
    "--task",
    "task_to_run",
    type=click.Choice(TASKS.keys()),
    required=True,
    help="Task to run",
)
def main(task_to_run):
    TASKS[task_to_run].perform()


if __name__ == "__main__":
    main()
