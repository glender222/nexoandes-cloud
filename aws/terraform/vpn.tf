variable "enable_gcp_vpn" {
  type    = bool
  default = false
}
variable "gcp_peer_ip" {
  type    = string
  default = ""
}
variable "gcp_private_cidr" {
  type    = string
  default = "10.30.1.0/24"
}
data "aws_ssm_parameter" "ubuntu_vpn" {
  count = var.enable_gcp_vpn ? 1 : 0
  name  = "/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id"
}
resource "aws_security_group" "vpn" {
  count       = var.enable_gcp_vpn ? 1 : 0
  name_prefix = "nexoandes-ipsec-"
  vpc_id      = aws_vpc.main.id
  dynamic "ingress" {
    for_each = var.gcp_peer_ip != "" ? [500, 4500] : []
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "udp"
      cidr_blocks = ["${var.gcp_peer_ip}/32"]
    }
  }
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.10.0.0/16"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "nexoandes-ipsec", proyecto = "nexoandes" }
}
resource "aws_instance" "vpn" {
  count                       = var.encendido && var.enable_gcp_vpn ? 1 : 0
  ami                         = data.aws_ssm_parameter.ubuntu_vpn[0].value
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.main["public_a"].id
  vpc_security_group_ids      = [aws_security_group.vpn[0].id]
  associate_public_ip_address = true
  source_dest_check           = false
  iam_instance_profile        = data.aws_iam_instance_profile.lab.name
  user_data                   = file("${path.module}/templates/vpn.sh")
  metadata_options { http_tokens = "required" }
  root_block_device {
    volume_size = 8
    volume_type = "gp3"
    encrypted   = true
  }
  credit_specification { cpu_credits = "standard" }
  tags       = { Name = "nexoandes-ipsec", proyecto = "nexoandes", administrado_por = "terraform" }
  depends_on = [aws_route.public]
}
resource "aws_route" "gcp" {
  count                  = var.encendido && var.enable_gcp_vpn ? 1 : 0
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = var.gcp_private_cidr
  network_interface_id   = aws_instance.vpn[0].primary_network_interface_id
}
