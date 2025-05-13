import os
import toml
import yaml
import shutil
from zuu.api.kv import parse_document
import subprocess
import platform

def build_input_md(toml_path):
    with open(toml_path, "r") as f:
        filecontent = f.read()
        filecontent = parse_document(filecontent)

    data = toml.loads(filecontent)

    with open("input.md", "w") as f:
        f.write("---\n")
        f.write(yaml.safe_dump(data))
        f.write("---\n")

    return data


def build(
    path: str,
    data_toml: str = "data.toml",
    run_profiles: list[str] = [],
    env: dict = {},
    output_dir: str = None,
    debug: bool = False,
    on_error_debug: bool = False,
):
    #print({k: v for k, v in locals().items() if not k.startswith("_")})
    assert os.path.exists(path), "path does not exist"
    assert os.path.exists(data_toml), "data_toml does not exist"
    bugged = False
    assert "std" not in run_profiles, "std profile is not allowed to be run"

    curr_cd = os.getcwd()
    
    if os.path.exists(os.path.join(curr_cd, "debug")):
        shutil.rmtree(os.path.join(curr_cd, "debug"))

    # copy preset to cd path
    shutil.copytree(path, os.path.join(curr_cd, "debug"))
    print(f"copying {path} to {os.path.join(curr_cd, 'debug')}")

    shutil.copy(data_toml, os.path.join(curr_cd, "debug", "data.toml"))
    print(f"copying {data_toml} to {os.path.join(curr_cd, 'debug', 'data.toml')}")

    # change to new path
    os.chdir(os.path.join(curr_cd, "debug"))

    context = toml.load("context.toml")

    assert all(profile in context for profile in run_profiles), (
        "All profiles must be in context"
    )
    
    meta = {
        "THIS_DIR": os.getcwd(),
        "CWD": curr_cd,
        "PROFILE_PATH": path,
        "os": os,
        "CONTEXT": context,
        **env,
        "DEBUG": debug,
        "ON_ERROR_DEBUG": on_error_debug,
    }
    
    try:
        output_files = build_cd(meta, run_profiles)
    except Exception as e:
        if debug or on_error_debug:
            bugged = True
        raise e
    finally:
        for file in output_files:
            if not os.path.exists(file):
                print(f"File {file} does not exist")
                continue

            if output_dir:
                shutil.copy(file, os.path.join(output_dir, os.path.basename(file)))
            else:
                shutil.copy(file, os.path.join(curr_cd, os.path.basename(file)))
        os.chdir(curr_cd)
        if not bugged and not debug:
            shutil.rmtree(os.path.join(curr_cd, "debug"))


PANDOC_COMMAND = 'pandoc input.md -o {OUTPUT_FILE} -f {FROM_TYPE} -t {TO_TYPE} --template="{TEMPLATE_PATH}"'


def build_cd(meta: dict, run_profiles: list[str]):
    context = meta["CONTEXT"]

    # build input.md
    with open("data.toml", "r") as f:
        filecontent = f.read()
        filecontent = parse_document(filecontent)

    data = toml.loads(filecontent)

    with open("input.md", "w") as f:
        f.write("---\n")
        f.write(yaml.safe_dump(data))
        f.write("---\n")

    # gather pres
    for profile in run_profiles:
        if profile not in context:
            raise ValueError(f"Profile {profile} not found in context")
        if "pre" in context[profile]:
            for line in context[profile]["pre"]:
                exec(line, meta)

    # pandoc command
    from_type = context["std"]["from"]
    to_type = context["std"]["to"]
    output = context["std"]["output"]
    template = context["std"]["template"]
    formatted = PANDOC_COMMAND.format(
        FROM_TYPE=from_type, TO_TYPE=to_type, OUTPUT_FILE=output, TEMPLATE_PATH=template
    )
    print(formatted)
    print(os.getcwd())
    os.system(formatted)

    for profile in run_profiles:
        if "post" in context[profile]:
            for line in context[profile]["post"]:
                exec(line, meta)

        if isinstance(output, str):
            output = [output]

        if "output_replace" in context[profile]:
            output = context[profile]["output_replace"]
        elif "output" in context[profile]:
            if isinstance(context[profile]["output"], str):
                output.append(context[profile]["output"])
            elif isinstance(context[profile]["output"], list):
                output.extend(context[profile]["output"])
            else:
                raise ValueError(f"Invalid output type for profile {profile}")

    if isinstance(output, str):
        output = [output]

    return output



def run_detached(cmd, pkg_path=None):
    # On Windows, use DETACHED_PROCESS flag
    if platform.system() == "Windows":
        subprocess.Popen(cmd, cwd=pkg_path, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    # On Unix-like systems, use nohup
    else:
        subprocess.Popen(["nohup"] + cmd, cwd=pkg_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
