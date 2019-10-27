#!/bin/bash 
id=$1
name='org'${id}
root='/home/speedwagon/azure'
cd $root
root=${root}/${name}
mkdir $name
cd $root
func init --worker-runtime python
func new --language python --name init --template 'HTTP trigger'
func new --language python --name queuer --template 'HTTP trigger'
func new --language python --name exec --template 'HTTP trigger'
src='/home/speedwagon/azure/src'
cp ${src}'/storage_client.py' ${root}
cp ${src}'/init/__init__.py' ${root}'/init'
cp ${src}'/queuer/__init__.py' ${root}'/queuer'
cp ${src}'/exec/__init__.py' ${root}'/exec'
cat ${src}'/requirements.txt' >> ${root}'/requirements.txt'