import pulumi
import pulumi_aws as aws

# Create a VPC
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.0.0.0/16",       #specifies the IP address range for the VPC
    enable_dns_support=True,        #enables or disables DNS support within the VPC
    enable_dns_hostnames=True       #enables or disables the assignment of public DNS hostnames to instances with public IP addresses
)

# Create an Internet Gateway
internet_gateway = aws.ec2.InternetGateway("my-internet-gateway",
    vpc_id=vpc.id
)
    #Internet Gateway: An Internet Gateway is a horizontally scaled, redundant, 
    #and highly available VPC component that allows communication between instances in your VPC and the internet.


# Create a Public Subnet
#public-subnet" is the name assigned to this subnet for identification within your Pulumi project
public_subnet = aws.ec2.Subnet("public-subnet",
    vpc_id=vpc.id,                    #creates a new subnet resource in AWS
    cidr_block="10.0.4.0/24",
    map_public_ip_on_launch=True,     #it enables automatic assignment of public IP addresses to instances launched in this subnet
    availability_zone="ap-south-1a"
)

# Create Private Subnets
#Private Subnet: A private subnet is a subnet that does not automatically assign public IP addresses to instances. 
private_subnet_1 = aws.ec2.Subnet("private-subnet-1",       #aws.ec2.Subnet is the Pulumi class used to define a subnet.
    vpc_id=vpc.id,
    cidr_block="10.0.5.0/24",           #defines the range of IP addresses available in this subnet (from 10.0.5.0 to 10.0.5.255)
    availability_zone="ap-south-1a"
)

private_subnet_2 = aws.ec2.Subnet("private-subnet-2",
    vpc_id=vpc.id,
    cidr_block="10.0.6.0/24",
    availability_zone="ap-south-1b"
)

# Create a Route Table for the public subnet and associate it with the Internet Gateway
public_route_table = aws.ec2.RouteTable("public-route-table",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",         #0.0.0.0/0 represents all IP addresses, meaning this route will match any destination IP address.
        gateway_id=internet_gateway.id
    )]
)

aws.ec2.RouteTableAssociation("public-route-table-association",
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id
)

# Security Group for EC2 Instance with NGINX
ec2_security_group = aws.ec2.SecurityGroup("ec2-security-group",
    vpc_id=vpc.id,
    description="Allow HTTP and SSH traffic",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,         #This rule allows SSH traffic (TCP protocol on port 22) from any IP address (0.0.0.0/0).
            cidr_blocks=["0.0.0.0/0"]
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,         #This rule allows HTTP traffic (TCP protocol on port 80) from any IP address (0.0.0.0/0).
            cidr_blocks=["0.0.0.0/0"]
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"]       #his rule allows all outbound traffic (protocol -1 represents all protocols) to any IP address (0.0.0.0/0).
        )
    ]
)

# Security Group for RDS
#RDS Security Group: A security group for Amazon RDS instances to control inbound and outbound traffic.
#Ingress Rules: Define the incoming traffic that is allowed to reach the RDS instance.
#Egress Rules: Define the outgoing traffic that is allowed from the RDS instance.
rds_security_group = aws.ec2.SecurityGroup("rds-security-group",
    vpc_id=vpc.id,
    description="Allow MySQL traffic from EC2",         #This parameter provides a description for the security group.
                                                    #It allows MySQL traffic from EC2 describes the purpose of the security group.
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=3306,  #3306 port number of mysql
            to_port=3306,
            cidr_blocks=[public_subnet.cidr_block]
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"]           #This rule allows all outbound traffic (protocol -1 represents all protocols) to any IP address (0.0.0.0/0).
        )
    ]
)

# IAM Role for EC2 to use SSM
ec2_role = aws.iam.Role("ec2-role-unique",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
    }"""
)

#This sets up an IAM role that EC2 instances can assume, allowing them to gain the permissions associated with this role.
ec2_role_policy_attachment = aws.iam.RolePolicyAttachment("ec2-role-policy-attachment",
    role=ec2_role.name,
    policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
)

# Create an Instance Profile for the EC2 instance
ec2_instance_profile = aws.iam.InstanceProfile("ec2-instance-profile",
    role=ec2_role.name
)

# EC2 Instance with NGINX
ec2_instance = aws.ec2.Instance("nginx-instance",
    instance_type="t2.micro",
    ami="ami-0e306788ff2473ccb",
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[ec2_security_group.id],
    associate_public_ip_address=True,
    iam_instance_profile=ec2_instance_profile.id,
    user_data="""#!/bin/bash
    sudo yum update -y
    sudo amazon-linux-extras install nginx1 -y
    sudo systemctl start nginx
    sudo systemctl enable nginx
    """
)

# RDS Subnet Group
rds_subnet_group = aws.rds.SubnetGroup("rds-subnet-group",
    subnet_ids=[private_subnet_1.id, private_subnet_2.id],
    tags={
        "Name": "rds-subnet-group"
    }
)

# RDS Instance
rds_instance = aws.rds.Instance("my-rds",
    engine="mysql",
    engine_version="8.0.35",
    instance_class="db.t3.micro",  # Updated to a supported instance class
    allocated_storage=20,
    db_subnet_group_name=rds_subnet_group.name,
    vpc_security_group_ids=[rds_security_group.id],
    db_name="mydatabase",
    username="admin",
    password="password",
    skip_final_snapshot=True
)

# Output the public IP of the EC2 instance
pulumi.export("ec2_public_ip", ec2_instance.public_ip)
