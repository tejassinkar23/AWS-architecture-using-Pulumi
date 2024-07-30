# AWS-architecture-using-Pulumi


That's the full AWS architecture created using pulumi code (IaaS)

# Infrastructure Architecture
This project sets up a cloud infrastructure on AWS using Pulumi, an Infrastructure as Code (IaC) tool. The architecture is designed to host a web application running on an EC2 instance with NGINX, and a MySQL database hosted on Amazon RDS. The setup also includes necessary networking components and security configurations.

# Components
Virtual Private Cloud (VPC):
A VPC is created to logically isolate the infrastructure within AWS. The VPC has a CIDR block of 10.0.0.0/16 and supports DNS hostnames and DNS resolution.
Subnets:

**Public Subnet:**
*A public subnet is created with a CIDR block of 10.0.4.0/24 within the VPC. This subnet is associated with an Internet Gateway to allow inbound and outbound internet access.*
**Private Subnets:**
*Two private subnets are created for hosting the RDS instance.*
private-subnet-1 with CIDR block 10.0.5.0/24 in Availability Zone ap-south-1a.
private-subnet-2 with CIDR block 10.0.6.0/24 in Availability Zone ap-south-1b.
Internet Gateway:

An Internet Gateway is attached to the VPC to allow internet access for resources within the public subnet.
Route Table:
*A route table is created for the public subnet with a default route (0.0.0.0/0) pointing to the Internet Gateway. This route table is associated with the public subnet.
Security Groups:*

# EC2 Security Group:
Allows inbound HTTP (port 80) and SSH (port 22) traffic from any IP address (0.0.0.0/0).
Allows all outbound traffic.

# RDS Security Group:
Allows inbound MySQL traffic (port 3306) from the public subnet.
Allows all outbound traffic.

**EC2 Instance with NGINX:**
*An EC2 instance is created in the public subnet, running Amazon Linux 2, with NGINX installed and configured to start on boot.
The instance is associated with an IAM role to allow access to AWS Systems Manager (SSM) for management.*

**Amazon RDS (MySQL) Instance:**

*An RDS instance running MySQL 8.0.35 is created in the private subnets for high availability.
The instance is associated with the RDS subnet group and the RDS security group to control network access.*

**IAM Role and Instance Profile:**
An IAM role is created and associated with the EC2 instance to grant it permissions to use AWS Systems Manager.

**Key Points**
The EC2 instance hosts a web server (NGINX) accessible via the public subnet.
The RDS MySQL instance is isolated within private subnets and only accessible from the EC2 instance.
Security groups ensure controlled access to the EC2 and RDS instances.
An Internet Gateway provides internet access to resources in the public subnet.
The VPC and subnets provide network isolation and segmentation.
Usage
