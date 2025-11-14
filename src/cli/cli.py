import click
import sys
import logging

from core.model.NodeType import NodeType
from core.storage.WavesLabRepository import repository

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='1.0.0')
def waveslab():
    """
    WavesLab Simulation Environment CLI

    Control WaveNodes and manage virtual users in the household simulation.
    """
    pass

@waveslab.command()
@click.argument('node_id')
def switch(node_id: str):
    """
    Switch the status of a WaveNode by id.

    id: The id of the WaveNode to switch

    Examples:
        waveslab switch "living-room-light"
        waveslab switch "kitchen-faucet"
    """
    try:
        success, message = repository.switch_node(node_id)

        if success:
            click.echo(message)
            sys.exit(0)
        else:
            click.echo(f"Error: {message}", err=True)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error switching node '{node_id}': {e}")
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)

@waveslab.command()
def status():
    """
    Shows the status of all nodes
    """
    try:
        nodes = repository.get_all_nodes()
        if not nodes:
            click.echo("No WaveNodes found.")
            return

        click.echo("\nWaveNodes:")
        click.echo("-" * 60)

        for node in nodes:
            bracket_id = f"[{node.id}]"
            click.echo(f"{bracket_id:<30} {node.status.lower():3} - {node.name}")
    except Exception as e:
        logger.error(f"Error listing nodes: {e}")
        click.echo(f"Error listing nodes: {e}", err=True)
        sys.exit(1)

def info_format(node):
    bracket_id = f"[{node.id}]"
    return f"[{node.endpoint[-2:]}] [{node.node_type.name[0]} - {node.real_time_consumption:<6}] {bracket_id:<30} {node.status.lower():3} - {node.name}"

@waveslab.command()
@click.option(
    '--active', '-a',
    is_flag=True,
    help='Show information of active-only nodes'
)
@click.option(
    '--utility', '-u',
    type=str,
    default=None,
    help='Specify a utility string'
)
def info(active: bool, utility: str):
    """
    Shows the information of all nodes
    """
    try:
        if active:
            nodes = repository.get_active_nodes()
        else:
            nodes = repository.get_all_nodes()

        if utility:
            nodes = [node for node in nodes if node.node_type == utility]

        if not nodes:
            click.echo("No WaveNodes found.")
            return

        click.echo("\nWaveNodes:")
        click.echo("-" * 60)

        for node in nodes:
            click.echo(info_format(node))
    except Exception as e:
        logger.error(f"Error listing nodes: {e}")
        click.echo(f"Error listing nodes: {e}", err=True)
        sys.exit(1)


def _info_utility(utility_type: NodeType):
    try:
        all_nodes = repository.get_active_nodes()

        nodes = [node for node in all_nodes if node.node_type == utility_type]
        if not nodes:
            click.echo("No WaveNodes found.")
            return

        click.echo("\nWaveNodes:")
        click.echo("-" * 60)

        for node in nodes:
            click.echo(info_format(node))
    except Exception as e:
        logger.error(f"Error listing nodes: {e}")
        click.echo(f"Error listing nodes: {e}", err=True)
        sys.exit(1)

@waveslab.command()
def users():
    """
    List all VirtualUsers in the system.
    """
    try:
        list_of_users = repository.get_all_users()

        if not list_of_users:
            click.echo("No VirtualUsers found.")
            return

        click.echo("\nVirtual Users:")
        click.echo("-" * 30)

        for user in list_of_users:
            click.echo(f"• {user.username}")

    except Exception as e:
        logger.error(f"Error listing users: {e}")
        click.echo(f"Error listing users: {e}", err=True)
        sys.exit(1)