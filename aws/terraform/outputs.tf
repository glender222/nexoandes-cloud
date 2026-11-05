output "control" {
  value = {
    cuenta              = var.expected_account_id
    region              = var.region
    encendido           = var.encendido
    vpc_id              = aws_vpc.main.id
    db_instance         = aws_instance.db.id
    db_ip               = aws_instance.db.private_ip
    db_volume           = aws_ebs_volume.db.id
    bucket              = terraform_data.backup.output.bucket
    vpn_instance        = try(aws_instance.vpn[0].id, null)
    vpn_ip              = try(aws_instance.vpn[0].public_ip, null)
    supabase_instance   = try(aws_instance.supabase[0].id, null)
    supabase_ip         = try(aws_instance.supabase[0].private_ip, null)
    supabase_volume     = try(aws_ebs_volume.supabase[0].id, null)
    supabase_target     = try(aws_lb_target_group.supabase[0].arn, null)
    supabase_studio_url = length(aws_lb_listener.supabase_studio) > 0 ? "https://${aws_lb.web[0].dns_name}:8443" : null
    target_group        = try(aws_lb_target_group.web[0].arn, null)
    url                 = var.encendido ? "http://${aws_lb.web[0].dns_name}" : null
    https_url           = var.encendido && var.certificate_arn != "" ? "https://${aws_lb.web[0].dns_name}" : null
  }
}
