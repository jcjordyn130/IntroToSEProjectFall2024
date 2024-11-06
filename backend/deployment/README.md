# deployment
I have provided a podman compatible Docker image and compose file for ease of deployment.

To deploy, follow these steps:

- Clone repository using `git clone https://github.com/jcjordyn130/IntroToSEProjectFall2024`
- Switch to backend branch using `git checkout backend-dev`
- Clone the repository AGAIN inside of `backend/deployment`
- Bring up the compose stack using your choice of program, for podman, use `podman-compose up`
- Profit!!!

### Defaults
The API is ran on port 5000, and the testing user credentials are `testing/password`.

For proper deployment, REMOVE that user accout either via the API or using `sqlite3`.
