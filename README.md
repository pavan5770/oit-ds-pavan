# Prefect Flow Template Repo

Template repository to use for defining Prefect Flows to be run in Prefect Cloud.

TO DO:
 - Keep all section headers in this README but replace this section and Description to match your own integration
 - Change the title header at the top of this README
 - Give the oit-eds team admin access to your new repo

## Description

Replace this section with a description of the integration the flows of this repo constitute. Be sure to include these critical points:
 - Who the customer served by this integration is and the current customer contact
 - What the general purpose of the entire pipelines is; particularly what the source and sink systems are
 - Any known upstream dependencies, such as EDB views tracked in another repo
 - Any known downstream expectations, such as required allow-listing for sftp connections or a specific ingest time

In general, follow these key principles when creating repos for Prefect-powered data pipelines:
 - You can define multiple flows in a single repo, as long as they work together to serve a single customer or application
 - It's best to use as few flow files as possible to take advantage of Prefect's multithreading. For example, if you want to read four separate queries and write to four separate files, just do this all in one flow. Separate flows when they serve different purposes, such as having completely distinct sources or sinks, or when they need to be run on different schedules.
 - Be sure to follow the `{org}-{team}-flows-{repo-name}` format for naming your repo (see this repo for an example)
 - The `image` folder should contain everything a dev needs to understand the repos dependencies. For example, even if your base Docker image has already imported some Python packages, make sure `requirements.txt` lists EVERY required package and any version constraints.
 - Flow logic should be contained in the flows folder, whereas the image folder should only be used for slowly changing dependencies.

## Testing

Checks for Pylint and Black are run automatically on PR, so be sure to run these before committing. See `Dependencies` section for installation instructions, then run, for example:

```
pylint flows/*.py flows/tests/*.py
```
(your code must score 8.5 or higher)

and

```
black flows/*.py flows/tests/*.py
```

PRs also automatically run Pytest (again see `Dependencies` section for installation instructions). See `flows/tests/test_flows.py` for a template for writing tests. Unit tests are intended to validate data tranformation logic, so flows with minimal transformation won't need tests, in which case the template file can be left untouched.

If you do have tests, simply run `pytest` from the repo base directory before opening a PR.

## Deployment

### Docker Image

See the [Image Builder Repo](https://github.com/UCBoulder/oit-ds-tools-image-builder) for information about how to build and push Docker images for Prefect flows.

### Flows

The `flows` folder contains flow definitions, with one Python file per flow. This folder can also contain additional files to be referenced by your flows, such as SQL files for longer queries. When any flow is deployed, this entire folder is copied into the flow storage for that deployment, minus anything excluded by the `.prefectignore` file.

The `main` branch of the repo should correspond to production-ready flows. These are given the `main` tag and run from the `main` work queue. When developing on a new branch, flows are tagged with `dev` and run from the `dev` work queue. After completing a pull request and deleting a dev branch, remember to delete the corresponding deployment from Prefect Cloud to keep things clean.

All this work of deploying flows properly is handled for you by the `util.run_flow_command_line_interface` function! To deploy from the active branch, simply run:

```
python3 flows/example_flow.py deploy
```

You must be authenticated to Prefect Cloud and have the required Python packages installed (see Dependencies).

If in rare cases you are using a dev version of your Docker image, you must specify when deploying to use this image (which is labeled after the non-main-branch it was built from):

```
python3 flows/example_flow.py deploy --docker-label my-branch
```


## Dependencies

You'll need the command line tools for Prefect, Docker, and Git installed.

To register or visualize flows you will also need to have the required Python packages installed.

First and optionally, create and activate a virtual environment, for example:

```
python3 -m venv env
source env/bin/activate
```

Then you can install the packages:

```
cd image
pip3 install -r requirements.txt
```

In addition, you'll want to install these dev tools:

```
pip install pylint 'black<23' pytest
```

## Usage

See Development and Deployment for running in Prefect Cloud. This is the preferred usage method even for development.
