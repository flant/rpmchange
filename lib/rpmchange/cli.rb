module Rpmchange
  class Cli < ::Thor
    class << self
      def shared_options
        (@shared_options || {}).each do |name, options|
          method_option name, options
        end
      end

      def spec_construct(options)
        Spec.loadfile(options['specfile'])
      end

      def spec_write!(spec, options)
        File.open(options['specfile'], 'w') {|f| f.write spec.dump}
      end
    end # << self

    @shared_options = {
      specfile: {type: :string, desc: "path to spec file", required: true},
    }

    desc "changelog", "get changelog entries or " +
                      "make a new changelog entry at the end of current entries"
    shared_options
    method_option :name, {type: :string, desc: "maintainer name"}
    method_option :email, {type: :string, desc: "maintainer email"}
    method_option :message, {type: :string, desc: "changelog message"}
    method_option :append, {type: :boolean, desc: "append new changelog entry"}
    def changelog
      spec = self.class.spec_construct options
      if options['append']
        spec.append_changelog(name: options['name'],
                              email: options['email'],
                              message: options['message'])
        self.class.spec_write! spec, options
      else
        puts spec.changelog_lines
      end
    end

    desc "tag", "get or set spec tag"
    shared_options
    method_option :name, {type: :string, desc: "tag name", required: true}
    method_option :value, {type: :string, desc: "tag value"}
    def tag
      spec = self.class.spec_construct options
      if options['value']
        spec.set_tag(options['name'], options['value'])
        self.class.spec_write! spec, options
      else
        if value = spec.tag(options['name'])
          puts value
        else
          exit(1)
        end
      end
    end

    desc "patch", "append patch"
    shared_options
    method_option :name, {type: :string, desc: "patch name", required: true}
    def patch
      spec = self.class.spec_construct options
      spec.append_patch(options['name'])
      self.class.spec_write! spec, options
    end
  end # Cli
end # Rpmchange
