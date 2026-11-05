mock_provider "aws" {
  mock_resource "aws_lb" {
    defaults = {
      arn        = "arn:aws:elasticloadbalancing:us-east-1:849533029543:loadbalancer/app/nexoandes-alb/0123456789abcdef"
      arn_suffix = "app/nexoandes-alb/0123456789abcdef"
      dns_name   = "nexoandes-test.us-east-1.elb.amazonaws.com"
    }
  }
  mock_resource "aws_lb_target_group" {
    defaults = { arn = "arn:aws:elasticloadbalancing:us-east-1:849533029543:targetgroup/nexo-test/0123456789abcdef" }
  }
  mock_resource "aws_instance" {
    defaults = { id = "i-0123456789abcdef0" }
  }
  mock_resource "aws_launch_template" {
    defaults = { id = "lt-0123456789abcdef0", latest_version = 1 }
  }
  mock_data "aws_availability_zones" {
    defaults = { names = ["us-east-1a", "us-east-1b"] }
  }
  mock_data "aws_ami" {
    defaults = { id = "ami-0123456789abcdef0" }
  }
  mock_data "aws_iam_instance_profile" {
    defaults = { name = "LabInstanceProfile" }
  }
  mock_data "aws_ssm_parameter" {
    defaults = { value = "ami-0123456789abcdef0" }
  }
}
variables {
  expected_account_id = "849533029543"
  team_number         = "XX"
}
run "encender" {
  command = plan
  variables {
    encendido = true
  }
  assert {
    condition     = length(aws_lb.web) == 1 && length(aws_nat_gateway.main) == 1
    error_message = "El encendido debe crear el balanceador y el NAT."
  }
  assert {
    condition     = aws_autoscaling_group.web[0].min_size == 2 && aws_autoscaling_group.web[0].max_size == 4
    error_message = "La capacidad web debe respetar el laboratorio."
  }
}
run "apagar" {
  command = plan
  variables {
    encendido = false
  }
  assert {
    condition     = length(aws_lb.web) == 0 && length(aws_nat_gateway.main) == 0 && length(aws_autoscaling_group.web) == 0
    error_message = "El apagado debe retirar los recursos temporales."
  }
  assert {
    condition     = aws_ec2_instance_state.db.state == "stopped"
    error_message = "La base de datos debe quedar detenida."
  }
  assert {
    condition     = aws_ebs_volume.db.size == 20 && aws_ebs_volume.db.encrypted && terraform_data.backup.input.bucket == "nexoandes-backup-849533029543-us-east-1"
    error_message = "Apagar debe mantener la configuración del disco y del bucket persistentes."
  }
}

run "supabase_encender" {
  command = plan
  variables {
    encendido       = true
    enable_supabase = true
  }
  assert {
    condition     = aws_instance.supabase[0].instance_type == "t3.medium" && !aws_instance.supabase[0].associate_public_ip_address && aws_ebs_volume.supabase[0].encrypted
    error_message = "Supabase debe ser privado, con datos cifrados y capacidad minima."
  }
  assert {
    condition     = aws_ec2_instance_state.supabase[0].state == "running" && length(aws_lb_listener_rule.supabase_no_http) == 1
    error_message = "Supabase debe arrancar y rechazar Auth sobre HTTP."
  }
  assert {
    condition     = length(aws_lb_listener.supabase_studio) == 0
    error_message = "Studio externo debe permanecer deshabilitado sin autorización explícita."
  }
}

run "studio_https_autorizado" {
  command = plan
  variables {
    encendido                = true
    enable_supabase          = true
    supabase_studio_external = true
    certificate_arn          = "arn:aws:acm:us-east-1:849533029543:certificate/00000000-0000-0000-0000-000000000001"
  }
  assert {
    condition     = aws_lb_listener.supabase_studio[0].port == 8443 && aws_lb_listener.supabase_studio[0].protocol == "HTTPS" && aws_lb_target_group.supabase[0].port == 8000
    error_message = "Studio requiere TLS en el ALB y el gateway privado existente."
  }
  assert {
    condition     = aws_lb_listener_rule.supabase_studio_internal_paths[0].action[0].fixed_response[0].status_code == "403"
    error_message = "Las rutas internas de meta y MCP no deben publicarse."
  }
}

run "studio_sin_tls_no_publicado" {
  command = plan
  variables {
    encendido                = true
    enable_supabase          = true
    supabase_studio_external = true
    certificate_arn          = ""
  }
  assert {
    condition     = length(aws_lb_listener.supabase_studio) == 0 && length(aws_security_group.alb.ingress) == 1
    error_message = "Sin certificado no se permite listener Studio ni apertura de 8443."
  }
}

run "supabase_apagar" {
  command = plan
  variables {
    encendido       = false
    enable_supabase = true
  }
  assert {
    condition     = length(aws_instance.supabase) == 1 && aws_ec2_instance_state.supabase[0].state == "stopped" && aws_ebs_volume.supabase[0].size == 40
    error_message = "Apagar debe detener la misma VM y conservar el disco Supabase."
  }
  assert {
    condition     = length(aws_lb_target_group.supabase) == 0 && length(aws_lb_listener_rule.supabase_no_http) == 0
    error_message = "Apagar debe retirar el acceso temporal al API."
  }
}

run "rechazar_clave_secreta_en_frontend" {
  command = plan
  variables {
    encendido                = true
    enable_supabase          = true
    supabase_publishable_key = "sb_secret_no_admitida"
  }
  expect_failures = [var.supabase_publishable_key]
}
