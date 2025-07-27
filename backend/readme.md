for tweet generator
python -m textblob.download_corpora

terraform init
terraform plan
terraform apply

gcloud auth application-default login
(can work on cmd)
(optional: C:\Users\vikik\AppData\Local\Google\Cloud SDK>)

---gloud command
gcloud auth login
gcloud config set project citypulse-466518
gcloud run deploy tweet-simulator --source . --region asia-south1 --allow-unauthenticated --timeout 15m --memory 512Mi


----Create GCP Free-tier VM
Go to Google Cloud Console → Compute Engine --> enable.
Click “Create Instance”.
Fill in:
    Name: tweet-vm
    Region: us-central1 (needed for free-tier)
    Machine type: e2-micro (free-tier eligible)
    Under Boot disk, choose:
        Debian 11 or Ubuntu 20.04 LTS
    Under Firewall, check both:
        Allow HTTP
        Allow HTTPS
    Under Advanced → Automation → Startup script, paste:
        #!/bin/bash
        sudo apt update
        sudo apt install -y python3-pip
        pip3 install --upgrade pip
        pip3 install google-cloud-pubsub

        mkdir -p /home/tweet_user
        cd /home/tweet_user

        # Download your script files (we’ll 
        upload them in next step)
        # Run the script in background
        nohup python3 main.py > output.log 2>&1 &
    Click Create.

-------Build and deply as cloud run service [Publisher]
gcloud auth login
gcloud config set project hackathon-zentrixel
docker build -t us-central1-docker.pkg.dev/hackathon-zentrixel/tweet-registry/tweet-simulator:latest .
gcloud artifacts repositories create tweet-registry --repository-format=docker  --location=us-central1
gcloud auth configure-docker us-central1-docker.pkg.dev
docker push us-central1-docker.pkg.dev/hackathon-zentrixel/tweet-registry/tweet-simulator:latest
gcloud run jobs create tweet-simulator --image us-central1-docker.pkg.dev/hackathon-zentrixel/tweet-registry/tweet-simulator:latest --region us-central1 --memory 512Mi --task-timeout 15m --max-retries 3
gcloud run jobs create tweet-simulator
gcloud scheduler jobs create http tweet-subscriber-schedule --schedule "*/15 * * * *" --region=us-central1 --http-method POST --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/hackathon-zentrixel/jobs/tweet-subscriber:run" --oauth-service-account-email scheduler-sa@hackathon-zentrixel.iam.gserviceaccount.com  

--------Build & Push the Docker Image [Subscriber]
docker build -t asia-south1-docker.pkg.dev/citypulse-466518/tweet-registry/tweet-subscriber:latest .
docker push asia-south1-docker.pkg.dev/citypulse-466518/tweet-registry/tweet-subscriber:latest
# Deploy Cloud Run Job
gcloud run jobs create tweet-subscriber --image asia-south1-docker.pkg.dev/citypulse-466518/tweet-registry/tweet-subscriber:latest --region asia-south1 --memory 512Mi --task-timeout 15m --max-retries 3
# IAM Binding (if not already done)
gcloud projects add-iam-policy-binding citypulse-466518 --member="serviceAccount:scheduler-sa@citypulse-466518.iam.gserviceaccount.com" --role="roles/run.invoker"
# Create Cloud Scheduler Job
gcloud scheduler jobs create http tweet-subscriber-schedule --schedule "*/15 * * * *" --region=asia-south1 --http-method POST --uri "https://asia-south1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/citypulse-466518/jobs/tweet-subscriber:run" --oauth-service-account-email scheduler-sa@citypulse-466518.iam.gserviceaccount.com



    Steps to Build docker container and Deploy: This will build using Dockerfile and deploying container to Cloud Run service [tweet-simulator] in project [citypulse-466518] region [asia-south1]

    (venv) PS C:\Users\vikik\Projects\GoogleHackathon\zencitypulse\publisher> gcloud auth login
    (venv) PS C:\Users\vikik\Projects\GoogleHackathon\zencitypulse\publisher> gcloud run deploy tweet-simulator --source . --region asia-south1 --allow-unauthenticated --timeout 15m --memory 512Mi
        The following APIs are not enabled on project [citypulse-466518]:
        artifactregistry.googleapis.com
        cloudbuild.googleapis.com
        run.googleapis.com
    Do you want enable these APIs to continue (this will take a few minutes)? (Y/n)?  Y

    Enabling APIs on project [citypulse-466518]...
    Operation "operations/acf.p2-331255869610-18cb6e4c-a791-4dbb-9bd2-62d290a88584" finished successfully.
    Deploying from source requires an Artifact Registry Docker repository to store built containers. A repository named [cloud-run-source-deploy] in region 
    [asia-south1] will be created.

    Do you want to continue (Y/n)?
    Building using Dockerfile and deploying container to Cloud Run service [tweet-simulator] in project [citypulse-466518] region [asia-south1]
X  Building and deploying new service... Building Container.
  OK Creating Container Repository...
  OK Uploading sources...
  OK Building Container... Logs are available at [https://console.cloud.google.com/cloud-build/builds;region=asia-south1/891bdc89-8e03-4278-a58e-24f1e90
  3e80d?project=331255869610].
  -  Creating Revision...
  .  Routing traffic...
  OK Setting IAM Policy...
Deployment failed
ERROR: (gcloud.run.deploy) Revision 'tweet-simulator-00001-kj5' is not ready and cannot serve traffic. The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable within the allocated timeout. This can happen when the container port is misconfigured or if the timeout is too short. The health check timeout can be extended. Logs for this revision might contain more information.

Logs URL: https://console.cloud.google.com/logs/viewer?project=citypulse-466518&resource=cloud_run_revision/service_name/tweet-simulator/revision_name/tweet-simulator-00001-kj5&advancedFilter=resource.type%3D%22cloud_run_revision%22%0Aresource.labels.service_name%3D%22tweet-simulator%22%0Aresource.labels.revision_name%3D%22tweet-simulator-00001-kj5%22
For more troubleshooting guidance, see https://cloud.google.com/run/docs/troubleshooting#container-failed-to-start

