VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "trusty64"
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.provision "shell", inline: 'apt-get update && apt-get upgrade -y && apt-get install python-pip docker.io nginx -y && (cd /vagrant && pip install'
  config.ssh.username = 'root'
  config.ssh.password = 'vagrant'
  config.ssh.insert_key = 'true'
end
