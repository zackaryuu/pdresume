import os
import sys
import click
from zu.pdresume.utils import build, run_detached

PATH = os.path.join(os.path.expanduser("~"), ".zu", "mods", "pdresume")
CURR_FILE_LOCATION = os.path.abspath(__file__)
try:
    POSSIBLE_PRESET_LOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURR_FILE_LOCATION))))
    assert os.path.exists(os.path.join(POSSIBLE_PRESET_LOC, "preset"))
    PATH = POSSIBLE_PRESET_LOC
except Exception:
    POSSIBLE_PRESET_LOC = None

#print(POSSIBLE_PRESET_LOC)
#os.makedirs(PATH, exist_ok=True)


@click.group(invoke_without_command=True)
def cli():
    os.chdir(os.environ["ZU_ACTUAL_CWD"])


@cli.command()
def update():
    if POSSIBLE_PRESET_LOC is not None:
        # this means it is installed as a zu component, should simply use the standard zu update mechanism
        run_detached(["zu", "update", "pdresume"])
        sys.exit(0)

    currdir = os.getcwd()
    os.chdir(PATH)
    try:
        if not os.path.exists(".git"):
            os.system("git init")
            os.system("git remote add origin https://github.com/zackaryuu/pdresume.git")
            
        # Set up sparse checkout directly
        os.system("git sparse-checkout init --cone")
        os.system("git sparse-checkout set profiles preset")
            
        os.system("git fetch origin")
        os.system("git reset --hard origin/main")
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
        os.path.join(PATH, "profiles", "awetex"),
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
        os.path.join(PATH, "profiles", "awetxt"),
        data,
        profile,
        output_dir=output,
        debug=debug,
        on_error_debug=on_error_debug,
    )

@cli.command()
@click.argument("path", type=str)
@click.option("--data", type=str, default="data.toml")
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
    #import sys
    #sys.argv.extend(["awetex", "--profile", "pdf"])
    cli()

