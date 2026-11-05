resource "terraform_data" "backup" {
  input = {
    bucket     = "nexoandes-backup-${var.expected_account_id}-${var.region}"
    region     = var.region
    account    = var.expected_account_id
    generation = var.bucket_generation
  }
  triggers_replace = var.bucket_generation
  # Academy deniega GetBucketObjectLockConfiguration: el recurso aws_s3_bucket
  # no puede refrescarse. Solo el alta del contenedor usa las APIs permitidas.
  # No hay provisioner de destrucción: reemplazar este marcador NO borra S3.
  provisioner "local-exec" {
    command = "python3 \"${path.module}/bootstrap-bucket.py\""
    environment = {
      NEXO_BUCKET  = self.input.bucket
      NEXO_REGION  = self.input.region
      NEXO_ACCOUNT = self.input.account
    }
  }
}
resource "aws_s3_bucket_public_access_block" "backup" {
  bucket                  = terraform_data.backup.output.bucket
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
resource "aws_s3_bucket_ownership_controls" "backup" {
  bucket = terraform_data.backup.output.bucket
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}
resource "aws_s3_bucket_versioning" "backup" {
  bucket = terraform_data.backup.output.bucket
  versioning_configuration {
    status = "Enabled"
  }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "backup" {
  bucket = terraform_data.backup.output.bucket
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
resource "aws_s3_bucket_lifecycle_configuration" "backup" {
  bucket = terraform_data.backup.output.bucket
  rule {
    id     = "supabase-14-dias"
    status = "Enabled"
    filter { prefix = "supabase/" }
    expiration { days = 14 }
    noncurrent_version_expiration { noncurrent_days = 14 }
    abort_incomplete_multipart_upload { days_after_initiation = 1 }
  }
  rule {
    id     = "postgresql-14-dias"
    status = "Enabled"
    filter {
      prefix = "postgresql/"
    }
    expiration {
      days = 14
    }
    noncurrent_version_expiration {
      noncurrent_days = 14
    }
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}
resource "aws_ebs_volume" "db" {
  availability_zone = aws_subnet.main["db"].availability_zone
  size              = 20
  type              = "gp3"
  encrypted         = true
  tags              = { Name = "${local.prefix}-postgresql-datos" }
  lifecycle {
    prevent_destroy = true
  }
}
resource "aws_instance" "db" {
  ami                         = local.selected_ami
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.main["db"].id
  vpc_security_group_ids      = [aws_security_group.db.id]
  associate_public_ip_address = false
  iam_instance_profile        = data.aws_iam_instance_profile.lab.name
  user_data = templatefile("${path.module}/templates/postgresql.sh.tftpl", {
    volume_id = replace(aws_ebs_volume.db.id, "-", "")
    bucket    = terraform_data.backup.output.bucket
    region    = var.region
  })
  metadata_options {
    http_tokens = "required"
  }
  root_block_device {
    volume_size = 8
    volume_type = "gp3"
    encrypted   = true
  }
  credit_specification {
    cpu_credits = "standard"
  }
  tags = { Name = "${local.prefix}-postgresql" }
  lifecycle {
    prevent_destroy = true
    ignore_changes  = [ami, user_data]
  }
  depends_on = [aws_route.private]
}
resource "aws_volume_attachment" "db" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.db.id
  instance_id = aws_instance.db.id
}
resource "aws_ec2_instance_state" "db" {
  instance_id = aws_instance.db.id
  state       = var.encendido ? "running" : "stopped"
  force       = false
  depends_on  = [aws_volume_attachment.db]
}
