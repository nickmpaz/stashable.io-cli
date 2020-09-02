terraform {
  backend "s3" {
    bucket = "nicholasmpaz-terraform"
    key    = "dolphin-cli/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "cli" {
  bucket = "cli.${var.root_domain_name}"
  acl    = "public-read"
  policy = <<POLICY
{
  "Version":"2012-10-17",
  "Statement":[
    {
      "Sid":"AddPermissions",
      "Effect":"Allow",
      "Principal": "*",
      "Action":["s3:GetObject"],
      "Resource":["arn:aws:s3:::cli.${var.root_domain_name}/*"]
    }
  ]
}
POLICY
}