provider "aws" {
  region = "us-east-1"  # or your preferred region
}

# ECR Repository
resource "aws_ecr_repository" "streaming_pipeline" {
  name = "streaming_pipeline"
}

# EC2 Instance
resource "aws_instance" "streaming_pipeline_server" {
  ami           = "ami-0b1ca8b711f1d1fd7"  # Ubuntu 20.04
  instance_type = "t2.small"
  key_name      = aws_key_pair.streaming_pipeline_key.key_name

  vpc_security_group_ids = [aws_security_group.streaming_pipeline_sg.id]

  tags = {
    Name = "streaming-pipeline-server"
  }

  user_data = templatefile("${path.module}/user_data.tpl", {
    ecr_repository_url = aws_ecr_repository.streaming_pipeline.repository_url
    region             = "eu-central-1"
    alpaca_api_key     = var.alpaca_api_key
    alpaca_api_secret  = var.alpaca_api_secret
    qdrant_api_key     = var.qdrant_api_key
    qdrant_url         = var.qdrant_url
  })

  iam_instance_profile = aws_iam_instance_profile.streaming_pipeline_profile.name
}

# Security Group
resource "aws_security_group" "streaming_pipeline_sg" {
  name        = "streaming-pipeline-sg"
  description = "Security group for streaming pipeline EC2 instance"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Key Pair
resource "aws_key_pair" "streaming_pipeline_key" {
  key_name   = "streaming-pipeline-key"
  public_key = file("~/.ssh/id_rsa.pub")  # Make sure this file exists
}

# IAM Role and Instance Profile
resource "aws_iam_role" "streaming_pipeline_role" {
  name = "streaming_pipeline_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecr_policy_attachment" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.streaming_pipeline_role.name
}

resource "aws_iam_instance_profile" "streaming_pipeline_profile" {
  name = "streaming_pipeline_profile"
  role = aws_iam_role.streaming_pipeline_role.name
}