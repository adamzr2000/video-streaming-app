## Kubernetes Deployment

To deploy the application:

```bash
kubectl apply -f config.yml -f video-streaming-app.yml
```

## Teardown

To delete the application:

```bash
kubectl delete -f config.yml -f video-streaming-app.yml
```