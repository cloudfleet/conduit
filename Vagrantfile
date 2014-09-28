VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "trusty64"
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.provision "shell", path: 'scripts/bootstrap-vagrant.sh'
end
