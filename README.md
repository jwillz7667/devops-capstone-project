# devops-capstone-project

[![CI Build](https://github.com/jwillz7667/devops-capstone-project/actions/workflows/ci-build.yaml/badge.svg?branch=main)](https://github.com/jwillz7667/devops-capstone-project/actions/workflows/ci-build.yaml)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9](https://img.shields.io/badge/Python-3.9-green.svg)](https://shields.io/)

Customer accounts microservice for an e-commerce application, developed through Agile planning, test-driven REST API development, continuous integration, application security, containerization, Kubernetes deployment, and automated delivery.

This project starts from the official template for [**IBM-CD0285EN-SkillsNetwork DevOps Capstone Project**](https://www.coursera.org/learn/devops-capstone-project?specialization=devops-and-software-engineering), part of the [**IBM DevOps and Software Engineering Professional Certificate**](https://www.coursera.org/professional-certificates/devops-and-software-engineering). Implementation and verification progress are tracked in this repository's issues and project board. Planned features are not claims of completed functionality.

## Template Provenance

Created as a new repository from `ibm-developer-skills-network/aolwx-devops-capstone-template`, not as a fork. The starter supplies the account model and create endpoint; subsequent stories add and verify the remaining operations.

## Security Lab Scope

Talisman enables HTTPS redirects, HSTS on secure responses, and the required browser security headers. The test fixture temporarily disables redirects only within the route test class and restores the previous value afterward; a separate test checks the actual redirect behavior.

Flask-CORS allows non-credentialed cross-origin reads of the public metadata endpoint (`/`) only. Account endpoints do not inherit this wildcard policy. CORS is not authentication or authorization. This course service uses synthetic data and a legacy Python 3.9/Flask dependency set required by the labs; it is not ready to store real customer data or be deployed as a production service.

## Development Environment

These labs are designed to be executed in the IBM Developer Skills Network Cloud IDE with OpenShift. Please use the links provided in the Coursera Capstone project to access the lab environment.

Once you are in the lab environment, you can initialize it with `bin/setup.sh` by sourcing it. (*Note: DO NOT run this program as a bash script. It sets environment variable and so must be sourced*):

```bash
source bin/setup.sh
```

This will install Python 3.9, make it the default, modify the bash prompt, create a Python virtual environment and activate it.

After sourcing it you prompt should look like this:

```bash
(venv) theia:project$
```

## Useful commands

Under normal circumstances you should not have to run these commands. They are performed automatically at setup but may be useful when things go wrong:

### Activate the Python 3.9 virtual environment

You can activate the Python 3.9 environment with:

```bash
source ~/venv/bin/activate
```

### Installing Python dependencies

These dependencies are installed as part of the setup process but should you need to install them again, first make sure that the Python 3.9 virtual environment is activated and then use the `make install` command:

```bash
make install
```

### Starting the Postgres Docker container

The labs use Postgres running in a Docker container. If for some reason the service is not available you can start it with:

```bash
make db
```

You can use the `docker ps` command to make sure that postgres is up and running.

## Project layout

The code for the microservice is contained in the `service` package. All of the test are in the `tests` folder. The code follows the **Model-View-Controller** pattern with all of the database code and business logic in the model (`models.py`), and all of the RESTful routing on the controller (`routes.py`).

```text
├── service         <- microservice package
│   ├── common/     <- common log and error handlers
│   ├── config.py   <- Flask configuration object
│   ├── models.py   <- code for the persistent model
│   └── routes.py   <- code for the REST API routes
├── setup.cfg       <- tools setup config
└── tests                       <- folder for all of the tests
    ├── factories.py            <- test factories
    ├── test_cli_commands.py    <- CLI tests
    ├── test_models.py          <- model unit tests
    └── test_routes.py          <- route unit tests
```

## Data Model

The Account model contains the following fields:

| Name | Type | Optional |
|------|------|----------|
| id | Integer| False |
| name | String(64) | False |
| email | String(64) | False |
| address | String(256) | False |
| phone_number | String(32) | True |
| date_joined | Date | False |

## Your Task

Complete this microservice by implementing REST API's for `READ`, `UPDATE`, `DELETE`, and `LIST` while maintaining **95%** code coverage. In true **Test Driven Development** fashion, first write tests for the code you "wish you had", and then write the code to make them pass.

## Continuous Delivery in the Assigned OpenShift Lab

`tekton/pipeline.yaml` connects cleanup, clone, parallel lint/tests, Buildah,
and deployment tasks. The test database is isolated SQLite; the application
uses the existing `postgresql` Secret and service. Do not bind the pipeline
workspace to a developer checkout: cleanup intentionally removes its contents.

The assigned lab must already provide the `pipeline` service account and the
`buildah` and `openshift-client` ClusterTasks. Install the course's `git-clone`
and `flake8` catalog tasks, then apply the repository resources:

```bash
oc apply -f tekton/pvc.yaml -f tekton/tasks.yaml -f tekton/pipeline.yaml
tkn pipeline start cd-pipeline \
  -p repo-url=https://github.com/jwillz7667/devops-capstone-project.git \
  -p branch=main \
  -p build-image=image-registry.openshift-image-registry.svc:5000/$SN_ICR_NAMESPACE/accounts:1 \
  -w name=pipeline-workspace,claimName=pipelinerun-pvc \
  -s pipeline --showlog
```

`deploy/deployment.yaml` deliberately contains the course's `IMAGE_NAME_HERE`
placeholder. The deploy task resolves it with `oc set image --local` before
applying the manifest and waits for `oc rollout status` to succeed. For a
standalone manual deployment, resolve that image reference first; do not apply
the placeholder directly. Keep credentials out of source control and logs.

## Local Kubernetes Development

This repo can also be used for local Kubernetes development. It is not advised that you run these commands in the Cloud IDE environment. The purpose of these commands are to simulate the Cloud IDE environment locally on your computer. 

At a minimum, you will need [Docker Desktop](https://www.docker.com/products/docker-desktop) installed on your computer. For the full development environment, you will also need [Visual Studio Code](https://code.visualstudio.com) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension from the Visual Studio Marketplace. All of these can be installed manually by clicking on the links above or you can use a package manager like **Homebrew** on Mac of **Chocolatey** on Windows.

Please only use these commands for working stand-alone on your own computer with the VSCode Remote Container environment provided.

1. Bring up a local K3D Kubernetes cluster

    ```bash
    $ make cluster
    ```

2. Install Tekton

    ```bash
    $ make tekton
    ```

3. Install the ClusterTasks that the Cloud IDE has

    ```bash
    $ make clustertasks
    ```

You can now perform Tekton development locally, just like in the Cloud IDE lab environment.

## Author

[John Rofrano](https://www.coursera.org/instructor/johnrofrano), Senior Technical Staff Member, DevOps Champion, @ IBM Research, and Instructor @ Coursera

## License

Licensed under the Apache License. See [LICENSE](LICENSE)

## <h3 align="center"> © IBM Corporation 2022. All rights reserved. <h3/>
