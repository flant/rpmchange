require 'bundler/setup'

Bundler.setup

require 'rpmchange'

module SpecHelper
  module Common
    def spec_loadfile(path)
      ::Rpmchange::Spec.loadfile(path)
    end

    def spec_load(str)
      ::Rpmchange::Spec.load(str)
    end
  end # Common

  module Fixture
    def fixture_rpmspec_dir_path
      Pathname.new(__FILE__).dirname.join('fixture').join('rpmspec').expand_path
    end

    def fixture_rpmspec_paths
      Dir[fixture_rpmspec_dir_path.join('*.spec')].map {|path| Pathname.new(path).expand_path}
    end

    def fixture_rpmspec_each(&blk)
      fixture_rpmspec_paths.each do |path|
        yield spec_loadfile(path), path
      end
    end
  end # Fixture
end # SpecHelper
