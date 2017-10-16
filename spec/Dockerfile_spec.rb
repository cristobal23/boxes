require "serverspec"
require "docker"

describe "Dockerfile" do
  before(:all) do
    image = Docker::Image.build_from_dir('.', { 'dockerfile' => 'Dockerfile' })

    set :os, family: :linux
    set :backend, :docker
    set :docker_image, image.id
  end

  it "installs the right version of Alpine" do
    expect(os_version).to include("3.4.6")
  end

  def os_version
    command("cat /etc/alpine-release").stdout
  end
end
