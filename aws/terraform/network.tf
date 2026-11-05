resource "aws_vpc" "main" {
  cidr_block           = "10.10.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "${local.prefix}-vpc" }
}
resource "aws_subnet" "main" {
  for_each                = local.subnets
  vpc_id                  = aws_vpc.main.id
  cidr_block              = each.value.cidr
  availability_zone       = data.aws_availability_zones.available.names[each.value.az]
  map_public_ip_on_launch = false
  tags                    = { Name = "${local.prefix}-${each.key}" }
}
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${local.prefix}-igw" }
}
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${local.prefix}-public" }
}
resource "aws_route" "public" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${local.prefix}-private" }
}
resource "aws_route_table_association" "main" {
  for_each       = local.subnets
  subnet_id      = aws_subnet.main[each.key].id
  route_table_id = each.value.public ? aws_route_table.public.id : aws_route_table.private.id
}
resource "aws_eip" "nat" {
  count  = var.encendido ? 1 : 0
  domain = "vpc"
  tags   = { Name = "${local.prefix}-nat" }
}
resource "aws_nat_gateway" "main" {
  count         = var.encendido ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.main["public_a"].id
  depends_on    = [aws_internet_gateway.main]
  tags          = { Name = "${local.prefix}-nat" }
}
resource "aws_route" "private" {
  count                  = var.encendido ? 1 : 0
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main[0].id
}
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]
}
resource "aws_security_group" "alb" {
  name_prefix = "${local.prefix}-alb-"
  vpc_id      = aws_vpc.main.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  dynamic "ingress" {
    for_each = var.certificate_arn != "" ? [1] : []
    content {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
  dynamic "ingress" {
    for_each = var.enable_supabase && var.supabase_studio_external && var.certificate_arn != "" ? [1] : []
    content {
      description = "Supabase Studio HTTPS con credenciales de dashboard"
      from_port   = 8443
      to_port     = 8443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.10.0.0/16"]
  }
}
resource "aws_security_group" "app" {
  name_prefix = "${local.prefix}-app-"
  vpc_id      = aws_vpc.main.id
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_security_group" "db" {
  name_prefix = "${local.prefix}-db-"
  vpc_id      = aws_vpc.main.id
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }
  dynamic "ingress" {
    for_each = var.enable_gcp_vpn ? [var.gcp_private_cidr] : []
    content {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
      description = "GCP por IPsec y rutas privadas"
    }
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
