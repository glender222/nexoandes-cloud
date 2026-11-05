resource "aws_lb" "web" {
  count              = var.encendido ? 1 : 0
  name               = "${local.prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.main["public_a"].id, aws_subnet.main["public_b"].id]
}
resource "aws_lb_target_group" "web" {
  count                = var.encendido ? 1 : 0
  name_prefix          = "nexo-"
  port                 = 80
  protocol             = "HTTP"
  vpc_id               = aws_vpc.main.id
  target_type          = "instance"
  deregistration_delay = 30
  health_check {
    path    = "/"
    matcher = "200"
  }
}
resource "aws_lb_listener" "http" {
  count             = var.encendido ? 1 : 0
  load_balancer_arn = aws_lb.web[0].arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web[0].arn
  }
}
resource "aws_lb_listener" "https" {
  count             = var.encendido && var.certificate_arn != "" ? 1 : 0
  load_balancer_arn = aws_lb.web[0].arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = var.certificate_arn
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web[0].arn
  }
}
resource "aws_launch_template" "web" {
  count         = var.encendido ? 1 : 0
  name_prefix   = "${local.prefix}-web-"
  image_id      = local.selected_ami
  instance_type = "t3.micro"
  monitoring { enabled = true }
  vpc_security_group_ids = [aws_security_group.app.id]
  user_data = base64encode(join("\n", [
    replace(file("${path.module}/../infraestructura/user-data.sh"), "TEAM_NUMBER=\"XX\"", "TEAM_NUMBER=\"${var.team_number}\""),
    var.enable_supabase && var.supabase_web_key != "" ? templatefile("${path.module}/templates/supabase-web.sh.tftpl", {
      bucket     = terraform_data.backup.output.bucket,
      object_key = var.supabase_web_key,
      sha256     = var.supabase_web_sha256,
      private_ip = aws_instance.supabase[0].private_ip,
      public_key = var.supabase_publishable_key
    }) : ""
  ]))
  iam_instance_profile {
    name = data.aws_iam_instance_profile.lab.name
  }
  metadata_options {
    http_tokens = "required"
  }
  block_device_mappings {
    device_name = "/dev/xvda"
    ebs {
      volume_size           = 8
      volume_type           = "gp3"
      encrypted             = true
      delete_on_termination = true
    }
  }
  credit_specification {
    cpu_credits = "standard"
  }
  tag_specifications {
    resource_type = "instance"
    tags = {
      Name             = "${local.prefix}-web"
      proyecto         = "nexoandes"
      administrado_por = "terraform"
    }
  }
}
resource "aws_autoscaling_group" "web" {
  count                     = var.encendido ? 1 : 0
  name                      = "${local.prefix}-web"
  min_size                  = 2
  desired_capacity          = 2
  max_size                  = 4
  vpc_zone_identifier       = [aws_subnet.main["app_a"].id, aws_subnet.main["app_b"].id]
  target_group_arns         = [aws_lb_target_group.web[0].arn]
  health_check_type         = "ELB"
  health_check_grace_period = 300
  default_instance_warmup   = 180
  wait_for_elb_capacity     = 2
  wait_for_capacity_timeout = "15m"
  launch_template {
    id      = aws_launch_template.web[0].id
    version = aws_launch_template.web[0].latest_version
  }
  # Academy deniega StartInstanceRefresh (INC-018). Las renovaciones de la
  # flota se ejecutan de forma controlada con el segundo destino saludable.
  tag {
    key                 = "proyecto"
    value               = "nexoandes"
    propagate_at_launch = true
  }
  depends_on = [aws_route.private, aws_lb_listener.http]
  lifecycle {
    ignore_changes = [desired_capacity]
  }
}
resource "aws_autoscaling_policy" "cpu" {
  count                  = var.encendido ? 1 : 0
  name                   = "${local.prefix}-cpu50"
  autoscaling_group_name = aws_autoscaling_group.web[0].name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    target_value = 50
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
  }
}
resource "aws_cloudwatch_metric_alarm" "cpu" {
  # CPU se conserva como métrica operativa; la prueba de crecimiento usa
  # solicitudes para no depender de créditos T3 Standard agotados.
  count               = var.encendido ? 1 : 0
  alarm_name          = "${local.prefix}-cpu-alta"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  dimensions          = { AutoScalingGroupName = aws_autoscaling_group.web[0].name }
}
resource "aws_autoscaling_policy" "requests" {
  count                  = var.encendido ? 1 : 0
  name                   = "${local.prefix}-solicitudes"
  autoscaling_group_name = aws_autoscaling_group.web[0].name
  policy_type            = "TargetTrackingScaling"
  target_tracking_configuration {
    target_value = 30 # Umbral de demostración, no capacidad de producción medida.
    predefined_metric_specification {
      predefined_metric_type = "ALBRequestCountPerTarget"
      resource_label         = "${aws_lb.web[0].arn_suffix}/${aws_lb_target_group.web[0].arn_suffix}"
    }
  }
}
resource "aws_cloudwatch_metric_alarm" "errors" {
  count               = var.encendido ? 1 : 0
  alarm_name          = "${local.prefix}-http5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 5
  treat_missing_data  = "notBreaching"
  dimensions          = { LoadBalancer = aws_lb.web[0].arn_suffix }
}
