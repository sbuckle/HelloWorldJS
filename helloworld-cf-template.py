"""Generating CloudFormation template"""
from troposphere import (
        Base64,
        ec2,
        GetAtt,
        Join,
        Output,
        Parameter,
        Ref,
        Template,
)

ApplicationPort = "3000"

t = Template()
t.add_description("Effective DevOps in AWS: HelloWorld web application")

t.add_parameter(Parameter(
        "KeyPair",
        Description="Name of an existing EC2 KeyPair",
        Type="AWS::EC2::KeyPair::KeyName",
        ConstraintDescription="must be the name of an existing EC2 keypair",
))

t.add_resource(ec2.SecurityGroup(
        "SecurityGroup",
        GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
        SecurityGroupIngress=[
                ec2.SecurityGroupRule(
                        IpProtocol="tcp",
                        FromPort="22",
                        ToPort="22",
                        CidrIp="0.0.0.0/0",
                ),
                ec2.SecurityGroupRule(
                        IpProtocol="tcp",
                        FromPort=ApplicationPort,
                        ToPort=ApplicationPort,
                        CidrIp="0.0.0.0/0",
                ),
        ],
))

ud = Base64(Join('\n', [
        "#!/bin/bash",
        "amazon-linux-extras install epel",
        "yum install -y nodejs",
        "wget https://bit.ly/3q8ADwr -O /home/ec2-user/helloworld.js",
        "wget https://bit.ly/38wyJjk -O /etc/systemd/system/helloworld.service",
        "systemctl daemon-reload",
        "systemctl enable helloworld",
        "systemctl start helloworld"
]))

t.add_resource(ec2.Instance(
        "instance",
        ImageId="ami-0e80a462ede03e653",
        InstanceType="t2.micro",
        SecurityGroups=[Ref("SecurityGroup")],
        KeyName=Ref("KeyPair"),
        UserData=ud,
))

t.add_output(Output(
        "InstancePublicIp",
        Description="Public IP of EC2 instance",
        Value=GetAtt("instance", "PublicIp"),
))

t.add_output(Output(
        "WebUrl",
        Description="Application endpoint",
        Value=Join("", [
                "http://", GetAtt("instance", "PublicDnsName"),
                ":", ApplicationPort
        ]),
))

print(t.to_yaml())
