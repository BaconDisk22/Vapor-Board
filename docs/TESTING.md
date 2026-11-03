# Automated test checks

The GitHub Actions workflow runs Python 3.10 and 3.12 syntax compilation and unittest discovery for every pull request and pushes to main. It does not require radio hardware or connect to a network. Desktop rendering on macOS, Meshtastic protocol interoperability, age verification, and packaging require separate tests. GitHub Actions execution status must be checked on each PR; the existence of a workflow file is not proof tests passed.
