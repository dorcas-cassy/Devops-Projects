module "network" { source = "./modules/network" project_name = var.project_name vpc_cidr = var.vpc_cidr }
output "vpc_id" { value = module.network.vpc_id }
output "private_subnet_ids" { value = module.network.private_subnet_ids }
