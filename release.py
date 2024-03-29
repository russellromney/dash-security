import os
import sys


if __name__ == "__main__":
    """
    Simple script to update the version in setup.py according to semantic versioning

    ```
    zsh release.sh minor
    zsh release.sh major
    zsh release.sh patch
    ```
    """
    arg = sys.argv[1]
    if arg not in ("major", "minor", "patch"):
        raise ValueError("arg must be in (major, minor, patch)")
    lines = open("pyproject.toml").read().split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("version ="):
            major, minor, patch = (
                line.strip()
                .replace("version = ", "")
                .replace(",", "")
                .replace('"', "")
                .split(".")
            )
            if arg == "major":
                print(
                    f"upgrading from v{major}.{minor}.{patch} to v{str(int(major) + 1)}.0.0"
                )
                major = str(int(major) + 1)
                minor = "0"
                patch = "0"
            elif arg == "minor":
                print(
                    f"upgrading from v{major}.{minor}.{patch} to v{major}.{str(int(minor) + 1)}.0"
                )
                minor = str(int(minor) + 1)
                patch = "0"
            elif arg == "patch":
                print(
                    f"upgrading from v{major}.{minor}.{patch} to v{major}.{minor}.{str(int(patch) + 1)}"
                )
                patch = str(int(patch) + 1)
            lines[i] = f'version = "{major}.{minor}.{patch}"'
        # if line.strip().startswith("download_url=") and line.strip().endswith(","):
        #     lines[
        #         i
        #     ] = f'    download_url="https://github.com/russellromney/dash-security/archive/v{major}.{minor}.{patch}.tar.gz",'

    if s := input("do you want to continue with the release to PyPi? y/n: "):
        if s.lower() == "y":
            # os.remove("dist")
            # os.remove("dash-security.egg-info")
            # with open("setup.py", "w") as f:
            with open("pyproject.toml", "w") as f:
                for line in lines:
                    f.writelines(line + "\n")
            with open("/tmp/dash-security-release-version", "w") as f:
                f.truncate()
                f.write(f"{major}.{minor}.{patch}")
        else:
            raise Exception("Exiting release bump.")
