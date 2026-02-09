import mlflow

def log_params_metrics(params, metrics):
    for k,v in params.items():
        mlflow.log_param(k,v)
    for k,v in metrics.items():
        mlflow.log_metric(k,v)
