variable "enable_supabase" {
  description = "Conservar una instancia Supabase; apagar la detiene sin borrar datos."
  type        = bool
  default     = false
}

variable "supabase_studio_external" {
  description = "Publicar Studio con Basic Auth por HTTPS 8443 del ALB existente."
  type        = bool
  default     = false
}

variable "supabase_publishable_key" {
  type    = string
  default = ""
  validation {
    condition     = var.supabase_publishable_key == "" || startswith(var.supabase_publishable_key, "sb_publishable_")
    error_message = "Solo se permite una clave publicable; nunca service_role ni sb_secret."
  }
}
variable "supabase_web_key" {
  type    = string
  default = ""
}
variable "supabase_web_sha256" {
  type    = string
  default = ""
}

data "aws_ssm_parameter" "ubuntu_supabase" {
  count = var.enable_supabase ? 1 : 0
  name  = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
}

resource "aws_security_group" "supabase" {
  count       = var.enable_supabase ? 1 : 0
  name_prefix = "nexoandes-supabase-"
  vpc_id      = aws_vpc.main.id
  ingress {
    description     = "API desde ALB y backend; administracion por SSM"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id, aws_security_group.app.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "nexoandes-supabase" }
}

resource "aws_ebs_volume" "supabase" {
  count             = var.enable_supabase ? 1 : 0
  availability_zone = aws_subnet.main["app_b"].availability_zone
  size              = 40
  type              = "gp3"
  encrypted         = true
  tags              = { Name = "nexoandes-supabase-datos" }
  lifecycle { prevent_destroy = true }
}

resource "aws_instance" "supabase" {
  count                       = var.enable_supabase ? 1 : 0
  ami                         = data.aws_ssm_parameter.ubuntu_supabase[0].value
  instance_type               = "t3.medium"
  subnet_id                   = aws_subnet.main["app_b"].id
  vpc_security_group_ids      = [aws_security_group.supabase[0].id]
  associate_public_ip_address = false
  iam_instance_profile        = data.aws_iam_instance_profile.lab.name
  user_data = templatefile("${path.module}/templates/supabase.sh.tftpl", {
    volume_id = replace(aws_ebs_volume.supabase[0].id, "-", "")
  })
  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 1 # Solo el host usa LabRole, no los contenedores.
  }
  root_block_device {
    volume_size = 12
    volume_type = "gp3"
    encrypted   = true
  }
  credit_specification { cpu_credits = "standard" }
  tags = { Name = "nexoandes-supabase" }
  lifecycle {
    prevent_destroy = true
    ignore_changes  = [ami, user_data]
  }
  depends_on = [aws_route.private]
}

resource "aws_volume_attachment" "supabase" {
  count       = var.enable_supabase ? 1 : 0
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.supabase[0].id
  instance_id = aws_instance.supabase[0].id
}

resource "aws_ec2_instance_state" "supabase" {
  count       = var.enable_supabase ? 1 : 0
  instance_id = aws_instance.supabase[0].id
  state       = var.encendido ? "running" : "stopped"
  force       = false
  depends_on  = [aws_volume_attachment.supabase]
}

resource "aws_lb_target_group" "supabase" {
  count                = var.encendido && var.enable_supabase ? 1 : 0
  name_prefix          = "nx-sb-"
  port                 = 8000
  protocol             = "HTTP"
  vpc_id               = aws_vpc.main.id
  deregistration_delay = 10
  health_check {
    path    = "/auth/v1/health"
    matcher = "200"
  }
}

resource "aws_lb_target_group_attachment" "supabase" {
  count            = var.encendido && var.enable_supabase ? 1 : 0
  target_group_arn = aws_lb_target_group.supabase[0].arn
  target_id        = aws_instance.supabase[0].id
  port             = 8000
}

resource "aws_lb_listener_rule" "supabase_https" {
  count        = var.encendido && var.enable_supabase && var.certificate_arn != "" ? 1 : 0
  listener_arn = aws_lb_listener.https[0].arn
  priority     = 20
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.supabase[0].arn
  }
  condition {
    path_pattern { values = ["/auth/v1/*", "/rest/v1/*"] }
  }
}

resource "aws_lb_listener_rule" "supabase_no_http" {
  count        = var.encendido && var.enable_supabase ? 1 : 0
  listener_arn = aws_lb_listener.http[0].arn
  priority     = 20
  action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      status_code  = "403"
      message_body = "Auth y API requieren HTTPS"
    }
  }
  condition {
    path_pattern { values = ["/auth/v1/*", "/rest/v1/*", "/api/privado"] }
  }
}

resource "aws_lb_listener_rule" "supabase_login_https" {
  count        = var.encendido && var.enable_supabase ? 1 : 0
  listener_arn = aws_lb_listener.http[0].arn
  priority     = 21
  action {
    type = "redirect"
    redirect {
      protocol    = "HTTPS"
      port        = "443"
      status_code = "HTTP_302"
    }
  }
  condition {
    path_pattern { values = ["/acceso/*"] }
  }
}

# Studio usa rutas absolutas de Next.js: un puerto HTTPS separado mantiene
# sus rutas completas y evita interferir con el portal/API en 443.
resource "aws_lb_listener" "supabase_studio" {
  count             = var.encendido && var.enable_supabase && var.supabase_studio_external && var.certificate_arn != "" ? 1 : 0
  load_balancer_arn = aws_lb.web[0].arn
  port              = 8443
  protocol          = "HTTPS"
  certificate_arn   = var.certificate_arn
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.supabase[0].arn
  }
}

resource "aws_lb_listener_rule" "supabase_studio_internal_paths" {
  count        = length(aws_lb_listener.supabase_studio)
  listener_arn = aws_lb_listener.supabase_studio[0].arn
  priority     = 1
  action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      status_code  = "403"
      message_body = "Ruta interna no publicada"
    }
  }
  condition {
    path_pattern { values = ["/pg", "/pg/*", "/mcp*", "/api/mcp*"] }
  }
}
