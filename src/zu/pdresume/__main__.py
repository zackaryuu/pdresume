import os
import click
from zu.pdresume.utils import build

PATH = os.path.join(os.path.expanduser("~"), ".zu", "mods", "pdresume")
os.makedirs(PATH, exist_ok=True)


@click.group()
def cli():
    pass


@cli.command()
def update():
    from zuu.main.git import sparse_checkout

    currdir = os.getcwd()
    os.chdir(PATH)
    try:
        if not os.path.exists(".git"):
            os.system("git init")
            os.system("git remote add origin https://github.com/zackaryuu/pdresume.git")
            os.system("git checkout -b main")
        sparse_checkout(
            "https://github.com/zackaryuu/pdresume.git", ["profiles", "preset"]
        )
        os.system("git fetch origin")
        os.system("git branch --set-upstream-to=origin/main main")
        os.system("git pull")
    except Exception as e:
        click.echo(f"Error updating pdresume: {e}")
    finally:
        os.chdir(currdir)


@cli.command()
@click.option("--data", type=str, default="data.toml")
@click.option("--output", type=click.Path(), default=None)
@click.option("--debug", is_flag=True)
@click.option("--on-error-debug", is_flag=True)
@click.option("-p", "--profile", type=str, multiple=True)
@click.pass_context
def awetex(ctx, data, output, debug, on_error_debug, profile):
    if not os.path.exists(os.path.join(PATH, "profiles", "awetex")):
        click.echo("awetex profile not found")
        ctx.invoke(update)

    if not data or not os.path.exists(data):
        data = os.path.join(PATH, "preset", "example.toml")

    build(
        os.getcwd(),
        data,
        profile,
        output_dir=output,
        debug=debug,
        on_error_debug=on_error_debug,
    )

@cli.command()
@click.option("--data", type=str, default="data.toml")
@click.option("--output", type=click.Path(), default=None)
@click.option("--debug", is_flag=True)
@click.option("--on-error-debug", is_flag=True)
@click.option("-p", "--profile", type=str, multiple=True)
@click.pass_context
def awetxt(ctx, data, output, debug, on_error_debug, profile):
    if not os.path.exists(os.path.join(PATH, "profiles", "awetxt")):
        click.echo("awetxt profile not found")
        ctx.invoke(update)

    if not data or not os.path.exists(data):
        data = os.path.join(PATH, "preset", "example.toml")


    build(
        os.getcwd(),
        data,
        profile,
        output_dir=output,
        debug=debug,
        on_error_debug=on_error_debug,
    )

@cli.command()
@click.option("--data", type=str, default="data.toml")
@click.option("--path", type=str, default=os.getcwd())
@click.option("--output", type=click.Path(), default=None)
@click.option("--debug", is_flag=True)
@click.option("--on-error-debug", is_flag=True)
@click.option("-p", "--profile", type=str, multiple=True)
def gen(path, output, debug, on_error_debug, profile, data):

    if not data or not os.path.exists(data):
        data = os.path.join(PATH, "preset", "example.toml")

    build(
        path,
        data_toml=data,
        profile=profile,
        output_dir=output,
        debug=debug,
        on_error_debug=on_error_debug,
    )

if __name__ == "__main__":
    import sys
    sys.argv.append("awetex")

    cli()

