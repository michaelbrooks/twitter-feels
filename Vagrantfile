# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "centos65-twitter-feels"
  config.vm.box_url = "http://sccl.hcde.washington.edu/~mjbrooks/vagrant/centos65-twitter-feels-20140311.box"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network :forwarded_port, guest: 80, host: 8080

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network :private_network, ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network :public_network

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  # config.ssh.forward_agent = true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"
  config.vm.synced_folder ".", "/home/vagrant/twitter-feels"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider :virtualbox do |vb|
    # Don't boot with headless mode
    vb.gui = true

    # Use VBoxManage to customize the VM. For example to change memory:
    vb.customize ["modifyvm", :id, "--memory", "1536"]
  end


  # Install Puppet
  config.vm.provision "shell", path: "scripts/provision/puppet.sh", :args => ['/vagrant']

  # A machine that does everything, the default
  config.vm.define "default", primary: true do |default|

    # Provision with Puppet
    config.vm.provision "puppet" do |puppet|
      puppet.options = ""
      puppet.manifest_file = "default.pp"
      puppet.manifests_path = "scripts/provision/manifests"
      puppet.facter = {
          "user_name" => "vagrant",
          "user_home" => "/home/vagrant",
          "project_dir" => "/home/vagrant/twitter-feels",
          "scripts_dir" => "/home/vagrant/twitter-feels/scripts",
          "django_environment" => 'dev',
          "app_name" => "twitter-feels"
      }
    end
  end

  # Provisions a base box
  config.vm.define "base_box" do |base_box|

    # Get the basic centos box
    config.vm.box = "centos65"
    config.vm.box_url = "https://github.com/2creatives/vagrant-centos/releases/download/v6.5.3/centos65-x86_64-20140116.box"

    # Don't sync to the home folder
    config.vm.synced_folder ".", "/home/vagrant/twitter-feels", disabled: true

    # Provision with Puppet
    config.vm.provision "puppet" do |puppet|
      puppet.options = ""
      puppet.manifest_file = "base_box.pp"
      puppet.manifests_path = "scripts/provision/manifests"
      puppet.facter = {
          "user_name" => "vagrant",
          "user_home" => "/home/vagrant",
          "project_dir" => "/home/vagrant/twitter-feels",
          "scripts_dir" => "/vagrant/scripts",
          "django_environment" => 'dev',
          "app_name" => "twitter-feels"
      }
    end
  end

end
