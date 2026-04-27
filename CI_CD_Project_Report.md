# CI/CD Implementation Report: ACEest Fitness API
**Project:** ACEest Fitness and Gym API
**Environment:** Local Minikube Cluster, Jenkins, GitHub Actions
**Date:** April 2026

---

## 1. CI/CD Architecture Overview

The CI/CD pipeline for the ACEest Fitness API is designed to automate code quality checks, containerization, and zero-downtime Kubernetes deployments. The architecture is powered by a robust **Jenkins** Pipeline, running in tandem with **GitHub Actions** for secondary validations. 

### Pipeline Stages (Jenkinsfile)
1. **SCM Polling:** Jenkins is configured to automatically poll the GitHub repository every day at 12:00 PM (`0 12 * * *`) to check for changes and trigger builds autonomously.
2. **Checkout & Linting:** Code is pulled from the repository. Python syntax is validated and linted using `ruff`.
3. **Unit Tests & Coverage:** `pytest` and `pytest-cov` execute the test suite, generating a `coverage.xml` report.
4. **Code Quality Analysis:** **SonarQube** ingests the coverage report and source code. A strict Quality Gate ensures code meets organizational standards before proceeding.
5. **Docker Build & Push:** The Flask application is packaged into a Docker container and securely pushed to Docker Hub (`2024tm93562/aceest-fitness`).
6. **Blue-Green Deployment (Kubernetes):** 
   - A custom PowerShell script dynamically interrogates the active Kubernetes cluster.
   - It identifies the active environment (Blue or Green) currently serving live traffic in the `blue-green-deployment` namespace.
   - The *inactive* deployment is updated with the newly built Docker image and allowed to initialize.
   - Once healthy, the `fitness-service` traffic router is instantly patched to switch traffic to the new environment, achieving zero-downtime.

---

## 2. Challenges Faced & Mitigation Strategies

During the implementation of this advanced CI/CD lifecycle, several complex technical challenges were encountered and resolved.

### Challenge 1: Premature SonarQube Quality Gate Failures
* **Issue:** The Jenkins pipeline was failing at the Quality Gate stage due to 0% code coverage. This occurred because the SonarQube analysis was executing *before* the unit tests ran, and the environment lacked a coverage generation tool.
* **Mitigation:** The pipeline was restructured. The "Unit Tests" stage was moved ahead of the "SonarQube Analysis" stage. Additionally, `pytest-cov` was added to `requirements.txt` to generate a `coverage.xml` artifact, which was then explicitly passed to the Sonar scanner via `-Dsonar.python.coverage.reportPaths`.

### Challenge 2: PowerShell JSON Parsing & Quotation Stripping
* **Issue:** During the Blue-Green cutover phase, the pipeline attempted to dynamically patch the Kubernetes service selector using a raw JSON string via the command line (`kubectl patch service ... -p '{"spec":...}'`). PowerShell aggressively stripped the quotation marks, resulting in malformed JSON and halting the deployment.
* **Mitigation:** The deployment logic was rewritten to bypass PowerShell's string interpolation entirely. The script now constructs the JSON string internally, exports it to a raw text file (`patch.json`) using `Out-File -Encoding ASCII`, and instructs `kubectl` to read directly from the file via the `--patch-file` argument.

### Challenge 3: Port-Forward Tunnels Masking Live Rollouts
* **Issue:** During testing, the `curl` loop polling `localhost:30002` failed to reflect the live environment flip from Blue to Green.
* **Mitigation:** It was determined that `kubectl port-forward` establishes a persistent connection to a *specific pod* behind the service, bypassing the dynamic load balancer. This was addressed by documenting testing protocols, ensuring developers understand that local port-forward tunnels must be restarted to observe real-time routing flips that occur at the service layer.

### Challenge 4: Live API Version Testing Mismatches
* **Issue:** Pushing application updates (e.g., updating the API version from `V2` to `V4`) caused subsequent pipeline failures because the automated unit testing suite (`test_app.py`) was tightly coupled to hardcoded strings and trailed behind application logic.
* **Mitigation:** Implemented synchronized commit practices ensuring `test_app.py` assertions exactly mirror the payload changes introduced in `app.py`. 

---

## 3. Key Automation Outcomes

The successful deployment of this architecture has resulted in several high-impact outcomes:

1. **True Zero-Downtime Deployments:** By deprecating the standard `RollingUpdate` in favor of a native `Blue-Green` strategy, the application guarantees that live user traffic is never routed to a terminating pod or a pod undergoing initialization.
2. **Safe Sandbox Testing:** All experimental deployments have been isolated into a dedicated `blue-green-deployment` Kubernetes namespace, entirely eliminating the risk of accidental overrides to production resources.
3. **Automated Quality Enforcement:** Merging broken or untested code is no longer possible. The SonarQube Quality Gate acts as an automated gatekeeper, rejecting any build that does not maintain adequate test coverage.
4. **Hands-Free Operations:** With the integration of daily SCM polling (`0 12 * * *`), the operational overhead has been drastically reduced. Developers simply push code to GitHub, and the entire lifecycle—from linting to cluster traffic switching—occurs without human intervention.
