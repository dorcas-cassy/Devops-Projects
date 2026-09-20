# Investigation test scenarios

These manifests create **only** resources in `ai-agent-test`. Apply them to a disposable cluster or a cluster where you are authorized to create test workloads. They intentionally cause failures and may consume cluster resources until removed.

```sh
kubectl --context <selected-context> apply -f scenarios/
kubectl --context <selected-context> get pods,deployments,services -n ai-agent-test
```

Choose the same context in the dashboard and run an investigation. The evidence layer should find:

| Scenario | Expected evidence | Diagnosis to assess |
|---|---|---|
| `missing-env` | CrashLoopBackOff and `DATABASE_URL missing` in logs | Missing environment variable, with a fix to supply it |
| `bad-image` | ErrImagePull/ImagePullBackOff and pull event | Invalid image tag, with a fix to use a valid image |
| `low-memory` | OOMKilled in container state | Memory limit too low, with a resource-limit recommendation |
| `selector-mismatch` | Service selector mismatch and no endpoints | Selector does not match pod labels |

The AI wording and confidence score can vary. Verify that its claims match the collected evidence; do not treat a plausible answer as proof. Remove the test namespace when done:

```sh
kubectl --context <selected-context> delete namespace ai-agent-test
```
