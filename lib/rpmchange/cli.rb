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

      def spec_write!(spec)
        File.open(options['specfile'], 'w') {|f| f.write spec.dump}
      end
    end # << self

    @shared_options = {
      specfile: {type: :string, desc: "path to spec file", required: true},
    }

    desc "append_changelog", "Make a new changelog entry at the end of current entries"
    shared_options
    method_option :name, {type: :string, desc: "maintainer name", required: true}
    method_option :email, {type: :string, desc: "maintainer email", required: true}
    method_option :message, {type: :string, desc: "changelog message", required: true}
    def append_changelog
      spec = self.class.spec_construct options
      spec.append_changelog(name: options['name'],
                            email: options['email'],
                            message: options['message'])
      self.class.spec_write! spec
    end

    desc "tag", "Get or set spec tag"
    shared_options
    method_option :name, {type: :string, desc: "tag name", required: true}
    method_option :value, {type: :string, desc: "tag value"}
    def tag
      spec = self.class.spec_construct options
      if options['value']
        spec.set_tag(options['name'], options['value'])
        self.class.spec_write! spec
      else
        value = spec.tag(options['name'])
        puts value if value
      end
    end
  end # Cli
end # Rpmchange
