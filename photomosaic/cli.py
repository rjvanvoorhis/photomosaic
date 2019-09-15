import subprocess
import click
from photomosaic.api import mosaicfy, is_animated


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--tile_size', default=8)
@click.option('--scale', default=1)
@click.option('--output_file')
@click.option('--show/--no-show', default=False)
def cli(filename, **kwargs):
    show = kwargs.pop('show', False)
    result = mosaicfy(filename, **kwargs)
    if show:
        if is_animated(filename):
            cmd = f'eog {result.gif_path}'
            subprocess.run(cmd.split())
        else:
            result.image.show()


if __name__ == '__main__':
    cli()
