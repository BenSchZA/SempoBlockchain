# Generating `kubeconfig` file for single namespace

See https://jeremievallee.com/2018/05/28/kubernetes-rbac-namespace-user.html

```bash
kubectl describe sa developer-user -n sarafu-production
kubectl get secret developer-user-token-xxxx -n sarafu-production -o "jsonpath={.data.token}" | base64

```

## `kubeconfig` template

```yaml
apiVersion: v1
kind: Config
preferences: {}

# Define the cluster
clusters:
  - cluster:
      certificate-authority-data: PLACE CERTIFICATE HERE
      # You'll need the API endpoint of your Cluster here:
      server: https://YOUR_KUBERNETES_API_ENDPOINT
    name: packet-cluster

# Define the user
users:
  - name: mynamespace-user
    user:
      as-user-extra: {}
      client-key-data: PLACE CERTIFICATE HERE
      token: PLACE USER TOKEN HERE

# Define the context: linking a user to a cluster
contexts:
  - context:
      cluster: packet-cluster
      namespace: sarafu-production
      user: developer-user
    name: sarafu-production

# Define current context
current-context: sarafu-production
```
