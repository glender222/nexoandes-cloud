#!/usr/bin/env python3
"""Compatibilidad Academy para el alta de S3; nunca borra buckets ni objetos."""
import json
import os
import subprocess
import sys


def call(*args, check=True):
    r = subprocess.run(["aws", *args, "--output", "json"], text=True, capture_output=True)
    if check and r.returncode:
        raise RuntimeError(r.stderr.strip())
    return r


def main():
    bucket, region, account = (os.environ[k] for k in ("NEXO_BUCKET", "NEXO_REGION", "NEXO_ACCOUNT"))
    actual = json.loads(call("sts", "get-caller-identity", "--region", region).stdout)["Account"]
    if actual != account:
        raise RuntimeError("Cuenta distinta de la esperada; no se crea ni adopta el bucket.")
    head = call("s3api", "head-bucket", "--bucket", bucket, "--expected-bucket-owner", account, check=False)
    created = False
    if head.returncode:
        if not any(code in head.stderr for code in ("(404)", "(NoSuchBucket)", "(NotFound)")):
            raise RuntimeError(head.stderr.strip())
        args = ["s3api", "create-bucket", "--bucket", bucket, "--region", region]
        if region != "us-east-1":
            args += ["--create-bucket-configuration", "LocationConstraint=" + region]
        call(*args)
        created = True
        call("s3api", "wait", "bucket-exists", "--bucket", bucket)
    location = json.loads(call("s3api", "get-bucket-location", "--bucket", bucket,
                               "--expected-bucket-owner", account).stdout)["LocationConstraint"] or "us-east-1"
    if location != region:
        raise RuntimeError("El bucket existe en otra región; no se adopta.")
    if not created:
        result = call("s3api", "get-bucket-tagging", "--bucket", bucket, "--expected-bucket-owner", account)
        tags = {item["Key"]: item["Value"] for item in json.loads(result.stdout)["TagSet"]}
        if tags.get("proyecto") != "nexoandes":
            raise RuntimeError("El bucket existente no está identificado como NexoAndes; no se adopta.")
    tags = {"TagSet": [{"Key": key, "Value": value} for key, value in {
        "proyecto": "nexoandes", "nube": "aws", "administrado_por": "terraform", "entorno": "laboratorio"}.items()]}
    call("s3api", "put-bucket-tagging", "--bucket", bucket, "--expected-bucket-owner", account,
         "--tagging", json.dumps(tags))
    print("Bucket S3 creado o conservado con propietario y región comprobados:", bucket)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, KeyError, ValueError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
