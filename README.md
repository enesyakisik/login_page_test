# Demo Login and Registration App

A minimal Flask application that supports user registration and login backed by PostgreSQL. Includes Docker and Kubernetes manifests for running in containers and pods.

## Features
- User registration with hashed passwords.
- Login/logout flow with session-based authentication.
- Dashboard for authenticated users.
- PostgreSQL persistence with automatic table creation.
- Docker image ready for deployment and Kubernetes manifests.

## Configuration
The application reads database connection details and the session secret from environment variables. Defaults match the sample values below:

```
DB_HOST=192.168.1.18
DB_PORT=5432
DB_NAME=appdb
DB_USER=k8suser
DB_PASSWORD=1qaz2wsx
FLASK_SECRET_KEY=change-this-secret
```

## Local Development
1. Create and activate a virtual environment (optional).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Export the database variables or update them in your shell.
4. Run the app:
   ```bash
   flask --app app.py --debug run -h 0.0.0.0 -p 5000
   ```

The app will create a `users` table on first request if it does not exist.

## Docker
Build and run the image locally:
```bash
docker build -t demo-auth:latest .
docker run -p 5000:5000 \
  -e DB_HOST=192.168.1.18 \
  -e DB_PORT=5432 \
  -e DB_NAME=appdb \
  -e DB_USER=k8suser \
  -e DB_PASSWORD=1qaz2wsx \
  -e FLASK_SECRET_KEY=change-this-secret \
  demo-auth:latest
```

## Kubernetes
A sample manifest is provided in `k8s/deployment.yaml`.

Apply it to your cluster after pushing the image to a registry and updating the `image` field:
```bash
kubectl apply -f k8s/deployment.yaml
```

This manifest creates:
- A `Secret` with the database password.
- A `ConfigMap` with the database connection details and Flask secret.
- A Deployment running the container.
- A ClusterIP Service exposing port 80 to the pod on port 5000.

## Database
The app uses SQLAlchemy with psycopg2. On start, it ensures the `users` table exists with the following columns:
- `id` (serial primary key)
- `email` (unique text)
- `password_hash` (hashed password)
- `created_at` (timestamp)

## Security Notes
- Replace the default `FLASK_SECRET_KEY` with a unique value in production.
- Store database credentials in secure secrets rather than plain ConfigMaps when possible.
- Add HTTPS, CSRF protection, and stricter password policies for production use.
