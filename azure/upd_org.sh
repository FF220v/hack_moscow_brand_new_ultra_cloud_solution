#!/bin/bash 
id=$1
name='org'${id}
root='/home/speedwagon/azure'
cd $root
root=${root}/${name}
src='/home/speedwagon/azure/src'
yes | cp -i ${src}'/storage_client.py' ${root}
yes | cp -i ${src}'/init/__init__.py' ${root}'/init'
yes | cp -i ${src}'/queuer/__init__.py' ${root}'/queuer'
yes | cp -i ${src}'/exec/__init__.py' ${root}'/exec'