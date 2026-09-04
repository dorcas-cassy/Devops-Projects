provider "aws" {
  region = "eu-central-1"
}

resource "aws_s3_bucket" "my_bucket" {
  bucket = "nextwork-unique-bucket-cass-2981"

  tags = { # Make sure this bucket name is globally unique by typing a long random number
    Project = "Create an S3 bucket with Terraform"
  }
}

resource "aws_s3_bucket_public_access_block" "my_bucket_public_access_block" {
  bucket = aws_s3_bucket.my_bucket.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "my_image" {
  bucket = aws_s3_bucket.my_bucket.id
  key    = "IMG_3513.JPG"
  source = "IMG_3513.JPG"
}