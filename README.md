# End-to-End Distributed ML Pipeline with Scalable Model Deoloyment on Kubernetes Cluster
<img width="1199" alt="image" src="https://github.com/user-attachments/assets/4399fe7f-96f1-40b1-ba58-c3a6a4df9d78" />
## About This Project

This project is a distributed rewrite of my original [Temporal Fusion Transformer (TFT) stock forecasting pipeline & MLOps project](https://github.com/Hiroaki0422/tft_stock_preds_mlops/#readme). The goal was to simulate a more **production-ready ML pipeline** by scaling up data preprocessing, model training, and deployment on a Kubernetes cluster.

While the underlying dataset is relatively small for personal experimentation, the architecture is designed to mimic real-world conditions — where **data volume is large** and **API traffic is high**. Each pipeline stage has been containerized, orchestrated with Helm, and deployed on Kubernetes to demonstrate how modern ML systems are built and scaled in production environments.

## Infrastructure: Kubernetes

This project runs entirely on a local **Minikube-based Kubernetes cluster**. The application is split into three services:
- **Spark Job**: for distributed data preprocessing
- **PyTorch Lightning Job**: for DDP-based model training
- **FastAPI Deployment**: for serving predictions via REST API

All components are containerized with Docker and orchestrated using **Helm charts** for declarative, reproducible deployments. Each service runs in its own namespace or pod, and persistent data access is simulated using host-mounted volumes.

---

## Distributed Data Pre-processing with Spark

The pipeline begins with a distributed Spark job that processes raw stock and sentiment data. Spark is run as a standalone containerized job inside the cluster using the Bitnami Spark image.

- **Input**: multiple CSV files with historical stock sentiment and price features
- **Output**: a curated CSV file ready for model training
- **Scalability**: Spark reads, transforms, and writes data in a distributed manner across multiple executors if scaled

This replaces a previous pandas-based pipeline and demonstrates how the same logic can be scaled using Spark's parallel data model.

---

## Distributed Model Training with DDP

The Temporal Fusion Transformer (TFT) model is trained using **PyTorch Lightning with `strategy="ddp"`**, which launches multiple processes for distributed gradient computation.

- **Input**: the curated dataset produced by the Spark job
- **Training**: split across multiple CPU/GPU workers (simulated here using CPU)
- **Syncing**: model gradients are averaged across processes to ensure consistency
- **Monitoring**: training metrics are logged via MLflow, and model checkpoints are automatically saved

This setup is future-proof and can scale seamlessly from local CPUs to multi-GPU clusters or cloud deployments.

---

## Scalable Model Deployment

The trained model is served using **FastAPI**, wrapped in a lightweight RESTful API that runs in a **Kubernetes `Deployment`**. Key features:

- **Horizontal Pod Autoscaling**: the service is configured with an HPA to scale between 2–5 replicas based on CPU usage
- **Low Latency Inference**: designed to respond to prediction requests in real time
- **Health and Monitoring**: Kubernetes probes and logs support observability

You can test the API by port-forwarding the FastAPI service and sending GET requests to `/predict`.

---

✅ **Result**: The entire pipeline simulates how a real production ML system would preprocess data, train models in parallel, and serve predictions reliably under load — all within a self-contained Kubernetes environment.

